import {Worker} from 'node:worker_threads';
import {configuration} from './research-project.mjs';
export class ResearchLifecycle {
  constructor(env,{authorized=false,deliver,workerFactory,authTimeoutMs=10000,requestTimeoutMs=10000,sessionTimeoutMs=300000}={}) {
    this.env=env;this.authorized=authorized;this.deliver=deliver;
    this.workerFactory=workerFactory ?? (config=>new Worker(new URL('./research-worker.mjs',import.meta.url),
      {workerData:config,env:{},stdout:true,stderr:true}));
    for(const n of [authTimeoutMs,requestTimeoutMs])
      if(!Number.isFinite(n)||n<=0||n>10000)throw new Error('bounded Research timeout required');
    if(!Number.isFinite(sessionTimeoutMs)||sessionTimeoutMs<=0||sessionTimeoutMs>300000)throw new Error('bounded Research session required');
    this.sessionTimeoutMs=sessionTimeoutMs;
    this.authTimeoutMs=authTimeoutMs;this.requestTimeoutMs=requestTimeoutMs;
    this.state=env.PHOTON_RESEARCH_ENABLED==='1'?'unavailable':'disabled';
    this.attempts=0;this.worker=null;this.pending=new Map();this.nextId=0;this.closed=false;
  }
  start() {
    if(this.attempts || this.closed || this.state==='disabled')return;
    // No automatic authentication retries. A fresh approved lifecycle is needed.
    this.attempts=1;
    let config;
    try {if(!this.authorized)throw Error();config=configuration(this.env);}catch {this.state='unavailable';return;}
    this.state='starting';this.abort=new AbortController();
    try {this.worker=this.workerFactory(config);}catch {this.state='unavailable';return;}
    const worker=this.worker;
    worker.stdout?.resume();worker.stderr?.resume(); // never forward SDK secrets/errors
    this.timer=setTimeout(()=>this.fail(),this.authTimeoutMs);
    this.sessionTimer=setTimeout(()=>this.fail(),this.sessionTimeoutMs);
    worker.on('message',message=>{
      if(this.worker!==worker || this.closed)return;
      if(message.type==='ready' && this.state==='starting') {clearTimeout(this.timer);this.state='ready';return;}
      if(message.type==='failed') {this.fail();return;}
      if(message.type==='inbound' && this.state==='ready') {
        // The worker is our independently authenticated project connection.
        Promise.resolve().then(()=>this.deliver(message.event,this.abort.signal)).then(
          ()=>{if(this.worker===worker)worker.postMessage({type:'delivered',id:message.id});},()=>this.fail());return;
      }
      if(message.type==='reply') {
        const p=this.pending.get(message.id);if(!p)return;
        clearTimeout(p.timer);this.pending.delete(message.id);
        message.ok?p.resolve(message.result):p.reject(new Error('Research outcome unavailable or unknown'));
      }
    });
    worker.on('error',()=>this.fail());worker.on('exit',()=>{if(this.worker===worker)this.fail();});
  }
  fail() {
    this.abort?.abort();
    clearTimeout(this.timer);clearTimeout(this.sessionTimer);this.state=this.closed?'stopped':'unavailable';
    for(const p of this.pending.values()){clearTimeout(p.timer);p.reject(new Error('Research outcome unknown'));}
    this.pending.clear();const worker=this.worker;this.worker=null;
    // Killing the isolated thread cancels SDK authentication and internal retries;
    // a Promise.race alone would leave a live late connection behind.
    if(worker)this.termination=Promise.resolve(worker.terminate()).catch(()=>{});
  }
  send(endpoint,body) {
    if(this.state!=='ready'||this.pending.size>=16)return Promise.reject(new Error('Research unavailable'));
    const id=++this.nextId;
    return new Promise((resolve,reject)=>{
      const timer=setTimeout(()=>this.fail(),this.requestTimeoutMs);
      this.pending.set(id,{resolve,reject,timer});
      try {this.worker.postMessage({type:'send',id,endpoint,body});}catch {this.fail();}
    });
  }
  async stop() {this.closed=true;this.fail();await this.termination;}
}
