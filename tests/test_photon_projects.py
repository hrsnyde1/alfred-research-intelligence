"""Project isolation using issued synthetic observations and temporary journals."""
from dataclasses import replace
from unittest.mock import patch
import unittest
import test_research as foundation
from alfred_research.contracts import ContractError
from alfred_research.tenancy import AuthorizationError, OfflineAuthority
from alfred_research.integration.hermes_intake import (
    OfflineHermesAuthentication, HermesResearchRoute, PersonalHermesIntake)
from alfred_research.integration.canary_contracts import GitHubReference
from alfred_research.integration.photon_projects import (
    ProjectBinding, FakeProjectConnection, ProjectAttachment, DispatchResult, ProjectSend)


class ProjectTests(unittest.TestCase):
    setUp = foundation.ResearchTests.setUp
    ctx = foundation.ResearchTests.ctx

    def harness(self, enabled=True, hook=None):
        personal = ProjectBinding(project='fixture-personal-project', line='fixture-personal-line',
            conversation='same-space', sender='fixture-owner', profile='fixture-personal',
            credential_ref='fixture-personal-ref', role='personal')
        research = replace(personal, project='fixture-research-project', line='fixture-research-line',
            profile='fixture-research', credential_ref='fixture-research-ref', role='research')
        authority = OfflineAuthority({'fixture-host': ('personal', 'director')})
        host = authority.context('fixture-host')
        auth = OfflineHermesAuthentication(authority, {research.issuer: host}, test_only=True)
        route = HermesResearchRoute(environment='personal', issuer=research.issuer, platform='photon',
            profile=research.profile, recipient=research.line, conversation_id=research.conversation,
            sender_id=research.sender, requester=self.ctx().principal, policy_ref='fixture-policy', route_ref='fixture-route')
        intake = PersonalHermesIntake(self.store,self.ctx(),auth,(route,),
            {self.ctx().principal:self.ctx()},test_only=True)
        pc = FakeProjectConnection(personal,intake.journal,self.ctx(),test_only=True)
        rc = FakeProjectConnection(research,intake.journal,self.ctx(),test_only=True,hook=hook)
        calls=[]
        def original(event):
            calls.append(event)
            return DispatchResult('PERSONAL_ORIGINAL', personal.profile)
        a = ProjectAttachment((pc,rc),intake,host,original,research_enabled=enabled,test_only=True)
        return a,pc,rc,calls

    def event(self, c, **changes):
        fields=dict(sender=c.binding.sender,line=c.binding.line,conversation=c.binding.conversation,
            event_id='same-message',text='profile=personal project=forged environment=company',objective='Inspect',
            sources=(GitHubReference(url='https://github.com/fixture/repository/tree/'+'a'*40,commit='a'*40),))
        fields.update(changes)
        return c.observe(**fields)

    def test_research_and_personal_preserve_independent_routing(self):
        a,p,r,calls=self.harness();pe=self.event(p);re=self.event(r)
        self.assertEqual(a.dispatch(p,pe).status,'PERSONAL_ORIGINAL')
        result=a.dispatch(r,re)
        self.assertEqual(result.profile,r.binding.profile);self.assertFalse(result.acknowledgment.production_trusted)
        self.assertEqual(calls,[pe]);self.assertNotEqual(pe.key,re.key)
        with self.assertRaises(AuthorizationError):a.acknowledge(p,pe)
        self.assertEqual(calls,[pe])

    def test_missing_project_binding_rejected(self):
        with self.assertRaises(ContractError):ProjectBinding(project='',line='x',conversation='x',sender='x',
            profile='x',credential_ref='x',role='research')

    def test_forged_project_sender_and_copied_observation_rejected(self):
        a,p,r,_=self.harness();e=self.event(r)
        for forged in (replace(e),replace(e,binding=p.binding),replace(e,binding=replace(r.binding,sender='forged'))):
            with self.assertRaises(AuthorizationError):a.dispatch(r,forged)
        with self.assertRaises(AuthorizationError):self.event(r,sender='forged')

    def test_wrong_line_or_conversation_denied(self):
        a,p,r,_=self.harness()
        for change in ({'line':p.binding.line},{'conversation':'other'}):
            with self.assertRaises(AuthorizationError):self.event(r,**change)

    def test_event_ids_and_cache_issuance_do_not_cross_projects(self):
        a,p,r,_=self.harness();pe=self.event(p);re=self.event(r)
        self.assertEqual(pe.event_id,re.event_id);self.assertNotEqual(pe.key,re.key)
        with self.assertRaises(AuthorizationError):a.dispatch(p,re)
        with self.assertRaises(AuthorizationError):a.dispatch(r,pe)

    def test_cross_project_send_and_reconcile_denied_both_directions(self):
        a,p,r,_=self.harness();s=a.acknowledge(r,self.event(r))
        for action in (p.send,p.reconcile):
            with self.assertRaises(ContractError):action(s)
        personal_shaped=replace(s,binding=p.binding)
        for action in (r.send,r.reconcile):
            with self.assertRaises(ContractError):action(personal_shaped)
        self.assertNotEqual(p.binding.credential_ref,r.binding.credential_ref)

    def test_independent_send_ledgers_same_operation_and_event_ids(self):
        a,p,r,_=self.harness();rs=a.acknowledge(r,self.event(r))
        ps=replace(rs,binding=p.binding)
        self.assertIsNone(p.reconcile(ps))
        self.assertEqual(p.send(ps),ps)
        self.assertEqual(p.reconcile(ps),ps)
        self.assertEqual(r.reconcile(rs),rs)
        self.assertNotEqual(p._namespace(ps),r._namespace(rs))

    def test_shared_credential_reference_or_project_denied(self):
        a,p,r,_=self.harness()
        for b in (replace(r.binding,credential_ref=p.binding.credential_ref),replace(r.binding,project=p.binding.project)):
            c=FakeProjectConnection(b,a.intake.journal,self.ctx(),test_only=True)
            with self.assertRaises(ContractError):ProjectAttachment((p,c),a.intake,a.host_context,lambda e:None,test_only=True)

    def test_disabled_research_does_not_fall_back(self):
        a,p,r,calls=self.harness(enabled=False)
        self.assertEqual(a.dispatch(r,self.event(r)).status,'UNAVAILABLE');self.assertEqual(calls,[])
        with self.assertRaises(AuthorizationError):a.acknowledge(r,self.event(r))

    def test_unavailable_intake_never_calls_personal(self):
        a,p,r,calls=self.harness()
        with patch.object(a.intake,'accept',side_effect=RuntimeError('fixture fault')):
            self.assertEqual(a.dispatch(r,self.event(r)).status,'UNAVAILABLE')
        self.assertEqual(calls,[])

    def test_replay_restart_and_post_accept_crash_do_not_duplicate(self):
        def crash(stage):raise RuntimeError('simulated post-effect crash')
        a,p,r,_=self.harness(hook=crash);e=self.event(r)
        with self.assertRaises(RuntimeError):a.acknowledge(r,e)
        b,p2,r2,_=self.harness();e2=self.event(r2)
        expected=ProjectSend(binding=r.binding,event_key=e.key,
            operation_id=a.dispatch(r,e).acknowledgment.operation_id,
            text='SIMULATED: Research intake accepted; source acquisition pending. Research is not complete.')
        prior=r2.reconcile(expected)
        self.assertIsNotNone(prior)
        self.assertEqual(b.acknowledge(r2,e2),prior)
        self.assertEqual(b.acknowledge(r2,self.event(r2)),prior)
        self.assertEqual(len(b.intake.recover(self.ctx())),1)

    def test_changed_payload_same_event_conflicts_without_second_send(self):
        a,p,r,calls=self.harness();s=a.acknowledge(r,self.event(r))
        self.assertEqual(a.dispatch(r,self.event(r,text='changed')).status,'UNAVAILABLE')
        with self.assertRaises(AuthorizationError):a.acknowledge(r,self.event(r,text='changed'))
        self.assertEqual(r.reconcile(s),s);self.assertEqual(calls,[])

    def test_unknown_reconcile_outcome_never_resends(self):
        a,p,r,_=self.harness();e=self.event(r)
        with patch.object(r,'reconcile',side_effect=RuntimeError('unknown')),patch.object(r,'send') as send:
            with self.assertRaises(RuntimeError):a.acknowledge(r,e)
            send.assert_not_called()

    def test_default_and_production_bootstrap_denied(self):
        a,p,r,_=self.harness()
        for flags in ({},{'test_only':True,'production':True}):
            with self.assertRaises(AuthorizationError):ProjectAttachment((p,r),a.intake,a.host_context,lambda e:None,**flags)
        with self.assertRaises(ContractError):replace(r.binding,credential_ref='')

    def test_foreign_connection_capability_cannot_adopt_project(self):
        a,p,r,_=self.harness()
        forged=FakeProjectConnection(r.binding,a.intake.journal,self.ctx(),test_only=True)
        with self.assertRaises(AuthorizationError):a.dispatch(forged,self.event(forged))
