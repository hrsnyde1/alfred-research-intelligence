import test from 'node:test';import assert from 'node:assert/strict';
import fs from 'node:fs';import os from 'node:os';import path from 'node:path';
import {Connector} from './connector.mjs';
const roots=[];process.on('exit',()=>roots.forEach(p=>fs.rmSync(p,{recursive:true,force:true})));
function setup(overrides={},extra={}){
 const root=fs.mkdtempSync(path.join(os.tmpdir(),'research-connector-'));roots.push(root);
 const p={role:'research',enabled:true,project_id:'fake-research',line:'fake-line',space:'fake-space',sender:'fake-owner',profile:'research',connection_ref:'fake-connection',state_dir:root,...overrides};
 let auth=0,sends=0;let release;const wait=new Promise(r=>release=r);
 const space={id:p.space,phone:p.line,send:async()=>{sends++;return{id:'fake-receipt'}}};
 const d={credentials:()=>({projectId:p.project_id,projectSecret:'fake-only-secret'}),
 factory:async options=>{auth++;assert.equal(options.projectId,'fake-research');assert.equal(options.projectSecret,'fake-only-secret');return{messages:{async *[Symbol.asyncIterator](){await wait;}},stop:async()=>release()};},
 imessage:Object.assign(()=>({space:{get:async(id,o)=>{assert.equal(o.phone,p.line);return space;}}}),{config:()=>({})}),text:x=>x,...extra};
 return {c:new Connector(p,d),p,space,auth:()=>auth,sends:()=>sends};
}
const msg=(id='event-1',text='https://github.com/example/repo/commit/'+'a'.repeat(40))=>({id,direction:'inbound',sender:{id:'fake-owner'},content:{type:'text',text},timestamp:'2026-10-16T00:00:00Z'});
test('disabled default never resolves credentials or creates client',async()=>{let reads=0;const x=setup({enabled:false},{credentials:()=>{reads++;throw Error();}});await x.c.start();assert.equal(reads,0);assert.equal(x.auth(),0);await assert.rejects(x.c.send('x','y'));});
test('independent explicit Research authentication',async()=>{const x=setup();await x.c.start();assert.equal(x.auth(),1);assert.equal(x.c.health().state,'READY');await x.c.stop();});
test('missing credentials fail closed',async()=>{const x=setup({}, {credentials:()=>null});await assert.rejects(x.c.start());assert.equal(x.auth(),0);});
test('wrong project credentials fail closed',async()=>{const x=setup({}, {credentials:()=>({projectId:'personal',projectSecret:'fake'})});await assert.rejects(x.c.start());assert.equal(x.auth(),0);});
test('unknown project binding rejected',()=>assert.throws(()=>setup({project_id:''})));
test('inbound durable correlation and replay create one pending record',async()=>{const x=setup();await x.c.start();await x.c.client.inbound(x.space,msg());await x.c.client.inbound(x.space,msg());const records=fs.readdirSync(x.p.state_dir).map(n=>JSON.parse(fs.readFileSync(path.join(x.p.state_dir,n))));const pending=records.filter(r=>r.status==='PENDING_INTAKE');assert.equal(pending.length,1);assert.equal(pending[0].productionTrusted,false);assert.equal((await x.c.intake(pending[0].correlation)).status,'UNAVAILABLE');await x.c.stop();});
test('forged sender or line or conversation denied',async()=>{const x=setup();await x.c.start();for(const s of [{...x.space,phone:'personal'},{...x.space,id:'other'}])await assert.rejects(x.c.client.inbound(s,msg()));await assert.rejects(x.c.client.inbound(x.space,{...msg(),sender:{id:'other'}}));await x.c.stop();});
test('changed payload same event rejected',async()=>{const x=setup();await x.c.start();await x.c.client.inbound(x.space,msg());await assert.rejects(x.c.client.inbound(x.space,msg('event-1','changed')));await x.c.stop();});
test('outbound selects only Research line and deduplicates operation',async()=>{const x=setup();await x.c.start();await x.c.send('operation-1','test');await x.c.send('operation-1','test');assert.equal(x.sends(),1);await assert.rejects(x.c.client.send('/send',{project:'personal'}));await x.c.stop();});
test('send conflict denied',async()=>{const x=setup();await x.c.start();await x.c.send('operation-1','test');await assert.rejects(x.c.send('operation-1','changed'));await x.c.stop();});
test('restart preserves outbound dedupe',async()=>{const x=setup();await x.c.start();await x.c.send('operation-1','test');await x.c.stop();const y=setup({state_dir:x.p.state_dir});await y.c.start();await y.c.send('operation-1','test');assert.equal(y.sends(),0);await y.c.stop();});
test('failed auth does not touch an unrelated Personal object',async()=>{const personal={running:true};const x=setup({}, {factory:async()=>{throw Error('fake-private-error')}});await assert.rejects(x.c.start(),/Research unavailable/);assert.deepEqual(personal,{running:true});});
test('live intake cannot invoke fake host seam',async()=>{const x=setup({intake_enabled:true},{intake:()=>{throw Error('must not run')}});await x.c.start();await assert.rejects(x.c.intake('anything'),/not registered/);await x.c.stop();});
test('uncertain send never blindly retries',async()=>{const x=setup();await x.c.start();let attempts=0;x.space.send=async()=>{attempts++;throw Error('fake timeout')};x.c.client.spaces.set(x.c.client.route,x.space);await assert.rejects(x.c.send('unknown-1','test'));await assert.rejects(x.c.send('unknown-1','test'));assert.equal(attempts,1);await x.c.stop();});
test('project/line scoped event IDs cannot collide',async()=>{const x=setup();const y=setup({line:'fake-other-line'});await x.c.start();await y.c.start();const a=await x.c.client.inbound(x.space,msg());const b=await y.c.client.inbound(y.space,msg());assert.notEqual(a.messageId,b.messageId);await x.c.stop();await y.c.stop();});
test('standalone disabled entrypoint starts without SDK or credential access',async()=>{const {spawnSync}=await import('node:child_process');const x=setup();const p=path.join(x.p.state_dir,'policy.json');fs.writeFileSync(p,JSON.stringify({...x.p,enabled:false}),{mode:0o600});const result=spawnSync(process.execPath,[new URL('./main.mjs',import.meta.url).pathname,'run',p],{encoding:'utf8',env:{},timeout:2000});assert.equal(result.status,0,result.stderr);assert.equal(JSON.parse(result.stdout).state,'DISABLED');});
test('protected credential references reject symlinks',async()=>{const {credentialReader}=await import('./connector.mjs');const x=setup();const f=path.join(x.p.state_dir,'fake-only');fs.writeFileSync(f,'fake',{mode:0o600});fs.symlinkSync(f,path.join(x.p.state_dir,'research-project-id'));assert.throws(credentialReader(x.p.state_dir));});
