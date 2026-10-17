// One-time binding discovery for the Research line. Authenticates with the Research
// project only, waits for ONE inbound text whose SHA-256 equals the owner's challenge,
// records the raw line label / conversation id / sender id for the owner to copy into
// the policy, and stops. Sends nothing, stores no message content, registers nothing.
import crypto from 'node:crypto';
import fs from 'node:fs';
import path from 'node:path';
const sha=s=>crypto.createHash('sha256').update(s).digest('hex');
const exact=v=>typeof v==='string'&&v.length>0&&v.length<=256&&v.trim()===v;
export async function discover(policy,{factory,imessage,credentials,deadlineMs=120000}){
  if(!/^[a-f0-9]{64}$/.test(policy.discovery_challenge_sha256||''))throw Error('discovery challenge digest required');
  if(!exact(policy.project_id)||!exact(policy.state_dir))throw Error('project and state directory required');
  const secret=await credentials();
  if(!exact(secret?.projectSecret)||secret.projectId!==policy.project_id)throw Error('credentials denied');
  const app=await factory({projectId:policy.project_id,projectSecret:secret.projectSecret,providers:[imessage.config()],options:{flattenGroups:true},telemetry:false});
  let timer;
  const timeout=new Promise(resolve=>{timer=setTimeout(()=>resolve(null),deadlineMs);});
  const first=(async()=>{
    for await(const [space,message] of app.messages){
      if(message?.direction!=='inbound'||message.content?.type!=='text'||typeof message.content.text!=='string')continue;
      if(sha(message.content.text.trim())!==policy.discovery_challenge_sha256)continue;  // ignore stray whitespace
      return {space,message};
    }
    return null;
  })();
  try{
    const found=await Promise.race([first,timeout]);
    if(!found)return {state:'NO_MATCH'};
    const {space,message}=found;
    const report={schema:'research.line.discovery/1',discovered_at:new Date().toISOString(),
      line:space.phone??null,space:space.id??null,sender:message.sender?.id??null,space_type:space.type??null,
      shared_line:space.phone==='shared',
      usable:exact(space.phone)&&space.phone!=='shared'&&exact(space.id)&&exact(message.sender?.id)&&message.sender.id!==space.id};
    const out=path.join(policy.state_dir,'discovery.json');
    const fd=fs.openSync(out,'wx',0o600);  // exclusive: never overwrite an earlier report
    try{fs.writeFileSync(fd,JSON.stringify(report,null,1));fs.fsyncSync(fd);}finally{fs.closeSync(fd);}
    return {state:report.usable?'DISCOVERED':'DISCOVERED_UNUSABLE',shared_line:report.shared_line};
  }finally{clearTimeout(timer);await app.stop();}
}
