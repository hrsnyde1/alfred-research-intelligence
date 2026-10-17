"""Dedicated conversation registry and test transport, never a messaging gateway."""
from dataclasses import replace
from ..contracts import ENVIRONMENTS, OutboxEvent, hash_content, require
from ..tenancy import AuthorizationError
from ..research.journal import WorkflowJournal
from ..memory import DeliveryAmbiguous
from .contracts import Conversation, Notice, NoticeState, TransportReceipt, Intake, FlowResult

LABELS = dict(zip(ENVIRONMENTS, ('Personal Alfred Research','Gabos Holdings Research',
                               'Fintra AI Research','SC Products Group Research')))

class ConversationRegistry:
    def __init__(self, authority, conversations, contexts, *, test_only=False):
        if test_only is not True:
            raise AuthorizationError('production conversation authorization unavailable')
        self.authority, self.contexts = authority, dict(contexts)
        require(len(conversations) == 4 and {c.environment for c in conversations} == set(ENVIRONMENTS),
                'four independent Research conversations required')
        self.configurations = {}
        for c in conversations:
            require(type(c) is Conversation and c.label == LABELS[c.environment] and
                    c.conversation_id not in self.configurations, 'invalid/ambiguous conversation configuration')
            for principal in (c.requester, c.recipient):
                context = self.contexts.get(principal)
                authority.authorize(context, env=c.environment)
                require(context.principal == principal, 'conversation principal substitution')
            require(bool(c.source_kinds) and set(c.source_kinds) <= {'github','website','article','pdf','document','youtube','instagram','tiktok','x'},
                    'unknown source permission')
            self.configurations[c.conversation_id] = c

    def authenticate(self, context, message):
        self.authority.authorize(context, env=message.environment, roles=('director','researcher'))
        c = self.configurations.get(message.conversation_id)
        if c is None or c.environment != context.environment or c.requester != context.principal or message.requester != context.principal:
            raise AuthorizationError('wrong conversation, requester or company')
        require(message.sources[0].kind in c.source_kinds, 'source kind not authorized for conversation')
        return c

    def route(self, context, notice):
        self.authority.authorize(context, env=notice.environment, roles=('director',))
        c = self.configurations.get(notice.conversation_id)
        if c is None or c.environment != notice.environment or c.recipient != notice.recipient:
            raise AuthorizationError('notice conversation/recipient scope mismatch')
        return c

class FakeConversationTransport:
    def __init__(self, store, registry, *, test_only=False, auto_confirm=True, hook=None):
        if test_only is not True or type(registry) is not ConversationRegistry:
            raise AuthorizationError('only test conversation transport available')
        require(registry.authority is store._authority and type(auto_confirm) is bool, 'transport authority mismatch')
        self.registry, self.journal = registry, WorkflowJournal(store._root, store._authority)
        self.auto_confirm, self.hook = auto_confirm, hook or (lambda stage: None)

    def _namespace(self, notice): return 'transport-' + notice.notification_id

    def lookup(self, context, notice):
        self.registry.route(context, notice)
        namespace = self._namespace(notice)
        receipt = self.journal.load(context,namespace,'packet:delivered',TransportReceipt) or self.journal.load(context,namespace,'packet:accepted',TransportReceipt)
        if receipt is not None:
            require(receipt.notice_digest == hash_content(notice) and receipt.notification_id == notice.notification_id and
                    receipt.conversation_id == notice.conversation_id and receipt.recipient == notice.recipient,
                    'transport receipt binding mismatch')
        return receipt

    def send(self, context, notice):
        self.registry.route(context, notice)
        namespace = self._namespace(notice)
        self.journal.provision(context,namespace)
        with self.journal.lock(context,namespace):
            previous = self.lookup(context,notice)
            if previous is not None: return previous
            receipt = TransportReceipt(environment=notice.environment,notification_id=notice.notification_id,
                notice_digest=hash_content(notice),conversation_id=notice.conversation_id,recipient=notice.recipient,state='ACCEPTED')
            self.journal.commit(context,namespace,'packet:accepted',receipt)
            self.hook('transport_accept')
            return receipt

    def confirm(self, context, notice):
        namespace = self._namespace(notice)
        self.registry.route(context,notice)
        with self.journal.lock(context,namespace):
            receipt = self.lookup(context,notice)
            require(receipt is not None, 'cannot confirm an unsent notification')
            if receipt.state == 'DELIVERED' or not self.auto_confirm: return receipt
            delivered = replace(receipt,state='DELIVERED')
            self.journal.commit(context,namespace,'packet:delivered',delivered)
            self.hook('transport_delivery')
            return delivered

