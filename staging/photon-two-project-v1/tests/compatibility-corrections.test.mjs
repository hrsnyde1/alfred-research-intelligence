import test from 'node:test';import assert from 'node:assert/strict';
import {EventEmitter,once} from 'node:events';import os from 'node:os';import path from 'node:path';import fs from 'node:fs';import vm from 'node:vm';
import {performance} from 'node:perf_hooks';import {Worker} from 'node:worker_threads';
import {CallerBindings} from '../modified/plugins/platforms/photon/sidecar/caller-bindings.mjs';
import {ResearchLifecycle} from '../modified/plugins/platforms/photon/sidecar/research-lifecycle.mjs';
const personalHeaders={'x-hermes-sidecar-token':'fixture-personal'};
const researchHeaders={'x-hermes-research-token':'fixture-research'};
const env={PHOTON_RESEARCH_ENABLED:'1',PHOTON_PERSONAL_LINE:'personal',PHOTON_RESEARCH_PROJECT_ID:'research-project',
 PHOTON_RESEARCH_PROJECT_SECRET:'fixture-project-secret',PHOTON_RESEARCH_CONNECTION_REF:'connection',
 PHOTON_RESEARCH_LINE:'research',PHOTON_RESEARCH_SPACE:'space',PHOTON_RESEARCH_SENDER:'owner',
 PHOTON_RESEARCH_PROFILE:'research',PHOTON_RESEARCH_STATE_DIR:'/fixture'};
