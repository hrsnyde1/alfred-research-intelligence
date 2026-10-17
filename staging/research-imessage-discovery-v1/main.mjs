import fs from 'node:fs';
import path from 'node:path';
import {pathToFileURL} from 'node:url';
import {startup,validate,stageRecorder} from './discovery.mjs';
// systemd LoadCredential files may be root-owned and group-readable (0440).
// Other accepted credentials are private to root or the dedicated service UID.
export function credentialMetadataAllowed(st, serviceUid) {
  const mode=st.mode & 0o7777;
  return [0,serviceUid].includes(st.uid) &&
    ([0o400,0o600].includes(mode) || (st.uid === 0 && mode === 0o440));
}
async function main() {
// No SDK diagnostics can reach stdout/stderr, including before dynamic imports.
console.log=console.info=console.warn=console.error=console.debug=()=>{};
let timer, diagnostic;
const stage=stageRecorder(line=>{
  if (diagnostic === undefined) return;
  fs.writeSync(diagnostic,line); fs.fsyncSync(diagnostic);
});
try {
  if (process.argv[2] !== '--live-discovery' || ![4,5].includes(process.argv.length) || (process.argv.length === 5 && process.argv[4] !== '--diagnostic')) throw Error();
  const read = (file, limit, privateOnly) => {
    const fd=fs.openSync(file,fs.constants.O_RDONLY|fs.constants.O_NOFOLLOW);
    try {
      const st=fs.fstatSync(fd);
      if (!st.isFile() || st.size>limit || (privateOnly ? !credentialMetadataAllowed(st,process.getuid()) :
          ((st.mode & 0o022) || ![0,process.getuid()].includes(st.uid)))) throw Error();
      return fs.readFileSync(fd,'utf8');
    } finally {fs.closeSync(fd);}
  };
  if (process.argv[4] === '--diagnostic')
    diagnostic=fs.openSync('/var/lib/alfred-research-discovery/startup-stages.txt','wx',0o600);
  const report=await startup({stage,loadPolicy:()=>{
  const policy=JSON.parse(read(process.argv[3],4096,false)); validate(policy);
  // Total deadline includes imports, authentication, iterator and teardown.
  timer=setTimeout(()=>{try {stage('FAILED');} finally {process.exit(3);}},policy.timeout_ms);
  return policy;
  },loadCredentials:()=>{
  const dir=process.env.CREDENTIALS_DIRECTORY;
  if (!dir || !path.isAbsolute(dir)) throw Error();
  const credentials={projectId:read(path.join(dir,'research-project-id'),4096,true).trim(),
    projectSecret:read(path.join(dir,'research-project-secret'),4096,true).trim()};
  return credentials;
  },loadSdk:async()=>{
  // Remove ambient SDK configuration/endpoint overrides before importing SDK.
  for (const key of Object.keys(process.env)) if (/^(SPECTRUM_|PHOTON_|OTEL_)/.test(key)) delete process.env[key];
  const {Spectrum}=await import('spectrum-ts');
  const {imessage}=await import('spectrum-ts/providers/imessage');
  return {factory:Spectrum,provider:imessage};
  }});
  if (!report) {stage('FAILED');process.exit(3);}
  // Exclusive write prevents reruns or duplicate delivery from replacing evidence.
  const fd=fs.openSync('/var/lib/alfred-research-discovery/report.json','wx',0o600);
  try {fs.writeFileSync(fd,JSON.stringify(report,null,2)+'\n');fs.fsyncSync(fd);} finally {fs.closeSync(fd);}
  clearTimeout(timer); process.exit(0);
} catch {clearTimeout(timer);try {stage('FAILED');} finally {process.exit(2);}}
}
// Importing the metadata validator for offline tests must not execute the CLI.
if (process.argv[1] && import.meta.url === pathToFileURL(process.argv[1]).href) await main();
