import crypto from 'node:crypto';
const valid = value => typeof value === 'string' && value.length > 0;
const equal = (a,b) => valid(a) && valid(b) && Buffer.byteLength(a)===Buffer.byteLength(b)
  && crypto.timingSafeEqual(Buffer.from(a),Buffer.from(b));
// Tokens are host-issued caller capabilities, not message payload fields.
export class CallerBindings {
  #personalToken; #researchToken; #personal; #research;
  constructor(personalToken,researchToken=null) {
    if (!valid(personalToken)) throw new Error('Personal caller authority required');
    this.#personalToken=personalToken;
    this.#researchToken=valid(researchToken) && !equal(personalToken,researchToken) ? researchToken : null;
    this.#personal=Object.freeze({principal:'legacy-personal',project:'personal'});
    this.#research=Object.freeze({principal:'research-intake',project:'research'});
  }
  get researchAvailable() {return this.#researchToken!==null;}
  authenticate(headers) {
    // Presence of Research authority never falls back on a valid legacy token.
    if (headers['x-hermes-research-token']!==undefined)
      return equal(headers['x-hermes-research-token'],this.#researchToken) ? this.#research : null;
    return equal(headers['x-hermes-sidecar-token'],this.#personalToken) ? this.#personal : null;
  }
  select(caller,body) {
    if (caller===this.#personal && body && (body.project===undefined || body.project==='personal')
        && !String(body.spaceId||'').startsWith('photon-research:')) return 'personal';
    if (caller===this.#research && body?.project==='research'
        && String(body.spaceId||'').startsWith('photon-research:')) return 'research';
    throw new Error('caller/project binding denied');
  }
  isPersonal(caller) {return caller===this.#personal;}
}
