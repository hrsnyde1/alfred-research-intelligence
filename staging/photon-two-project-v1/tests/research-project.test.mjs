import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';import os from 'node:os';import path from 'node:path';
import {configuration,ResearchProject,FileLedger,createResearch} from '../modified/plugins/platforms/photon/sidecar/research-project.mjs';
const config={connection_ref:'synthetic-research-connection',project_id:'synthetic-research',project_secret:'synthetic-only',line:'test-line',space:'same-space',sender:'owner',profile:'research',state_dir:'/unused'};
function harness(ledger) {
 const records=new Map(),sent=[],delivered=[],resolved=[];
 ledger??={get:k=>records.get(k)??null,put:(k,v)=>records.set(k,v)};
 const space={id:config.space,phone:config.line,send:async text=>{sent.push(text);return {id:'same-message'}}};
 const imessage=()=>({space:{get:async(id,options)=>{resolved.push([id,options]);return space}}});
 const r=new ResearchProject(config,{factory:async()=>({messages:(async function*(){})(),stop:async()=>{}}),
   imessage,normalize:async(s,m)=>({messageId:m.id,space:{id:s.id,phone:s.phone},sender:m.sender,content:{type:'text',text:'hello'}}),
   deliver:async s=>delivered.push(JSON.parse(s)),text:x=>x,ledger});r.app={};
 return {r,space,sent,delivered,resolved,records};
}
const message={content:{type:'text',text:'hello'},id:'same-message',sender:{id:'owner'},direction:'inbound'};
const request=r=>({project:'research',spaceId:r.route,text:'ACK',operationId:'research:event'});
test('disabled mode never initializes or subscribes Research',async()=>{
 let calls=0;assert.equal(await createResearch({}, {factory:()=>{calls++}}),null);assert.equal(calls,0);
});
test('missing credentials and reused Personal credentials deny enabled Research',()=>{
 assert.throws(()=>configuration({PHOTON_RESEARCH_ENABLED:'1'}));
 const env={PHOTON_RESEARCH_ENABLED:'1',PHOTON_PERSONAL_LINE:'synthetic-personal-line'};for(const [k,v]of Object.entries(config))env['PHOTON_RESEARCH_'+k.toUpperCase()]=v;
 assert.equal(configuration(env).project_id,config.project_id);
 env.PHOTON_PROJECT_SECRET=config.project_secret;assert.throws(()=>configuration(env));
});
test('inbound project and message namespaces are independent of Personal originals',async()=>{
 const h=harness();const e=await h.r.inbound(h.space,message);
 assert.equal(e.project,'research');assert.notEqual(e.space.id,h.space.id);assert.notEqual(e.messageId,message.id);
 assert.equal(e.research.originalMessageId,message.id);assert.equal(e.research.line,config.line);
 assert.equal(h.delivered.length,1);
});
test('wrong line sender or space cannot enter shared consumer',async()=>{
 const h=harness();for(const [s,m]of [[{...h.space,phone:'unknown'},message],[{...h.space,id:'other'},message],[h.space,{...message,sender:{id:'forged'}}]])
 await assert.rejects(h.r.inbound(s,m));assert.equal(h.delivered.length,0);
});
test('explicit project and exact scope required for send',async()=>{
 const h=harness();for(const body of [{...request(h.r),project:'personal'},{...request(h.r),project:undefined},{...request(h.r),spaceId:'same-space'}, {...request(h.r),operationId:''}])
 await assert.rejects(h.r.send('/send',body));assert.equal(h.sent.length,0);
});
test('cache restore pins dedicated line and duplicate logical send is accepted once',async()=>{
 const h=harness();const result=await h.r.send('/send',request(h.r));assert.equal(h.sent.length,1);
 assert.deepEqual(h.resolved,[[config.space,{phone:config.line}]]);
 assert.deepEqual(await h.r.send('/send',request(h.r)),result);assert.equal(h.sent.length,1);
 await assert.rejects(h.r.send('/send',{...request(h.r),text:'changed'}));
});
test('same ACK for separate inbound operations does not collapse',async()=>{
 const h=harness();await h.r.send('/send',request(h.r));await h.r.send('/send',{...request(h.r),operationId:'research:second'});
 assert.equal(h.sent.length,2);
});
test('ambiguous external outcome never resends',async()=>{
 const h=harness();h.space.send=async()=>{h.sent.push('effect');throw Error('unknown')};
 await assert.rejects(h.r.send('/send',request(h.r)));await assert.rejects(h.r.send('/send',request(h.r)));
 assert.equal(h.sent.length,1);
});
test('restart with protected durable ledger preserves project send separation',async()=>{
 const root=fs.mkdtempSync(path.join(os.tmpdir(),'research-ledger-'));fs.chmodSync(root,0o700);
 try{const h=harness(new FileLedger(root));const a=await h.r.send('/send',request(h.r));
 const b=harness(new FileLedger(root));assert.deepEqual(await b.r.send('/send',request(b.r)),a);assert.equal(b.sent.length,0);
 await b.r.inbound(b.space,message);await b.r.inbound(b.space,message);assert.equal(b.delivered.length,2);
 }finally{fs.rmSync(root,{recursive:true});}
});
test('unsupported Research media/actions deny without Personal fallback',async()=>{
 const h=harness();for(const endpoint of ['/typing','/send-richlink','/send-attachment','/react'])await assert.rejects(h.r.send(endpoint,request(h.r)));
 assert.equal(h.sent.length,0);
});

test('separate app receives only explicit Research project credentials',async()=>{
 const h=harness();const calls=[];
 h.r.dependencies.factory=async options=>{calls.push(options);return {messages:(async function*(){})(),stop:async()=>{}}};
 h.r.dependencies.imessage.config=()=>({type:'imessage'});
 await h.r.start();await h.r.pump;
 assert.equal(calls.length,1);assert.equal(calls[0].projectId,config.project_id);
 assert.equal(calls[0].projectSecret,config.project_secret);assert.equal(calls[0].telemetry,false);
 await h.r.stop();
});
