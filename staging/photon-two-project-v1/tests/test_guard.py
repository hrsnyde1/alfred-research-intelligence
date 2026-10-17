import ast
import asyncio
import importlib.util
from pathlib import Path
from types import SimpleNamespace, ModuleType
from unittest.mock import patch, AsyncMock
import unittest
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('staged_guard',ROOT/'modified/gateway/photon_research.py')
g=importlib.util.module_from_spec(spec);spec.loader.exec_module(g)
ENV={'PHOTON_RESEARCH_CONNECTION_REF':'connection', 'PHOTON_RESEARCH_ENABLED':'1','PHOTON_RESEARCH_LINE':'line','PHOTON_RESEARCH_SPACE':'space',
     'PHOTON_RESEARCH_SENDER':'owner','PHOTON_RESEARCH_PROFILE':'research'}
class Event:
    def __init__(self,**values):self.__dict__.update(values)
class Source(SimpleNamespace):
    def to_dict(self):return dict(vars(self))
class Adapter:
    def build_source(self,**values):return Source(**values)
def wire(**changes):
    value={'project':'research','projectBinding':'research-connection-v1','research':{
        'connection_ref':'connection','line':'line','space':'space','sender':'owner','profile':'research','originalMessageId':'original','route':'photon-research:scope'},
        'space':{'id':'photon-research:scope'},'sender':{'id':'owner'},'messageId':'research:message',
        'content':{'type':'text','text':'/personal override project'}}
    value.update(changes);return value
class Scope:
    async def __aenter__(self):pass
    async def __aexit__(self,*args):pass
