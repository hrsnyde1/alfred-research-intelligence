"""Adapter for the observed Memory boundary. No invented live operation names."""
import http.client
import json
import os
from pathlib import Path
import stat
from urllib.parse import urlsplit

from .verify import VerificationResult
from .workers import digest

# Mirrors alfred-memory src/obsidian_candidate/routing.py (r59): approved records from the
# research-fox principal, kind task_progress, on task research-line/<topic> export to
# Alfred HQ Research/<Topic>/<uuid>.md. Fox tests/test_topics.py checks these against that file.
RESEARCH_TOPICS = ('General', 'Taxes', 'Legal', 'Business', 'Personal')
DEFAULT_RESEARCH_TOPIC = 'General'
RESEARCH_KIND = 'task_progress'
RESEARCH_TASK_PREFIX = 'research-line/'


def research_task(topic):
    if topic not in RESEARCH_TOPICS:
        raise ValueError('Unknown Research topic')
    return RESEARCH_TASK_PREFIX + topic.lower()


class MemoryBlocked(RuntimeError):
    pass


UNCORROBORATED = {'status': 'unverified', 'independent_groups': 0,
                  'note': 'No corroboration stage ran for this job; only the original source was checked.'}


def corroboration_record(row):
    """What a candidate claim carries about its corroboration. Only ``corroborated`` claims count independent publisher
    groups; original_source_only and unverified are never described as corroborated."""
    groups = len(set(row.independent_groups)) if row.status == 'corroborated' else 0
    return {'status': row.status, 'independent_groups': groups, 'note': row.rationale}


def withheld_claims(corroboration):
    """Claim ids the corroboration stage found disputed or contradicted; these never reach Memory.

    Jobs from before the corroboration stage have no artifact and keep source-support-only
    selection. A malformed artifact raises rather than silently publishing everything.
    """
    if corroboration is None:
        return set()
    return set(VerificationResult.from_dict(corroboration).conflicts())


class AuthoritativeMemoryAdapter:
    """Observed /v1/memory supports generic create/review, not Research promotion.

    Generic create may auto-approve depending on actor/kind. Consequently it is
    not an admissible substitute for submit_candidate/commit/promote. Never call
    it with unapproved Research output. Pending files are Research work products,
    not Memory records or external acceptance receipts.
    """
    observed_actions = ('capture', 'create', 'update', 'delete', 'search', 'forget', 'review', 'pending_reviews')
    blocker = ('Installed Memory has no authorized live Research candidate/promotion interface '
               'or independent attestation trust contract. No Memory write attempted.')

    def prepare(self, job_id, request, claims, sources, verification, report_sha256, corroboration=None):
        if verification.get('packet_sha256') != digest(claims):
            raise ValueError('Candidate packet differs from verified packet')
        rows = verification.get('assessments', [])
        if len(rows) != len(claims) or {r['claim_id'] for r in rows} != {c['claim_id'] for c in claims}:
            raise ValueError('Incomplete independent verification')
        if corroboration is None:
            statuses = {}
        else:
            result = VerificationResult.from_dict(corroboration)
            if result.packet_sha256 != digest(claims) or {c.claim_id for c in result.claims} != {c['claim_id'] for c in claims}:
                raise ValueError('Corroboration packet differs from verified packet')
            statuses = {c.claim_id: corroboration_record(c) for c in result.claims}
        approved = {r['claim_id'] for r in rows if r['supported'] is True} - withheld_claims(corroboration)
        eligible = [{**c, 'corroboration': statuses.get(c['claim_id'], UNCORROBORATED)}
                    for c in claims if c['claim_id'] in approved and c['kind'] == 'source_statement']
        if not eligible:
            return None
        body = {'schema': 'research.local.pending-memory/1', 'job_id': job_id, 'environment': 'personal',
                'request': request, 'claims': eligible, 'sources': sources,
                'verification': verification, 'report_sha256': report_sha256,
                'status': 'PENDING_OWNER_REVIEW', 'promotion_status': 'BLOCKED',
                'memory_record_id': None, 'memory_receipt': None,
                'authority': 'Research work product only; not authoritative Memory',
                'verification_scope': verification['scope'], 'blocker': self.blocker}
        return {**body, 'candidate_sha256': digest(body)}

    def submit(self, candidate):
        self._validate(candidate)
        raise MemoryBlocked(self.blocker)

    def promote(self, candidate):
        self._validate(candidate)
        raise MemoryBlocked(self.blocker)

    def _validate(self, candidate):
        if not isinstance(candidate, dict) or candidate.get('schema') != 'research.local.pending-memory/1':
            raise ValueError('Pending Research candidate required')
        body = {k: v for k, v in candidate.items() if k != 'candidate_sha256'}
        if candidate.get('candidate_sha256') != digest(body):
            raise ValueError('Candidate content changed after preparation')


def credential_metadata_allowed(info, service_uid):
    """Same rule as the Research connector: systemd LoadCredential files are root-owned 0440;
    otherwise only 0400/0600 owned by root or the service UID."""
    mode = stat.S_IMODE(info.st_mode)
    return info.st_uid in (0, service_uid) and (mode in (0o400, 0o600) or (info.st_uid == 0 and mode == 0o440))


def corroboration_line(claim):
    record = claim.get('corroboration') or UNCORROBORATED   # candidates prepared before corroboration was recorded
    if record['status'] == 'corroborated' and record.get('independent_groups', 0) > 0:
        return 'independently corroborated by ' + str(record['independent_groups']) + ' publisher group(s)'
    return 'not independently corroborated (' + record['status'].replace('_', ' ') + ')'


