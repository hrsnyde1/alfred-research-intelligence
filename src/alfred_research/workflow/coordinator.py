"""On-demand integration of accepted Research modules; no global scheduler."""
from dataclasses import replace
from ..contracts import ResearchRequest, hash_content, require, ContractError
from ..tenancy import AuthorizationError
from ..budgets import EscalationRequired
from ..research.journal import WorkflowJournal
from ..sources import SourceProcessor, SourceResult
from ..memory import MemoryCommand, MemoryReceipt, RetrievalResult, KnowledgeCandidate, FakeMemoryAdapter
from ..memory.contracts import MUTATIONS
from ..memory.fake import DeliveryAmbiguous
from ..persistence import PersistenceError
from ..intelligence import Proposal
from .contracts import Intake, FixtureSnapshot, Stage, FlowResult, Notice

INDEX = 'phase6-authenticated-intakes-v1'

class ResearchWorkflow:
    def __init__(self, registry, director, verifier, organizer, memory, notifications, options,
                 readers, *, hook=None, test_only=False):
        if test_only is not True: raise AuthorizationError('only offline Research integration enabled')
        require(type(memory) is FakeMemoryAdapter, 'only accepted test Memory adapter is enabled')
        self.registry, self.director, self.verifier = registry, director, verifier
        self.organizer, self.memory, self.notifications = organizer, memory, notifications
        self.store, self.authority = director.store, director.authority
        require(registry.authority is self.authority and organizer.store is self.store and memory.store is self.store and
                notifications.store is self.store and verifier.store is self.store, 'workflow must reuse one trusted foundation')
        require(notifications.memory is None or notifications.memory is memory, 'notification Memory boundary mismatch')
        notifications.memory = memory
        self.options, self.readers = dict(options), {e:tuple(v) for e,v in readers.items()}
        require(set(self.options) == set(memory.services), 'four configured environment policies required')
        for env, contexts in self.readers.items():
            for context in contexts: self.authority.authorize(context,env=env)
        self.journal = WorkflowJournal(self.store._root,self.authority)
        self.hook = hook or (lambda stage: None)

    def _namespace(self, task_id): return 'flow-' + hash_content(task_id)

    def _service(self, env): return self.memory.services[env]

    def _step(self, context, namespace, name, cls, action):
        key = 'packet:flow:' + name
        value = self.journal.load(context,namespace,key,cls)
        if value is None:
            value = action()
            self.hook(name + ':effect')
            self.journal.commit(context,namespace,key,value)
            self.hook(name)
        return value

    def _reference(self, context, namespace, task, name, action):
        def invoke():
            value = action()
            return Stage(environment=task.environment,research_task_id=task.task_id,name=name,
                         reference=hash_content(value))
        return self._step(context,namespace,name,Stage,invoke)

    def _notice(self, service, configuration, task_id, kind, message, receipts=()):
        notice = Notice(environment=configuration.environment,research_task_id=task_id,
            conversation_id=configuration.conversation_id,recipient=configuration.recipient,kind=kind,
            message=message,receipt_refs=tuple(r.receipt_id for r in receipts))
        self.notifications.deliver(service,notice)
        return notice

    def run(self, context, message, fixture):
        configuration = self.registry.authenticate(context,message)
        options = self.options[configuration.environment]
        service = self._service(configuration.environment)
        request = ResearchRequest(environment=configuration.environment,
            request_id='conversation-' + hash_content((configuration.conversation_id,message.message_id)),
            requested_by=context.principal,objective=message.objective,sources=message.sources,max_retries=options.max_retries)
        intake = Intake(environment=configuration.environment,message=message,fixture=FixtureSnapshot.capture(fixture),
            options=options,configuration_digest=hash_content((configuration.payload(),options.payload())),request=request)
        self.journal.provision(service,INDEX)
        with self.journal.lock(service,INDEX):
            prior = self.journal.load(service,INDEX,'packet:'+request.request_id,Intake)
            require(prior is not None or len(self.journal.records(service,INDEX,'packet:',Intake)) < 128,
                    'bounded offline intake inventory exhausted')
            self.journal.commit(service,INDEX,'packet:'+request.request_id,intake)
        self.hook('intake_intent')
        task = self.store.submit(context,request)
        self.hook('intake_task')
        namespace = self._namespace(task.task_id)
        self.journal.provision(service,namespace)
        with self.journal.lock(service,namespace):
            self.journal.commit(service,namespace,'packet:origin',intake)
            self._notice(service,configuration,task.task_id,'ACK','SIMULATED: Research request received.')
            self.hook('acknowledgment')
            result = self.journal.load(service,namespace,'packet:result',FlowResult)
            if result is None:
                result = self._process(service,configuration,task,fixture,options,namespace)
                self.journal.commit(service,namespace,'packet:result',result)
                self.hook('result')
            result = self._finalize(service, configuration, namespace, result)
            self.hook('completion')
            return result

    def _finalize(self, service, configuration, namespace, original):
        def deliver(receipts):
            require(type(receipts) is tuple and all(r in original.receipts for r in receipts),
                    'invalid completion reconciliation')
            result = original if receipts == original.receipts else replace(original,
                receipts=receipts, outcome='PARTIAL', reason='INCOMPLETE')
            self.journal.commit(service, namespace, 'packet:final-result:' + hash_content(result), result)
            notice = Notice(environment=configuration.environment,research_task_id=result.research_task_id,
                conversation_id=configuration.conversation_id,recipient=configuration.recipient,kind='FINAL',
                message=self.completion_text(result),receipt_refs=tuple(r.receipt_id for r in result.receipts))
            previous = self.notifications.journal.load(service,self.notifications._namespace(notice),
                                                       'packet:notice',Notice)
            # A prepared/accepted/delivered notice is immutable. No update channel
            # exists in Phase 6: return the corrected result without resending or
            # confirming an obsolete message (including ambiguous transport state).
            if previous is None or previous == notice:
                self.notifications._deliver_reconciled(service,notice,result=result)
            return result
        if not original.receipts:
            return deliver(())
        snapshot = getattr(self.memory, 'completion_snapshot', None)
        try:
            require(callable(snapshot), 'completion reconciliation unavailable')
            current = snapshot(service, original.receipts)
            require(hasattr(current, '__enter__') and hasattr(current, '__exit__'),
                    'completion snapshot unresolved')
            with current as receipts:
                return deliver(receipts)
        except (ContractError, AuthorizationError, DeliveryAmbiguous, PersistenceError, EscalationRequired):
            return deliver(())  # No current receipt-based success claims can be confirmed.

    def recover(self, context):
        self.authority.authorize(context,roles=('director','researcher'))
        service = self._service(context.environment)
        intakes = self.journal.records(service,INDEX,'packet:',Intake)
        # Includes tasks whose Research verdict is terminal but whose delivery
        # stages or notifications were interrupted. No background polling.
        return tuple(self.run(context,i.message,i.fixture.restore()) for i in intakes if i.message.requester == context.principal)

    def _memory_step(self, service, namespace, candidate, operation, sequence=0, prerequisite=None):
        operation_id = namespace + ':' + operation
        def perform():
            rows = self.memory.history(service,service.environment)
            existing = next((e.receipt for e in rows if e.receipt.operation_id == operation_id),None)
            if existing is not None:
                require(existing.record_digest == hash_content(candidate.record) and existing.operation == operation and
                        existing.actor == service.principal and existing.record_version == candidate.record_version,
                        'recovered Memory receipt binding mismatch')
                return existing
            if operation in ('commit','promote'):
                state,_ = self.memory._state(rows,candidate.record.record_id)
                if state in (('COMMITTED','PROMOTED') if operation == 'commit' else ('PROMOTED',)):
                    old = next((e.receipt for e in reversed(rows) if e.receipt.record_id == candidate.record.record_id and
                                e.receipt.operation == operation and e.receipt.outcome == 'SUCCESS'),None)
                    require(old is not None, 'existing lifecycle state lacks receipt')
                    return old
            fields = {}
            if operation in ('request_export','export_status','sync_status'):
                fields = dict(export_attempt=(namespace+':request_export',),
                    export_destination=('test-obsidian:'+service.environment,),export_record_version=(candidate.record_version,),
                    prerequisite_receipt=() if prerequisite is None else (prerequisite.receipt_id,))
            command = MemoryCommand(environment=service.environment,record_id=candidate.record.record_id,
                record_digest=hash_content(candidate.record),operation=operation,operation_id=operation_id,
                expected_sequence=sequence,fixture_result=self.options[service.environment].outcome(operation),**fields)
            return getattr(self.memory,operation)(service,command)
        def reconcile_receipt(receipt):
            reconcile = getattr(self.memory, 'reconcile_receipt', None)
            require(callable(reconcile), 'Memory receipt reconciliation unavailable')
            require(reconcile(service, receipt) == receipt, 'Memory receipt reconciliation unresolved')
            return receipt
        receipt = self._step(service,namespace,'memory_'+operation,MemoryReceipt,
                             lambda: reconcile_receipt(perform()))
        return reconcile_receipt(receipt)

    def _retrieve(self, service, namespace, candidate):
        operation_id = namespace+':retrieve'
        def perform():
            reader = next((c for c in self.readers.get(service.environment,())
                           if self._can_read(c,candidate.record)),None)
            if reader is None: raise AuthorizationError('no authorized specialist retrieval binding')
            rows = self.memory.history(service,service.environment)
            require(self.memory._state(rows,candidate.record.record_id)[0] == 'PROMOTED', 'record no longer promoted')
            self.memory._live(service,candidate)
            receipt = next((e.receipt for e in rows if e.receipt.operation_id == operation_id),None)
            if receipt is not None:
                require(receipt.actor == reader.principal and receipt.operation == 'retrieve' and receipt.outcome == 'SUCCESS' and
                        receipt.record_digest == hash_content(candidate.record), 'recovered retrieval mismatch')
                return RetrievalResult(environment=service.environment,candidate=candidate,receipt=receipt)
            command = MemoryCommand(environment=service.environment,record_id=candidate.record.record_id,
                record_digest=hash_content(candidate.record),operation='retrieve',operation_id=operation_id)
            return self.memory.retrieve(reader,command)
        return self._step(service,namespace,'retrieval',RetrievalResult,perform)

    def _can_read(self, context, record):
        try:
            self.memory.access.specialist(context,record)
            return True
        except AuthorizationError: return False

    def _process(self, service, configuration, task, fixture, options, namespace):
        steps, receipts, proposals, record_ids = [], [], (), ()
        outcome = 'COMPLETED'
        reason = 'NONE'
        try:
            def deadline():
                if self.director.clock() >= options.policy.deadline:
                    raise EscalationRequired('workflow deadline exhausted')
            deadline()
            def source_action():
                processor = SourceProcessor(self.authority)
                source = task.request.sources[0]
                grant = processor.grant(service,service,source,origins=(fixture.origin,))
                return processor.process(service,source,fixture,grant)
            source = self._step(service,namespace,'source',SourceResult,source_action)
            steps.append('source:'+source.outcome)
            if source.outcome not in ('SUPPORTED_FETCHED','PARTIAL') or not source.evidence:
                raise EscalationRequired('source inaccessible or no usable evidence')
            deadline()
            self.director.plan(service,task.task_id,source,options.policy)
            packet_reference = self._reference(service,namespace,task,'research',lambda:self.director.run(service,task.task_id,source))
            packet = self.store.get_packet(service,task.task_id)
            require(packet_reference.reference == hash_content(packet), 'changed research packet')
            steps.append('research')
            deadline()
            verifier_context = self.verifier.roster.context(self.verifier.roster.select(service.environment,'verifier'))
            self._reference(service,namespace,task,'verification',lambda:self.verifier.verify(verifier_context,task.task_id,packet.packet_version,packet.digest))
            verdicts = self.store.verification_history(service,task.task_id,packet.packet_version)
            require(len(verdicts) == 1 and verdicts[0].packet_digest == packet.digest, 'exact authoritative verdict required')
            verdict = verdicts[0].verdict
            steps.append('verification:'+verdict)
            if verdict != 'APPROVED':
                outcome = verdict
            else:
                deadline()
                from ..intelligence import Batch
                batch = self._step(service,namespace,'intelligence',Batch,
                    lambda:self.organizer.process(service,task.task_id,packet.packet_version,packet.digest,namespace,valid_until=options.valid_until))
                record_ids = (batch.record.record_id,)
                proposals = batch.proposals
                primary = batch.record.classification.primary
                if not primary.startswith('Development:'):
                    proposals += (Proposal(environment=service.environment,proposal_id=hash_content((namespace,'generic',primary)),
                        department=primary,capability='source',specialist='proposed:'+primary,
                        source_revision=source.revision,source_digest=source.digest,evidence_ids=tuple(e.evidence_id for e in source.evidence)),)
                steps.append('intelligence')
                candidate = self._step(service,namespace,'candidate',KnowledgeCandidate,
                    lambda:self.memory.candidate(service,batch.record.record_id,namespace+':submit'))
                submitted = self._step(service,namespace,'memory_submit',MemoryReceipt,lambda:self.memory.submit(service,candidate))
                receipts.append(submitted); deadline()
                committed = self._memory_step(service,namespace,candidate,'commit',submitted.sequence)
                receipts.append(committed)
                if committed.outcome != 'SUCCESS': raise EscalationRequired('Memory commit incomplete')
                deadline()
                promoted = self._memory_step(service,namespace,candidate,'promote',committed.sequence)
                receipts.append(promoted)
                if promoted.outcome != 'SUCCESS': raise EscalationRequired('Memory promotion incomplete')
                deadline()
                retrieval = self._retrieve(service,namespace,candidate)
                receipts.append(retrieval.receipt); steps.append('specialist_view')
                if configuration.environment != 'personal' and options.hq_eligible:
                    deadline()
                    allowed = self._memory_step(service,namespace,candidate,'hq_allow')
                    receipts.append(allowed)
                    synced = self._memory_step(service,namespace,candidate,'hq_sync')
                    receipts.append(synced)
                    if synced.outcome != 'SUCCESS' or synced.state != 'HQ_SYNCED': raise EscalationRequired('HQ synchronization incomplete')
                if options.export_selected:
                    deadline()
                    requested = self._memory_step(service,namespace,candidate,'request_export')
                    receipts.append(requested)
                    if requested.outcome != 'SUCCESS': raise EscalationRequired('export request incomplete')
                    exported = self._memory_step(service,namespace,candidate,'export_status',prerequisite=requested)
                    receipts.append(exported)
                    if exported.outcome != 'SUCCESS': raise EscalationRequired('export incomplete')
                    synced = self._memory_step(service,namespace,candidate,'sync_status',prerequisite=exported)
                    receipts.append(synced)
                    if synced.outcome != 'SUCCESS': raise EscalationRequired('Obsidian Sync incomplete')
        except (DeliveryAmbiguous, PersistenceError):
            outcome = 'PARTIAL' if receipts or record_ids else 'BLOCKED'
            reason = 'INCOMPLETE'
        except EscalationRequired as exc:
            outcome = 'PARTIAL' if receipts or record_ids else 'BLOCKED'
            text = str(exc).lower()
            reason = ('RESOURCE_LIMIT' if 'budget' in text or 'deadline' in text else
                      'SOURCE_UNAVAILABLE' if 'source' in text else 'INCOMPLETE')
        except (ContractError, AuthorizationError) as exc:
            outcome = 'PARTIAL' if receipts or record_ids else 'BLOCKED'
            reason = 'AUTHORIZATION' if isinstance(exc,AuthorizationError) else 'VALIDATION'
        return FlowResult(environment=service.environment,research_task_id=task.task_id,
            conversation_id=configuration.conversation_id,requester=task.request.requested_by,outcome=outcome,
            steps=tuple(steps),receipts=tuple(receipts),record_id=record_ids,proposals=proposals,reason=reason)

    @staticmethod
    def completion_text(result):
        successes = {r.operation for r in result.receipts if r.outcome == 'SUCCESS'}
        pieces = ['SIMULATED: '+result.outcome.lower()+'.']
        if result.reason == 'RESOURCE_LIMIT': pieces.append('Budget/deadline limit.')
        if result.reason == 'SOURCE_UNAVAILABLE': pieces.append('Source unavailable; no transcript invented.')
        if {'commit','promote','retrieve'} <= successes: pieces.append('Memory commit/promotion/read receipts recorded.')
        elif 'promote' in successes: pieces.append('Memory promotion receipt; retrieval incomplete.')
        elif 'commit' in successes: pieces.append('Memory commit receipt; promotion incomplete.')
        else: pieces.append('No confirmed Memory promotion/read.')
        if any(r.operation=='hq_sync' and r.outcome=='SUCCESS' and r.state=='HQ_SYNCED' for r in result.receipts): pieces.append('HQ sync receipt recorded.')
        if 'export_status' in successes: pieces.append('Export receipt recorded.')
        if 'sync_status' in successes: pieces.append('Obsidian Sync receipt recorded.')
        return ' '.join(pieces)
