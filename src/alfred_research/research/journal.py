"""Research-only immutable checkpoints beside existing tenant task databases.

No Memory data, credentials, model service or global queue. Same-account hostile
filesystem mutation is outside the offline trust boundary, as in Phase 1.
"""
from contextlib import contextmanager
from hashlib import sha256
from pathlib import Path
import json
import os
import stat
import tempfile
import time
try:
    import fcntl
except ImportError:
    fcntl = None

from ..contracts import canonical, require
from ..tenancy import AuthorizationError
from ..budgets import EscalationRequired


class WorkflowJournal:
    def __init__(self, root, authority):
        if fcntl is None or not hasattr(os, 'O_NOFOLLOW'):
            raise AuthorizationError('safe workflow filesystem primitives unavailable')
        self.root = Path(root).resolve()
        self.authority = authority

    def _directory(self, context, task_id):
        env = self.authority.authorize(context)
        require(type(task_id) is str and 0 < len(task_id) <= 128, 'bounded task identity required')
        directory = self.root / env / 'research-workflow' / sha256(task_id.encode()).hexdigest()
        for path in (self.root, self.root / env, directory.parent, directory):
            if path.is_symlink():
                raise AuthorizationError('workflow symlink path forbidden')
        return directory

    def provision(self, director, task_id):
        self.authority.authorize(director, roles=('director',))
        directory = self._directory(director, task_id)
        directory.mkdir(parents=True, exist_ok=True, mode=0o700)

    @contextmanager
    def lock(self, context, task_id, *, deadline=None, clock=time.time):
        directory = self._directory(context, task_id)
        if not directory.is_dir():
            raise AuthorizationError('workflow not provisioned by Director')
        fd = os.open(directory / 'task.lock', os.O_RDWR | os.O_CREAT | os.O_NOFOLLOW, 0o600)
        try:
            require(stat.S_ISREG(os.fstat(fd).st_mode), 'regular workflow lock required')
            # No indefinite lock wait can bypass the task deadline. Use both the
            # supplied wall clock and a bounded monotonic acquisition window.
            remaining = 5.0 if deadline is None else min(5.0, max(0.0, deadline - clock()))
            started = time.monotonic()
            while True:
                if (deadline is not None and clock() >= deadline) or time.monotonic() - started >= remaining:
                    raise EscalationRequired('workflow lock deadline/busy limit exhausted; replay is safe')
                try:
                    fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
                    break
                except BlockingIOError:
                    time.sleep(min(0.01, remaining))
            yield
        finally:
            os.close(fd)

    def _path(self, context, task_id, key):
        require(type(key) is str and 0 < len(key) <= 512, 'bounded checkpoint key required')
        return self._directory(context, task_id) / (sha256(key.encode()).hexdigest() + '.json')

    def _envelope(self, context, task_id, path):
        self.authority.authorize(context)
        fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW)
        with os.fdopen(fd, 'rb') as stream:
            require(stat.S_ISREG(os.fstat(stream.fileno()).st_mode), 'regular checkpoint required')
            raw = stream.read(2_000_001)
        require(len(raw) <= 2_000_000, 'checkpoint oversized')
        def unique(pairs):
            result = {}
            for key, value in pairs:
                require(key not in result, 'duplicate checkpoint JSON key')
                result[key] = value
            return result
        value = json.loads(raw, object_pairs_hook=unique)
        require(set(value) == {'environment', 'task_id', 'key', 'record'} and
                value['environment'] == context.environment and value['task_id'] == task_id,
                'checkpoint scope mismatch')
        require(self._path(context, task_id, value['key']) == path, 'checkpoint key substitution')
        return value

    def load(self, context, task_id, key, cls):
        path = self._path(context, task_id, key)
        try:
            value = self._envelope(context, task_id, path)
        except FileNotFoundError:
            return None
        record = cls.from_payload(value['record'])
        require(record.environment == context.environment, 'record environment mismatch')
        if hasattr(record, 'task_id'):
            require(record.task_id == task_id, 'record task mismatch')
        return record

    def commit(self, context, task_id, key, record):
        path = self._path(context, task_id, key)
        if key == 'plan' or key.startswith(('source:', 'packet:')):
            self.authority.authorize(context, roles=('director',))
        elif key.startswith('review:'):
            self.authority.authorize(context, roles=('verifier',))
            require(record.verifier == context.principal, 'review writer mismatch')
        elif key.startswith(('intent:', 'output:')):
            self.authority.authorize(context, roles=('researcher', 'verifier'))
            principal = record.agent.principal if hasattr(record, 'agent') else record.principal
            require(principal == context.principal, 'model checkpoint writer mismatch')
            if hasattr(record, 'agent'):
                require(record.agent.role == context.role, 'model checkpoint role mismatch')
        else:
            raise AuthorizationError('unknown workflow checkpoint operation')
        require(record.environment == context.environment, 'checkpoint record scope mismatch')
        if hasattr(record, 'task_id'):
            require(record.task_id == task_id, 'checkpoint record task mismatch')
        raw = canonical({'environment': context.environment, 'task_id': task_id, 'key': key,
                         'record': record.payload()})
        require(len(raw) <= 2_000_000, 'checkpoint oversized')
        fd, staged = tempfile.mkstemp(prefix='.checkpoint-', dir=path.parent)
        try:
            with os.fdopen(fd, 'wb') as stream:
                stream.write(raw)
                stream.flush()
                os.fsync(stream.fileno())
            try:
                os.link(staged, path)
                parent = os.open(path.parent, os.O_RDONLY)
                try:
                    os.fsync(parent)
                finally:
                    os.close(parent)
            except FileExistsError:
                existing = self.load(context, task_id, key, type(record))
                require(existing == record, 'conflicting immutable checkpoint')
        finally:
            os.unlink(staged)
        return record

    def records(self, context, task_id, prefix, cls):
        directory = self._directory(context, task_id)
        result = []
        paths = list(directory.glob('*.json'))
        require(len(paths) <= 512, 'checkpoint inventory exceeds task bound')
        for path in sorted(paths):
            value = self._envelope(context, task_id, path)
            if value['key'].startswith(prefix):
                result.append(self.load(context, task_id, value['key'], cls))
        return tuple(result)
