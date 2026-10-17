// Started only after Personal listener readiness and explicit Research enable/auth.
import {parentPort,workerData} from 'node:worker_threads';
import {ResearchProject,FileLedger} from './research-project.mjs';
let connector;let releaseReady;const readiness=new Promise(resolve=>{releaseReady=resolve;});
const deliveries=new Map();let deliveryId=0;
parentPort.on('message',async message=>{
  if(message.type==='delivered') {deliveries.get(message.id)?.();deliveries.delete(message.id);return;}
  if(message.type!=='send'||!connector)return;
  try {parentPort.postMessage({type:'reply',id:message.id,ok:true,result:await connector.send(message.endpoint,message.body)});}
  catch {parentPort.postMessage({type:'reply',id:message.id,ok:false});}
});
try {
  const {Spectrum,text}=await import('spectrum-ts');
  const {imessage}=await import('spectrum-ts/providers/imessage');
  connector=new ResearchProject(workerData,{factory:Spectrum,imessage,text,
    ledger:new FileLedger(workerData.state_dir),
    normalize:async(space,message)=>({messageId:message.id,direction:message.direction,platform:'imessage',
      space:{id:space.id,phone:space.phone,type:space.type},sender:{id:message.sender?.id},
      content:{type:'text',text:message.content.text},
      timestamp:message.timestamp instanceof Date?message.timestamp.toISOString():message.timestamp??null}),
    deliver:async event=>{await readiness;return new Promise(resolve=>{
      const id=++deliveryId;deliveries.set(id,resolve);parentPort.postMessage({type:'inbound',id,event});
    });}});
  await connector.start();parentPort.postMessage({type:'ready'});releaseReady();
  connector.pump.then(()=>parentPort.postMessage({type:'failed'}));
} catch {parentPort.postMessage({type:'failed'});}
