"""IN-MEMORY TEST AUTHORITY ONLY. Not a production credential/registry service.

Trusted bootstrap injects this object independently of DB/receipt contents.
Snapshots are explicit test-harness trust inputs, never read from those files.
"""
from contextlib import contextmanager
from copy import deepcopy
from pathlib import Path
from threading import RLock
from uuid import uuid4

from .contracts import ENVIRONMENTS, require
from .tenancy import AuthorizationError


class OfflineRegistrationAuthority:
    test_only = True

    def __init__(self, identity_authority, root, *, test_only=False):
        if test_only is not True:
            raise AuthorizationError('offline registration authority requires explicit test_only=True')
        self._identity_authority = identity_authority
        self._root = Path(root).resolve()
        self._authority_id = str(uuid4())
        self._epochs = {env: str(uuid4()) for env in ENVIRONMENTS}
        self._records = {}
        self._active = {}
        self._lock = RLock()

    def _scope(self, context, path, tenant, *, roles=('director', 'researcher', 'verifier')):
        self._identity_authority.authorize(context, tenant, roles)
        expected = self._root / tenant / 'research.sqlite3'
        if Path(path).resolve() != expected or Path(path).is_symlink():
            raise AuthorizationError('database path is outside the registration authority scope')

    @contextmanager
    def guard(self, context, path, tenant):
        with self._lock:
            self._scope(context, path, tenant)
            yield

    def _record(self, context, identity, *, replace=False):
        key = (identity['environment'], identity['path'])
        if key in self._active and not replace:
            raise AuthorizationError('registration exists; explicit authorized replacement required')
        record = {'receipt_version': 2, 'authority_id': self._authority_id,
                  'epoch': self._epochs[identity['environment']], 'registration_id': str(uuid4()),
                  'registered_by': context.principal, 'identity': deepcopy(identity)}
        self._records[record['registration_id']] = deepcopy(record)
        self._active[key] = record['registration_id']
        return record

    def register(self, context, identity, *, replace=False):
        """Called by the validated, director-only persistence registration operation."""
        with self._lock:
            self._scope(context, identity['path'], identity['environment'], roles=('director',))
            require(type(replace) is bool, 'boolean replacement required')
            return self._record(context, identity, replace=replace)

    def _register_new(self, context, identity):
        """Trusted persistence calls this only for a file it has just initialized."""
        with self._lock:
            self._scope(context, identity['path'], identity['environment'], roles=('director',))
            return self._record(context, identity)

    def verify(self, context, identity, receipt):
        with self._lock:
            self._scope(context, identity['path'], identity['environment'])
            if type(receipt) is not dict:
                raise AuthorizationError('registration receipt required')
            registration_id = receipt.get('registration_id')
            key = (identity['environment'], identity['path'])
            if (type(registration_id) is not str or
                    self._active.get(key) != registration_id or
                    self._records.get(registration_id) != receipt or
                    receipt.get('identity') != identity or
                    receipt.get('authority_id') != self._authority_id or
                    receipt.get('epoch') != self._epochs[identity['environment']]):
                raise AuthorizationError('unknown, edited, substituted or revoked registration')

    def revoke(self, context, registration_id):
        with self._lock:
            self._identity_authority.authorize(context, roles=('director',))
            record = self._records.get(registration_id)
            if record is None or record['identity']['environment'] != context.environment:
                raise AuthorizationError('registration not available in authorized environment')
            key = (context.environment, record['identity']['path'])
            if self._active.get(key) == registration_id:
                del self._active[key]

    def rotate(self, context):
        """Invalidate all registrations in this director's environment only."""
        with self._lock:
            self._identity_authority.authorize(context, roles=('director',))
            env = context.environment
            self._epochs[env] = str(uuid4())
            self._active = {k: v for k, v in self._active.items() if k[0] != env}

    def snapshot_for_tests(self):
        """Trusted harness export for child-process tests; not a backup/import API."""
        with self._lock:
            return deepcopy({'test_snapshot_version': 1, 'root': str(self._root),
                             'authority_id': self._authority_id, 'epochs': self._epochs,
                             'records': self._records,
                             'active': [[*key, value] for key, value in self._active.items()]})

    @classmethod
    def from_test_snapshot(cls, identity_authority, root, snapshot, *, test_only=False):
        """INJECT ONLY trusted current harness state, never DB/receipt/user input.

        Production restoration and anti-rollback are deliberately not implemented.
        """
        instance = cls(identity_authority, root, test_only=test_only)
        require(type(snapshot) is dict and snapshot.get('test_snapshot_version') == 1 and
                snapshot.get('root') == str(instance._root), 'invalid trusted test snapshot')
        instance._authority_id = snapshot['authority_id']
        instance._epochs = deepcopy(snapshot['epochs'])
        instance._records = deepcopy(snapshot['records'])
        instance._active = {(env, path): value for env, path, value in snapshot['active']}
        return instance
