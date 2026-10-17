import test from 'node:test';import assert from 'node:assert/strict';
import fs from 'node:fs';import os from 'node:os';import path from 'node:path';
import {credentialMetadataAllowed,credentialReader} from '../connector.mjs';
const roots=[];process.on('exit',()=>roots.forEach(p=>fs.rmSync(p,{recursive:true,force:true})));
const SERVICE=980;
// Synthetic fstat metadata (regular-file type bits included): no root, chown or systemd needed.
const meta=(uid,mode)=>({uid,mode:0o100000|mode});
test('accepts systemd LoadCredential files: root-owned 0440',()=>{
 assert.equal(credentialMetadataAllowed(meta(0,0o440),SERVICE),true);});
for(const uid of [0,SERVICE])for(const mode of [0o400,0o600])
 test(`accepts private uid=${uid} mode=${mode.toString(8)}`,()=>assert.equal(credentialMetadataAllowed(meta(uid,mode),SERVICE),true));
for(const uid of [0,SERVICE,981])for(const mode of [0o000,0o440,0o640,0o460,0o660,0o402,0o404,0o444,0o604,0o644,0o666,0o700,0o1400,0o2400,0o4400]){
 if(uid===0&&mode===0o440)continue;
 test(`rejects uid=${uid} mode=${mode.toString(8)}`,()=>assert.equal(credentialMetadataAllowed(meta(uid,mode),SERVICE),false));}
test('group-readable 0440 is accepted only when root owns the file',()=>{
 assert.equal(credentialMetadataAllowed(meta(SERVICE,0o440),SERVICE),false);
 assert.equal(credentialMetadataAllowed(meta(981,0o440),SERVICE),false);});

function directory(files){
 const root=fs.mkdtempSync(path.join(os.tmpdir(),'research-credentials-'));roots.push(root);
 for(const [name,[content,mode]] of Object.entries(files)){fs.writeFileSync(path.join(root,name),content);fs.chmodSync(path.join(root,name),mode);}
 return root;}
test('reader returns trimmed Research credentials from owner-private files',()=>{
 const root=directory({'research-project-id':['research-project\n',0o600],'research-project-secret':['fake-only-secret\n',0o400]});
 assert.deepEqual(credentialReader(root)(),{projectId:'research-project',projectSecret:'fake-only-secret'});});
test('reader rejects world-readable, group-writable and oversized credential files',()=>{
 for(const [mode,content] of [[0o644,'x'],[0o620,'x'],[0o600,'y'.repeat(5000)]]){
  const root=directory({'research-project-id':['research-project',0o600],'research-project-secret':[content,mode]});
  assert.throws(credentialReader(root),/credential denied/);}});
test('reader rejects symlinked and missing credentials and a missing directory',()=>{
 const root=directory({'research-project-id':['research-project',0o600],'target':['fake',0o600]});
 fs.symlinkSync(path.join(root,'target'),path.join(root,'research-project-secret'));
 assert.throws(credentialReader(root));
 assert.throws(credentialReader(directory({'research-project-id':['research-project',0o600]})));
 assert.throws(credentialReader(undefined));});
test('reader only opens the two Research credential names',()=>{
 const root=directory({'research-project-id':['research-project',0o600],'research-project-secret':['fake',0o600],'project-secret':['personal',0o600]});
 const opened=[];const original=fs.openSync;fs.openSync=(p,...a)=>{opened.push(path.basename(p));return original(p,...a);};
 try{credentialReader(root)();}finally{fs.openSync=original;}
 assert.deepEqual(opened,['research-project-id','research-project-secret']);});
