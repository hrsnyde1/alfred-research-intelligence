// Isolated Research project only. No Personal transport or ordinary-agent fallback.
import crypto from 'node:crypto';
import fs from 'node:fs';
import path from 'node:path';
import {ResearchProject, FileLedger} from './research-project.mjs';
const hash=v=>crypto.createHash('sha256').update(JSON.stringify(v)).digest('hex');
const valid=v=>typeof v==='string' && v.length>0 && v.length<=256 && v.trim()===v;
export class Connector {
  constructor(policy, dependencies) {
    this.policy=Object.freeze({...policy});this.d=dependencies;this.state='DISABLED';this.client=null;
    if(policy.role!=='research' || !['project_id','line','space','sender','profile','connection_ref'].every(k=>valid(policy[k])) || policy.line==='shared') throw Error('binding denied');
  }
  async start() {
    if(this.policy.enabled!==true)return;
    if(this.state!=='DISABLED')throw Error('already started');
    this.state='STARTING';
    try {
      const secret=await this.d.credentials();
      if(!valid(secret?.projectSecret)||secret.projectId!==this.policy.project_id)throw Error('credentials denied');
      const ledger=new FileLedger(this.policy.state_dir);
      this.client=new ResearchProject({...this.policy,project_secret:secret.projectSecret},{...this.d,ledger,
        deliver:wire=>this.persist(wire),
        normalize:async(space,m)=>({messageId:m.id,direction:m.direction,platform:'imessage',
          space:{id:space.id,phone:space.phone,type:space.type},sender:{id:m.sender?.id},
          content:{type:m.content?.type,text:m.content?.text},timestamp:m.timestamp instanceof Date?m.timestamp.toISOString():m.timestamp??null})});
      await this.client.start();this.state='READY';
      this.client.pump.then(()=>{if(this.state==='READY')this.state='UNAVAILABLE';});
    } catch {this.state='UNAVAILABLE';throw Error('Research unavailable');}
  }
  persist(wire) {
    const event=JSON.parse(wire),key=hash(['intake',event.messageId]);
    const fingerprint=hash(event),old=this.client.ledger.get(key);
    if(old){if(old.fingerprint!==fingerprint)throw Error('intake conflict');return old;}
    // A pending intake correlation is NOT a Research task or source digest.
    const record={schema:'research.connector.pending/1',fingerprint,
      correlation:'research-pending:'+key,event,status:'PENDING_INTAKE',productionTrusted:false};
    this.client.ledger.put(key,record);return record;
  }
  async intake(correlation) {
    // No wire input has authority to invoke Hermes. No live registration exists.
    if(this.policy.intake_enabled!==true || !this.d.intake) return {status:'UNAVAILABLE'};
    if(this.d.testOnly!==true)throw Error('live Hermes attachment not registered');
    if(typeof correlation!=='string'||!/^research-pending:[a-f0-9]{64}$/.test(correlation))throw Error('correlation denied');
    const r=this.client.ledger.get(correlation.slice('research-pending:'.length));
    if(!r||r.correlation!==correlation)throw Error('correlation denied');
    return this.d.intake(r); // synthetic seam only; existing intake owns task deduplication
  }
  async send(operationId,text) {
    if(this.state!=='READY')throw Error('Research unavailable');
    return this.client.send('/send',{project:'research',spaceId:this.client.route,operationId,text,format:'text'});
  }
  health(){return {schema:'research.connector.health/1',state:this.state,intake:'DISABLED',projectRole:'research'};}
  async stop(){this.state='STOPPED';if(this.client)await this.client.stop();}
}
// Protected references only; never consult Personal environment/configuration.
export function credentialReader(directory) {
  return ()=>{
    const read=name=>{
      const p=path.join(directory,name),fd=fs.openSync(p,fs.constants.O_RDONLY|fs.constants.O_NOFOLLOW);
      try {const st=fs.fstatSync(fd);if(!st.isFile()||st.size>4096||(st.mode&0o077))throw Error('credential denied');
        return fs.readFileSync(fd,'utf8').trim();}finally{fs.closeSync(fd);}
    };
    return {projectId:read('research-project-id'),projectSecret:read('research-project-secret')};
  };
}
