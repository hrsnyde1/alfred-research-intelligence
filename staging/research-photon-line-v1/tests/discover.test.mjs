import test from 'node:test';import assert from 'node:assert/strict';
import fs from 'node:fs';import os from 'node:os';import path from 'node:path';import crypto from 'node:crypto';
import {discover} from '../discover.mjs';
const roots=[];process.on('exit',()=>roots.forEach(p=>fs.rmSync(p,{recursive:true,force:true})));
const sha=s=>crypto.createHash('sha256').update(s).digest('hex');
const CHALLENGE='4821993705126640';
function setup(events,{phone='+14152250168',delay=0}={}){
 const root=fs.mkdtempSync(path.join(os.tmpdir(),'research-discover-'));roots.push(root);
 let sends=0,stopped=false,auth=0;
 const space={id:'space-abc',phone,type:'dm',send:async()=>{sends++;}};
 const app={messages:{async *[Symbol.asyncIterator](){for(const e of events){if(delay)await new Promise(r=>setTimeout(r,delay));yield [space,e];}await new Promise(()=>{});}},stop:async()=>{stopped=true;}};
 const deps={factory:async o=>{auth++;assert.equal(o.projectId,'research-project');return app;},imessage:{config:()=>({})},
  credentials:()=>({projectId:'research-project',projectSecret:'fake-only'}),deadlineMs:300};
 const policy={project_id:'research-project',state_dir:root,discovery_challenge_sha256:sha(CHALLENGE)};
 return {root,policy,deps,sends:()=>sends,stopped:()=>stopped,auth:()=>auth};
}
const text=(t,sender='owner-handle',direction='inbound')=>({direction,sender:{id:sender},content:{type:'text',text:t}});
test('records raw binding for the challenge message only, sends nothing',async()=>{
 const x=setup([text('hello there'),text(CHALLENGE,'owner-handle','outbound'),text(' '+CHALLENGE+'\n')]);
 const r=await discover(x.policy,x.deps);assert.equal(r.state,'DISCOVERED');
 const report=JSON.parse(fs.readFileSync(path.join(x.root,'discovery.json'),'utf8'));
 assert.deepEqual([report.line,report.space,report.sender,report.shared_line,report.usable],['+14152250168','space-abc','owner-handle',false,true]);
 assert.ok(!JSON.stringify(report).includes(CHALLENGE),'no message content stored');
 assert.equal((fs.statSync(path.join(x.root,'discovery.json')).mode&0o777),0o600);
 assert.equal(x.sends(),0);assert.ok(x.stopped());});
test('shared line is reported unusable',async()=>{
 const x=setup([text(CHALLENGE)],{phone:'shared'});const r=await discover(x.policy,x.deps);
 assert.deepEqual(r,{state:'DISCOVERED_UNUSABLE',shared_line:true});});
test('no challenge within the window writes nothing',async()=>{
 const x=setup([text('not it')]);const r=await discover(x.policy,x.deps);
 assert.equal(r.state,'NO_MATCH');assert.equal(fs.existsSync(path.join(x.root,'discovery.json')),false);assert.ok(x.stopped());});
test('existing report is never overwritten',async()=>{
 const x=setup([text(CHALLENGE)]);fs.writeFileSync(path.join(x.root,'discovery.json'),'{}',{mode:0o600});
 await assert.rejects(discover(x.policy,x.deps));});
test('missing challenge digest or wrong project credentials refused before authenticating',async()=>{
 const x=setup([]);await assert.rejects(discover({...x.policy,discovery_challenge_sha256:''},x.deps),/challenge/);
 await assert.rejects(discover(x.policy,{...x.deps,credentials:()=>({projectId:'personal',projectSecret:'x'})}),/credentials/);
 assert.equal(x.auth(),0);});
