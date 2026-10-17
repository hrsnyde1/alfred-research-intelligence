"""Owner-local orchestration, genuine source evidence, durable jobs and reports."""
import json
import fcntl
import os
from pathlib import Path
import subprocess
import sys

from .memory import AuthoritativeMemoryAdapter
from .sources import acquire, discover, sha, UnsupportedSource
from .store import JobStore
from .verify import run_stage as corroborate
from .workers import codex_available, digest, plan, research


class ResearchEngine:
    def __init__(self, root='data/research-v1'):
        self.store = JobStore(root)

    def submit(self, objective, sources=(), *, article=None, provider='auto', request_key=None):
        if not isinstance(objective, str) or not 1 <= len(objective.strip()) <= 8000:
            raise ValueError('Objective must be 1–8000 characters')
        if provider not in ('auto', 'codex', 'extractive'):
            raise ValueError('Provider must be auto, codex, or extractive')
        if len(sources) > 4 or any(not isinstance(s, str) or not 0 < len(s) <= 2048 for s in sources):
            raise ValueError('At most four bounded source URLs/files')
        if article is not None and (not isinstance(article, str) or not 1 <= len(article.encode()) <= 1_000_000):
            raise ValueError('Article must be nonempty UTF-8 text, at most 1 MB')
        request = {'objective': objective.strip(), 'sources': list(sources), 'article': article, 'provider': provider}
        return self.store.submit(request, request_key)

    def run(self, job_id):
        self.store.get(job_id)
        with (self.store.root / (job_id + '.lock')).open('a') as lock:
            try:
                fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
            except BlockingIOError:
                raise ValueError('Job already executing in another process')
            return self._run(job_id)

    def recover(self, job_id):
        """Mark a hard-killed job interrupted, only after acquiring its run lock."""
        self.store.get(job_id)
        with (self.store.root / (job_id + '.lock')).open('a') as lock:
            try:
                fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
            except BlockingIOError:
                raise ValueError('Job is still running; recovery denied')
            if self.store.get(job_id)['status'] not in ('collecting', 'planning', 'researching', 'verifying', 'synthesizing'):
                raise ValueError('Only abandoned in-progress jobs need recovery')
            self.store.update(job_id, 'interrupted', 'Abandoned process recovered; stage artifacts preserved. Submit a new job to retry.')
        return self.store.get(job_id)

    def _run(self, job_id):
        self.store.claim(job_id)
        job = self.store.get(job_id)
        request = job['request']
        directory = self.store.root / job_id
        try:
            directory.mkdir(mode=0o700)
            provider = request['provider']
            if provider == 'auto':
                provider = 'codex' if codex_available() else 'extractive'
            locators = list(request['sources'])
            if request['article'] is not None:
                article = directory / 'submitted-article.txt'
                article.write_text(request['article'], encoding='utf-8')
                article.chmod(0o600)
                locators.insert(0, str(article))
            discovery = None
            if not locators:
                try:
                    locators = discover(request['objective'])
                    discovery = {'provider': 'Wikipedia public search', 'sources': locators,
                                 'limitation': 'Limited public search; Wikipedia is a starting point, not independent corroboration.'}
                except Exception as error:
                    discovery = {'provider': 'Wikipedia public search', 'sources': [], 'error': str(error)[:300]}
                self.store.put(job_id, 'discovery', discovery)
                if not locators:
                    self.store.update(job_id, 'needs_sources', 'Public search unavailable or empty. Add source URLs/files with a new submission.')
                    return self.store.get(job_id)
            sources, failures = [], []
            for index, locator in enumerate(locators, 1):
                try:
                    source = acquire(locator, directory, index)
                    sources.append(source)
                    self.store.put(job_id, 'source-' + str(index), source)
                except Exception as error:
                    failures.append({'locator': locator, 'error': type(error).__name__ + ': ' + str(error)[:500],
                                     'unsupported': isinstance(error, UnsupportedSource),
                                     'metadata': getattr(error, 'metadata', {})})
            self.store.put(job_id, 'acquisition-failures', failures)
            if not sources:
                status = 'unsupported' if failures and all(f['unsupported'] for f in failures) else 'failed'
                self.store.update(job_id, status, 'No usable source acquired', error=json.dumps(failures))
                return self.store.get(job_id)
            self.store.update(job_id, 'planning', 'Research Director assigning source workers and separate verifier')
            assignment = plan(request['objective'], sources, provider)
            self.store.put(job_id, 'plan', assignment)
            self.store.update(job_id, 'researching', 'Executing ' + provider + ' source workers')
            drafts, claims, recommendations, limitations = [], [], [], []
            for source in sources:
                draft = research(request['objective'], source, provider)
                drafts.append(draft)
                for item in draft['claims']:
                    claims.append({**item, 'claim_id': 'C' + str(len(claims) + 1),
                                   'source_id': source['source_id'], 'researcher': draft['worker']})
                recommendations.extend(draft['recommendations'])
                limitations.extend(draft['limitations'])
            self.store.put(job_id, 'research', {'drafts': drafts, 'claims': claims})
            self.store.update(job_id, 'verifying', 'Independent worker checking pinned snapshots and claim support')
            payload = {'sources': sources, 'claims': claims, 'provider': provider, 'recommendations': recommendations}
            environment = os.environ.copy()
            environment['PYTHONPATH'] = str(Path(__file__).resolve().parents[2]) + os.pathsep + environment.get('PYTHONPATH', '')
            result = subprocess.run([sys.executable, '-m', 'alfred_research.local.workers'],
                                    input=json.dumps(payload), text=True, capture_output=True, env=environment, timeout=210)
            if result.returncode:
                raise RuntimeError('Independent verification failed; no candidate authorized. ' + result.stdout[:400])
            verification = json.loads(result.stdout)
            if verification['packet_sha256'] != digest(claims) or verification['pid'] == os.getpid():
                raise ValueError('Verification packet/process binding mismatch')
            self.store.put(job_id, 'verification', verification)
            # Fact verification: separate process discovers independent sources per claim.
            corroboration = corroborate(sources, claims, verification['assessments'], directory / 'corroboration')
            self.store.put(job_id, 'corroboration', corroboration.to_dict())
            self.store.update(job_id, 'synthesizing', 'Generating source-cited report and pending candidate')
            report = render(job_id, request, sources, claims, recommendations, limitations, failures, verification, provider, discovery)
            report_path = directory / 'report.md'
            report_path.write_text(report, encoding='utf-8')
            report_path.chmod(0o600)
            self.store.put(job_id, 'report', {'sha256': sha(report.encode()), 'path': str(report_path), 'text': report})
            candidate = AuthoritativeMemoryAdapter().prepare(job_id, request, claims, sources, verification, sha(report.encode()),
                                                             corroboration.to_dict())
            if candidate:
                self.store.put(job_id, 'memory-candidate', candidate)
                (directory / 'memory-candidate.json').write_text(json.dumps(candidate, indent=2, ensure_ascii=False), encoding='utf-8')
                (directory / 'memory-candidate.json').chmod(0o600)
            accepted = [a for a in verification['assessments'] if a['supported']]
            complete = bool(claims) and len(accepted) == len(claims) and not failures and verification['recommendations_supported'] is True \
                and not corroboration.conflicts()
            self.store.update(job_id, 'completed' if complete else 'needs_more_research',
                              'Report stored; Memory promotion blocked pending authoritative interface', report_path=str(report_path))
        except KeyboardInterrupt:
            self.store.update(job_id, 'interrupted', 'Execution interrupted; submit a new job to retry')
            raise
        except Exception as error:
            self.store.update(job_id, 'failed', 'Execution failed; completed stage artifacts preserved',
                              error=type(error).__name__ + ': ' + str(error)[:600])
        return self.store.get(job_id)


