// Research-only second app. No ambient fallback to Personal credentials.
import crypto from 'node:crypto';
import fs from 'node:fs';
import path from 'node:path';
const hash = x => crypto.createHash('sha256').update(JSON.stringify(x)).digest('hex');
const exact = x => typeof x === 'string' && x.length > 0 && x.length <= 256 && x === x.trim();
export function configuration(env) {
  if (env.PHOTON_RESEARCH_ENABLED !== '1') return null;
  const names = ['PROJECT_ID','PROJECT_SECRET','CONNECTION_REF','LINE','SPACE','SENDER','PROFILE','STATE_DIR'];
  const c = Object.fromEntries(names.map(n => [n.toLowerCase(),env['PHOTON_RESEARCH_'+n]]));
  if (!exact(env.PHOTON_PERSONAL_LINE) || env.PHOTON_PERSONAL_LINE === c.line || !names.every(n=>exact(c[n.toLowerCase()]))) throw new Error('Research configuration unavailable');
  if (c.project_id === env.PHOTON_PROJECT_ID || c.project_secret === env.PHOTON_PROJECT_SECRET || c.line === 'shared')
    throw new Error('Research project isolation required');
  return c;
}
export class FileLedger {
  constructor(root) {
    const st=fs.lstatSync(root);
    if (!st.isDirectory() || st.isSymbolicLink() || (st.mode & 0o077) || st.uid !== process.getuid())
      throw new Error('protected Research state directory required');
    this.root=root;
  }
  get(key) {
    try { return JSON.parse(fs.readFileSync(path.join(this.root,key+'.json'),'utf8')); }
    catch(e) { if(e.code==='ENOENT') return null; throw new Error('Research ledger unavailable'); }
  }
  put(key,value) {
    if(!/^[a-f0-9]{64}$/.test(key)) throw new Error('invalid ledger key');
    const target=path.join(this.root,key+'.json');
    if (!fs.existsSync(target) && fs.readdirSync(this.root).length >= 1024) throw new Error('Research ledger full');
    const tmp=target+'.'+crypto.randomUUID();
    const fd=fs.openSync(tmp,'wx',0o600);
    try {fs.writeFileSync(fd,JSON.stringify(value));fs.fsyncSync(fd);} finally {fs.closeSync(fd);}
    fs.renameSync(tmp,target);
    const dir=fs.openSync(this.root,'r');try {fs.fsyncSync(dir);} finally {fs.closeSync(dir);}
  }
}
export class ResearchProject {
  constructor(config,{factory,imessage,normalize,deliver,text,ledger}) {
    this.config=config;this.dependencies={factory,imessage,normalize,deliver,text};
    this.ledger=ledger;this.spaces=new Map();this.locks=new Set();this.app=null;this.stopped=false;
    this.route='photon-research:'+hash([config.project_id,config.line,config.space]);
  }
  async start() {
    const c=this.config,d=this.dependencies;
    this.app=await d.factory({projectId:c.project_id,projectSecret:c.project_secret,
      providers:[d.imessage.config()],options:{flattenGroups:true},telemetry:false});
    this.pump=this.consume().catch(()=>{this.stopped=true;}); // no raw SDK errors/secrets in logs
  }
  async consume() {
    for await(const [space,message] of this.app.messages) {
      if(this.stopped) break;
      if(message.direction !== 'inbound') continue;
      try {await this.inbound(space,message);} catch { /* terminal quarantine, never Personal */ }
    }
  }
  async inbound(space,message) {
    const c=this.config;
    if(space.phone!==c.line || space.id!==c.space || message.sender?.id!==c.sender || !exact(message.id) || message.content?.type !== 'text')
      throw new Error('Research identity denied');
    const event=await this.dependencies.normalize(space,message);
    if (event.content?.type !== 'text' || typeof event.content.text !== 'string' || Buffer.byteLength(event.content.text)>65536) throw new Error('Research text required');
    const key=hash([c.project_id,c.line,c.space,message.id]);
    const fingerprint=hash(event),record=this.ledger.get(key);
    if(record && record.fingerprint!==fingerprint) throw new Error('Research event conflict');
    if(!record)this.ledger.put(key,{fingerprint});
    // Replay is intentional: durable intake owns logical dedupe, not this cache.
    event.project='research';event.projectBinding='research-connection-v1';
    event.research={connection_ref:c.connection_ref,line:c.line,space:c.space,sender:c.sender,profile:c.profile,
      originalMessageId:message.id,route:this.route};
    event.space={...event.space,id:this.route};event.messageId='research:'+key;
    this.spaces.set(this.route,space);
    await this.dependencies.deliver(JSON.stringify(event));
    return event;
  }
  async send(endpoint,body) {
    const c=this.config;
    if (!this.app || this.stopped) throw new Error('Research unavailable');
    if(body.project!=='research' || body.spaceId!==this.route || endpoint!=='/send' ||
       typeof body.text!=='string' || Buffer.byteLength(body.text)>65536 || !exact(body.operationId) || body.format && body.format!=='text')
      throw new Error('Research outbound binding denied');
    const key=hash(['send',c.project_id,c.line,c.space,body.operationId]);
    const fingerprint=hash([this.route,body.text]);
    const prior=this.ledger.get(key);
    if(prior) {
      if(prior.fingerprint!==fingerprint)throw new Error('Research send conflict');
      if(prior.state!=='ACCEPTED')throw new Error('Research delivery unknown; reconciliation required');
      return {messageId:prior.messageId};
    }
    if(this.locks.has(key))throw new Error('Research delivery in progress');
    this.locks.add(key);
    try {
      this.ledger.put(key,{fingerprint,state:'UNKNOWN'}); // before any possible external effect
      const space=this.spaces.get(this.route) ?? await this.dependencies.imessage(this.app).space.get(c.space,{phone:c.line});
      if(space.phone!==c.line || space.id!==c.space) throw new Error('Research space mismatch');
      const result=await space.send(this.dependencies.text(body.text));
      if(!exact(result?.id))throw new Error('Research delivery unknown');
      this.ledger.put(key,{fingerprint,state:'ACCEPTED',messageId:'research:'+hash([c.project_id,c.line,result.id])});
      return {messageId:this.ledger.get(key).messageId};
    } finally {this.locks.delete(key);}
  }
  async stop() {this.stopped=true;if(this.app)await this.app.stop();}
}
export async function createResearch(env,dependencies) {
  const c=configuration(env);if(!c)return null;
  const connector=new ResearchProject(c,{...dependencies,ledger:dependencies.ledger ?? new FileLedger(c.state_dir)});
  await connector.start();return connector;
}
