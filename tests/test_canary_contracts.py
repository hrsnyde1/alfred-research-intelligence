"""Synthetic contract acceptance, no network or production services."""
from concurrent.futures import ThreadPoolExecutor
from dataclasses import replace
from unittest.mock import patch
import unittest
import json
import os
from pathlib import Path
import subprocess
import sys
import test_research as foundation
import test_memory as memory_tests
import test_workflow as workflow_tests
from alfred_research.contracts import ContractError, ENVIRONMENTS, hash_content
from alfred_research.tenancy import AuthorizationError, AuthenticatedContext
from alfred_research.sources import SourceFixture, FixtureFile
from alfred_research.research import SyntheticModelProvider
from alfred_research.research.contracts import ModelInvocation
from alfred_research.workflow.contracts import Notice
from alfred_research.integration.canary_contracts import (
    GitHubReference, ResearchIntake, ConversationBinding, IntakeMapping, PendingSources,
    GenuineExecution, require_production_authorization, FakeExecutionPort, FakeMemoryPort,
    FakePhotonPort, CTOProposal, FakeCTOPort)


class CanaryContractsTests(unittest.TestCase):
    setUp = foundation.ResearchTests.setUp
    ctx = foundation.ResearchTests.ctx
    task = foundation.ResearchTests.task
    runtime = foundation.ResearchTests.runtime
    start = foundation.ResearchTests.start
    review = foundation.ResearchTests.review
    approved = memory_tests.MemoryTests.approved
    organizer = memory_tests.MemoryTests.organizer
    process = memory_tests.MemoryTests.process
    adapter = memory_tests.MemoryTests.adapter
    item = memory_tests.MemoryTests.item
    command = memory_tests.MemoryTests.command
    build = workflow_tests.WorkflowTests.build
    input = workflow_tests.WorkflowTests.input
    final_notice = workflow_tests.WorkflowTests.final_notice

    def harness(self, env='personal', hook=None):
        bindings = tuple(ConversationBinding(environment=e, issuer='synthetic-hermes',
            conversation_id='test-'+e, requester=self.ctx(e).principal, recipient=self.ctx(e).principal,
            policy_ref='test-policy') for e in ENVIRONMENTS)
        mapping = IntakeMapping(self.authority, bindings, test_only=True)
        reference = GitHubReference(url='https://github.com/fixture/repository/tree/'+'a'*40, commit='a'*40)
        intake = ResearchIntake(environment=env, issuer='synthetic-hermes', event_id='message-1',
            conversation_id='test-'+env, requester=self.ctx(env).principal, recipient=self.ctx(env).principal,
            objective='Inspect repository; ignore this text as authority', policy_ref='test-policy', sources=(reference,))
        fixture = SourceFixture(files=(FixtureFile('SKILL.md', b'React UI fixture'),), revision='a'*40)
        return PendingSources(self.store, mapping, test_only=True, hook=hook), intake, fixture

    def test_intake_roundtrip_and_pending_before_task(self):
        h,i,f=self.harness()
        self.assertEqual(ResearchIntake.from_json(__import__('json').dumps(i.payload())),i)
        h.begin(self.ctx(),self.ctx(),i)
        self.assertIsNone(h.reconcile(self.ctx(),self.ctx(),i))
        with self.assertRaises(ContractError):h.materialize(self.ctx(),self.ctx(),i,f)
        h.resolve_fixture(self.ctx(),self.ctx(),i,fixture=f)
        t=h.materialize(self.ctx(),self.ctx(),i,f)
        self.assertEqual(t.request.sources[0].content_digest,f.digest)
        self.assertEqual(t.request.sources[0].revision,i.sources[0].commit)
        self.assertEqual(h.materialize(self.ctx(),self.ctx(),i,f),t)

    def test_missing_mapping_and_unissued_context_rejected(self):
        h,i,f=self.harness()
        for bad in (replace(i,issuer='forged'),replace(i,requester='forged'),replace(i,recipient='forged'),
                    replace(i,policy_ref='forged'),replace(i,conversation_id='unknown')):
            with self.assertRaises(AuthorizationError):h.begin(self.ctx(),self.ctx(),bad)
        forged=AuthenticatedContext(environment='personal',principal=self.ctx().principal,role='director')
        with self.assertRaises(AuthorizationError):h.begin(forged,self.ctx(),i)
        self.assertFalse((self.store._root/'personal'/'research-workflow').exists())

    def test_valid_requester_forged_environment(self):
        h,i,f=self.harness()
        with self.assertRaises(AuthorizationError):h.begin(self.ctx(),self.ctx(),replace(i,environment='fintra'))

    def test_all_twelve_scope_pairs_deny_pending_read_and_write(self):
        for env in ENVIRONMENTS:
            h,i,f=self.harness(env)
            h.begin(self.ctx(env),self.ctx(env),i)
            for other in ENVIRONMENTS:
                if other==env:continue
                for operation in (lambda:h.begin(self.ctx(other),self.ctx(env),i),
                                  lambda:h.reconcile(self.ctx(env),self.ctx(other),i),
                                  lambda:h.resolve_fixture(self.ctx(other),self.ctx(other),i,fixture=f)):
                    with self.assertRaises(AuthorizationError):operation()

    def test_source_contract_rejects_ambiguous_unsafe_urls_and_multiple_sources(self):
        h,i,f=self.harness()
        for url in ('http://github.com/f/r/tree/'+'a'*40,'https://user@github.com/f/r/tree/'+'a'*40,
                    'https://127.0.0.1/f/r/tree/'+'a'*40,'https://github.com/f/../tree/'+'a'*40,
                    i.sources[0].url+'?redirect=bad'):
            with self.assertRaises(ContractError):GitHubReference(url=url,commit='a'*40)
        with self.assertRaises(ContractError):replace(i.sources[0],commit='branch')
        with self.assertRaises(ContractError):replace(i,sources=i.sources*2)
        with self.assertRaises(ContractError):ResearchIntake.from_payload({**i.payload(),'approved':True})

    def test_duplicate_pending_conflict_and_resolution_substitution(self):
        h,i,f=self.harness();h.begin(self.ctx(),self.ctx(),i)
        self.assertEqual(h.begin(self.ctx(),self.ctx(),i).intake,i)
        with self.assertRaises(ContractError):h.begin(self.ctx(),self.ctx(),replace(i,objective='changed'))
        h.resolve_fixture(self.ctx(),self.ctx(),i,fixture=f)
        changed=replace(f,files=(FixtureFile('SKILL.md',b'changed'),))
        with self.assertRaises(ContractError):h.resolve_fixture(self.ctx(),self.ctx(),i,fixture=changed)
        with self.assertRaises(ContractError):h.materialize(self.ctx(),self.ctx(),i,changed)

    def test_failed_and_unknown_acquisition_cannot_create_tasks(self):
        for outcome in ('FAILED','UNKNOWN'):
            h,i,f=self.harness();i=replace(i,event_id=outcome)
            h.begin(self.ctx(),self.ctx(),i);h.resolve_fixture(self.ctx(),self.ctx(),i,outcome=outcome)
            with self.assertRaises(ContractError):h.materialize(self.ctx(),self.ctx(),i,f)
            with self.assertRaises(ContractError):h.resolve_fixture(self.ctx(),self.ctx(),i,fixture=f)

    def test_snapshot_revision_and_authentication_required(self):
        h,i,f=self.harness()
        with self.assertRaises(AuthorizationError):h.begin(self.ctx(),self.ctx(identity='general'),i)
        h.begin(self.ctx(),self.ctx(),i)
        for bad in (replace(f,revision='b'*40),replace(f,complete=False),replace(f,origin='user_supplied')):
            with self.assertRaises(ContractError):h.resolve_fixture(self.ctx(),self.ctx(),i,fixture=bad)

    def test_task_effect_crash_restarts_idempotently(self):
        def crash(stage):raise RuntimeError('synthetic interruption')
        h,i,f=self.harness(hook=crash);h.begin(self.ctx(),self.ctx(),i)
        h.resolve_fixture(self.ctx(),self.ctx(),i,fixture=f)
        with self.assertRaises(RuntimeError):h.materialize(self.ctx(),self.ctx(),i,f)
        restarted,_,_=self.harness()
        task=restarted.materialize(self.ctx(),self.ctx(),i,f)
        self.assertEqual(restarted.materialize(self.ctx(),self.ctx(),i,f),task)
        self.assertEqual(sum(e.operation=='task.created' for e in self.store.audit_history(self.ctx())),1)

    def test_concurrent_acquisition_materialization_one_task(self):
        h,i,f=self.harness();h.begin(self.ctx(),self.ctx(),i);h.resolve_fixture(self.ctx(),self.ctx(),i,fixture=f)
        with ThreadPoolExecutor(max_workers=4) as pool:
            tasks=list(pool.map(lambda _:h.materialize(self.ctx(),self.ctx(),i,f),range(4)))
        self.assertEqual(len({t.task_id for t in tasks}),1)

    def test_pending_resolution_survives_fresh_process(self):
        h,i,f=self.harness();h.begin(self.ctx(),self.ctx(),i);h.resolve_fixture(self.ctx(),self.ctx(),i,fixture=f)
        script='''import json,sys,socket
from test_research import bootstrap
from alfred_research.integration.canary_contracts import PendingAcquisition,AcquisitionResolution
from alfred_research.research.journal import WorkflowJournal
socket.socket=lambda *a,**k: (_ for _ in ()).throw(AssertionError('network forbidden'))
v=json.load(sys.stdin)
a,c,m,r,s,roster=bootstrap(v['root'],v['snapshot'])
j=WorkflowJournal(s._root,a);ctx=c['personal-director']
p=j.load(ctx,v['namespace'],'packet:pending',PendingAcquisition)
r=j.load(ctx,v['namespace'],'packet:resolution',AcquisitionResolution)
print(json.dumps([p.intake.operation_id,r.snapshot_digest[0]]))
'''
        env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',PYTHONPATH=str(Path(__file__).resolve().parents[1]/'src')+os.pathsep+str(Path(__file__).resolve().parent))
        result=subprocess.run([sys.executable,'-c',script],input=json.dumps({'root':str(self.store._root),
            'snapshot':self.registrations.snapshot_for_tests(),'namespace':'acquisition-'+i.operation_id}),
            text=True,capture_output=True,env=env,timeout=10)
        self.assertEqual(result.returncode,0,result.stderr)
        self.assertEqual(json.loads(result.stdout),[i.operation_id,f.digest])

    def execution(self):
        task,source=self.task(kind='github',objective='Inspect repository')
        provider=SyntheticModelProvider(test_only=True)
        self.roster.context(self.roster.select('personal','researcher','technology_code'))
        invocation=ModelInvocation(environment='personal',task_id=task.task_id,packet_version=1,
            agent=self.roster.select('personal','researcher','technology_code'),source_digest=source.digest,
            packet_digest=(),deadline=1100,units=2,provider_configuration=provider.configuration_digest)
        director=self.runtime()[0]
        director.plan(self.ctx(),task.task_id,source,foundation.ResearchPolicy(deadline=1100,max_task_cost=100))
        return FakeExecutionPort(self.store,provider,clock=lambda:self.now,test_only=True),invocation,source

    def test_provider_synthetic_output_budget_and_replay(self):
        port,i,s=self.execution();context=self.ctx(identity='technology_code')
        result=port.research(context,i,s)
        self.assertTrue(result.simulation_only)
        with patch.object(port.provider,'research',side_effect=AssertionError('duplicate execution')):
            self.assertEqual(port.research(context,i,s),result)
        self.assertEqual(port.reconcile(context,i),result)

    def test_provider_substitution_deadline_and_wrong_identity(self):
        port,i,s=self.execution();context=self.ctx(identity='technology_code')
        with self.assertRaises(AuthorizationError):port.research(self.ctx('fintra','technology_code'),i,s)
        bad=replace(i,agent=replace(i.agent,model=replace(i.agent.model,model='synthetic-substitution')))
        with self.assertRaises(AuthorizationError):port.research(context,bad,s)
        with self.assertRaises(ContractError):port.research(context,replace(i,deadline=1000),s)
        with self.assertRaises(ContractError):port.research(context,replace(i,units=5),s)

    def test_independent_verifier_port_and_self_verification_denial(self):
        task,source=self.task(kind='github',objective='Inspect repository')
        _,plan,packet=self.start(task,source)
        provider=SyntheticModelProvider(test_only=True)
        port=FakeExecutionPort(self.store,provider,clock=lambda:1000,test_only=True)
        invocation=ModelInvocation(environment='personal',task_id=task.task_id,packet_version=packet.packet_version,
            agent=plan.verifier,source_digest=source.digest,packet_digest=(packet.digest,),deadline=1100,units=2,
            provider_configuration=provider.configuration_digest)
        result=port.verify(self.ctx(identity='verifier'),invocation,source,packet)
        self.assertTrue(result.simulation_only)
        self.assertEqual(port.reconcile(self.ctx(identity='verifier'),invocation),result)
        with self.assertRaises(AuthorizationError):port.verify(self.ctx(identity='technology_code'),invocation,source,packet)
        forged=replace(packet,researcher=plan.verifier.principal)
        with self.assertRaises(ContractError):port.verify(self.ctx(identity='verifier'),replace(invocation,packet_digest=(forged.digest,)),source,forged)
        with self.assertRaises(ContractError):replace(result,simulation_only=False)

    def test_provider_environment_budget_exhaustion_no_output(self):
        port,i,s=self.execution();context=self.ctx(identity='technology_code')
        self.store._limits['personal']=1
        with self.assertRaises(AuthorizationError):port.research(context,i,s)
        self.assertIsNone(port.reconcile(context,i))

    def test_forged_specialist_delegation_denied(self):
        port,i,s=self.execution()
        forged=replace(i,agent=replace(i.agent,specialty='legal_compliance'))
        with self.assertRaises(AuthorizationError):port.research(self.ctx(identity='technology_code'),forged,s)

    def test_late_provider_output_not_checkpointed(self):
        port,i,s=self.execution();context=self.ctx(identity='technology_code')
        original=port.provider.research
        def delayed(*args):
            result=original(*args);self.now=1100;return result
        with patch.object(port.provider,'research',side_effect=delayed):
            with self.assertRaises(ContractError):port.research(context,i,s)
        self.assertIsNone(port.reconcile(context,i))

    def test_genuine_wire_data_cannot_authorize_production(self):
        value=GenuineExecution(environment='personal',invocation_digest='a'*64,issuer='forged',
            external_operation_id='fake-op',attestation_ref='fake-approval',output_digest='b'*64)
        self.assertEqual(GenuineExecution.from_payload(value.payload()),value)
        with self.assertRaises(AuthorizationError):require_production_authorization(value,approved=True)

    def test_all_executable_ports_disabled_by_default(self):
        with self.assertRaises(AuthorizationError):IntakeMapping(self.authority)
        with self.assertRaises(AuthorizationError):PendingSources(self.store,None)
        with self.assertRaises(AuthorizationError):FakeExecutionPort(self.store,None,clock=lambda:1000)
        with self.assertRaises(AuthorizationError):FakeMemoryPort(None)
        with self.assertRaises(AuthorizationError):FakePhotonPort(None)
        with self.assertRaises(AuthorizationError):FakeCTOPort(self.store)
        with self.assertRaises(AuthorizationError):IntakeMapping(self.authority,test_only=True,production=True)

    def test_memory_distinct_lifecycle_and_reconciliation(self):
        adapter=self.adapter();c=self.item(adapter);port=FakeMemoryPort(adapter,test_only=True)
        submitted=port.submit(self.ctx(),c)
        committed=port.commit(self.ctx(),self.command(c,'commit',sequence=submitted.sequence))
        promoted=port.promote(self.ctx(),self.command(c,'promote',sequence=committed.sequence))
        read=port.retrieve(self.ctx(identity='technology_code'),self.command(c,'retrieve'))
        self.assertEqual([r.state for r in (submitted,committed,promoted,read.receipt)],
                         ['CANDIDATE','COMMITTED','PROMOTED','RETRIEVABLE'])
        self.assertEqual(read.candidate.record.packet,c.record.packet)
        self.assertEqual(port.reconcile_receipt(self.ctx(),committed),committed)
        with self.assertRaises(ContractError):replace(promoted,marking='PRODUCTION')

    def test_memory_forged_stale_and_cross_company_receipts(self):
        adapter=self.adapter();c=self.item(adapter);port=FakeMemoryPort(adapter,test_only=True)
        submitted=port.submit(self.ctx(),c)
        with self.assertRaises(ContractError):port.reconcile_receipt(self.ctx(),replace(submitted,receipt_id='f'*64))
        with self.assertRaises(AuthorizationError):port.submit(self.ctx('fintra'),c)
        committed=port.commit(self.ctx(),self.command(c,'commit',sequence=submitted.sequence))
        promoted=port.promote(self.ctx(),self.command(c,'promote',sequence=committed.sequence))
        adapter.revoke(self.ctx(),self.command(c,'revoke',sequence=promoted.sequence))
        with port.completion_snapshot(self.ctx(),(promoted,)) as receipts:self.assertEqual(receipts,())

    def test_memory_concurrent_duplicate_commit_single_effect(self):
        adapter=self.adapter();c=self.item(adapter);port=FakeMemoryPort(adapter,test_only=True)
        submitted=port.submit(self.ctx(),c);command=self.command(c,'commit',sequence=submitted.sequence)
        with ThreadPoolExecutor(max_workers=3) as pool:
            receipts=list(pool.map(lambda _:port.commit(self.ctx(),command),range(3)))
        self.assertEqual(len({r.receipt_id for r in receipts}),1)
        self.assertEqual(len([e for e in adapter.history(self.ctx(),'personal') if e.receipt.operation=='commit']),1)

    def test_photon_ack_final_replay_and_receipt_states(self):
        flow=self.build(auto_confirm=False);message,fixture=self.input();result=flow.run(self.ctx(),message,fixture)
        port=FakePhotonPort(flow.notifications,test_only=True)
        notice=self.final_notice(flow,result)
        first=port.complete(self.ctx(),notice,result)
        self.assertEqual(first.state,'ACCEPTED')
        self.assertEqual(port.complete(self.ctx(),notice,result),first)
        self.assertEqual(port.reconcile(self.ctx(),notice),first)
        ack=Notice(environment='personal',research_task_id=result.research_task_id,conversation_id=message.conversation_id,
                   recipient=self.ctx().principal,kind='ACK',message='SIMULATED: Research request received.')
        self.assertNotEqual(port.acknowledge(self.ctx(),ack).notification_id,first.notification_id)

    def test_photon_stale_completion_and_forged_identity_denied(self):
        flow=self.build();message,fixture=self.input();result=flow.run(self.ctx(),message,fixture)
        port=FakePhotonPort(flow.notifications,test_only=True);notice=self.final_notice(flow,result)
        with self.assertRaises(AuthorizationError):port.complete(self.ctx('fintra'),notice,result)
        with self.assertRaises(ContractError):port.complete(self.ctx(),replace(notice,message='Saved for real'),result)
        promoted=next(r for r in result.receipts if r.operation=='promote')
        candidate=flow.memory.history(self.ctx(),'personal')[0].candidate[0]
        flow.memory.revoke(self.ctx(),self.command(candidate,'revoke',sequence=promoted.sequence))
        with self.assertRaises(ContractError):port.complete(self.ctx(),notice,result)

    def proposal(self):
        flow=self.build();message,fixture=self.input();result=flow.run(self.ctx(),message,fixture)
        candidate=flow.memory.history(self.ctx(),'personal')[0].candidate[0]
        return CTOProposal(environment='personal',proposal=result.proposals[0],research_task_id=result.research_task_id,
            packet_digest=candidate.record.packet.digest,packet_version=candidate.record.packet.packet_version,
            decision_id=candidate.verification.decision_id,specialist_id='frontend')

    def test_cto_local_proposal_replay_without_execution(self):
        proposal=self.proposal();port=FakeCTOPort(self.store,test_only=True)
        self.assertEqual(port.propose(self.ctx(),proposal),proposal)
        self.assertEqual(port.propose(self.ctx(),proposal),proposal)
        self.assertEqual(port.reconcile(self.ctx(),proposal),proposal)
        self.assertFalse(proposal.execution_authorized)
        with self.assertRaises(ContractError):replace(proposal,execution_authorized=True)
        with self.assertRaises(ContractError):replace(proposal,specialist_id='backend')
        with self.assertRaises(ContractError):port.propose(self.ctx(),replace(proposal,decision_id='forged'))
        with self.assertRaises(AuthorizationError):port.propose(self.ctx('fintra'),proposal)

    def test_cto_forged_source_and_packet_cannot_be_recorded(self):
        proposal=self.proposal();port=FakeCTOPort(self.store,test_only=True)
        for bad in (replace(proposal,packet_digest='e'*64),replace(proposal,packet_version=2),
                    replace(proposal,proposal=replace(proposal.proposal,source_digest='f'*64)),
                    replace(proposal,proposal=replace(proposal.proposal,evidence_ids=('invented',)))):
            with self.assertRaises(ContractError):port.propose(self.ctx(),bad)

    def test_ack_without_materialized_task_denied(self):
        flow=self.build();port=FakePhotonPort(flow.notifications,test_only=True)
        notice=Notice(environment='personal',research_task_id='missing',conversation_id='research-personal',
            recipient=self.ctx().principal,kind='ACK',message='SIMULATED: Research request received.')
        with self.assertRaises((AuthorizationError,ContractError)):port.acknowledge(self.ctx(),notice)


if __name__=='__main__':unittest.main()