class MemoryServicePublisher:
    """Publish verified findings to the installed Alfred Memory service (``POST /v1/memory``).

    Uses Memory's existing ``create`` action with a dedicated Research agent
    principal token read from a protected file; the token is never logged or
    stored. One ``task_progress`` record per independently verified source
    statement, on the job's topic task ``research-line/<topic>``. Memory's create
    response is not trusted for the review state (it reports ``approved`` for any
    duplicate, even when the earlier row is pending), so each record is approved
    only if the agent's own ``search``, which returns approved rows only, finds it.
    """
    kind = RESEARCH_KIND

    def __init__(self, url, token_file, *, timeout=10):
        parsed = urlsplit(url)
        if parsed.scheme != 'http' or parsed.hostname != '127.0.0.1' or parsed.path != '/v1/memory' or \
                not parsed.port or parsed.query or parsed.username:
            raise ValueError('Memory URL must be http://127.0.0.1:PORT/v1/memory (loopback only)')
        self.port, self.token_file, self.timeout = parsed.port, Path(token_file), timeout

    def token(self):
        info = os.stat(self.token_file, follow_symlinks=False)
        if not stat.S_ISREG(info.st_mode) or not credential_metadata_allowed(info, os.getuid()) or info.st_size > 4096:
            raise MemoryBlocked('Memory credential file must be a private regular file')
        value = self.token_file.read_text().strip()
        if len(value) < 32:
            raise MemoryBlocked('Memory credential unavailable')
        return value

    def call(self, token, body):
        connection = http.client.HTTPConnection('127.0.0.1', self.port, timeout=self.timeout)
        try:
            data = json.dumps(body).encode()
            connection.request('POST', '/v1/memory', body=data, headers={
                'Content-Type': 'application/json', 'Authorization': 'Bearer ' + token})
            response = connection.getresponse()
            payload = response.read(65536)
        finally:
            connection.close()
        try:
            result = json.loads(payload)
        except ValueError:
            result = {}
        if response.status != 200:
            error = result.get('error', '') if isinstance(result, dict) else ''
            raise MemoryBlocked('Memory refused the request (HTTP ' + str(response.status) + ' ' + str(error) + ')')
        return result

    def approved(self, token, task_id, memory_id, reference):
        """True only if Memory shows this row to the agent, which it does for approved rows alone."""
        rows = self.call(token, {'action': 'search', 'task_id': task_id, 'query': reference, 'limit': 4})
        return isinstance(rows, list) and any(isinstance(r, dict) and r.get('id') == memory_id for r in rows)

    def publish(self, job_id, candidate, topic=DEFAULT_RESEARCH_TOPIC, exclude=()):
        """``exclude``: claim ids withheld at publish time (disputed or contradicted by corroboration)."""
        AuthoritativeMemoryAdapter()._validate(candidate)
        task_id = research_task(topic)
        sources, exclude = {s['source_id']: s for s in candidate['sources']}, set(exclude)
        claims = [c for c in candidate['claims'] if c['claim_id'] not in exclude]
        withheld = sorted(c['claim_id'] for c in candidate['claims'] if c['claim_id'] in exclude)
        if not claims:
            return {'status': 'nothing_to_publish', 'kind': self.kind, 'topic': topic, 'task_id': task_id, 'receipts': [],
                    'withheld': withheld, 'candidate_sha256': candidate['candidate_sha256'],
                    'detail': 'every finding was disputed or contradicted by independent sources; none sent to Memory'}
        token, receipts = self.token(), []
        for claim in claims:
            source = sources.get(claim['source_id'], {})
            location = next((e['location'] for e in source.get('evidence', []) if e['evidence_id'] == claim['evidence_id']),
                            claim['evidence_id']).split(':char')[0]
            title = (source.get('metadata') or {}).get('title')
            reference = 'Research job ' + job_id + ', claim ' + claim['claim_id'] + '.'
            content = '\n'.join(filter(None, [
                'Research finding: ' + claim['statement'],
                'Source: ' + ((title + ' - ') if title else '') + source.get('locator', '?') + ' (' + location + '), retrieved ' +
                str(source.get('acquired_at', '?')) + '.',
                'Verification: exact quotation checked against the saved source; ' + corroboration_line(claim) + '.',
                reference]))[:4096]
            result = self.call(token, {'action': 'create', 'task_id': task_id, 'kind': self.kind, 'content': content,
                                       'source_message_id': 'research:' + job_id + ':' + claim['claim_id']})
            if not isinstance(result, dict) or result.get('saved') is not True or not isinstance(result.get('id'), str):
                raise MemoryBlocked('Memory did not confirm the record was saved')
            state = 'approved' if self.approved(token, task_id, result['id'], reference) else 'not_approved'
            receipts.append({'claim_id': claim['claim_id'], 'memory_id': result['id'], 'review_state': state,
                             'reported_state': result.get('review_state'), 'duplicate': bool(result.get('duplicate'))})
        states = {r['review_state'] for r in receipts}
        status = 'published' if receipts and states == {'approved'} else ('pending_review' if receipts else 'nothing_to_publish')
        return {'status': status, 'kind': self.kind, 'topic': topic, 'task_id': task_id, 'receipts': receipts,
                'withheld': withheld, 'candidate_sha256': candidate['candidate_sha256'],
                'detail': 'review_state read back with search after create; Memory create responses are not trusted for it.'}
