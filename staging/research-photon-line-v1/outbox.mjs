// Research reply outbox: the Python Research worker writes one JSON file per reply;
// this pump sends each through Connector.send exactly once, in sequence order.
// At-most-once: send() records UNKNOWN before any external effect, so an
// interrupted or failed send is quarantined for reconciliation, never resent.
import fs from 'node:fs';
import path from 'node:path';
const exact=v=>typeof v==='string'&&v.length>0&&v.length<=256&&v.trim()===v;
const NAME=/^[a-f0-9]{64}\.json$/;
export class Outbox {
  constructor(dir,send){
    const st=fs.lstatSync(dir);
    if(!st.isDirectory()||st.isSymbolicLink()||(st.mode&0o077)||st.uid!==process.getuid())throw Error('protected outbox required');
    this.dir=dir;this.send=send;this.running=false;
    for(const sub of ['sent','unknown','rejected'])fs.mkdirSync(path.join(dir,sub),{mode:0o700,recursive:true});
  }
  entries(){
    const items=[];
    for(const name of fs.readdirSync(this.dir)){
      if(!NAME.test(name))continue;
      const file=path.join(this.dir,name);
      try{
        const st=fs.lstatSync(file);if(!st.isFile()||st.isSymbolicLink()||st.size>131072)throw Error('bad entry');
        const r=JSON.parse(fs.readFileSync(file,'utf8'));
        if(r.schema!=='research.outbox/1'||!exact(r.operationId)||typeof r.text!=='string'||Buffer.byteLength(r.text)>65536)throw Error('bad entry');
        items.push({name,file,record:r});
      }catch{this.move(name,'rejected');}
    }
    return items.sort((a,b)=>(a.record.sequence??0)-(b.record.sequence??0)||a.name.localeCompare(b.name));
  }
  move(name,where){try{fs.renameSync(path.join(this.dir,name),path.join(this.dir,where,name));}catch{}}
  async pumpOnce(){
    if(this.running)return {sent:0};
    this.running=true;let sent=0;
    try{
      for(const {name,record} of this.entries()){
        try{await this.send(record.operationId,record.text);this.move(name,'sent');sent++;}
        catch(e){
          const m=String(e?.message??'');
          if(/unavailable|in progress/i.test(m))break;          // transport down: try again later, nothing recorded
          if(/conflict|binding denied/i.test(m)){this.move(name,'rejected');continue;}
          this.move(name,'unknown');                              // possible external effect: reconcile, never resend
        }
      }
    }finally{this.running=false;}
    return {sent};
  }
}
