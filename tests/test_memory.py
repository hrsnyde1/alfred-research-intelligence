"""Phase 5 explicit fake lifecycle/HQ acceptance using real synthetic Research records."""
import test_intelligence as intelligence
from alfred_research.contracts import ENVIRONMENTS, ContractError, hash_content
from alfred_research.tenancy import AuthorizationError, AuthenticatedContext
from alfred_research.memory import (FakeMemoryAdapter, TestMemoryAccess, MemoryCommand,
                                    KnowledgeCandidate, DeliveryAmbiguous)
from alfred_research.memory.fake import NAMESPACE
from concurrent.futures import ThreadPoolExecutor
from dataclasses import replace
from unittest.mock import patch
import unittest

class MemoryTests(unittest.TestCase):
    setUp = intelligence.IntelligenceTests.setUp
    ctx = intelligence.IntelligenceTests.ctx
    task = intelligence.IntelligenceTests.task
    runtime = intelligence.IntelligenceTests.runtime
    start = intelligence.IntelligenceTests.start
    review = intelligence.IntelligenceTests.review
    approved = intelligence.IntelligenceTests.approved
    organizer = intelligence.IntelligenceTests.organizer
    process = intelligence.IntelligenceTests.process

    def adapter(self):
        o = self.organizer()
        access = TestMemoryAccess(self.authority, test_only=True,
            specialists=tuple((self.ctx(e, 'technology_code'), ('Frontend', 'Backend'), ('internal',)) for e in ENVIRONMENTS),
            owners=((self.ctx(), ENVIRONMENTS[1:], ('internal',)),))
        return FakeMemoryAdapter(o, access, {e:self.ctx(e) for e in ENVIRONMENTS}, test_only=True)

    def item(self, adapter, env='personal', text='React UI evidence', key='request'):
        packet = self.approved(env, text=text, request_id=key)
        batch = self.process(adapter.organizer, packet, key)
        return adapter.candidate(self.ctx(env), batch.record.record_id, 'candidate-' + key)

    def command(self, candidate, operation, key=None, sequence=0, **kwargs):
        operation_id = key or operation + '-' + candidate.idempotency_id
        if operation in ('request_export','export_status','sync_status'):
            rows = self.adapter().history(self.ctx(candidate.environment), candidate.environment)
            request = next((e.receipt for e in reversed(rows) if e.receipt.record_id == candidate.record.record_id and e.receipt.operation == 'request_export'), None)
            prior = request if operation == 'export_status' else next((e.receipt for e in reversed(rows) if e.receipt.record_id == candidate.record.record_id and e.receipt.operation == 'export_status'), None)
            kwargs.setdefault('export_attempt',(operation_id,) if operation == 'request_export' else (request.operation_id if request else 'missing',))
            kwargs.setdefault('export_destination',('test-obsidian:' + candidate.environment,))
            kwargs.setdefault('export_record_version',(candidate.record_version,))
            kwargs.setdefault('prerequisite_receipt',() if operation == 'request_export' else (prior.receipt_id if prior else '0'*64,))
        return MemoryCommand(environment=candidate.environment, record_id=candidate.record.record_id,
            record_digest=hash_content(candidate.record), operation=operation,
            operation_id=operation_id, expected_sequence=sequence, **kwargs)

    def promote_item(self, adapter, candidate):
        ctx = self.ctx(candidate.environment)
        submitted = adapter.submit(ctx, candidate)
        committed = adapter.commit(ctx, self.command(candidate, 'commit', sequence=submitted.sequence))
        promoted = adapter.promote(ctx, self.command(candidate, 'promote', sequence=committed.sequence))
        return submitted, committed, promoted

    def test_four_environment_lifecycle_and_citations(self):
        a=self.adapter()
        for env in ENVIRONMENTS:
            c=self.item(a,env)
            receipts=self.promote_item(a,c)
            result=a.retrieve(self.ctx(env,'technology_code'),self.command(c,'retrieve'))
            self.assertEqual([r.operation for r in receipts]+[result.receipt.operation],['submit','commit','promote','retrieve'])
            self.assertEqual([r.state for r in receipts],['CANDIDATE','COMMITTED','PROMOTED'])
            self.assertEqual(result.receipt.state,'RETRIEVABLE')
            self.assertEqual(result.candidate,c)
            self.assertTrue(result.candidate.record.source.evidence)
            self.assertTrue(all(r.marking=='SIMULATED / NON_PRODUCTION' for r in receipts))
            self.assertFalse(result.candidate.record.memory_eligible)
            self.assertEqual(c.verification.packet_digest,c.record.packet.digest)

    def test_distinct_commit_promotion_and_fresh_retrieval(self):
        a=self.adapter();c=self.item(a);s=a.submit(self.ctx(),c)
        commit=a.commit(self.ctx(),self.command(c,'commit',sequence=s.sequence))
        with self.assertRaises(ContractError):a.retrieve(self.ctx(identity='technology_code'),self.command(c,'retrieve'))
        promotion=a.promote(self.ctx(),self.command(c,'promote',sequence=commit.sequence))
        result=a.retrieve(self.ctx(identity='technology_code'),self.command(c,'retrieve'))
        self.assertNotEqual(promotion.receipt_id,result.receipt.receipt_id)
        with self.assertRaises(ContractError):a.retrieve(self.ctx(identity='technology_code'),self.command(c,'retrieve'))
        self.assertEqual(a.retrieve(self.ctx(identity='technology_code'),self.command(c,'retrieve','fresh')).candidate,c)

    def test_duplicate_submit_commit_promote_are_idempotent(self):
        a=self.adapter();c=self.item(a);s,commit,promote=self.promote_item(a,c)
        before=a.history(self.ctx(),'personal')
        self.assertEqual(a.submit(self.ctx(),c),s)
        self.assertEqual(a.commit(self.ctx(),self.command(c,'commit',sequence=s.sequence)),commit)
        self.assertEqual(a.promote(self.ctx(),self.command(c,'promote',sequence=commit.sequence)),promote)
        self.assertEqual(a.history(self.ctx(),'personal'),before)
        self.assertEqual(len([e for e in self.store.outbox(self.ctx()) if e.topic.startswith('offline.memory.')]),3)

    def test_replayed_candidate_identity_cannot_change_packet(self):
        a=self.adapter();c=self.item(a);a.submit(self.ctx(),c)
        with self.assertRaises(ContractError):replace(c,verification=replace(c.verification,packet_digest='0'*64))
        forged=replace(c,record=replace(c.record,valid_until=c.record.valid_until-1))
        with self.assertRaises(ContractError):a.submit(self.ctx(),forged)
        with self.assertRaises(ContractError):a.commit(self.ctx(),replace(self.command(c,'commit',sequence=1),record_digest='0'*64))

    def test_production_and_grant_forgery_fail_closed(self):
        a=self.adapter();c=self.item(a);self.promote_item(a,c)
        for options in ({'test_only':False},{'test_only':True,'production':True}):
            with self.assertRaises(AuthorizationError):FakeMemoryAdapter(a.organizer,a.access,a.services,**options)
        with self.assertRaises(ContractError):replace(c,marking='PRODUCTION')
        with self.assertRaises(ContractError):replace(c.record,memory_eligible=True)
        with self.assertRaises(AuthorizationError):a.retrieve(self.ctx(identity='general'),self.command(c,'retrieve'))
        forged=AuthenticatedContext(environment='personal',principal=self.ctx().principal,role='director')
        with self.assertRaises(AuthorizationError):a.commit(forged,self.command(c,'commit'))

    def test_all_twelve_pairs_deny_memory_and_hq_operations(self):
        a=self.adapter();items={e:self.item(a,e) for e in ENVIRONMENTS}
        promoted={e:self.promote_item(a,c)[2] for e,c in items.items()}
        count=0
        for env in ENVIRONMENTS:
            for other in ENVIRONMENTS:
                if env==other:continue
                c=items[other]
                operations=[lambda:a.submit(self.ctx(env),c),lambda:a.history(self.ctx(env),other),
                    lambda:a.retrieve(self.ctx(env,'technology_code'),self.command(c,'retrieve','cross-read')),
                    lambda:a.commit(self.ctx(env),self.command(c,'commit','cross-commit')),
                    lambda:a.promote(self.ctx(env),self.command(c,'promote','cross-promote')),
                    lambda:a.revoke(self.ctx(env),self.command(c,'revoke','cross-revoke',sequence=promoted[other].sequence)),
                    lambda:a.delete(self.ctx(env),self.command(c,'delete','cross-delete',sequence=promoted[other].sequence)),
                    lambda:a.request_export(self.ctx(env),self.command(c,'request_export','cross-export')),
                    lambda:a.export_status(self.ctx(env),self.command(c,'export_status','cross-export-status')),
                    lambda:a.sync_status(self.ctx(env),self.command(c,'sync_status','cross-sync-status')),
                    lambda:a.hq_allow(self.ctx(env),self.command(c,'hq_allow','cross-hq-allow')),
                    lambda:a.hq_sync(self.ctx(env),self.command(c,'hq_sync','cross-hq-sync')),
                    lambda:a.expire(self.ctx(env),self.command(c,'expire','cross-expire',sequence=promoted[other].sequence)),
                    lambda:a.supersede(self.ctx(env),self.command(c,'supersede','cross-revise'))]
                for operation in operations:
                    with self.assertRaises(AuthorizationError):operation()
                    count+=1
        self.assertEqual(count,168)

    def test_owner_partition_retrieval_and_company_denial(self):
        a=self.adapter()
        for env in ENVIRONMENTS[1:]:
            c=self.item(a,env);self.promote_item(a,c)
            a.hq_allow(self.ctx(env),self.command(c,'hq_allow'))
            sync=a.hq_sync(self.ctx(env),self.command(c,'hq_sync'))
            self.assertEqual(sync.state,'HQ_SYNCED')
            result=a.hq_retrieve(self.ctx(),self.command(c,'hq_retrieve'))
            self.assertEqual(result.environment,env)
            self.assertEqual(result.candidate.record.source,c.record.source)
            for company in ENVIRONMENTS[1:]:
                with self.assertRaises(AuthorizationError):a.hq_retrieve(self.ctx(company),self.command(c,'hq_retrieve','company-owner'))
        with self.assertRaises(AuthorizationError):TestMemoryAccess(self.authority,test_only=True,owners=((self.ctx('fintra'),('fintra',),('internal',)),))

    def test_no_default_hq_eligibility_or_owner_authority(self):
        a=self.adapter();c=self.item(a,'fintra');self.promote_item(a,c)
        sync=a.hq_sync(self.ctx('fintra'),self.command(c,'hq_sync'))
        self.assertEqual(sync.state,'HQ_TOMBSTONE')
        with self.assertRaises(ContractError):a.hq_retrieve(self.ctx(),self.command(c,'hq_retrieve'))
        policy=TestMemoryAccess(self.authority,test_only=True)
        b=FakeMemoryAdapter(a.organizer,policy,a.services,test_only=True)
        with self.assertRaises(AuthorizationError):b.hq_retrieve(self.ctx(),self.command(c,'hq_retrieve'))

    def test_hq_revocation_deletion_and_expiry_tombstones(self):
        a=self.adapter()
        for index,op in enumerate(('revoke','delete','expire')):
            c=self.item(a,'fintra',text='React evidence '+str(index),key=str(index));_,_,promoted=self.promote_item(a,c)
            a.hq_allow(self.ctx('fintra'),self.command(c,'hq_allow'))
            a.hq_sync(self.ctx('fintra'),self.command(c,'hq_sync'))
            if op=='expire':self.now=c.record.valid_until
            receipt=getattr(a,op)(self.ctx('fintra'),self.command(c,op,sequence=promoted.sequence))
            self.assertEqual(receipt.state,op.upper()+'D' if op=='expire' else {'revoke':'REVOKED','delete':'DELETED'}[op])
            for method,ctx in ((a.retrieve,self.ctx('fintra','technology_code')),(a.hq_retrieve,self.ctx())):
                with self.assertRaises(ContractError):method(ctx,self.command(c,'retrieve' if method==a.retrieve else 'hq_retrieve','after-'+op))
            tombstone=a.hq_sync(self.ctx('fintra'),self.command(c,'hq_sync','tombstone-'+op))
            self.assertEqual(tombstone.state,'HQ_TOMBSTONE')
            self.now=1000

    def test_exports_sync_partial_failure_are_distinct(self):
        a=self.adapter();c=self.item(a);self.promote_item(a,c)
        with self.assertRaises(ContractError):a.sync_status(self.ctx(),self.command(c,'sync_status'))
        request=a.request_export(self.ctx(),self.command(c,'request_export'))
        partial=a.export_status(self.ctx(),self.command(c,'export_status','partial',fixture_result='PARTIAL'))
        self.assertEqual(partial.outcome,'PARTIAL')
        with self.assertRaises(ContractError):a.sync_status(self.ctx(),self.command(c,'sync_status'))
        a.request_export(self.ctx(),self.command(c,'request_export','retry-after-partial'))
        export=a.export_status(self.ctx(),self.command(c,'export_status'))
        failed=a.sync_status(self.ctx(),self.command(c,'sync_status','sync-failure',fixture_result='FAILED'))
        a.request_export(self.ctx(),self.command(c,'request_export','retry-after-sync-failure'))
        a.export_status(self.ctx(),self.command(c,'export_status','retry-export'))
        sync=a.sync_status(self.ctx(),self.command(c,'sync_status'))
        self.assertEqual(failed.outcome,'FAILED')
        self.assertEqual(len({r.receipt_id for r in (request,export,sync)}),3)
        self.assertEqual([r.operation for r in (request,export,sync)],['request_export','export_status','sync_status'])

    def test_timeout_after_commit_restart_reconciles_without_duplicate(self):
        a=self.adapter();c=self.item(a)
        with self.assertRaises(DeliveryAmbiguous):a.submit(self.ctx(),c,timeout_after_commit=True)
        self.assertEqual(len(a.history(self.ctx(),'personal')),1)
        self.assertFalse(any(e.topic=='offline.memory.submit' for e in self.store.outbox(self.ctx())))
        restarted=self.adapter()
        receipt=restarted.submit(self.ctx(),c)
        restarted.reconcile(self.ctx())
        self.assertEqual(receipt.state,'CANDIDATE')
        self.assertEqual(len(restarted.history(self.ctx(),'personal')),1)
        self.assertEqual(len([e for e in self.store.outbox(self.ctx()) if e.topic=='offline.memory.submit']),1)

    def test_outbox_exception_repairs_durable_receipt(self):
        a=self.adapter();c=self.item(a)
        with patch.object(self.store,'enqueue',side_effect=RuntimeError('delivery interrupted')):
            with self.assertRaises(RuntimeError):a.submit(self.ctx(),c)
        self.assertEqual(self.adapter().submit(self.ctx(),c).state,'CANDIDATE')
        self.assertEqual(len(a.history(self.ctx(),'personal')),1)

    def test_out_of_order_concurrent_stale_mutations(self):
        a=self.adapter();c=self.item(a);s=a.submit(self.ctx(),c)
        with self.assertRaises(ContractError):a.promote(self.ctx(),self.command(c,'promote',sequence=s.sequence))
        command=self.command(c,'commit',sequence=s.sequence)
        with ThreadPoolExecutor(max_workers=4) as pool:
            receipts=list(pool.map(lambda _:a.commit(self.ctx(),command),range(8)))
        self.assertTrue(all(r==receipts[0] for r in receipts))
        self.assertEqual(len(a.history(self.ctx(),'personal')),2)
        with self.assertRaises(ContractError):a.promote(self.ctx(),self.command(c,'promote','stale',sequence=s.sequence))

    def test_hq_failure_and_revocation_race_fail_closed(self):
        a=self.adapter();c=self.item(a,'fintra');_,_,promoted=self.promote_item(a,c)
        a.hq_allow(self.ctx('fintra'),self.command(c,'hq_allow'))
        failed=a.hq_sync(self.ctx('fintra'),self.command(c,'hq_sync','failed',fixture_result='FAILED'))
        self.assertEqual(failed.outcome,'FAILED')
        with self.assertRaises(ContractError):a.hq_retrieve(self.ctx(),self.command(c,'hq_retrieve'))
        with ThreadPoolExecutor(max_workers=2) as pool:
            sync=pool.submit(a.hq_sync,self.ctx('fintra'),self.command(c,'hq_sync','race-sync'))
            revoke=pool.submit(a.revoke,self.ctx('fintra'),self.command(c,'revoke',sequence=promoted.sequence))
            sync.result();revoke.result()
        with self.assertRaises(ContractError):a.hq_retrieve(self.ctx(),self.command(c,'hq_retrieve','after-race'))
        self.assertEqual(a.hq_sync(self.ctx('fintra'),self.command(c,'hq_sync','final-tombstone')).state,'HQ_TOMBSTONE')

    def test_supersession_preserves_history_and_hq_provenance(self):
        a=self.adapter();old=self.item(a,'fintra');_,_,promoted=self.promote_item(a,old)
        a.hq_allow(self.ctx('fintra'),self.command(old,'hq_allow'))
        a.hq_sync(self.ctx('fintra'),self.command(old,'hq_sync'))
        packet=self.approved('fintra',text='React corrected evidence',request_id='corrected')
        batch=self.process(a.organizer,packet,'correction',relation='CORRECTION',targets=(old.record.record_id,),expected_head=hash_content(old.record))
        new=a.candidate(self.ctx('fintra'),batch.record.record_id,'corrected-candidate')
        self.promote_item(a,new)
        with self.assertRaises(ContractError):a.hq_retrieve(self.ctx(),self.command(old,'hq_retrieve'))
        superseded=a.supersede(self.ctx('fintra'),self.command(old,'supersede',sequence=promoted.sequence,related_ids=(new.record.record_id,)))
        self.assertEqual(superseded.state,'SUPERSEDED')
        self.assertEqual(a.hq_sync(self.ctx('fintra'),self.command(old,'hq_sync','old-tombstone')).state,'HQ_TOMBSTONE')
        a.hq_allow(self.ctx('fintra'),self.command(new,'hq_allow'))
        a.hq_sync(self.ctx('fintra'),self.command(new,'hq_sync'))
        self.assertEqual(a.hq_retrieve(self.ctx(),self.command(new,'hq_retrieve')).candidate,new)
        self.assertEqual(a.history(self.ctx('fintra'),'fintra')[0].candidate[0],old)

    def test_disputed_or_expired_research_denied_after_promotion(self):
        a=self.adapter();c=self.item(a);self.promote_item(a,c)
        other=self.approved(text='React contradictory evidence',request_id='conflict')
        self.process(a.organizer,other,'conflict',relation='CONFLICT',targets=(c.record.record_id,))
        with self.assertRaises(ContractError):a.retrieve(self.ctx(identity='technology_code'),self.command(c,'retrieve'))
        with self.assertRaises(ContractError):a.candidate(self.ctx(),c.record.record_id,'resubmit')

    def test_failed_commit_does_not_promote_and_audit_is_scoped(self):
        a=self.adapter();c=self.item(a);s=a.submit(self.ctx(),c)
        failed=a.commit(self.ctx(),self.command(c,'commit','failure',sequence=s.sequence,fixture_result='FAILED'))
        self.assertEqual(failed.state,'CANDIDATE')
        with self.assertRaises(ContractError):a.promote(self.ctx(),self.command(c,'promote',sequence=s.sequence))
        history=a.history(self.ctx(),'personal')
        self.assertTrue(all(e.environment==e.receipt.environment=='personal' for e in history))
        self.assertTrue(all(e.receipt.actor==self.ctx().principal for e in history))
        self.assertEqual(history[-1].receipt.outcome,'FAILED')

    def test_unapproved_candidate_verdicts_and_expired_promotion_denied(self):
        a=self.adapter();c=self.item(a)
        for verdict in ('REJECTED','NEEDS_MORE_RESEARCH'):
            with self.assertRaises(ContractError):replace(c,verification=replace(c.verification,verdict=verdict))
        s=a.submit(self.ctx(),c)
        committed=a.commit(self.ctx(),self.command(c,'commit',sequence=s.sequence))
        self.now=c.record.valid_until
        with self.assertRaises(ContractError):a.promote(self.ctx(),self.command(c,'promote',sequence=committed.sequence))
        with self.assertRaises(ContractError):a.retrieve(self.ctx(identity='technology_code'),self.command(c,'retrieve'))

    def test_hq_owner_grant_cannot_be_reissued_or_selected_in_metadata(self):
        a=self.adapter();c=self.item(a,'fintra');self.promote_item(a,c)
        a.hq_allow(self.ctx('fintra'),self.command(c,'hq_allow'))
        a.hq_sync(self.ctx('fintra'),self.command(c,'hq_sync'))
        reissued=self.authority.context(self.ctx().principal)
        with self.assertRaises(AuthorizationError):a.hq_retrieve(reissued,self.command(c,'hq_retrieve'))
        with self.assertRaises(ContractError):replace(c,environment='sc_products')
        with self.assertRaises(ContractError):replace(c,company_name='SC Products Group')
        with self.assertRaises(AuthorizationError):a.hq_retrieve(self.ctx('sc_products'),self.command(c,'hq_retrieve'))

    def test_fresh_process_replays_lost_receipt_and_reads_citations(self):
        import subprocess,sys,os,json
        a=self.adapter();c=self.item(a);s=a.submit(self.ctx(),c)
        command=self.command(c,'commit',sequence=s.sequence)
        with self.assertRaises(DeliveryAmbiguous):a.commit(self.ctx(),command,timeout_after_commit=True)
        script="""
import sys,json,socket
from unittest.mock import patch
patch.object(socket,'socket',side_effect=AssertionError('network forbidden in restart worker')).start()
from test_research import bootstrap
from alfred_research.intelligence import IntelligenceOrganizer
from alfred_research.memory import FakeMemoryAdapter,TestMemoryAccess,KnowledgeCandidate,MemoryCommand
from alfred_research.contracts import ENVIRONMENTS
payload=json.load(sys.stdin)
authority,contexts,models,registrations,store,roster=bootstrap(sys.argv[1],snapshot=payload['registration'])
c=KnowledgeCandidate.from_payload(payload['candidate'])
command=MemoryCommand.from_payload(payload['command'])
o=IntelligenceOrganizer(store,clock=lambda:1000)
services={e:contexts[e+'-director'] for e in ENVIRONMENTS}
access=TestMemoryAccess(authority,test_only=True,specialists=((contexts['personal-technology_code'],('Frontend',),('internal',)),))
adapter=FakeMemoryAdapter(o,access,services,test_only=True)
receipt=adapter.commit(services['personal'],command)
assert receipt.state=='COMMITTED'
adapter.reconcile(services['personal'])
assert len(adapter.history(services['personal'],'personal'))==2
assert adapter.history(services['personal'],'personal')[0].candidate[0].record.source.evidence
promote=MemoryCommand(environment='personal',record_id=command.record_id,record_digest=command.record_digest,
    operation='promote',operation_id='child-promote',expected_sequence=receipt.sequence)
assert adapter.promote(services['personal'],promote).state=='PROMOTED'
read=MemoryCommand(environment='personal',record_id=command.record_id,record_digest=command.record_digest,
    operation='retrieve',operation_id='child-fresh-read')
result=adapter.retrieve(contexts['personal-technology_code'],read)
assert result.candidate.record.source.evidence and result.receipt.state=='RETRIEVABLE'
print('fresh process recovered COMMITTED receipt and retrieved promoted citations; no duplicate')
"""
        payload={'registration':self.registrations.snapshot_for_tests(),'candidate':c.payload(),'command':command.payload()}
        result=subprocess.run([sys.executable,'-c',script,self.temp.name],input=json.dumps(payload),
            capture_output=True,text=True,timeout=30,env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',PYTHONPATH='src:tests'))
        self.assertEqual(result.returncode,0,result.stderr)
        self.assertIn('no duplicate',result.stdout)

    def test_concurrent_distinct_revisions_have_one_winner(self):
        a=self.adapter();c=self.item(a);_,_,promoted=self.promote_item(a,c)
        def mutate(op):
            try:return getattr(a,op)(self.ctx(),self.command(c,op,sequence=promoted.sequence))
            except ContractError:return None
        with ThreadPoolExecutor(max_workers=2) as pool:
            receipts=list(pool.map(mutate,('revoke','delete')))
        self.assertEqual(sum(r is not None for r in receipts),1)
        self.assertEqual(len(a.history(self.ctx(),'personal')),4)
        with self.assertRaises(ContractError):a.retrieve(self.ctx(identity='technology_code'),self.command(c,'retrieve'))

    def test_export_simulation_creates_no_vault_files(self):
        from pathlib import Path
        a=self.adapter();c=self.item(a);self.promote_item(a,c)
        a.request_export(self.ctx(),self.command(c,'request_export'))
        a.export_status(self.ctx(),self.command(c,'export_status'))
        a.sync_status(self.ctx(),self.command(c,'sync_status'))
        self.assertFalse(list(Path(self.temp.name).rglob('*.md')))
        self.assertFalse(list(Path(self.temp.name).rglob('*.markdown')))
        self.assertTrue(all(e.receipt.marking=='SIMULATED / NON_PRODUCTION' for e in a.history(self.ctx(),'personal')))

    def test_specialist_association_does_not_override_classification_grant(self):
        a=self.adapter();c=self.item(a,'fintra');self.promote_item(a,c)
        a.hq_allow(self.ctx('fintra'),self.command(c,'hq_allow'))
        a.hq_sync(self.ctx('fintra'),self.command(c,'hq_sync'))
        restricted=TestMemoryAccess(self.authority,test_only=True,
            specialists=((self.ctx('fintra','technology_code'),('Frontend',),('public',)),),
            owners=((self.ctx(),('fintra',),('public',)),))
        b=FakeMemoryAdapter(a.organizer,restricted,a.services,test_only=True)
        with self.assertRaises(AuthorizationError):b.retrieve(self.ctx('fintra','technology_code'),self.command(c,'retrieve'))
        with self.assertRaises(AuthorizationError):b.hq_retrieve(self.ctx(),self.command(c,'hq_retrieve'))

    def test_failed_partial_requests_cannot_authorize_export_or_sync(self):
        a=self.adapter();c=self.item(a);self.promote_item(a,c)
        for outcome in ('FAILED','PARTIAL'):
            request=a.request_export(self.ctx(),self.command(c,'request_export',outcome,fixture_result=outcome))
            before=a.history(self.ctx(),'personal')
            for op in ('export_status','sync_status'):
                with self.assertRaises(ContractError):getattr(a,op)(self.ctx(),self.command(c,op,'bad-'+outcome+op))
            self.assertEqual(a.history(self.ctx(),'personal'),before)
            self.assertEqual(request.outcome,outcome)
        with self.assertRaises(ContractError):self.command(c,'request_export','rejected',fixture_result='REJECTED')

    def test_bound_export_and_sync_success_replay(self):
        a=self.adapter();c=self.item(a);self.promote_item(a,c)
        request_command=self.command(c,'request_export')
        request=a.request_export(self.ctx(),request_command)
        export_command=self.command(c,'export_status')
        exported=a.export_status(self.ctx(),export_command)
        sync_command=self.command(c,'sync_status')
        synced=a.sync_status(self.ctx(),sync_command)
        before=a.history(self.ctx(),'personal')
        for method,command,receipt in ((a.request_export,request_command,request),(a.export_status,export_command,exported),(a.sync_status,sync_command,synced)):
            self.assertEqual(method(self.ctx(),command),receipt)
        self.assertEqual(a.history(self.ctx(),'personal'),before)
        self.assertEqual(exported.prerequisite_receipt,(request.receipt_id,))
        self.assertEqual(synced.prerequisite_receipt,(exported.receipt_id,))
        self.assertEqual(synced.export_attempt,request.export_attempt)
        self.assertEqual(len({request.receipt_id,exported.receipt_id,synced.receipt_id}),3)

    def test_old_completion_replays_cannot_override_new_failed_attempt(self):
        a=self.adapter();c=self.item(a);self.promote_item(a,c)
        a.request_export(self.ctx(),self.command(c,'request_export','first'))
        export_command=self.command(c,'export_status','first-export');a.export_status(self.ctx(),export_command)
        sync_command=self.command(c,'sync_status','first-sync');a.sync_status(self.ctx(),sync_command)
        a.request_export(self.ctx(),self.command(c,'request_export','new-failed',fixture_result='FAILED'))
        before=a.history(self.ctx(),'personal')
        for method,command in ((a.export_status,export_command),(a.sync_status,sync_command)):
            with self.assertRaises(ContractError):method(self.ctx(),command)
        self.assertEqual(a.history(self.ctx(),'personal'),before)

    def test_old_success_cannot_override_new_failure_in_same_attempt(self):
        a=self.adapter();c=self.item(a);self.promote_item(a,c)
        a.request_export(self.ctx(),self.command(c,'request_export'))
        command=self.command(c,'export_status');a.export_status(self.ctx(),command)
        failed=a.export_status(self.ctx(),self.command(c,'export_status','later-failure',fixture_result='FAILED'))
        with self.assertRaises(ContractError):a.export_status(self.ctx(),command)
        with self.assertRaises(ContractError):a.sync_status(self.ctx(),self.command(c,'sync_status'))
        self.assertEqual(failed.outcome,'FAILED')

    def test_export_binding_rejects_wrong_record_version_destination_attempt(self):
        a=self.adapter();c=self.item(a);self.promote_item(a,c)
        a.request_export(self.ctx(),self.command(c,'request_export'))
        command=self.command(c,'export_status')
        for changed in ({'export_record_version':(c.record_version+1,)},
            {'export_destination':('test-obsidian:fintra',)}, {'export_attempt':('forged-attempt',)},
            {'prerequisite_receipt':('0'*64,)}, {'record_digest':'0'*64}, {'record_id':'wrong-record'}):
            with self.assertRaises(ContractError):a.export_status(self.ctx(),replace(command,**changed))
        with self.assertRaises(AuthorizationError):a.export_status(self.ctx('fintra'),command)
        a.export_status(self.ctx(),command)
        sync=self.command(c,'sync_status')
        with self.assertRaises(ContractError):a.sync_status(self.ctx(),replace(sync,prerequisite_receipt=command.prerequisite_receipt))

    def test_export_crash_restart_requires_actual_completion(self):
        a=self.adapter();c=self.item(a);self.promote_item(a,c)
        command=self.command(c,'request_export')
        with self.assertRaises(DeliveryAmbiguous):a.request_export(self.ctx(),command,timeout_after_commit=True)
        restarted=self.adapter();restarted.reconcile(self.ctx())
        request=restarted.request_export(self.ctx(),command)
        self.assertEqual(request.state,'EXPORT_REQUESTED')
        with self.assertRaises(ContractError):restarted.sync_status(self.ctx(),self.command(c,'sync_status'))
        export=restarted.export_status(self.ctx(),self.command(c,'export_status'))
        self.assertEqual(export.state,'EXPORTED')
        self.assertEqual(restarted.sync_status(self.ctx(),self.command(c,'sync_status')).state,'SYNCED')

    def test_revocation_and_supersession_block_delayed_export_success(self):
        a=self.adapter();c=self.item(a);_,_,promoted=self.promote_item(a,c)
        a.request_export(self.ctx(),self.command(c,'request_export'))
        command=self.command(c,'export_status');a.export_status(self.ctx(),command)
        a.revoke(self.ctx(),self.command(c,'revoke',sequence=promoted.sequence))
        with self.assertRaises(ContractError):a.export_status(self.ctx(),command)
        other=self.item(a,text='React separate version',key='other');self.promote_item(a,other)
        a.request_export(self.ctx(),self.command(other,'request_export','other-request'))
        delayed=self.command(other,'export_status','other-completion')
        p=self.approved(text='React corrected version',request_id='new')
        self.process(a.organizer,p,'new',relation='CORRECTION',targets=(other.record.record_id,),expected_head=hash_content(other.record))
        with self.assertRaises(ContractError):a.export_status(self.ctx(),delayed)

if __name__=='__main__':unittest.main()
