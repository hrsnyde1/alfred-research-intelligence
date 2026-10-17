// Long-running Research line entrypoint. No SDK import or credential read when disabled.
// Differences from research-photon-service-v1/main.mjs: no fixed 5-minute session
// (optional policy.session_seconds), and an outbox pump when policy.outbox_enabled.
import fs from 'node:fs';import path from 'node:path';
import {Connector,credentialReader} from './connector.mjs';
import {Outbox} from './outbox.mjs';
const [mode,configPath,operationId]=process.argv.slice(2);
if(!['run','send','health'].includes(mode)||!configPath)throw Error('usage: main.mjs run|health|send CONFIG [OPERATION_ID]');
const fd=fs.openSync(configPath,fs.constants.O_RDONLY|fs.constants.O_NOFOLLOW);
let p;
try{const st=fs.fstatSync(fd);if(!st.isFile()||st.size>16384||(st.mode&0o022)||![0,process.getuid()].includes(st.uid))throw Error('policy denied');p=JSON.parse(fs.readFileSync(fd,'utf8'));}finally{fs.closeSync(fd);}
if(p.enabled!==true){console.log(JSON.stringify({state:'DISABLED',intake:'DISABLED'}));process.exit(0);}
if(mode==='health'){
 const h=JSON.parse(fs.readFileSync(path.join(p.state_dir,'health.json'),'utf8'));
 // Only these nonsecret fields are emitted; stale READY is not liveness proof.
 console.log(JSON.stringify({state:h.state,intake:h.intake,outbox:h.outbox,updated:h.updated}));process.exit(0);
}
let c;const timer=setTimeout(()=>process.exit(2),10000); // hard process auth deadline
try{
 const {Spectrum,text}=await import('spectrum-ts');
 const {imessage}=await import('spectrum-ts/providers/imessage');
 c=new Connector(p,{factory:Spectrum,text,imessage,credentials:credentialReader(process.env.CREDENTIALS_DIRECTORY)});
 await c.start();clearTimeout(timer);
 const outbox=p.outbox_enabled===true?new Outbox(path.join(p.state_dir,'outbox'),(id,body)=>c.send(id,body)):null;
 const health=()=>{const out=path.join(p.state_dir,'health.json'),tmp=out+'.tmp';fs.writeFileSync(tmp,JSON.stringify({...c.health(),outbox:outbox?'ENABLED':'DISABLED',updated:new Date().toISOString()}),{mode:0o600});fs.renameSync(tmp,out);};
 health();
 if(mode==='send'){
  const text=fs.readFileSync(0,'utf8');if(Buffer.byteLength(text)>65536)throw Error('text too large');
  const sendDeadline=setTimeout(()=>process.exit(2),10000);
  await c.send(operationId,text);clearTimeout(sendDeadline);await c.stop();health();console.log('Research send accepted; delivery not established');process.exit(0);
 }
 const ticker=setInterval(health,5000);
 const pump=outbox?setInterval(()=>{outbox.pumpOnce().catch(()=>{});},2000):null;
 let stopping=false;
 const stop=async code=>{if(stopping)return;stopping=true;clearInterval(ticker);if(pump)clearInterval(pump);const hard=setTimeout(()=>process.exit(2),2000);await c.stop();health();clearTimeout(hard);process.exit(code??0);};
 process.on('SIGTERM',()=>stop(0));process.on('SIGINT',()=>stop(0));
 // A dropped provider stream ends the process so systemd can restart it (Restart=on-failure).
 c.client.pump.then(()=>stop(3));
 if(Number.isInteger(p.session_seconds)&&p.session_seconds>0)setTimeout(()=>stop(0),p.session_seconds*1000);
}catch{clearTimeout(timer);console.error('Research connector unavailable');process.exit(2);}
