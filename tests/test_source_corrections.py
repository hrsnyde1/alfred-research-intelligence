"""Targeted regressions for the two independently reproduced Phase 2 defects."""
from contextlib import contextmanager
from dataclasses import replace
from hashlib import sha256
from pathlib import Path
import errno
import os
import tempfile
import unittest
from unittest.mock import patch

import test_sources as foundation
from alfred_research.contracts import SourceIdentity
from alfred_research.sources import SourceProcessor, SourceFixture, FixtureFile


class SourceCorrectionTests(unittest.TestCase):
    setUp = foundation.SourceTests.setUp
    ctx = foundation.SourceTests.ctx
    run_source = foundation.SourceTests.run_source

    @contextmanager
    def repository(self, *, visible=True):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            blocked = root / 'blocked'
            blocked.mkdir()
            (blocked / 'SKILL.md').write_bytes(b'Synthetic omitted capability')
            files = ()
            if visible:
                (root / 'README.md').write_bytes(b'Synthetic accessible evidence')
                files = (FixtureFile('README.md', b'Synthetic accessible evidence'),)
            fixture = SourceFixture(files=files, revision=foundation.COMMIT)
            identity = foundation.source('github', fixture)
            processor = SourceProcessor(self.authority, fixture_roots={'personal': root})
            grant = processor.grant(self.ctx(role='director'), self.ctx(), identity, local_root=root)
            try:
                yield root, blocked, processor, identity, grant
            finally:
                blocked.chmod(0o700)

    @contextmanager
    def deny_subtree(self, blocked, *, error_number=errno.EACCES, stage='open'):
        # Real fwalk handles directory-open failures through onerror; some
        # runtimes propagate scandir errors directly. Exercise both paths.
        original_open, original_scandir = os.open, os.scandir
        target = blocked.stat()
        calls = []
        def denied(current, path):
            if (current.st_dev, current.st_ino) == (target.st_dev, target.st_ino):
                calls.append(path)
                raise OSError(error_number, os.strerror(error_number), str(blocked))
        def open_directory(path, flags, *args, **kwargs):
            denied(os.stat(path, dir_fd=kwargs.get('dir_fd'), follow_symlinks=False), path)
            return original_open(path, flags, *args, **kwargs)
        def scandir(path):
            denied(os.fstat(path) if isinstance(path, int) else os.stat(path), path)
            return original_scandir(path)
        with patch('os.open' if stage == 'open' else 'os.scandir',
                   side_effect=open_directory if stage == 'open' else scandir):
            yield calls
        self.assertTrue(calls, 'diagnostic must actually exercise failed subtree traversal')

    def assert_partial_inspection(self, result, identity):
        self.assertEqual(result.outcome, 'PARTIAL')
        self.assertEqual(result.submitted, identity)
        self.assertEqual(result.revision, (foundation.COMMIT,))
        self.assertEqual([f.path for f in result.files], ['README.md'])
        self.assertEqual([e.text for e in result.evidence], ['Synthetic accessible evidence'])
        self.assertTrue(any('blocked' in l and 'PermissionError' in l and 'errno=13' in l
                            for l in result.limitations), result.limitations)
        self.assertFalse(any('omitted capability' in e.text for e in result.evidence))

    def test_review_reproduction_unreadable_subtree_reports_partial(self):
        with self.repository() as (root, blocked, processor, identity, grant):
            blocked.chmod(0)
            if os.access(blocked, os.R_OK | os.X_OK):
                with self.deny_subtree(blocked):
                    result = processor.process_directory(self.ctx(), identity, grant, revision=foundation.COMMIT)
            else:
                result = processor.process_directory(self.ctx(), identity, grant, revision=foundation.COMMIT)
            self.assert_partial_inspection(result, identity)
            self.assertEqual(sorted(p.name for p in root.iterdir()), ['README.md', 'blocked'])

    def test_injected_traversal_denial_is_reported_and_repeatable(self):
        with self.repository() as (_, blocked, processor, identity, grant):
            with self.deny_subtree(blocked):
                first = processor.process_directory(self.ctx(), identity, grant, revision=foundation.COMMIT)
            with self.deny_subtree(blocked):
                second = processor.process_directory(self.ctx(), identity, grant, revision=foundation.COMMIT)
            self.assert_partial_inspection(first, identity)
            self.assertEqual(first, second)
            self.assertEqual(first.files[0].content_digest, sha256(b'Synthetic accessible evidence').hexdigest())

    def test_unreadable_only_subtree_returns_explicit_error(self):
        with self.repository(visible=False) as (_, blocked, processor, identity, grant):
            with self.deny_subtree(blocked):
                result = processor.process_directory(self.ctx(), identity, grant, revision=foundation.COMMIT)
            self.assertEqual(result.outcome, 'ERROR')
            self.assertEqual(result.evidence, ())
            self.assertEqual(result.submitted, identity)
            self.assertTrue(any('blocked' in l and 'PermissionError' in l for l in result.limitations))

    def test_other_traversal_errors_preserve_accessible_evidence(self):
        with self.repository() as (_, blocked, processor, identity, grant):
            with self.deny_subtree(blocked, error_number=errno.EIO):
                result = processor.process_directory(self.ctx(), identity, grant, revision=foundation.COMMIT)
            self.assertEqual(result.outcome, 'PARTIAL')
            self.assertTrue(result.evidence)
            self.assertTrue(any('blocked' in l and 'errno=5' in l for l in result.limitations))

    def article(self, reference=None, *, original='https://example.com/news/original', supplied=False):
        link = '' if reference is None or supplied else '<link rel="canonical" href="' + reference + '">'
        data = SourceFixture(files=(FixtureFile('page.html', (link + '<p>Real content</p>').encode()),),
                             revision='v1', metadata=(('canonical_url', reference),) if supplied else ())
        identity = replace(foundation.source('article', data), locator=original)
        grant = self.processor.grant(self.ctx(role='director'), self.ctx(), identity)
        result = self.processor.process(self.ctx(), identity, data, grant)
        self.assertEqual(result.submitted, identity)
        self.assertEqual([e.text for e in result.evidence], ['Real content'])
        self.assertEqual(result.evidence[0].file_digest, sha256(data.files[0].data).hexdigest())
        self.assertEqual(result.files[0].content_digest, result.evidence[0].file_digest)
        self.assertEqual(result.evidence[0].origin, 'fixture')
        self.assertEqual(result.snapshot_digest, data.digest)
        return result

    def test_review_reproduction_root_relative_canonical_preserves_body(self):
        result = self.article('/report', original='https://example.com/original')
        self.assertEqual(result.outcome, 'PARTIAL')
        self.assertEqual(result.canonical_identity, ('https://example.com/report',))
        self.assertFalse(any('canonical identity omitted' in l for l in result.limitations))

    def test_path_relative_canonical_urls(self):
        for reference, expected in (('report', 'https://example.com/news/report'),
                                    ('//example.com/report', 'https://example.com/report'),
                                    ('../report', 'https://example.com/report'),
                                    ('?edition=2', 'https://example.com/news/original?edition=2')):
            with self.subTest(reference=reference):
                self.assertEqual(self.article(reference).canonical_identity, (expected,))

    def test_absolute_canonical_urls_and_missing_metadata(self):
        result = self.article('https://EXAMPLE.COM/report#part')
        self.assertEqual(result.canonical_identity, ('https://example.com/report',))
        public_ip = self.article('https://[2606:4700:4700::1111]/report')
        self.assertEqual(public_ip.canonical_identity, ('https://[2606:4700:4700::1111]/report',))
        missing = self.article()
        self.assertEqual(missing.canonical_identity, ())
        self.assertFalse(any('canonical identity omitted' in l for l in missing.limitations))

    def test_invalid_canonical_metadata_preserves_body_and_omits_identity(self):
        for reference in ('http://example.com/report', 'javascript:alert(1)',
                          'https://user:pass@example.com/report', 'https://127.0.0.1/report',
                          'https://169.254.169.254/report', 'https://10.0.0.1/report',
                          'https://[::1]/report', 'https://[::ffff:127.0.0.1]/report',
                          'https://localhost/report', '//127.0.0.1/report', 'https://service.internal/report',
                          'https://example.com:444/report', 'https://[invalid/report',
                          'https://example.com/unsafe path', 'https://example.com\\@127.0.0.1/report'):
            for supplied in (False, True):
                with self.subTest(reference=reference, supplied=supplied):
                    result = self.article(reference, supplied=supplied)
                    self.assertEqual(result.outcome, 'PARTIAL')
                    self.assertEqual(result.canonical_identity, ())
                    self.assertTrue(any('canonical identity omitted' in l for l in result.limitations))

    def test_relative_canonical_requires_safe_original_page_url(self):
        for original in ('fixture://not-a-page', 'http://example.com/page',
                         'https://127.0.0.1/page', 'https://user:pass@example.com/page'):
            with self.subTest(original=original):
                result = self.article('/report', original=original)
                self.assertEqual(result.canonical_identity, ())
                self.assertTrue(any('canonical identity omitted' in l for l in result.limitations))

    def test_propagated_scandir_error_also_reports_partial(self):
        with self.repository() as (_, blocked, processor, identity, grant):
            with self.deny_subtree(blocked, stage='scandir'):
                result = processor.process_directory(self.ctx(), identity, grant, revision=foundation.COMMIT)
            self.assert_partial_inspection(result, identity)
