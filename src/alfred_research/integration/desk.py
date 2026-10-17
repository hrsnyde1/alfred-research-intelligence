"""Shared Research front desk: intake, background execution, Memory publication, delivery.

Front ends (the dedicated Research line, a future Personal Alfred hook) only
decide *who* is asking and *where* replies go; this class owns everything else
on top of the existing persistent ResearchEngine and its job store.
"""
from datetime import datetime, timedelta, timezone
import logging
import threading

from ..local.engine import ResearchEngine

log = logging.getLogger(__name__)
ROUTE_ARTIFACT = 'hermes-route'           # name kept for stored-job compatibility
DELIVERY_ARTIFACT = 'hermes-delivery'
PUBLICATION_ARTIFACT = 'memory-publication'
IN_PROGRESS = ('collecting', 'planning', 'researching', 'verifying', 'synthesizing')
OWNER_STATUS = {'queued': 'accepted', 'collecting': 'running', 'planning': 'running', 'researching': 'running',
                'verifying': 'running', 'synthesizing': 'running', 'completed': 'completed', 'failed': 'failed',
                'needs_more_research': 'partially completed', 'unsupported': 'unsupported source',
                'needs_sources': 'needs sources', 'interrupted': 'interrupted'}
RETRYABLE = ('failed', 'unsupported', 'interrupted', 'needs_sources')
DEDUPE_WINDOW = timedelta(hours=24)


def short(text, limit):
    text = ' '.join(str(text).split())
    return text if len(text) <= limit else text[:limit - 1].rstrip() + '…'


class ResearchDesk:
    def __init__(self, working_directory, *, deliver=None, provider='auto', runner='thread', max_concurrent=2,
                 clock=None, publisher=None, publish_extractive=False):
        if runner not in ('thread', 'inline'):
            raise ValueError('runner must be thread or inline')
        self.engine = ResearchEngine(working_directory)
        self.deliver, self.provider, self.runner, self.publisher = deliver, provider, runner, publisher
        # Owner decision 2026-10-16: no-model (extractive) quotes are not auto-published to Memory.
        self.publish_extractive = publish_extractive is True
        self.slots = threading.BoundedSemaphore(max_concurrent)
        self.clock = clock or (lambda: datetime.now(timezone.utc))

    # ------------------------------------------------------------ intake

    def accept(self, intent, route, key):
        """Create (or replay) the job for one inbound message; returns the acknowledgement text."""
        request = {'objective': intent.objective, 'sources': list(intent.sources), 'article': None, 'provider': self.provider}
        replay = self.engine.store.by_request_key(key)
        if replay is None and not intent.rerun:
            since = (self.clock() - DEDUPE_WINDOW).strftime('%Y-%m-%dT%H:%M:%SZ')
            prior = self.engine.store.find_recent(request, since)
            if prior and self.engine.store.get(prior)['status'] not in RETRYABLE:
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
            job = self.publish(job)
            self.notify(job)

    def publish(self, job):
        """Send verified findings to Alfred Memory once; the receipt is stored with the job."""
        if self.publisher is None or PUBLICATION_ARTIFACT in job['artifacts'] or 'memory-candidate' not in job['artifacts']:
            return job
        if job['artifacts'].get('plan', {}).get('mode') != 'codex' and not self.publish_extractive:
            record = {'status': 'skipped', 'receipts': [],
                      'detail': 'findings came from the no-model extractive worker; configure a model provider to publish'}
            self.engine.store.put(job['id'], PUBLICATION_ARTIFACT, record)
            return self.engine.store.get(job['id'])
        try:
            topic = (job['artifacts'].get(ROUTE_ARTIFACT) or {}).get('topic', 'General')
            record = self.publisher.publish(job['id'], job['artifacts']['memory-candidate'], topic=topic)
        except Exception as error:
            log.exception('Memory publication failed for %s', job['id'])
            record = {'status': 'failed', 'detail': short(error, 300), 'receipts': []}
        self.engine.store.put(job['id'], PUBLICATION_ARTIFACT, record)
        return self.engine.store.get(job['id'])

    def notify(self, job):
        if DELIVERY_ARTIFACT in job['artifacts']:
            return
        route = job['artifacts'].get(ROUTE_ARTIFACT)
        record = {'status': 'not_configured', 'detail': 'No delivery function; result retrievable by status command.'}
        if route and self.deliver:
            try:
                self.deliver(route, final_message(job))
                record = {'status': 'handed_to_host', 'detail': 'deliver() returned; not proof of recipient delivery.'}
            except Exception as error:
                log.exception('Research result delivery failed for %s', job['id'])
                record = {'status': 'failed', 'detail': short(error, 300)}
        self.engine.store.put(job['id'], DELIVERY_ARTIFACT, record)

    def resume(self):
        """After a restart: run accepted jobs, retry abandoned ones once, finish publication and delivery."""
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
                self.notify(self.publish(job))
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


def memory_line(job):
    publication = job['artifacts'].get(PUBLICATION_ARTIFACT)
    candidate = job['artifacts'].get('memory-candidate')
    if publication:
        receipts = publication.get('receipts') or []
        approved = sum(1 for r in receipts if r.get('review_state') == 'approved')
        pending = len(receipts) - approved
        topic = (' under ' + publication['topic']) if publication.get('topic') else ''
        if publication['status'] == 'published':
            return 'Memory: ' + str(approved) + ' finding(s) saved to Alfred\'s Memory' + topic + ' as approved; Alfred can now use them.'
        if publication['status'] == 'pending_review':
            return 'Memory: ' + str(approved) + ' approved' + topic + ', ' + str(pending) + ' not yet approved in Alfred\'s Memory.'
        if publication['status'] == 'skipped':
            return 'Memory: not published (' + short(publication.get('detail', ''), 120) + '); kept as a local candidate.'
        return 'Memory: not saved (' + short(publication.get('detail', 'error'), 120) + '); findings kept as a local candidate.'
    if candidate:
        return 'Memory: candidate kept locally, not published to Alfred\'s Memory.'
    return 'Memory: nothing to save (no source-supported findings).'


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
    lines.append(memory_line(job))
    lines.append('Full report: research status ' + job['id'])
    return '\n'.join(lines)
