import {test} from 'node:test';
import assert from 'node:assert/strict';
import {Qualifier,discover,digest} from './discovery.mjs';
const policy={role:'research-discovery',project_sha256:digest('research'),line_sha256:digest('+15550000001'),challenge_sha256:digest('OWNER-ONE-TIME-CHALLENGE'),timeout_ms:1000};
const event=()=>[{platform:'imessage',phone:'+15550000001',id:'conversation-A'}, {platform:'imessage',direction:'inbound',id:'message-A',sender:{platform:'imessage',id:'owner-A'},content:{type:'text',text:'OWNER-ONE-TIME-CHALLENGE'}}];
test('exact event produces allowlisted evidence, then stops duplicates',()=>{
 const q=new Qualifier(policy,'research'), e=event(), r=q.accept(...e);
 assert.deepEqual(Object.keys(r),['project_binding','receiving_line','conversation','sender','correlation_sha256']);
 const out=JSON.stringify(r);
 for(const secret of ['OWNER-ONE-TIME-CHALLENGE','+15550000001','message-A'])assert.ok(!out.includes(secret));
 assert.equal(q.accept(...e),null);
});
test('Personal credentials and explicit Personal event bindings rejected',()=>{
 assert.throws(()=>new Qualifier(policy,'personal'));
 for(const index of [0,1]){const e=event();e[index].projectId='personal';assert.equal(new Qualifier(policy,'research').accept(...e),null);}
});
test('unknown/ambiguous line and malformed identities fail closed',()=>{
 for(const phone of [undefined,'shared','+15550000002',['+15550000001'],{id:'+15550000001'}]){
 const e=event();e[0].phone=phone;assert.equal(new Qualifier(policy,'research').accept(...e),null);}
 for(const mutate of [e=>delete e[1].sender,e=>e[1].direction='outbound',e=>e[0].platform='slack',e=>e[1].content.text='wrong']){
 const e=event();mutate(e);assert.equal(new Qualifier(policy,'research').accept(...e),null);}
});
test('replayed ID cannot change from wrong challenge into qualifying event',()=>{
 const q=new Qualifier(policy,'research'),e=event();e[1].content.text='wrong';assert.equal(q.accept(...e),null);
 e[1].content.text='OWNER-ONE-TIME-CHALLENGE';assert.equal(q.accept(...e),null);
});
test('phone/email sender identifiers are digested',()=>{
 for(const sender of ['+15551234567','owner@example.test']){const e=event();e[1].sender.id=sender;
 const r=new Qualifier(policy,'research').accept(...e);assert.deepEqual(r.sender,{sha256:digest(sender)});assert.ok(!JSON.stringify(r).includes(sender));}
});
test('one connection, one accepted event, teardown; no send, task, Hermes or Memory calls',async()=>{
 let starts=0,stops=0,consumed=0;const forbidden=()=>assert.fail('side effect');
 const e=event();e[0].send=e[1].reply=e[1].read=forbidden;
 const r=await discover({policy,credentials:{projectId:'research',projectSecret:'SYNTHETIC-SECRET'},provider:{config:()=>({})},factory:async opts=>{
 starts++;assert.equal(opts.projectId,'research');assert.equal(opts.telemetry,false);
 return {send:forbidden,deliver:forbidden,intake:forbidden,memory:forbidden,stop:async()=>{stops++;},messages:(async function*(){consumed++;yield e;consumed++;yield e;})()};}});
 assert.ok(r);assert.equal(starts,1);assert.equal(stops,1);assert.equal(consumed,1);assert.ok(!JSON.stringify(r).includes('SYNTHETIC-SECRET'));
});
test('iterator error closes client',async()=>{
 let stopped=false;await assert.rejects(discover({policy,credentials:{projectId:'research',projectSecret:'synthetic'},provider:{config:()=>({})},factory:async()=>({stop:async()=>{stopped=true;},messages:(async function*(){throw Error('secret');})()})}));assert.ok(stopped);
});

const codes=['POLICY_OK','CREDENTIALS_OK','SDK_IMPORT_OK','PROVIDER_OK','AUTHENTICATION_OK','STREAM_READY'];
for (const failure of ['policy','credentials','import','provider','authentication','stream','iteration','stop',null]) {
 test(`offline startup stages: ${failure ?? 'success'}`,async()=>{
  const {startup}=await import('./discovery.mjs');
  const recorded=[];
  const fail=at=>{if(failure===at)throw Error('RAW-SDK-ERROR TOKEN PROJECT MESSAGE owner@example.test');};
  const run=()=>startup({stage:code=>recorded.push(code),
   loadPolicy:()=>{fail('policy');return policy;},
   loadCredentials:()=>({projectId:failure==='credentials'?'personal':'research',projectSecret:'SYNTHETIC-SECRET'}),
   loadSdk:async()=>{fail('import');return {
    provider:{config:()=>{fail('provider');return {};}},
    factory:async()=>{fail('authentication');return {
     stop:async()=>{fail('stop');},
     get messages(){fail('stream');return (async function*(){fail('iteration');yield event();})();}
    };}
   };}
  });
  if(failure){await assert.rejects(run());recorded.push('FAILED');}else assert.ok(await run());
  const last={policy:0,credentials:1,import:2,provider:3,authentication:4,stream:5,iteration:6,stop:6};
  assert.deepEqual(recorded,failure?[...codes.slice(0,last[failure]),'FAILED']:codes);
  assert.ok(recorded.every(code=>[...codes,'FAILED'].includes(code)));
 });
}
test('diagnostics accept only fixed codes, are bounded and can be disabled',async()=>{
 const {stageRecorder}=await import('./discovery.mjs');
 let output='';const record=stageRecorder(line=>{output+=line;});
 for(let n=0;n<100;n++)for(const code of [...codes,'FAILED'])record(code);
 assert.equal(output,[...codes,'FAILED'].join('\n')+'\n');
 assert.throws(()=>record('RAW-SDK-ERROR owner@example.test'));
 assert.equal(output,[...codes,'FAILED'].join('\n')+'\n');
 const disabled=stageRecorder();for(const code of codes)disabled(code);
});

// Synthetic fstat metadata: no credential files, SDK, or privileged chown needed.
const {credentialMetadataAllowed}=await import('./main.mjs');
for (const uid of [0,980]) {
 for (const mode of [0o400,0o600]) {
  test(`credential metadata accepts uid=${uid} mode=${mode.toString(8)}`,()=>{
   assert.equal(credentialMetadataAllowed({uid,mode:0o100000|mode},980),true);
  });
 }
}
test('credential metadata accepts systemd root-owned 0440 for service UID 980',()=>{
 assert.equal(credentialMetadataAllowed({uid:0,mode:0o100440},980),true);
});
for (const uid of [0,980,981]) {
 for (const mode of [0o000,0o440,0o640,0o460,0o660,0o402,0o404,0o444,0o604,0o644,0o666,0o700,0o1400,0o2400,0o4400]) {
  if (uid===0 && mode===0o440) continue;
  test(`credential metadata rejects uid=${uid} mode=${mode.toString(8)}`,()=>{
   assert.equal(credentialMetadataAllowed({uid,mode:0o100000|mode},980),false);
  });
 }
}
test('credential metadata rejects unexpected ownership even with private modes',()=>{
 for (const mode of [0o400,0o600]) assert.equal(credentialMetadataAllowed({uid:981,mode},980),false);
});
