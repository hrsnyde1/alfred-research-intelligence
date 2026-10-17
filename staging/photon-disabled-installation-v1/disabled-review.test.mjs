import test from 'node:test';import assert from 'node:assert/strict';import fs from 'node:fs';import vm from 'node:vm';
import {CallerBindings} from '../photon-two-project-v1/modified/plugins/platforms/photon/sidecar/caller-bindings.mjs';
import {ResearchLifecycle} from '../photon-two-project-v1/modified/plugins/platforms/photon/sidecar/research-lifecycle.mjs';
const source=fs.readFileSync(new URL('../photon-two-project-v1/modified/plugins/platforms/photon/sidecar/index.mjs',import.meta.url),'utf8');
function fixture(){
 const env={PHOTON_RESEARCH_ENABLED:'0',get PHOTON_RESEARCH_SIDECAR_TOKEN(){throw Error('disabled secret access');},
 get PHOTON_RESEARCH_PROJECT_SECRET(){throw Error('disabled project secret access');}};
 const sent=[];const context={process:{env},sharedToken:'fixture-legacy',CallerBindings,ResearchLifecycle,deliver:async()=>{},
 http:{createServer:handler=>({handler})},unauthorized:()=>401,badRequest:()=>400,ok:(r,data)=>data,
 readBody:async req=>req.body,resolveSpace:async id=>({send:async text=>{sent.push([id,text]);return {id:'fixture-personal'}}}),
 chooseSendFormat:()=> 'text',spectrumText:x=>x,spectrumMarkdown:x=>x,console:{error:()=>{}}};
 const a=source.indexOf('const callers = new CallerBindings'),b=source.indexOf('server.listen(',a);
 vm.runInNewContext(source.slice(a,b)+';this.handle=server.handler;this.lifecycle=researchProject;',context);
 return {context,sent,send:(headers,body)=>context.handle({method:'POST',url:'/send',headers,body},{})};
}
test('exact disabled initialization never resolves Research secrets or starts worker',async()=>{
 const h=fixture();h.context.lifecycle.start();assert.equal(h.context.lifecycle.state,'disabled');assert.equal(h.context.lifecycle.attempts,0);await h.context.lifecycle.stop();
});
test('Research caller cannot authenticate while disabled, even alongside legacy token',async()=>{
 const h=fixture();for(const headers of [{'x-hermes-research-token':'fixture-research'},
 {'x-hermes-research-token':'fixture-research','x-hermes-sidecar-token':'fixture-legacy'}])
 assert.equal(await h.send(headers,{project:'research',spaceId:'photon-research:scope',text:'x'}),401);
 assert.equal(h.sent.length,0);await h.context.lifecycle.stop();
});
test('legacy Development body and source instructions stay Personal; unknown caller denied',async()=>{
 const h=fixture();const body={spaceId:'fixture-space',text:'project=research',format:'text'};
 assert.equal((await h.send({'x-hermes-sidecar-token':'fixture-legacy'},body)).messageId,'fixture-personal');
 assert.equal(await h.send({},body),401);assert.equal(h.sent.length,1);await h.context.lifecycle.stop();
});
test('legacy caller cannot select disabled Research or reserved route',async()=>{
 const h=fixture();for(const body of [{project:'research',spaceId:'photon-research:scope',text:'x'},
 {spaceId:'photon-research:scope',text:'x'}])assert.equal(await h.send({'x-hermes-sidecar-token':'fixture-legacy'},body),401);
 assert.equal(h.sent.length,0);await h.context.lifecycle.stop();
});
test('source retains exactly one shared listener and one existing inbound subscription',()=>{
 assert.equal((source.match(/http.createServer\(/g)||[]).length,1);assert.equal((source.match(/server.listen\(/g)||[]).length,1);
 const adapter=fs.readFileSync(new URL('../photon-two-project-v1/modified/plugins/platforms/photon/adapter.py',import.meta.url),'utf8');
 assert.equal((adapter.match(/self\._sidecar_url\("\/inbound"\)/g)||[]).length,1);
});
