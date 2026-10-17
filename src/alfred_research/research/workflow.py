"""On-demand Research coordination, durable synthetic calls and independent review.

No scheduler, live provider, Memory promotion, developer routing or host ingress.
"""
from dataclasses import replace
import time

from ..contracts import (Claim, Evidence, ResearchPacket, VerificationDecision, require, hash_content)
from ..sources.contracts import SourceResult
from ..tenancy import AuthorizationError
from ..budgets import EscalationRequired
from .contracts import (SPECIALTIES, SIMULATION, ResearchAgent, ResearchPolicy, ResearchPlan,
    ResearchDraft, VerifierProposal, ModelInvocation, ClaimTrace, PacketPreparation,
    ClaimAssessment, VerificationReview)
from .provider import SyntheticModelProvider
from .journal import WorkflowJournal
from .execution import execute_invocation


def classify(objective, kind):
    """Only the authenticated request objective and source kind influence routing."""
    import re
    words = set(re.findall(r'[a-z]+', objective.lower()))
    groups = (('finance_tax', {'tax', 'taxation', 'finance', 'financial', 'accounting'}),
              ('legal_compliance', {'legal', 'compliance', 'law', 'contract', 'regulation'}),
              ('business_market', {'business', 'market', 'marketing', 'competitor', 'sales'}),
              ('technology_code', {'code', 'technology', 'software', 'repository', 'programming'}))
    matches = [specialty for specialty, tokens in groups if words & tokens]
    if not matches:
        matches = ['technology_code' if kind == 'github' else 'general']
    return matches[0], tuple(matches[1:])


class AgentRoster:
    """Explicit trusted bootstrap; never populated from source/model text."""
    def __init__(self, authority, models, agents, contexts):
        self.authority, self.models = authority, models
        self.agents, self.contexts = {}, dict(contexts)
        for agent in agents:
            require(type(agent) is ResearchAgent, 'validated agent required')
            key = (agent.environment, agent.role, agent.specialty if agent.role == 'researcher' else 'general')
            require(key not in self.agents, 'ambiguous agent assignment')
            context = self.contexts.get(agent.principal)
            authority.authorize(context, agent.environment, (agent.role,))
            require(context.principal == agent.principal, 'roster principal mismatch')
            self.resolve(agent)
            self.agents[key] = agent

    def resolve(self, agent):
        fixed = self.models.resolve(agent.environment, agent.role, agent.model.provider, agent.model.model)
        require(fixed == agent.model, 'agent approval/price/model differs from fixed configuration')
        return fixed

    def select(self, env, role, specialty='general'):
        agent = self.agents.get((env, role, specialty))
        if agent is None:
            raise EscalationRequired('missing explicitly approved logical agent assignment')
        self.resolve(agent)
        return agent

    def context(self, agent):
        context = self.contexts[agent.principal]
        self.authority.authorize(context, agent.environment, (agent.role,))
        return context


