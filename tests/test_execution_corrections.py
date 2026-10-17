"""Phase 7E exact reviewer reproductions and execution-boundary regressions."""
from concurrent.futures import ThreadPoolExecutor
from dataclasses import replace
import json
import os
from pathlib import Path
import subprocess
import sys
import unittest
from unittest.mock import patch

import test_canary_contracts as canary
from alfred_research.contracts import ContractError, ENVIRONMENTS
from alfred_research.tenancy import AuthorizationError
from alfred_research.research import ResearchDirector, ResearchPolicy, SyntheticModelProvider
from alfred_research.research.contracts import ModelInvocation, ResearchDraft, VerifierProposal
from alfred_research.research.execution import reservation_id, RejectedExecution
from alfred_research.integration.canary_contracts import FakeExecutionPort


class ExecutionCorrectionTests(unittest.TestCase):
    setUp = canary.CanaryContractsTests.setUp
    ctx = canary.CanaryContractsTests.ctx
    task = canary.CanaryContractsTests.task
    runtime = canary.CanaryContractsTests.runtime
    start = canary.CanaryContractsTests.start
    execution = canary.CanaryContractsTests.execution

    def budget(self, env='personal'):
        from alfred_research.persistence import open_database
        with open_database(Path(self.temp.name)/env/'research.sqlite3',env,
                registration_authority=self.registrations,context=self.ctx(env)) as db:
            return tuple(db.execute('SELECT id,body FROM reservations ORDER BY id'))

    def rejected(self, port, invocation, context):
        return port.journal.records(context,invocation.task_id,'output:rejected:',RejectedExecution)

    def verifier(self):
        task,source=self.task(kind='github',objective='Inspect repository')
        director,plan,packet=self.start(task,source)
        provider=SyntheticModelProvider(test_only=True)
        port=FakeExecutionPort(self.store,provider,clock=lambda:self.now,test_only=True)
        invocation=ModelInvocation(environment='personal',task_id=task.task_id,packet_version=1,agent=plan.verifier,
            source_digest=source.digest,packet_digest=(packet.digest,),deadline=1100,units=1,
            provider_configuration=provider.configuration_digest)
        return port,invocation,source,packet

    def assert_bad_response(self, change, verifier=False):
        if verifier:
            port,i,source,packet=self.verifier();ctx=self.ctx(identity='verifier')
            original=port.provider.verify
            def call():return port.verify(ctx,i,source,packet)
            method='verify'
        else:
            port,i,source=self.execution();ctx=self.ctx(identity='technology_code')
            original=port.provider.research
            def call():return port.research(ctx,i,source)
            method='research'
        def wrong(*args):return change(original(*args))
        with patch.object(port.provider,method,side_effect=wrong):
            with self.assertRaises(ContractError):call()
        self.assertIsNone(port.reconcile(ctx,i))
        self.assertEqual(len(self.rejected(port,i,ctx)),1)
        rows=self.budget()
        reservation=next(json.loads(body) for key,body in rows if key==reservation_id(i))
        self.assertEqual(reservation['state'],'reserved')
        self.assertEqual(reservation['consumed'],0)
        if verifier:self.assertEqual(self.store.verification_history(self.ctx(),i.task_id),())

    def test_wrong_invocation_digest_reviewer_reproduction(self):
        self.assert_bad_response(lambda r:replace(r,invocation_digest='f'*64))

    def test_wrong_researcher_response_identity(self):
        self.assert_bad_response(lambda r:replace(r,principal='personal-general'))

    def test_wrong_verifier_response_identity(self):
        self.assert_bad_response(lambda r:replace(r,principal='personal-director'),verifier=True)

    def test_wrong_response_task(self):
        self.assert_bad_response(lambda r:replace(r,task_id='other-task'))

    def test_wrong_response_environment(self):
        self.assert_bad_response(lambda r:replace(r,environment='fintra'))

    def test_malformed_response_has_no_success_checkpoint(self):
        self.assert_bad_response(lambda r:{'approved':True})

    def test_wrong_response_type(self):
        def wrong(r):
            return VerifierProposal(environment=r.environment,task_id=r.task_id,principal=r.principal,
                invocation_digest=r.invocation_digest,verdict='APPROVED',rationale='wrong role')
        self.assert_bad_response(wrong)

    def test_stale_verifier_digest_cannot_authorize_approval(self):
        self.assert_bad_response(lambda r:replace(r,invocation_digest='e'*64),verifier=True)

    def test_model_substitution_before_reservation(self):
        port,i,s=self.execution();ctx=self.ctx(identity='technology_code');before=self.budget()
        wrong=replace(i,agent=replace(i.agent,model=replace(i.agent.model,model='synthetic-forged')))
        with patch.object(port.provider,'research',side_effect=AssertionError('must not call')):
            with self.assertRaises(AuthorizationError):port.research(ctx,wrong,s)
        self.assertEqual(self.budget(),before)

    def test_longer_deadline_reviewer_reproduction(self):
        port,i,s=self.execution();self.now=1200;before=self.budget()
        with patch.object(port.provider,'research',side_effect=AssertionError('must not call')):
            with self.assertRaises(ContractError):port.research(self.ctx(identity='technology_code'),replace(i,deadline=2000),s)
        self.assertEqual(self.budget(),before)

    def test_expired_plan_cannot_start_call(self):
        port,i,s=self.execution();self.now=1100
        with patch.object(port.provider,'research',side_effect=AssertionError('must not call')):
            with self.assertRaises(AuthorizationError):port.research(self.ctx(identity='technology_code'),i,s)
        self.assertEqual(self.budget(),())

    def test_committed_replay_after_deadline_only_reconciles(self):
        port,i,s=self.execution();ctx=self.ctx(identity='technology_code');output=port.research(ctx,i,s)
        before=self.budget();self.now=1200
        with patch.object(port.provider,'research',side_effect=AssertionError('must not call')):
            self.assertEqual(port.research(ctx,i,s),output)
            self.assertEqual(port.reconcile(ctx,i),output)
        self.assertEqual(self.budget(),before)

    def test_limits_and_retry_revision_cannot_be_extended(self):
        port,i,s=self.execution();ctx=self.ctx(identity='technology_code');port.max_units=16
        with patch.object(port.provider,'research',side_effect=AssertionError('must not call')):
            for wrong in (replace(i,units=5),replace(i,packet_version=99)):
                with self.assertRaises(ContractError):port.research(ctx,wrong,s)
        self.assertEqual(self.budget(),())

    def test_task_cost_ceiling_shared_with_director(self):
        task,source=self.task(kind='github',objective='Inspect repository')
        director,_=self.runtime();plan=director.plan(self.ctx(),task.task_id,source,
            ResearchPolicy(deadline=1100,max_task_cost=1))
        port=FakeExecutionPort(self.store,director.provider,clock=lambda:1000,test_only=True)
        invocation=ModelInvocation(environment='personal',task_id=task.task_id,packet_version=1,agent=plan.lead,
            source_digest=source.digest,packet_digest=(),deadline=1100,units=2,
            provider_configuration=director.provider.configuration_digest)
        with self.assertRaises(AuthorizationError):port.research(self.ctx(identity='technology_code'),invocation,source)
        self.assertEqual(self.budget(),())

    def test_director_first_reviewer_reproduction_one_charge(self):
        task,source=self.task(kind='github',objective='Inspect repository')
        director,plan,packet=self.start(task,source);ctx=self.ctx(identity='technology_code')
        invocation=director.journal.load(ctx,task.task_id,'intent:1:'+ctx.principal,ModelInvocation)
        before=self.budget();port=FakeExecutionPort(self.store,director.provider,clock=lambda:1000,test_only=True)
        with patch.object(port.provider,'research',side_effect=AssertionError('must not call')):
            port.research(ctx,invocation,source);port.reconcile(ctx,invocation)
        self.assertEqual(self.budget(),before)
        events=self.store.audit_history(self.ctx())
        self.assertEqual(sum(e.operation=='budget.reserved' for e in events),1)
        self.assertEqual(sum(e.operation=='budget.settled' for e in events),1)

    def test_port_first_director_continuation_one_charge(self):
        port,i,s=self.execution();ctx=self.ctx(identity='technology_code')
        port.research(ctx,i,s);before=self.budget()
        director=ResearchDirector(self.authority,self.store,self.roster,port.provider,clock=lambda:1000)
        with patch.object(port.provider,'research',side_effect=AssertionError('must not call')):
            packet=director.run(self.ctx(),i.task_id,s)
        self.assertEqual(packet.researcher,ctx.principal)
        self.assertEqual(self.budget(),before)

    def test_concurrent_port_and_director_one_execution_and_charge(self):
        port,i,s=self.execution();i=replace(i,units=1);ctx=self.ctx(identity='technology_code')
        director=ResearchDirector(self.authority,self.store,self.roster,port.provider,clock=lambda:1000)
        original=port.provider.research
        with patch.object(port.provider,'research',wraps=original) as model:
            with ThreadPoolExecutor(max_workers=4) as pool:
                futures=[pool.submit(port.research,ctx,i,s),pool.submit(director.run,self.ctx(),i.task_id,s),
                         pool.submit(port.research,ctx,i,s),pool.submit(director.run,self.ctx(),i.task_id,s)]
                for f in futures:f.result()
            self.assertEqual(model.call_count,1)
        self.assertEqual(len(self.budget()),1)
        self.assertEqual(sum(e.operation=='budget.settled' for e in self.store.audit_history(self.ctx())),1)

    def test_conflicting_replay_does_not_change_budget(self):
        port,i,s=self.execution();ctx=self.ctx(identity='technology_code');port.research(ctx,i,s)
        before=self.budget()
        for wrong in (replace(i,units=1),replace(i,source_digest='f'*64)):
            with self.assertRaises(ContractError):port.research(ctx,wrong,s)
        self.assertEqual(self.budget(),before)

    def test_reservation_conflict_rejected_before_execution(self):
        port,i,s=self.execution();ctx=self.ctx(identity='technology_code')
        self.store.reserve(ctx,reservation_id(i),'researcher',i.agent.model.provider,i.agent.model.model,1)
        before=self.budget()
        with patch.object(port.provider,'research',side_effect=AssertionError('must not call')):
            with self.assertRaises(ContractError):port.research(ctx,i,s)
        self.assertEqual(self.budget(),before)

    def test_output_checkpoint_before_settlement_repairs_once(self):
        port,i,s=self.execution();ctx=self.ctx(identity='technology_code');original=self.store.settle
        with patch.object(self.store,'settle',side_effect=RuntimeError('crash before settlement')):
            with self.assertRaises(RuntimeError):port.research(ctx,i,s)
        restarted=FakeExecutionPort(self.store,port.provider,clock=lambda:1200,test_only=True)
        with patch.object(port.provider,'research',side_effect=AssertionError('must not call')):
            with ThreadPoolExecutor(max_workers=3) as pool:
                results=list(pool.map(lambda _:restarted.reconcile(ctx,i),range(3)))
        self.assertEqual(len({r.invocation_digest for r in results}),1)
        self.assertEqual(sum(e.operation=='budget.settled' for e in self.store.audit_history(self.ctx())),1)

    def test_fresh_process_director_resumes_port_checkpoint(self):
        port,i,s=self.execution();i=replace(i,units=1);port.research(self.ctx(identity='technology_code'),i,s)
        before=self.budget()
        code='''import json,sys,socket
from test_research import bootstrap
from alfred_research.research import ResearchDirector,SyntheticModelProvider
from alfred_research.sources import SourceResult
v=json.load(sys.stdin);a,c,m,r,store,roster=bootstrap(v['root'],v['registration'])
socket.socket=lambda *a,**k: (_ for _ in ()).throw(AssertionError('network forbidden'))
provider=SyntheticModelProvider(test_only=True)
provider.research=lambda *a,**k: (_ for _ in ()).throw(AssertionError('duplicate model call'))
d=ResearchDirector(a,store,roster,provider,clock=lambda:1000)
p=d.run(c['personal-director'],v['task'],SourceResult.from_payload(v['source']))
print(p.digest)
'''
        env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',PYTHONPATH=str(Path(__file__).resolve().parents[1]/'src')+os.pathsep+str(Path(__file__).resolve().parent))
        result=subprocess.run([sys.executable,'-c',code],input=json.dumps({'root':str(self.temp.name),
            'registration':self.registrations.snapshot_for_tests(),'task':i.task_id,'source':s.payload()}),
            text=True,capture_output=True,env=env,timeout=10)
        self.assertEqual(result.returncode,0,result.stderr)
        self.assertEqual(self.budget(),before)
        self.assertEqual(len(result.stdout.strip()),64)

    def test_all_environment_pairs_deny_execution_and_reconciliation(self):
        for env in ENVIRONMENTS:
            task,source=self.task(env,kind='github',objective='Inspect repository')
            director,_=self.runtime();plan=director.plan(self.ctx(env),task.task_id,source,
                ResearchPolicy(deadline=1100,max_task_cost=100))
            port=FakeExecutionPort(self.store,director.provider,clock=lambda:1000,test_only=True)
            i=ModelInvocation(environment=env,task_id=task.task_id,packet_version=1,agent=plan.lead,
                source_digest=source.digest,packet_digest=(),deadline=1100,units=1,
                provider_configuration=director.provider.configuration_digest)
            port.research(self.ctx(env,'technology_code'),i,source)
            for other in ENVIRONMENTS:
                if env==other:continue
                with self.assertRaises(AuthorizationError):port.research(self.ctx(other,'technology_code'),i,source)
                with self.assertRaises(AuthorizationError):port.reconcile(self.ctx(other,'technology_code'),i)
