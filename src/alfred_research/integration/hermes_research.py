"""Personal Alfred -> Research adapter for Hermes' existing post_gateway_admission hook.

Prepared, not installed. Hermes' plugin lifecycle calls
``on_post_gateway_admission(payload)`` with the routed message; returning
``{'action': 'handled', 'reply': text}`` consumes the turn, returning ``None``
leaves it to normal Personal Alfred chat. The adapter:

* acts only when explicitly enabled and only for exact configured owner
  identities (platform, chat_id, user_id); everything else passes through;
* starts Research automatically for supported links/attachments
  (``message_intake.detect``) and acknowledges immediately;
* executes jobs in the background with the existing persistent engine and
  delivers a message-friendly result through a host-supplied ``deliver``;
* never grants Research access beyond the Personal environment, never writes
  Memory, and treats source content purely as data.
"""
from datetime import datetime, timedelta, timezone
import hashlib
import json
import logging
import re
import threading

from ..local.engine import ResearchEngine
from ..local.memory import AuthoritativeMemoryAdapter
from .message_intake import detect

log = logging.getLogger(__name__)
HOOK = 'post_gateway_admission'
ROUTE_ARTIFACT = 'hermes-route'
DELIVERY_ARTIFACT = 'hermes-delivery'
IN_PROGRESS = ('collecting', 'planning', 'researching', 'verifying', 'synthesizing')
OWNER_STATUS = {'queued': 'accepted', 'collecting': 'running', 'planning': 'running', 'researching': 'running',
                'verifying': 'running', 'synthesizing': 'running', 'completed': 'completed', 'failed': 'failed',
                'needs_more_research': 'partially completed', 'unsupported': 'unsupported source',
                'needs_sources': 'needs sources', 'interrupted': 'interrupted'}
STATUS_COMMAND = re.compile(r'^\s*(?:alfred[\s,]+)?research (?:status|jobs)(?:\s+(research-[0-9a-f]{32}))?\s*\??\s*$', re.I)
DEDUPE_WINDOW = timedelta(hours=24)


class Owner(tuple):
    """Exact (platform, chat_id, user_id). No wildcards or fallbacks."""
    def __new__(cls, platform, chat_id, user_id):
        values = (platform, chat_id, user_id)
        if any(not isinstance(v, str) or not v.strip() or v != v.strip() or '*' in v for v in values):
            raise ValueError('Owner identity must be exact non-empty strings')
        if chat_id == user_id:
            raise ValueError('Owner user_id must differ from chat_id (Photon sender fallback is not identity)')
        return super().__new__(cls, values)


def short(text, limit):
    text = ' '.join(str(text).split())
    return text if len(text) <= limit else text[:limit - 1].rstrip() + '…'