class _Runtime:
    def __init__(self, authority, store, roster, provider, *, clock=time.time, production=False):
        if production or type(provider) is not SyntheticModelProvider:
            raise AuthorizationError('only deterministic synthetic model execution is enabled')
        require(roster.authority is authority and store._authority is authority and
                roster.models is store._models, 'workflow must reuse trusted store authority/model policy')
        self.authority, self.store, self.roster, self.provider = authority, store, roster, provider
        self.clock = clock
        self.journal = WorkflowJournal(store._root, authority)

    def _deadline(self, policy):
        if self.clock() >= policy.deadline:
            raise EscalationRequired('research deadline exhausted; no further work authorized')

    def _source(self, task, source):
        require(type(source) is SourceResult and source.environment == task.environment and
                source.submitted == task.request.sources[0], 'source does not belong to original task')
        if source.outcome not in ('SUPPORTED_FETCHED', 'PARTIAL') or not source.evidence:
            raise EscalationRequired('source has no authorized usable evidence; no conclusions fabricated')
        require(len(source.evidence) <= 256 and all(len(e.evidence_id) <= 128 for e in source.evidence),
                'source evidence exceeds workflow bounds')

    def _call(self, context, plan, source, version, *, packet=None):
        self.authority.authorize(context, plan.environment, ('researcher', 'verifier'))
        agents = (plan.lead, *plan.supporting, plan.verifier)
        agent = next((a for a in agents if a.principal == context.principal), None)
        if agent is None or agent.role != context.role:
            raise AuthorizationError('principal is not assigned to this investigation')
        self.roster.resolve(agent)
        if agent.role == 'researcher':
            require(self.provider.configuration_digest == plan.provider_configuration,
                    'research provider fixture configuration changed after plan authorization')
        units = min(plan.policy.max_call_units, max(1, (source.extracted_characters + 3999) // 4000))
        invocation = ModelInvocation(environment=plan.environment, task_id=plan.task_id,
            packet_version=version, agent=agent, source_digest=source.digest,
            packet_digest=(packet.digest,) if packet is not None else (), deadline=plan.policy.deadline,
            units=units, provider_configuration=self.provider.configuration_digest)
        # A port may have already authorized a different reservation size within
        # the same fixed plan ceiling. Continue that exact durable invocation;
        # do not resize its reservation using this caller's estimate.
        prior = self.journal.load(context, plan.task_id,
                                  f'intent:{version}:{context.principal}', ModelInvocation)
        if prior is not None:
            invocation = replace(invocation, units=prior.units)
        return execute_invocation(self.store, self.journal, self.provider, context, plan,
                                  invocation, source, packet, self.clock)



class ResearchDirector(_Runtime):
    def plan(self, context, task_id, source, policy):
        self.authority.authorize(context, source.environment, ('director',))
        require(type(policy) is ResearchPolicy, 'validated research policy required')
        task = self.store.get_task(context, task_id)
        self._source(task, source)
        self._deadline(policy)
        director = self.roster.select(task.environment, 'director')
        if director.principal != context.principal:
            raise AuthorizationError('Director not assigned to this environment')
        specialty, supporting = classify(task.request.objective, source.submitted.kind)
        if len(supporting) > 2:
            raise EscalationRequired('requested specialty coverage exceeds bounded support authorization')
        lead = self.roster.select(task.environment, 'researcher', specialty)
        supporters = tuple(self.roster.select(task.environment, 'researcher', s) for s in supporting)
        plan = ResearchPlan(environment=task.environment, task_id=task_id, director=director, lead=lead,
            supporting=supporters, support_reasons=tuple('Authenticated objective also requires ' + s for s in supporting),
            verifier=self.roster.select(task.environment, 'verifier'), policy=policy,
            provider_configuration=self.provider.configuration_digest)
        self.journal.provision(context, task_id)
        with self.journal.lock(context, task_id, deadline=policy.deadline, clock=self.clock):
            return self.journal.commit(context, task_id, 'plan', plan)

    def run(self, context, task_id, source, *, packet_version=1):
        self.authority.authorize(context, source.environment, ('director',))
        task = self.store.get_task(context, task_id)
        self._source(task, source)
        preflight = self.journal.load(context, task_id, 'plan', ResearchPlan)
        require(preflight is not None, 'authorized plan required')
        with self.journal.lock(context, task_id, deadline=preflight.policy.deadline, clock=self.clock):
            task = self.store.get_task(context, task_id)
            plan = self.journal.load(context, task_id, 'plan', ResearchPlan)
            require(plan is not None and plan.director.principal == context.principal, 'authorized plan required')
            require(type(packet_version) is int and packet_version >= 1, 'positive packet revision required')
            if packet_version > task.request.max_retries + 1:
                raise EscalationRequired('packet revision exceeds bounded retry authorization')
            snapshot_key = f'source:{packet_version}'
            previous_source = self.journal.load(context, task_id, snapshot_key, SourceResult)
            if previous_source is not None:
                require(previous_source == source, 'source changed during logical revision; new revision required')
            if task.state in ('awaiting_verification', 'approved', 'rejected', 'needs_more_research'):
                current = self.store.get_packet(context, task_id)
                if current.packet_version >= packet_version:
                    prepared = self.journal.load(context, task_id, f'packet:{packet_version}', PacketPreparation)
                    packet = self.store.get_packet(context, task_id, packet_version)
                    require(prepared is not None and prepared.packet == packet and prepared.source_digest == source.digest,
                            'historical replay source/packet mismatch')
                    return packet
                require(task.state == 'needs_more_research' and current.packet_version + 1 == packet_version,
                        'fresh revision requires an independent NEEDS_MORE_RESEARCH verdict')
                if task.retries >= task.request.max_retries:
                    raise EscalationRequired('bounded research rework exhausted')
            else:
                require(packet_version == 1 and task.state in ('received', 'collecting', 'researching'),
                        'task cannot start or revise research')
            self._deadline(plan.policy)
            self.journal.commit(context, task_id, snapshot_key, source)
            for before, after in (('received', 'collecting'), ('collecting', 'researching')):
                if task.state == before:
                    task = self.store.transition(context, task_id, before, after)
            drafts = tuple(self._call(self.roster.context(agent), plan, source, packet_version)
                           for agent in (plan.lead, *plan.supporting))
            prepared = prepare_packet(plan, source, drafts, packet_version)
            self._deadline(plan.policy)
            self.journal.commit(context, task_id, f'packet:{packet_version}', prepared)
            self._deadline(plan.policy)
            lead_context = self.roster.context(plan.lead)
            with self.store.bounded_commit(lead_context, plan.policy.deadline, clock=self.clock):
                self.store.put_packet(lead_context, prepared.packet)
            return prepared.packet


def prepare_packet(plan, source, drafts, version):
    evidence = tuple(Evidence(evidence_id=e.evidence_id, environment=plan.environment,
        source_id=source.submitted.source_id, location=e.location, content_digest=hash_content(e))
        for e in source.evidence)
    ids = {e.evidence_id for e in evidence}
    claims, traces = [], []
    notes = [SIMULATION, 'phase3.source_result.sha256:' + source.digest, 'phase3.source.outcome:' + source.outcome,
             'phase3.source.observed_revision:' + (source.revision[0] if source.revision else 'unavailable'),
             *source.limitations, *('source flag: ' + f for f in source.flags)]
    for agent, draft in zip((plan.lead, *plan.supporting), drafts):
        require(draft.principal == agent.principal and draft.environment == plan.environment, 'foreign specialist draft')
        notes.append('phase3.contribution.sha256:' + hash_content(draft))
        notes.extend('unknown: ' + v for v in draft.unknowns)
        notes.extend(draft.limitations)
        for assertion in draft.assertions:
            require(set((*assertion.supporting, *assertion.contradicting)) <= ids,
                    'unsupported source citation; no fabricated evidence inserted')
            claim_id = 'claim-' + hash_content([agent.principal, assertion.assertion_id])[:24]
            references = tuple(dict.fromkeys((*assertion.supporting, *assertion.contradicting)))
            claims.append(Claim(claim_id=claim_id, environment=plan.environment, statement=assertion.statement,
                                evidence_ids=references, kind=assertion.kind))
            traces.append(ClaimTrace(claim_id=claim_id, contributor=agent.principal,
                                    supporting=assertion.supporting, contradicting=assertion.contradicting))
    packet = ResearchPacket(packet_id='packet-' + plan.task_id, task_id=plan.task_id, environment=plan.environment,
        scope=plan.environment, classification='internal', researcher=plan.lead.principal,
        researcher_model=plan.lead.model.model, researcher_provider=plan.lead.model.provider, packet_version=version,
        source=source.submitted, claims=tuple(claims), evidence=evidence, limitations=tuple(notes))
    return PacketPreparation(environment=plan.environment, task_id=plan.task_id, packet=packet,
                             source_digest=source.digest, traces=tuple(traces))


class IndependentVerificationAgent(_Runtime):
    def verify(self, context, task_id, packet_version, packet_digest):
        self.authority.authorize(context, roles=('verifier',))
        task = self.store.get_task(context, task_id)
        preflight = self.journal.load(context, task_id, 'plan', ResearchPlan)
        require(preflight is not None, 'authorized plan required')
        with self.journal.lock(context, task_id, deadline=preflight.policy.deadline, clock=self.clock):
            task = self.store.get_task(context, task_id)
            plan = self.journal.load(context, task_id, 'plan', ResearchPlan)
            require(plan is not None, 'research plan required')
            if plan.verifier.principal != context.principal or context.principal in {
                    a.principal for a in (plan.lead, *plan.supporting)}:
                raise AuthorizationError('independent assigned verifier required; self-approval forbidden')
            packet = self.store.get_packet(context, task_id)
            require(packet.packet_version == packet_version and packet.digest == packet_digest, 'stale packet review')
            source = self.journal.load(context, task_id, f'source:{packet_version}', SourceResult)
            prepared = self.journal.load(context, task_id, f'packet:{packet_version}', PacketPreparation)
            require(source is not None and prepared is not None and prepared.packet == packet and
                    prepared.source_digest == source.digest, 'missing/changed packet source provenance')
            self._source(task, source)
            drafts = tuple(self.journal.load(context, task_id, f'output:{packet_version}:{a.principal}', ResearchDraft)
                           for a in (plan.lead, *plan.supporting))
            require(all(d is not None for d in drafts) and prepare_packet(plan, source, drafts, packet_version) == prepared,
                    'packet does not match accountable specialist contributions')
            review_key = f'review:{packet_version}'
            review = self.journal.load(context, task_id, review_key, VerificationReview)
            if review is None:
                require(task.state == 'awaiting_verification', 'task not awaiting independent review')
                self._deadline(plan.policy)
                proposal = self._call(context, plan, source, packet_version, packet=packet)
                review = assess(plan, source, prepared, drafts, proposal)
                self._deadline(plan.policy)
                self.journal.commit(context, task_id, review_key, review)
            proposal = self.journal.load(context, task_id, f'output:{packet_version}:{context.principal}', VerifierProposal)
            invocation = self.journal.load(context, task_id, f'intent:{packet_version}:{context.principal}', ModelInvocation)
            require(proposal is not None and invocation is not None and
                    invocation.agent == plan.verifier and invocation.source_digest == source.digest and
                    invocation.packet_digest == (packet.digest,) and invocation.packet_version == packet_version and
                    proposal.invocation_digest == invocation.digest and proposal.principal == context.principal and
                    proposal.consumed_units <= invocation.units, 'missing or changed independent verifier execution')
            require(review == assess(plan, source, prepared, drafts, proposal),
                    'cached review does not match complete independent evidence assessment')
            require(review.packet_digest == packet.digest and review.verifier == context.principal, 'stale review checkpoint')
            decisions = self.store.verification_history(context, task_id, packet_version)
            decision = VerificationDecision(decision_id='review-' + review.digest, environment=plan.environment,
                packet_digest=packet.digest, verifier=context.principal, verifier_model=plan.verifier.model.model,
                verifier_provider=plan.verifier.model.provider, verdict=review.verdict,
                rationale=SIMULATION + '; review.sha256:' + review.digest + '; ' +
                          '; '.join(review.corrections[:8]))
            if decision not in decisions:
                self._deadline(plan.policy)
                with self.store.bounded_commit(context, plan.policy.deadline, clock=self.clock):
                    self.store.verify(context, task_id, decision)
            return review

    def history(self, context, task_id):
        self.authority.authorize(context)
        self.store.get_task(context, task_id)
        return self.journal.records(context, task_id, 'review:', VerificationReview)


def assess(plan, source, prepared, drafts, proposal):
    packet = prepared.packet
    originals = {e.evidence_id: e for e in source.evidence}
    assessments = []
    corrections = []
    for claim, trace in zip(packet.claims, prepared.traces):
        if not all(i in originals for i in (*trace.supporting, *trace.contradicting)):
            verdict, reason = 'REJECTED', 'Unsupported citation'
        elif claim.kind != 'finding':
            verdict, reason = 'NEEDS_MORE_RESEARCH', 'Inference/forecast/unknown is not a source-established finding'
        elif not all(claim.statement in originals[i].text for i in trace.supporting):
            verdict, reason = 'REJECTED', 'Finding is not an exact supported source excerpt in this synthetic verifier'
        elif trace.contradicting:
            verdict, reason = 'NEEDS_MORE_RESEARCH', 'Declared contradictory evidence requires resolution'
        else:
            verdict, reason = 'APPROVED', 'Exact supplied-text excerpt checked; simulated evidence consistency only'
        assessments.append(ClaimAssessment(claim_id=claim.claim_id, verdict=verdict, rationale=reason))
        if verdict != 'APPROVED':
            corrections.append(claim.claim_id + ': ' + reason)
    if any(a.verdict == 'REJECTED' for a in assessments) or proposal.verdict == 'REJECTED':
        verdict = 'REJECTED'
    elif (any(a.verdict == 'NEEDS_MORE_RESEARCH' for a in assessments) or source.outcome == 'PARTIAL' or
          any('prompt_injection_candidate:' in flag for flag in source.flags) or
          any(d.unknowns for d in drafts) or proposal.verdict == 'NEEDS_MORE_RESEARCH'):
        verdict = 'NEEDS_MORE_RESEARCH'
    else:
        verdict = 'APPROVED'
    if source.outcome == 'PARTIAL':
        corrections.append('Partial source extraction cannot establish a complete approved investigation')
    if any('prompt_injection_candidate:' in flag for flag in source.flags):
        corrections.append('Untrusted instruction flags require independent resolution; instructions were not executed')
    if any(d.unknowns for d in drafts):
        corrections.append('Resolve explicitly recorded investigation unknowns')
    corrections.extend(proposal.corrections)
    if proposal.verdict != 'APPROVED':
        corrections.append('Synthetic verifier proposal: ' + proposal.rationale)
    return VerificationReview(environment=plan.environment, task_id=plan.task_id,
        packet_version=packet.packet_version, packet_digest=packet.digest, source_digest=source.digest,
        verifier=plan.verifier.principal, verdict=verdict, assessments=tuple(assessments),
        corrections=tuple(corrections), limitations=(SIMULATION, *source.limitations))