class Tests(unittest.IsolatedAsyncioTestCase):
    async def test_personal_route_is_untouched_and_unknown_reserved_never_falls_back(self):
        self.assertEqual(await g.guard(None,Event(source=Source(chat_id='personal'),raw_message={})),(False,None))
        self.assertEqual(await g.guard(None,Event(source=Source(chat_id='photon-research:unknown'),raw_message={})),(True,None))

    async def test_identity_survives_and_only_research_hook_runs(self):
        with patch.dict('os.environ',ENV,clear=True):
            e=g.receive(Adapter(),wire(),Event)
            lifecycle=ModuleType('hermes_cli.lifecycle');lifecycle.has_hook=lambda n:n=='research_project_intake'
            lifecycle.ainvoke_hook=AsyncMock(return_value=[{'action':'handled','reply':'pending only'}])
            consumer=ModuleType('gateway.run_inbound_consumer');consumer._routed_scope=lambda *a:Scope()
            runner=SimpleNamespace(_profile_name_for_source=lambda s:'research')
            with patch.dict('sys.modules',{'hermes_cli.lifecycle':lifecycle,'gateway.run_inbound_consumer':consumer}):
                self.assertEqual(await g.guard(runner,e),(True,'pending only'))
                args=lifecycle.ainvoke_hook.call_args.kwargs
                self.assertEqual(args['research_identity']['originalMessageId'],'original')
                self.assertEqual(args['source']['profile'],'research')
                self.assertEqual(args['text'],'/personal override project')
                lifecycle.ainvoke_hook.side_effect=RuntimeError('failure')
                self.assertTrue((await g.guard(runner,e))[0])

    async def test_missing_profile_and_disabled_mode_deny(self):
        with patch.dict('os.environ',ENV,clear=True):
            e=g.receive(Adapter(),wire(),Event)
            self.assertEqual(await g.guard(SimpleNamespace(_profile_name_for_source=lambda s:None),e),(True,None))
        with patch.dict('os.environ',{},clear=True):
            with self.assertRaises(ValueError):g.receive(Adapter(),wire(),Event)
            self.assertTrue((await g.guard(None,e))[0])

    async def test_missing_unknown_and_forged_identity_denied(self):
        for field in ('project','projectBinding','messageId','sender'):
            w=wire();w.pop(field)
            with self.subTest(field=field),self.assertRaises(ValueError):g.receive(Adapter(),w,Event,ENV)
        w=wire();w['research']['sender']='forged'
        with self.assertRaises(ValueError):g.receive(Adapter(),w,Event,ENV)

    async def test_outbound_projects_explicit_and_no_caller_override(self):
        self.assertEqual(g.outbound('/send',{'spaceId':'personal','text':'hello'})['project'],'personal')
        with self.assertRaises(ValueError):g.outbound('/send',{'spaceId':'personal','project':'research'})
        with patch.dict('os.environ',ENV,clear=True):
            for body in ({'spaceId':'photon-research:scope','text':'ACK'},):
                with self.assertRaises(ValueError):g.outbound('/send',body)
            b=g.outbound('/send',{'spaceId':'photon-research:scope','operationId':'research:event','text':'ACK'})
            self.assertEqual(b['project'],'research')
            with self.assertRaises(ValueError):g.outbound('/typing',b)

    async def test_personal_initialization_and_handlers_preserved_structurally(self):
        old=(ROOT/'baseline/plugins/platforms/photon/sidecar/index.mjs').read_text()
        new=(ROOT/'modified/plugins/platforms/photon/sidecar/index.mjs').read_text()
        a=old.index('const app = await Spectrum(');b=old.index('// Effect-name',a)
        self.assertIn(old[a:b],new)
        a=old.index('    if (req.url === "/send")');b=old.index('    res.statusCode = 404;',a)
        self.assertIn(old[a:b],new) # every Personal send/media/reaction/typing handler unchanged
        a=old.index('async function resolveSpace');b=old.index('// Constant-time',a)
        self.assertIn(old[a:b],new)

    async def test_gateway_guard_precedes_all_ordinary_paths(self):
        s=(ROOT/'modified/gateway/run_inbound.py').read_text();tree=ast.parse(s)
        method=next(n for n in ast.walk(tree) if isinstance(n,ast.AsyncFunctionDef) and n.name=='_handle_message')
        self.assertEqual(ast.unparse(method.body[1]),'from gateway.photon_research import guard')
        self.assertIn('if reserved:',ast.unparse(method.body[3]))
        self.assertLess(s.index('reserved, reply = await guard'),s.index('_admitted = await self._hm_admit_event'))

    async def test_adapter_dispatch_prefix_is_terminal_and_personal_tail_unchanged(self):
        path='plugins/platforms/photon/adapter.py'
        def method(tree):return next(n for n in ast.walk(ast.parse(tree)) if isinstance(n,ast.AsyncFunctionDef) and n.name=='_dispatch_inbound')
        old=method((ROOT/'baseline'/path).read_text());new=method((ROOT/'modified'/path).read_text())
        self.assertEqual([ast.dump(n) for n in old.body[1:]],[ast.dump(n) for n in new.body[3:]])
        prefix=ast.unparse(new.body[1]);self.assertIn('return',prefix)
        self.assertIn('await self._message_handler(message)',prefix)
        self.assertNotIn('await self.handle_message(message)',prefix)

    async def test_installed_personal_send_function_matches_staged_with_fake_transport(self):
        def load(tree):
            node=next(n for n in ast.walk(ast.parse(tree)) if isinstance(n,ast.AsyncFunctionDef) and n.name=='_sidecar_send')
            namespace={'_richlink_candidate':lambda s:'https://synthetic.invalid' if s=='url' else None,
                '_markdown_enabled':lambda:False,'_sidecar_payload_text':lambda text,md:text,
                'logger':SimpleNamespace(warning=lambda *a:None)}
            exec('from __future__ import annotations\n'+ast.unparse(node),namespace)
            return namespace['_sidecar_send']
        old=load((ROOT/'baseline/plugins/platforms/photon/adapter.py').read_text())
        new=load((ROOT/'modified/plugins/platforms/photon/adapter.py').read_text())
        for text in ('hello','url','x'*30):
            outputs=[]
            for fn in (old,new):
                calls=[]
                async def post(path,body,**kwargs):
                    calls.append((path,body,kwargs));return SimpleNamespace(success=path!='/send-richlink',error='synthetic failure')
                adapter=SimpleNamespace(MAX_MESSAGE_LENGTH=20,_post_send=post)
                result=await fn(adapter,'personal-space',text)
                outputs.append((result.success,calls))
            self.assertEqual(*outputs)

    async def test_installed_personal_http_payload_only_adds_explicit_project(self):
        def load(tree):
            node=next(n for n in ast.walk(ast.parse(tree)) if isinstance(n,ast.AsyncFunctionDef) and n.name=='_sidecar_call')
            class Client:
                async def __aenter__(self):return self
                async def __aexit__(self,*a):pass
                async def post(self,url,**kwargs):
                    captured.append(kwargs['json']);return SimpleNamespace(status_code=200,json=lambda:{'ok':True,'messageId':'original'})
            namespace={'httpx':SimpleNamespace(AsyncClient=lambda **kw:Client())}
            exec('from __future__ import annotations\n'+ast.unparse(node),namespace)
            return namespace['_sidecar_call']
        captured=[]
        adapter=SimpleNamespace(_http_client=True,_sidecar_url=lambda p:p,_sidecar_headers=lambda:{})
        old=load((ROOT/'baseline/plugins/platforms/photon/adapter.py').read_text())
        new=load((ROOT/'modified/plugins/platforms/photon/adapter.py').read_text())
        with patch.dict('sys.modules',{'gateway.photon_research':g}):
            for endpoint in ('/send','/typing','/react','/send-attachment','/send-poll'):
                body={'spaceId':'personal-space','text':'synthetic'}
                a=await old(adapter,endpoint,body);b=await new(adapter,endpoint,body)
                self.assertEqual(a,b);self.assertEqual(captured[-1],{**captured[-2],'project':'personal'})

    async def test_research_http_uses_separate_host_credential_and_missing_never_falls_back(self):
        node=next(n for n in ast.walk(ast.parse((ROOT/'modified/plugins/platforms/photon/adapter.py').read_text()))
            if isinstance(n,ast.AsyncFunctionDef) and n.name=='_sidecar_call')
        captured=[]
        class Client:
            async def __aenter__(self):return self
            async def __aexit__(self,*a):pass
            async def post(self,url,**kwargs):
                captured.append(kwargs['headers']);return SimpleNamespace(status_code=200,json=lambda:{'ok':True})
        namespace={'httpx':SimpleNamespace(AsyncClient=lambda **kw:Client()),'_get_scoped_secret':lambda key:'fixture-research-token'}
        exec('from __future__ import annotations\n'+ast.unparse(node),namespace)
        adapter=SimpleNamespace(_http_client=True,_sidecar_token='fixture-personal-token',
            _sidecar_url=lambda path:path,_sidecar_headers=lambda:{'X-Hermes-Sidecar-Token':'fixture-personal-token'})
        body={'spaceId':'photon-research:scope','operationId':'research:event','text':'ACK'}
        with patch.dict('os.environ',ENV,clear=True),patch.dict('sys.modules',{'gateway.photon_research':g}):
            await namespace['_sidecar_call'](adapter,'/send',body)
            self.assertEqual(captured,[{'X-Hermes-Research-Token':'fixture-research-token'}])
            for token in (None,'fixture-personal-token'):
                namespace['_get_scoped_secret']=lambda key:token
                with self.assertRaises(RuntimeError):await namespace['_sidecar_call'](adapter,'/send',body)
            self.assertEqual(len(captured),1)