const pause=ms=>new Promise(resolve=>setTimeout(resolve,ms));
class FakeWorker extends EventEmitter {
 constructor(){super();this.terminations=0;this.posts=[];}
 postMessage(message){this.posts.push(message);}
 async terminate(){this.terminations++;this.emit('exit',0);return 0;}
}
function life({environment=env,worker=new FakeWorker(),...options}={}) {
 const lifecycle=new ResearchLifecycle(environment,{authorized:true,deliver:async()=>{},workerFactory:()=>worker,
 authTimeoutMs:25,requestTimeoutMs:25,sessionTimeoutMs:1000,...options});return {lifecycle,worker};
}
function httpHarness(sourceOverride=null) {
 const callers=new CallerBindings('fixture-personal','fixture-research');const personal=[],research=[];
 const source=sourceOverride??fs.readFileSync(new URL('../modified/plugins/platforms/photon/sidecar/index.mjs',import.meta.url),'utf8');
 const start=source.indexOf('const server = http.createServer');const end=source.indexOf('server.listen(',start);
 const sandbox={callers,tokenOk:token=>token==='fixture-personal',researchProject:{send:async(endpoint,body)=>{research.push(body);return {messageId:'research-id'}}},
 http:{createServer:handler=>({handler})},readBody:async req=>req.body,
 unauthorized:()=>({status:401}),badRequest:()=>({status:400}),ok:(res,result)=>({status:200,...result}),
 serverError:()=>({status:500}),resolveSpace:async id=>({send:async builder=>{personal.push([id,builder]);return {id:'personal-id'}}}),
 chooseSendFormat:()=> 'text',spectrumText:x=>x,spectrumMarkdown:x=>x,console:{error:()=>{}}};
 vm.runInNewContext(source.slice(start,end)+';this.handle=server.handler;',sandbox);
 const send=(headers,body)=>sandbox.handle({method:'POST',url:'/send',headers,body},{});
 return {send,personal,research,source};
}
test('original Development request reproduces and succeeds unchanged through Personal',async()=>{
 const oldSource=fs.readFileSync(new URL('./fixtures/pre-correction-index.mjs',import.meta.url),'utf8');
 const h=httpHarness();const body={spaceId:'development-space',text:'fixture preview',format:'text'};
 assert.equal((await httpHarness(oldSource).send(personalHeaders,body)).status,400);
 assert.equal((await h.send(personalHeaders,body)).messageId,'personal-id');
 assert.equal(h.personal.length,1);assert.equal(h.research.length,0);assert.equal(body.project,undefined);
});
test('explicit Personal and authorized Research select independent connections concurrently',async()=>{
 const h=httpHarness();const [p,r]=await Promise.all([h.send(personalHeaders,{project:'personal',spaceId:'same-space',text:'p'}),
 h.send(researchHeaders,{project:'research',spaceId:'photon-research:scope',text:'r',operationId:'research:event'})]);
 assert.equal(p.messageId,'personal-id');assert.equal(r.messageId,'research-id');
 assert.equal(h.personal.length,1);assert.equal(h.research.length,1);
});
test('legacy authority cannot elevate itself using a Research project field',async()=>{
 const h=httpHarness();assert.equal((await h.send(personalHeaders,{project:'research',spaceId:'photon-research:scope',text:'x'})).status,401);
 assert.equal(h.research.length,0);assert.equal(h.personal.length,0);
});
test('Research authority has no Personal default and no Personal send permission',async()=>{
 const h=httpHarness();for(const body of [{spaceId:'space',text:'x'},{project:'personal',spaceId:'space',text:'x'}])
 assert.equal((await h.send(researchHeaders,body)).status,401);
 assert.equal(h.personal.length,0);
});
test('unknown or invalid credentials cannot use either project; no token fallback',async()=>{
 const h=httpHarness();for(const headers of [{},{'x-hermes-sidecar-token':'unknown'},
 {...personalHeaders,'x-hermes-research-token':'invalid'}])
 assert.equal((await h.send(headers,{spaceId:'space',text:'x'})).status,401);
 assert.equal(h.personal.length,0);
});
test('copied caller objects and colliding caller tokens cannot gain Research authority',()=>{
 const b=new CallerBindings('same','same');assert.equal(b.researchAvailable,false);
 assert.throws(()=>b.select({principal:'legacy-personal',project:'personal'},{spaceId:'space'}));
 const c=new CallerBindings('p','r');const issued=c.authenticate({'x-hermes-sidecar-token':'p'});
 assert.throws(()=>c.select({...issued},{spaceId:'space'}));
});
test('disabled Research performs no configuration/factory work; original Personal startup retained',async()=>{
 let calls=0;const {lifecycle}=life({environment:{},workerFactory:()=>{calls++;throw Error();}});
 lifecycle.start();assert.equal(lifecycle.state,'disabled');assert.equal(calls,0);
 const h=httpHarness();assert.ok(h.source.indexOf('researchProject.start();')>h.source.indexOf('server.listen('));
 assert.ok(!h.source.includes('await createResearch('));
 assert.equal((await h.send(personalHeaders,{spaceId:'space',text:'hello'})).status,200);await lifecycle.stop();
});
test('authentication stall cannot delay Personal readiness and is terminated without retries',async()=>{
 const {lifecycle,worker}=life();const start=performance.now();lifecycle.start();
 const h=httpHarness();assert.equal((await h.send(personalHeaders,{spaceId:'space',text:'p'})).status,200);
 assert.ok(performance.now()-start<100);await pause(45);
 assert.equal(lifecycle.state,'unavailable');assert.equal(worker.terminations,1);
 lifecycle.start();assert.equal(lifecycle.attempts,1);assert.equal(worker.terminations,1);await lifecycle.stop();
});
test('authentication failure never terminates or changes healthy Personal connection',async()=>{
 const {lifecycle,worker}=life();lifecycle.start();worker.emit('error',Error('fixture auth failure'));
 const h=httpHarness();assert.equal((await h.send(personalHeaders,{spaceId:'space',text:'still p'})).status,200);
 assert.equal(lifecycle.state,'unavailable');assert.equal(worker.terminations,1);await lifecycle.stop();
});
test('missing Research credentials or caller authority fails closed without affecting Personal',async()=>{
 for(const options of [{environment:{PHOTON_RESEARCH_ENABLED:'1'}},{authorized:false}]) {
  let called=0;const {lifecycle}=life({...options,workerFactory:()=>{called++;return new FakeWorker();}});
  lifecycle.start();assert.equal(called,0);assert.equal(lifecycle.state,'unavailable');await lifecycle.stop();
 }
});
test('Research send timeout rejects its pending state without Personal retry leakage',async()=>{
 const {lifecycle,worker}=life();lifecycle.start();worker.emit('message',{type:'ready'});
 const sent=lifecycle.send('/send',{project:'research'});await assert.rejects(sent);
 assert.equal(worker.posts.length,1);assert.equal(lifecycle.pending.size,0);assert.equal(lifecycle.state,'unavailable');
 const h=httpHarness();assert.equal((await h.send(personalHeaders,{spaceId:'space',text:'p'})).status,200);await lifecycle.stop();
});
test('shutdown and late ready events cannot revive Research; restart is a new independent lifecycle',async()=>{
 const a=life();a.lifecycle.start();await a.lifecycle.stop();a.worker.emit('message',{type:'ready'});
 assert.equal(a.lifecycle.state,'stopped');assert.equal(a.worker.terminations,1);
 const b=life();b.lifecycle.start();b.worker.emit('message',{type:'ready'});assert.equal(b.lifecycle.state,'ready');
 assert.equal(b.lifecycle.attempts,1);await b.lifecycle.stop();
});
test('Research internal retries have a hard session lifetime and no automatic reconnect',async()=>{
 const {lifecycle,worker}=life({sessionTimeoutMs:20});lifecycle.start();worker.emit('message',{type:'ready'});
 await pause(35);assert.equal(lifecycle.state,'unavailable');assert.equal(worker.terminations,1);
 lifecycle.start();assert.equal(lifecycle.attempts,1);await lifecycle.stop();
});
test('real disposable worker stall is terminated; no SDK/credentials are imported',async()=>{
 let worker;const {lifecycle}=life({authTimeoutMs:30,workerFactory:()=>{
  worker=new Worker('setInterval(()=>{},1000)',{eval:true,env:{}});return worker;
 }});lifecycle.start();await pause(65);await lifecycle.termination;
 assert.equal(lifecycle.state,'unavailable');assert.equal(worker.threadId,-1);await lifecycle.stop();
});