DISPLAYED_METADATA = ('title', 'author', 'channel', 'published_at', 'created_at', 'revision', 'pages',
                      'duration_seconds', 'captions', 'files_read', 'files_total', 'license')


def render(job_id, request, sources, claims, recommendations, limitations, failures, verification, provider, discovery):
    supported = {a['claim_id']: a for a in verification['assessments']}
    refs = {e['evidence_id']: (s, e) for s in sources for e in s['evidence']}
    lines = ['# Alfred Research & Intelligence', '', 'Job: `' + job_id + '`', '',
             'Objective: ' + request['objective'], '',
             'Execution: real acquisition and ' + ('configured Codex model workers' if provider == 'codex' else 'deterministic extractive workers (no LLM)') + '.', '',
             'Verification: separate worker process; source support checked against pinned byte snapshots. '
             'This establishes what the sources support, not independent real-world truth.', '', '## Findings', '']
    for claim in claims:
        check = supported[claim['claim_id']]
        lines += ['### ' + claim['claim_id'] + ' — ' + ('SOURCE-SUPPORTED' if check['supported'] else 'NOT VERIFIED'), '',
                  claim['statement'], '', 'Kind: ' + claim['kind'] + '.', '']
        bound = refs.get(claim['evidence_id'])
        if bound:
            source, item = bound
            lines += ['Evidence [' + claim['evidence_id'] + '](' + source['locator'] + ') — `' + item['location'] + '`', '',
                      '> ' + claim['quote'].replace('\n', '\n> '), '']
        lines += ['Verification: ' + check['reason'], '']
    if not claims:
        lines += ['No relevant claims established from the acquired sources.', '']
    lines += ['## Recommendations', '']
    if verification['recommendations_supported'] is True and any(a['supported'] for a in supported.values()):
        lines += ['- ' + value for value in dict.fromkeys(recommendations)]
    else:
        lines += ['Recommendations withheld: independent review did not establish adequate support.']
    lines += ['', '## Sources and acquisition', '']
    for source in sources:
        lines += ['- [' + source['source_id'] + '](' + source['locator'] + '): acquired ' + source['acquired_at'] +
                  '; SHA-256 `' + source['sha256'] + '`; ' + str(source['bytes']) + ' bytes; origin ' + source['provenance']['origin'] + '.']
        if source.get('handler'):
            details = ['handler ' + source['handler'], 'evidence basis ' + source['content_basis']]
            details += [key + ' ' + str(source['metadata'][key]) for key in DISPLAYED_METADATA if source['metadata'].get(key)]
            lines += ['  ' + '; '.join(details) + '.']
    lines += ['', '## Limitations and unresolved work', '']
    all_limits = list(limitations) + [x for s in sources for x in s['limitations']]
    all_limits += ['At most four findings per source. Model research sees up to 40 keyword-ranked excerpts / 48,000 characters per source; this is a focused analysis, not exhaustive coverage.']
    all_limits += ['No independent source corroboration or authenticated factual attestation. Memory promotion is blocked; pending candidates are not authoritative knowledge.']
    if discovery:
        all_limits.append(discovery.get('limitation', 'Public discovery attempted.'))
    all_limits += ['Acquisition failed for ' + f['locator'] + ': ' + f['error'] +
                   (' Observed metadata (not analyzed): ' + '; '.join(k + ' ' + str(v) for k, v in f['metadata'].items() if k in DISPLAYED_METADATA and v) + '.'
                    if any(f.get('metadata', {}).get(k) for k in DISPLAYED_METADATA) else '')
                   for f in failures]
    all_limits += [flag for s in sources for flag in s['flags']]
    lines += ['- ' + item for item in dict.fromkeys(all_limits)]
    return '\n'.join(lines) + '\n'