class HermesResearchAdapter:
    def __init__(self, working_directory, owners, *, enabled=False, deliver=None, provider='auto',
                 attachment_roots=(), runner='thread', max_concurrent=2, clock=None):
        if runner not in ('thread', 'inline'):
            raise ValueError('runner must be thread or inline')
        self.engine = ResearchEngine(working_directory)
        self.owners = frozenset(Owner(*o) if not isinstance(o, dict) else Owner(o['platform'], o['chat_id'], o['user_id'])
                                for o in owners)
        self.enabled = enabled is True
        self.deliver, self.provider, self.runner = deliver, provider, runner
        self.attachment_roots = tuple(attachment_roots)
        self.slots = threading.BoundedSemaphore(max_concurrent)
        self.clock = clock or (lambda: datetime.now(timezone.utc))

    # ------------------------------------------------------------ hook entry

    def on_post_gateway_admission(self, payload):
        if not self.enabled or not isinstance(payload, dict):
            return None
        source = payload.get('source') if isinstance(payload.get('source'), dict) else {}
        platform = payload.get('platform') or source.get('platform')
        chat_id, user_id = source.get('chat_id'), source.get('user_id')
        if (platform, chat_id, user_id) not in self.owners:
            return None  # not the owner: Research stays out of the way
        text = payload.get('text') or payload.get('message') or ''
        status = STATUS_COMMAND.match(text) if isinstance(text, str) else None
        if status:
            return self.handled(self.status_reply(status.group(1)))
        intent = detect(text, payload.get('attachments') or payload.get('media') or (), self.attachment_roots)
        if intent is None:
            return None
        message_id = payload.get('message_id')
        if not isinstance(message_id, str) or not message_id.strip() or len(message_id) > 256:
            log.warning('Research intake skipped: host event has no message_id for idempotency')
            return None
        route = {'platform': platform, 'chat_id': chat_id, 'user_id': user_id, 'message_id': message_id,
                 'session_key': payload.get('session_key'), 'profile': source.get('profile'),
                 'environment': 'personal'}
        try:
            return self.handled(self.accept(intent, route))
        except Exception as error:  # an honest failure beats falling through to an ungrounded chat answer
            log.exception('Research intake failed')
            return self.handled('I couldn\'t start research on that: ' + short(error, 200) + ' Nothing was researched.')

    @staticmethod
    def handled(reply):
        return {'action': 'handled', 'reply': reply}

    # ------------------------------------------------------------ intake

    def accept(self, intent, route):
        request = {'objective': intent.objective, 'sources': list(intent.sources), 'article': None, 'provider': self.provider}
        key = 'hermes:' + hashlib.sha256(json.dumps([route['platform'], route['chat_id'], route['message_id']]).encode()).hexdigest()
        replay = self.engine.store.by_request_key(key)
        if replay is None and not intent.rerun:
            since = (self.clock() - DEDUPE_WINDOW).strftime('%Y-%m-%dT%H:%M:%SZ')
            prior = self.engine.store.find_recent(request, since)
            if prior and self.engine.store.get(prior)['status'] not in ('failed', 'unsupported', 'interrupted', 'needs_sources'):
                job = self.engine.store.get(prior)
                return ('Already researched in the last day (job ' + prior + ', ' + OWNER_STATUS.get(job['status'], job['status']) +
                        '). Say "research this again" with the link to redo it.')
        job_id = self.engine.submit(intent.objective, intent.sources, provider=self.provider, request_key=key)
        job = self.engine.store.get(job_id)
        if ROUTE_ARTIFACT not in job['artifacts']:
            self.engine.store.put(job_id, ROUTE_ARTIFACT, {**route, 'notes': intent.notes})
            self.start(job_id)
        label = ('the question "' + short(intent.objective, 80) + '"') if intent.question_only else \
            ', '.join(short(s if s.startswith('https://') else s.rsplit('/', 1)[-1], 80) for s in intent.sources)
        lines = ['On it: researching ' + label + ' (job ' + job_id + ').']
        lines.append('I\'ll send the cited findings when it finishes.' if self.deliver else
                     'Ask "research status ' + job_id + '" for the result.')
        lines += intent.notes[:3]
        return '\n'.join(lines)

    # ------------------------------------------------------------ execution

    def start(self, job_id):
        if self.runner == 'inline':
            self.execute(job_id)
        else:
            threading.Thread(target=self.execute, args=(job_id,), name='research-' + job_id[-8:], daemon=True).start()

    def execute(self, job_id):
        with self.slots:
            try:
                job = self.engine.run(job_id)
            except Exception as error:
                log.exception('Research job %s did not run', job_id)
                job = self.engine.store.get(job_id)
                if job['status'] == 'queued':
                    self.engine.store.update(job_id, 'failed', 'Execution could not start', error=short(error, 600))
                    job = self.engine.store.get(job_id)
            self.notify(job)

    def notify(self, job):
        if DELIVERY_ARTIFACT in job['artifacts']:
            return
        route = job['artifacts'].get(ROUTE_ARTIFACT)
        record = {'status': 'not_configured', 'detail': 'No host delivery function; result retrievable by status command.'}
        if route and self.deliver:
            try:
                self.deliver(route, final_message(job))
                record = {'status': 'handed_to_host', 'detail': 'Host deliver() returned; not proof of recipient delivery.'}
            except Exception as error:
                log.exception('Research result delivery failed for %s', job['id'])
                record = {'status': 'failed', 'detail': short(error, 300)}
        self.engine.store.put(job['id'], DELIVERY_ARTIFACT, record)

    def resume(self):
        """After a Hermes restart: run accepted jobs, retry abandoned ones once, deliver pending results."""
        resumed = []
        for row in self.engine.store.list():
            job = self.engine.store.get(row['id'])
            route = job['artifacts'].get(ROUTE_ARTIFACT)
            if route is None:
                continue
            if job['status'] == 'queued':
                self.start(job['id'])
                resumed.append(job['id'])
            elif job['status'] in IN_PROGRESS:
                try:
                    self.engine.recover(job['id'])
                except ValueError:
                    continue  # still running in another process
                if 'retry_of' in job['artifacts']:
                    self.notify(self.engine.store.get(job['id']))
                    continue
                request = job['request']
                retry = self.engine.submit(request['objective'], request['sources'], provider=request['provider'])
                self.engine.store.put(retry, ROUTE_ARTIFACT, route)
                self.engine.store.put(retry, 'retry_of', job['id'])
                self.engine.store.put(job['id'], DELIVERY_ARTIFACT, {'status': 'superseded', 'detail': 'Retried as ' + retry})
                self.start(retry)
                resumed.append(retry)
            elif DELIVERY_ARTIFACT not in job['artifacts'] and job['status'] in OWNER_STATUS:
                self.notify(job)
        return resumed

    # ------------------------------------------------------------ status

    def status_reply(self, job_id=None):
        if job_id:
            try:
                job = self.engine.store.get(job_id)
            except KeyError:
                return 'No research job ' + job_id + '.'
            if job['status'] in IN_PROGRESS or job['status'] == 'queued':
                return 'Job ' + job_id + ' is ' + OWNER_STATUS[job['status']] + ' (' + job['events'][-1]['detail'] + ').'
            return final_message(job)
        rows = [r for r in self.engine.store.list()[:20] if ROUTE_ARTIFACT in self.engine.store.get(r['id'])['artifacts']][:5]
        if not rows:
            return 'No research jobs yet.'
        return 'Recent research:\n' + '\n'.join(
            '- ' + r['id'] + ': ' + OWNER_STATUS.get(r['status'], r['status']) + ' (' + r['updated_at'] + ')' for r in rows)