test('production worker protocol with substituted fake SDK keeps concurrent traffic separate',async()=>{
 const directory=fs.mkdtempSync(path.join(os.tmpdir(),'photon-worker-fixture-'));fs.chmodSync(directory,0o700);
 let controller;
 try {
  let source=fs.readFileSync(new URL('../modified/plugins/platforms/photon/sidecar/research-worker.mjs',import.meta.url),'utf8');
  const projectURL=new URL('../modified/plugins/platforms/photon/sidecar/research-project.mjs',import.meta.url).href;
  source=source.replace("'./research-project.mjs'",JSON.stringify(projectURL));
  source=source.replace("const {Spectrum,text}=await import('spectrum-ts');",`const fakeSpace={id:workerData.space,phone:workerData.line,type:'dm',send:async()=>({id:'fake-sent'})};
    const Spectrum=async()=>({messages:(async function*(){yield [fakeSpace,{id:'same-event',direction:'inbound',sender:{id:workerData.sender},content:{type:'text',text:'synthetic source'}}];await new Promise(()=>{});})(),stop:async()=>{}});
    const text=x=>x;`);
  source=source.replace("const {imessage}=await import('spectrum-ts/providers/imessage');",'const imessage=()=>({space:{get:async()=>fakeSpace}});imessage.config=()=>({});');
  assert.ok(!source.includes("await import('spectrum-ts"));
  const received=[];
  controller=new ResearchLifecycle(env,{authorized:true,deliver:async event=>{received.push(JSON.parse(event));},
    authTimeoutMs:500,requestTimeoutMs:500,sessionTimeoutMs:1000,
    workerFactory:config=>new Worker(new URL('data:text/javascript,'+encodeURIComponent(source)),
      {workerData:{...config,state_dir:directory},env:{},stdout:true,stderr:true})});
  controller.start();for(let i=0;i<100 && !received.length;i++)await pause(5);
  assert.equal(controller.state,'ready');assert.equal(received.length,1);
  assert.equal(received[0].research.connection_ref,'connection');
  const h=httpHarness();const [r,p]=await Promise.all([
    controller.send('/send',{project:'research',spaceId:received[0].space.id,text:'ACK',operationId:received[0].messageId}),
    h.send(personalHeaders,{spaceId:'same-space',text:'personal'})]);
  assert.ok(r.messageId.startsWith('research:'));assert.equal(p.messageId,'personal-id');
 } finally {await controller?.stop();fs.rmSync(directory,{recursive:true,force:true});}
});

test('cancelling Research delivery retains healthy Personal consumer and removes only its waiter',async()=>{
 const source=fs.readFileSync(new URL('../modified/plugins/platforms/photon/sidecar/index.mjs',import.meta.url),'utf8');
 const a=source.indexOf('function waitForConsumer('),b=source.indexOf('async function normalizeBinary',a);
 assert.ok(b>a);
 const res=new EventEmitter();res.write=()=>false;
 const sandbox={consumerRes:res,consumerWaiters:[],once,Error};
 vm.runInNewContext(source.slice(a,b)+';this.deliverLine=deliver;this.wait=waitForConsumer;',sandbox);
 const abort=new AbortController();const delivery=sandbox.deliverLine('synthetic',abort.signal);
 await pause(1);abort.abort();await assert.rejects(delivery);assert.equal(sandbox.consumerRes,res);
 sandbox.consumerRes=null;const another=new AbortController();const wait=sandbox.wait(another.signal);
 assert.equal(sandbox.consumerWaiters.length,1);another.abort();await assert.rejects(wait);
 assert.equal(sandbox.consumerWaiters.length,0);
});

test('original awaited startup blocker reproduces before correction and releases only after auth',async()=>{
 const source=fs.readFileSync(new URL('./fixtures/pre-correction-index.mjs',import.meta.url),'utf8');
 const a=source.indexOf('let researchProject = null;'),b=source.indexOf('const server =',a);
 let release;const context={process:{env:{}},Spectrum:null,imessage:null,normalizeEvent:null,deliver:null,spectrumText:null,
   console:{error:()=>{}},createResearch:()=>new Promise(resolve=>{release=resolve;}),personalReady:false};
 const promise=vm.runInNewContext('(async()=>{'+source.slice(a,b)+';personalReady=true;})()',context);
 await pause(2);assert.equal(context.personalReady,false);release(null);await promise;assert.equal(context.personalReady,true);
});
