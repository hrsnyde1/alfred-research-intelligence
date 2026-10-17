"""Adapter for the observed Memory boundary. No invented live operation names."""
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