class Notifications:
    def __init__(self, store, registry, transport, *, hook=None):
        require(type(transport) is FakeConversationTransport and transport.registry is registry, 'fake notification transport required')
        self.store, self.registry, self.transport = store, registry, transport
        self.memory = None  # Bound only by trusted offline workflow bootstrap.
        self.journal = WorkflowJournal(store._root,store._authority)
        self.hook = hook or (lambda stage: None)

    def _namespace(self, notice): return 'notice-' + notice.notification_id

    def _state(self, context, namespace, notice, state, attempt):
        value = NoticeState(environment=notice.environment,notification_id=notice.notification_id,state=state,attempt=attempt)
        return self.journal.commit(context,namespace,f'packet:state:{state}:{attempt}',value)

    def deliver(self, context, notice, *, result=None):
        self.registry.route(context, notice)
        if notice.kind == 'FINAL':
            require(self.memory is not None, 'current completion validation unavailable')
            namespace = 'flow-' + hash_content(notice.research_task_id)
            result = result or self.journal.load(context,namespace,'packet:result',FlowResult)
            require(result is not None, 'workflow result required')
            if not result.receipts:
                return self._deliver_reconciled(context,notice,result=result)
            with self.memory.completion_snapshot(context,result.receipts) as receipts:
                require(receipts == result.receipts, 'stale final notification denied')
                return self._deliver_reconciled(context,notice,result=result)
        return self._deliver_reconciled(context,notice)

    def _deliver_reconciled(self, context, notice, *, result=None):
        # Internal caller holds the Memory completion snapshot through delivery.
        # Public replay always enters deliver(), which rechecks current receipts.
        configuration = self.registry.route(context,notice)
        task = self.store.get_task(context,notice.research_task_id)
        require(task.environment == notice.environment, 'notification task scope mismatch')
        flow_namespace = 'flow-' + hash_content(task.task_id)
        origin = self.journal.load(context,flow_namespace,'packet:origin',Intake)
        require(origin is not None and origin.request == task.request and
                origin.message.conversation_id == notice.conversation_id and
                origin.message.requester == configuration.requester, 'notification lacks authenticated conversation origin')
        if notice.kind == 'ACK':
            require(notice.message == 'SIMULATED: Research request received.' and not notice.receipt_refs,
                    'acknowledgment cannot claim downstream completion')
        else:
            from .coordinator import ResearchWorkflow
            original = self.journal.load(context,flow_namespace,'packet:result',FlowResult)
            result = original if result is None else result
            projected = None if result is None else self.journal.load(context,flow_namespace,
                'packet:final-result:' + hash_content(result),FlowResult)
            require(original is not None and projected == result and
                    result.environment == original.environment and result.requester == original.requester and
                    result.research_task_id == original.research_task_id and
                    result.conversation_id == original.conversation_id and
                    result.record_id == original.record_id and result.proposals == original.proposals and
                    all(r in original.receipts for r in result.receipts), 'authorized reconciled result required')
            require(result is not None and result.research_task_id == task.task_id and
                    result.conversation_id == notice.conversation_id and
                    notice.message == ResearchWorkflow.completion_text(result) and
                    notice.receipt_refs == tuple(r.receipt_id for r in result.receipts),
                    'final notification must match durable receipt-based workflow result')
        namespace = self._namespace(notice)
        self.journal.provision(context,namespace)
        with self.journal.lock(context,namespace):
            self.journal.commit(context,namespace,'packet:notice',notice)
            self._state(context,namespace,notice,'PREPARED',0)
            self.store.enqueue(context,OutboxEvent(environment=notice.environment,event_id='notice-'+notice.notification_id,
                task_id=notice.research_task_id,topic='offline.notification.'+notice.kind.lower(),payload_digest=hash_content(notice)))
            self.hook('notification_prepare')
            states = self.journal.records(context,namespace,'packet:state:',NoticeState)
            attempt = max((s.attempt for s in states),default=0)
            try:
                # Lookup is authoritative within this deterministic fake. An
                # unavailable lookup never means safe-to-resend.
                receipt = self.transport.lookup(context,notice)
                if receipt is None:
                    if attempt >= 3:
                        self._state(context,namespace,notice,'FAILED',attempt)
                        return None
                    attempt += 1
                    self._state(context,namespace,notice,'SENDING',attempt)
                    receipt = self.transport.send(context,notice)
                self._state(context,namespace,notice,'ACCEPTED',attempt)
                self.hook('notification_accept')
                if receipt.state != 'DELIVERED': receipt = self.transport.confirm(context,notice)
                if receipt.state == 'DELIVERED':
                    self._state(context,namespace,notice,'DELIVERED',attempt)
                    self.store.record_delivery(context,'notice-'+notice.notification_id,delivered=True)
                    self.hook('notification_delivery')
                return receipt
            except DeliveryAmbiguous:
                self._state(context,namespace,notice,'UNKNOWN',attempt)
                return None

    def states(self, context, notice):
        self.registry.route(context,notice)
        return self.journal.records(context,self._namespace(notice),'packet:state:',NoticeState)
