import test from 'node:test';import assert from 'node:assert/strict';
import fs from 'node:fs';import os from 'node:os';import path from 'node:path';import crypto from 'node:crypto';
import {Connector} from '../connector.mjs';
import {Outbox} from '../outbox.mjs';
const roots=[];process.on('exit',()=>roots.forEach(p=>fs.rmSync(p,{recursive:true,force:true})));
const sha=s=>crypto.createHash('sha256').update(s).digest('hex');
function setup(){
 const root=fs.mkdtempSync(path.join(os.tmpdir(),'research-outbox-'));roots.push(root);
 const outbox=path.join(root,'outbox');fs.mkdirSync(outbox,{mode:0o700});
 const p={role:'research',enabled:true,project_id:'fake-research',line:'fake-line',space:'fake-space',sender:'fake-owner',profile:'research',connection_ref:'fake-connection',state_dir:root};
 const sent=[];let release;const wait=new Promise(r=>release=r);
 const space={id:p.space,phone:p.line,send:async t=>{sent.push(t);return{id:'fake-receipt-'+sent.length}}};
 const d={credentials:()=>({projectId:p.project_id,projectSecret:'fake-only-secret'}),
  factory:async()=>({messages:{async *[Symbol.asyncIterator](){await wait;}},stop:async()=>release()}),
  imessage:Object.assign(()=>({space:{get:async()=>space}}),{config:()=>({})}),text:x=>x};
 const c=new Connector(p,d);
 return {c,space,sent,outbox,box:new Outbox(outbox,(id,t)=>c.send(id,t))};
}
const write=(dir,operationId,text,sequence)=>fs.writeFileSync(path.join(dir,sha(operationId)+'.json'),
 JSON.stringify({schema:'research.outbox/1',operationId,text,sequence,created_at:'2026-10-16T00:00:00Z'}),{mode:0o600});
const listing=(dir,sub)=>fs.readdirSync(path.join(dir,sub)).length;

test('sends in sequence order exactly once and archives',async()=>{const x=setup();await x.c.start();
 write(x.outbox,'final:k1','Result',2);write(x.outbox,'reply:k1','On it',1);
 assert.equal((await x.box.pumpOnce()).sent,2);assert.deepEqual(x.sent,['On it','Result']);
 assert.equal(listing(x.outbox,'sent'),2);
 write(x.outbox,'reply:k1','On it',1);await x.box.pumpOnce();assert.equal(x.sent.length,2,'replayed entry not resent');
 await x.c.stop();});
test('transport unavailable leaves entries queued without a send record',async()=>{const x=setup();
 write(x.outbox,'reply:k2','On it',1);assert.equal((await x.box.pumpOnce()).sent,0);
 assert.equal(fs.readdirSync(x.outbox).filter(n=>n.endsWith('.json')).length,1);
 await x.c.start();assert.equal((await x.box.pumpOnce()).sent,1);await x.c.stop();});
test('uncertain delivery is quarantined, never resent',async()=>{const x=setup();await x.c.start();
 let attempts=0;x.space.send=async()=>{attempts++;throw Error('fake timeout')};x.c.client.spaces.set(x.c.client.route,x.space);
 write(x.outbox,'final:k3','Result',1);await x.box.pumpOnce();
 assert.equal(listing(x.outbox,'unknown'),1);write(x.outbox,'final:k3','Result',1);await x.box.pumpOnce();
 assert.equal(attempts,1);assert.equal(listing(x.outbox,'unknown'),1);await x.c.stop();});
test('changed text for a sent operation is rejected',async()=>{const x=setup();await x.c.start();
 write(x.outbox,'reply:k4','First',1);await x.box.pumpOnce();write(x.outbox,'reply:k4','Changed',1);await x.box.pumpOnce();
 assert.deepEqual(x.sent,['First']);assert.equal(listing(x.outbox,'rejected'),1);await x.c.stop();});
test('malformed or oversized entries are rejected unsent',async()=>{const x=setup();await x.c.start();
 fs.writeFileSync(path.join(x.outbox,'a'.repeat(64)+'.json'),'{not json',{mode:0o600});
 fs.writeFileSync(path.join(x.outbox,'b'.repeat(64)+'.json'),JSON.stringify({schema:'research.outbox/1',operationId:'x',text:'y'.repeat(70000)}),{mode:0o600});
 fs.writeFileSync(path.join(x.outbox,'note.txt'),'ignored');
 await x.box.pumpOnce();assert.equal(x.sent.length,0);assert.equal(listing(x.outbox,'rejected'),2);await x.c.stop();});
test('unprotected outbox directory refused',()=>{const root=fs.mkdtempSync(path.join(os.tmpdir(),'research-outbox-open-'));roots.push(root);
 fs.chmodSync(root,0o755);assert.throws(()=>new Outbox(root,async()=>{}),/protected/);});
