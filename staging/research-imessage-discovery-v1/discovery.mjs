import crypto from 'node:crypto';
export const digest = value => crypto.createHash('sha256').update(value).digest('hex');
const id = v => typeof v === 'string' && v.length > 0 && v.length <= 512 && !/[\x00-\x20\x7f]/.test(v);
const hex = v => typeof v === 'string' && /^[a-f0-9]{64}$/.test(v);
export function validate(p) {
  if (p.role !== 'research-discovery' || !hex(p.project_sha256) || !hex(p.line_sha256) ||
      !hex(p.challenge_sha256) || !Number.isInteger(p.timeout_ms) || p.timeout_ms < 1000 || p.timeout_ms > 120000)
    throw Error('policy denied');
}
// Phone-like identifiers are represented by digests; never persist handles accidentally.
const safeId = v => /\d{7}/.test(v.replace(/[+(). -]/g, '')) || v.includes('@')
  ? {sha256:digest(v)} : {id:v};
export class Qualifier {
  constructor(policy, projectId) {
    validate(policy);
    if (!id(projectId) || digest(projectId) !== policy.project_sha256) throw Error('binding denied');
    this.p = policy; this.projectId = projectId; this.seen = new Set(); this.done = false;
  }
  accept(space, message) {
    if (this.done) return null;
    const p = this.p;
    for (const obj of [space, message]) {
      if (obj?.projectId !== undefined && obj.projectId !== this.projectId) return null;
    }
    if (message?.direction !== 'inbound' || message.platform !== 'imessage' ||
        space?.platform !== 'imessage' || !id(space.phone) || space.phone === 'shared' ||
        digest(space.phone) !== p.line_sha256 || !id(space.id) || !id(message.id) ||
        !id(message.sender?.id) || message.sender.platform !== 'imessage') return null;
    const key = digest(JSON.stringify([space.phone, space.id, message.id]));
    if (this.seen.has(key)) return null;
    // Bound memory even if the project receives unexpected traffic.
    if (this.seen.size >= 1024) throw Error('event limit');
    this.seen.add(key);
    if (message.content?.type !== 'text' || typeof message.content.text !== 'string' ||
        Buffer.byteLength(message.content.text) > 4096 || digest(message.content.text) !== p.challenge_sha256) return null;
    this.done = true;
    return {project_binding:{role:'research',sha256:p.project_sha256},
      receiving_line:{sha256:p.line_sha256}, conversation:safeId(space.id),
      sender:safeId(message.sender.id), correlation_sha256:key};
  }
}
export async function startup({loadPolicy, loadCredentials, loadSdk, stage=()=>{}}) {
  const policy=await loadPolicy(); validate(policy); stage('POLICY_OK');
  const credentials=await loadCredentials();
  new Qualifier(policy, credentials.projectId);
  if (!id(credentials.projectSecret)) throw Error('credentials denied');
  stage('CREDENTIALS_OK');
  const {factory,provider}=await loadSdk(); stage('SDK_IMPORT_OK');
  return discover({policy,credentials,factory,provider,stage});
}
export async function discover({policy, credentials, factory, provider, stage=()=>{}}) {
  const q = new Qualifier(policy, credentials.projectId);
  if (!id(credentials.projectSecret)) throw Error('credentials denied');
  let app;
  try {
    const config=provider.config(); stage('PROVIDER_OK');
    app = await factory({projectId:credentials.projectId, projectSecret:credentials.projectSecret,
      providers:[config], options:{flattenGroups:true}, telemetry:false});
    stage('AUTHENTICATION_OK');
    const iterator=app.messages[Symbol.asyncIterator]();
    if (!iterator || typeof iterator.next !== 'function') throw Error('stream denied');
    stage('STREAM_READY');
    for await (const [space, message] of {[Symbol.asyncIterator]:()=>iterator}) {
      const report = q.accept(space, message);
      if (report) return report;
    }
    return null;
  } finally { if (app) await app.stop(); }
}

// A run can persist at most seven fixed lines; no caller data is serialized.
export function stageRecorder(write) {
  const seen=new Set();
  return code=>{
    if (!['POLICY_OK','CREDENTIALS_OK','SDK_IMPORT_OK','PROVIDER_OK',
          'AUTHENTICATION_OK','STREAM_READY','FAILED'].includes(code)) throw Error('stage denied');
    if (!write || seen.has(code)) return;
    seen.add(code); write(code+'\n');
  };
}
