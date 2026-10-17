import test from 'node:test';import assert from 'node:assert/strict';import fs from 'node:fs';import vm from 'node:vm';
const root=new URL('../linux-sdk/',import.meta.url);
test('copied installed SDK packages are consistently 12.7.0',()=>{
 for(const p of ['spectrum-ts','@spectrum-ts/core','@spectrum-ts/imessage'])
 assert.equal(JSON.parse(fs.readFileSync(new URL(p+'/package.json',root),'utf8')).version,'12.7.0');
});
test('installed client selector selects exact line and rejects another project line',()=>{
 const source=fs.readFileSync(new URL('@spectrum-ts/imessage/dist/index.js',root),'utf8');
 const start=source.indexOf('const isSharedMode =');const end=source.indexOf('//#endregion',start);assert.ok(start>0&&end>start);
 const sandbox={};vm.runInNewContext('const SHARED_PHONE="shared";'+source.slice(start,end)+';this.select=clientForPhone;',sandbox);
 const personal={tag:'personal'},research={tag:'research'};
 assert.equal(sandbox.select([{phone:'r',client:research}],'r'),research);
 assert.throws(()=>sandbox.select([{phone:'p',client:personal}],'r'));
 assert.throws(()=>sandbox.select([{phone:'r',client:research}],undefined));
});
