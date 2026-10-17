"""Adapter for the observed Memory boundary. No invented live operation names."""
import http.client
import json
import os
from pathlib import Path
import stat
from urllib.parse import urlsplit

from .workers import digest


class MemoryBlocked(RuntimeError):
    pass


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

    def prepare(self, job_id, request, claims, sources, verification, report_sha256):
        if verification.get('packet_sha256') != digest(claims):
            raise ValueError('Candidate packet differs from verified packet')
        rows = verification.get('assessments', [])
        if len(rows) != len(claims) or {r['claim_id'] for r in rows} != {c['claim_id'] for c in claims}:
            raise ValueError('Incomplete independent verification')
        approved = {r['claim_id'] for r in rows if r['supported'] is True}
        eligible = [c for c in claims if c['claim_id'] in approved and c['kind'] == 'source_statement']
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


class MemoryServicePublisher:
    """Publish verified findings to the installed Alfred Memory service (``POST /v1/memory``).

    Uses Memory's existing ``create`` action with a dedicated Research agent
    principal token read from a protected file; the token is never logged or
    stored. One record per independently verified source statement. The
    resulting review state is whatever Memory reports: auto-approval depends on
    Memory's own rules for the configured kind, and nothing is called approved
    unless Memory's response says so.
    """
    def __init__(self, url, token_file, task_id, kind, *, timeout=10):
        parsed = urlsplit(url)
        if parsed.scheme != 'http' or parsed.hostname != '127.0.0.1' or parsed.path != '/v1/memory' or \
                not parsed.port or parsed.query or parsed.username:
            raise ValueError('Memory URL must be http://127.0.0.1:PORT/v1/memory (loopback only)')
        if not isinstance(task_id, str) or not task_id or not isinstance(kind, str) or not kind:
            raise ValueError('Memory task_id and kind required')
        self.port, self.token_file, self.task_id, self.kind, self.timeout = parsed.port, Path(token_file), task_id, kind, timeout

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
            raise MemoryBlocked('Memory refused the record (HTTP ' + str(response.status) + ' ' +
                                str(result.get('error', '')) + ')')
        return result

    def publish(self, job_id, candidate):
        AuthoritativeMemoryAdapter()._validate(candidate)
        sources = {s['source_id']: s for s in candidate['sources']}
        token, receipts = self.token(), []
        for claim in candidate['claims']:
            source = sources.get(claim['source_id'], {})
            location = next((e['location'] for e in source.get('evidence', []) if e['evidence_id'] == claim['evidence_id']),
                            claim['evidence_id']).split(':char')[0]
            title = (source.get('metadata') or {}).get('title')
            content = '\n'.join(filter(None, [
                'Research finding: ' + claim['statement'],
                'Source: ' + ((title + ' - ') if title else '') + source.get('locator', '?') + ' (' + location + '), retrieved ' +
                str(source.get('acquired_at', '?')) + '.',
                'Verification: exact quotation checked against the saved source; not independently corroborated.',
                'Research job ' + job_id + ', claim ' + claim['claim_id'] + '.']))[:4096]
            result = self.call(token, {'action': 'create', 'task_id': self.task_id, 'kind': self.kind, 'content': content,
                                       'source_message_id': 'research:' + job_id + ':' + claim['claim_id']})
            if result.get('saved') is not True or not isinstance(result.get('id'), str):
                raise MemoryBlocked('Memory did not confirm the record was saved')
            receipts.append({'claim_id': claim['claim_id'], 'memory_id': result['id'],
                             'review_state': result.get('review_state'), 'duplicate': bool(result.get('duplicate'))})
        states = {r['review_state'] for r in receipts}
        status = 'published' if receipts and states == {'approved'} else ('pending_review' if receipts else 'nothing_to_publish')
        return {'status': status, 'kind': self.kind, 'task_id': self.task_id, 'receipts': receipts,
                'candidate_sha256': candidate['candidate_sha256'],
                'detail': 'Memory create responses; review_state as reported by Memory.'}