def final_message(job):
    """Message-friendly summary; the full cited report stays with the job."""
    artifacts, status = job['artifacts'], job['status']
    objective = short(job['request']['objective'], 120)
    if status in ('failed', 'unsupported', 'needs_sources', 'interrupted') or 'report' not in artifacts:
        failures = artifacts.get('acquisition-failures') or []
        reason = '; '.join(short(f['error'].split(': ', 1)[-1], 220) for f in failures[:2]) or short(job.get('error') or job['events'][-1]['detail'], 220)
        outcome = {'unsupported': 'stopped: unsupported source', 'needs_sources': 'stopped: needs sources'}
        return ('Research ' + outcome.get(status, OWNER_STATUS.get(status, status)) + ' (job ' + job['id'] + '): ' + reason +
                '\nNothing was inferred or reported as findings.')
    sources = [v for k, v in sorted(artifacts.items()) if k.startswith('source-')]
    assessments = {a['claim_id']: a['supported'] for a in artifacts['verification']['assessments']}
    claims = artifacts['research']['claims']
    supported = [c for c in claims if assessments.get(c['claim_id'])]
    header = 'Research complete' if status == 'completed' else 'Research partially completed'
    lines = [header + ': ' + objective]
    for source in sources:
        title = source.get('metadata', {}).get('title') or source['locator']
        lines.append('Source ' + source['source_id'] + ': ' + short(title, 100) + ' [' + source.get('content_basis', 'text') + ']')
    lines.append(str(len(supported)) + ' of ' + str(len(claims)) + ' findings source-supported (checked against the pinned source, '
                 'not independently corroborated):')
    for number, claim in enumerate(supported[:4], 1):
        location = claim['evidence_id'].split(':', 1)[0]
        cited = next((e['location'] for s in sources for e in s['evidence'] if e['evidence_id'] == claim['evidence_id']), location)
        lines.append(str(number) + '. ' + short(claim['statement'], 220) + ' [' + cited.split(':char')[0] + ']')
    limits = [x for s in sources for x in s.get('limitations', [])][:1]
    if limits:
        lines.append('Limits: ' + short(limits[0], 200))
    failures = artifacts.get('acquisition-failures') or []
    if failures:
        lines.append('Not researched: ' + '; '.join(short(f['locator'], 80) for f in failures))
    candidate = artifacts.get('memory-candidate')
    lines.append('Memory: ' + ('candidate pending review, not promoted (' + short(AuthoritativeMemoryAdapter.blocker, 90) + ')'
                               if candidate else 'no candidate'))
    lines.append('Full report: research status ' + job['id'])
    return '\n'.join(lines)


def register(ctx, config):
    """Plugin entry point. Registers the hook only when ``config['enabled'] is True``.

    ``config``: working_directory, owners [{platform, chat_id, user_id}],
    enabled, provider, attachment_roots, and optionally a ``deliver(route, text)``
    callable bound to Hermes' existing delivery for the original conversation.
    """
    adapter = HermesResearchAdapter(config['working_directory'], config.get('owners', ()),
                                    enabled=config.get('enabled') is True, deliver=config.get('deliver'),
                                    provider=config.get('provider', 'auto'),
                                    attachment_roots=config.get('attachment_roots', ()))
    if not adapter.enabled:
        log.info('Alfred Research hook prepared but disabled; nothing registered')
        return adapter
    ctx.register_hook(HOOK, adapter.on_post_gateway_admission)
    adapter.resume()
    return adapter
