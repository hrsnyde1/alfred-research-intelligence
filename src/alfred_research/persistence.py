"""Schema v2: validate existing files without DDL; never migrate implicitly."""
from contextlib import closing
from functools import lru_cache
from hashlib import sha256
import json
import os
from pathlib import Path
import sqlite3
import tempfile
from urllib.parse import quote

from .registration import OfflineRegistrationAuthority
from .tenancy import AuthorizationError

SCHEMA_VERSION = 2


class PersistenceError(RuntimeError):
    """An explicit storage/open/SQLite failure, with its original cause attached."""


class UnsupportedSchemaError(PersistenceError):
    """Compatibility rejection; opening layer reports any recovery permission."""


class RecoveryRequiredError(PersistenceError):
    """Hot database identity is unestablished; no recovery write was attempted."""
    recovery_attempted = False


class RecoveryValidationError(PersistenceError):
    """Writable SQLite recovery was permitted; database may already have changed."""
    recovery_attempted = True


STATEMENTS = (
    'CREATE TABLE metadata (version INTEGER PRIMARY KEY, environment TEXT NOT NULL)',
    '''CREATE TABLE tasks (id TEXT PRIMARY KEY, request_id TEXT UNIQUE NOT NULL,
        request_hash TEXT NOT NULL, body TEXT NOT NULL)''',
    'CREATE TABLE audit (seq INTEGER PRIMARY KEY AUTOINCREMENT, body TEXT NOT NULL)',
    'CREATE TABLE outbox (id TEXT PRIMARY KEY, body TEXT NOT NULL)',
    '''CREATE TABLE packets (
        task_id TEXT NOT NULL, packet_version INTEGER NOT NULL,
        packet_id TEXT NOT NULL, environment TEXT NOT NULL,
        digest TEXT NOT NULL UNIQUE, body TEXT NOT NULL,
        PRIMARY KEY (task_id, packet_version),
        UNIQUE (task_id, packet_version, digest, environment),
        FOREIGN KEY (task_id) REFERENCES tasks(id))''',
    '''CREATE TABLE packet_heads (
        task_id TEXT PRIMARY KEY, packet_version INTEGER NOT NULL,
        FOREIGN KEY (task_id, packet_version) REFERENCES packets(task_id, packet_version))''',
    '''CREATE TABLE decisions (
        id TEXT PRIMARY KEY, task_id TEXT NOT NULL, packet_version INTEGER NOT NULL,
        digest TEXT NOT NULL, environment TEXT NOT NULL, body TEXT NOT NULL,
        FOREIGN KEY (task_id, packet_version, digest, environment)
            REFERENCES packets(task_id, packet_version, digest, environment))''',
    'CREATE TABLE budget_policy (id INTEGER PRIMARY KEY, ceiling INTEGER NOT NULL)',
    'CREATE TABLE reservations (id TEXT PRIMARY KEY, body TEXT NOT NULL)',
    '''CREATE TABLE retry_operations (
        id TEXT PRIMARY KEY, task_id TEXT NOT NULL, environment TEXT NOT NULL,
        principal TEXT NOT NULL, body TEXT NOT NULL,
        FOREIGN KEY (task_id) REFERENCES tasks(id))''',
) + tuple(
    f"CREATE TRIGGER immutable_{table}_{action.lower()} BEFORE {action} ON {table} "
    f"BEGIN SELECT RAISE(ABORT, 'immutable {table}'); END"
    for table in ('packets', 'decisions', 'retry_operations') for action in ('UPDATE', 'DELETE')
)


def _manifest(db):
    return db.execute('SELECT type,name,tbl_name,sql FROM sqlite_master ORDER BY type,name').fetchall()


@lru_cache(maxsize=1)
def _expected_manifest():
    with closing(sqlite3.connect(':memory:')) as db:
        for statement in STATEMENTS:
            db.execute(statement)
        return _manifest(db)


def validate_schema(db, tenant):
    """SELECT-only validation. Also binds the database file to its tenant."""
    tables = {row[0] for row in db.execute("SELECT name FROM sqlite_master WHERE type='table'")}
    if 'metadata' not in tables:
        raise UnsupportedSchemaError('missing persistence metadata; explicit migration required')
    columns = [row[1] for row in db.execute('PRAGMA table_info(metadata)')]
    if columns != ['version', 'environment']:
        raise UnsupportedSchemaError('unsupported metadata layout; explicit migration required')
    if db.execute('SELECT version,environment FROM metadata').fetchall() != [(SCHEMA_VERSION, tenant)]:
        raise UnsupportedSchemaError('unsupported persistence version or database environment')
    if _manifest(db) != _expected_manifest():
        raise UnsupportedSchemaError('unsupported persistence structure; no automatic repair')


def _initialize_new(path, tenant):
    """Publish a fully initialized file without replacing a concurrent winner.

    Private staging is in the same directory; only new schemas are written here.
    Existing files (including zero-byte files) are never treated as new databases.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, staged = tempfile.mkstemp(prefix='.research-init-', suffix='.sqlite3', dir=path.parent)
    os.close(fd)
    try:
        with closing(sqlite3.connect(staged)) as db:
            with db:
                db.execute('PRAGMA synchronous=FULL')
                db.execute('BEGIN IMMEDIATE')
                for statement in STATEMENTS:
                    db.execute(statement)
                db.execute('INSERT INTO metadata VALUES (?,?)', (SCHEMA_VERSION, tenant))
        try:
            os.link(staged, path)
            return True
        except FileExistsError:
            return False  # Never claim another process's file as newly provisioned.
    finally:
        os.unlink(staged)


def _identity(path, tenant):
    stat = path.stat()
    if not stat.st_ino:
        raise RecoveryRequiredError('stable filesystem identity unavailable; recovery refused')
    return {'path': str(path.resolve()), 'environment': tenant, 'schema_version': SCHEMA_VERSION,
            'device': stat.st_dev, 'inode': stat.st_ino,
            'manifest_digest': sha256(json.dumps(_expected_manifest(), sort_keys=True).encode()).hexdigest()}


def _receipt_path(path):
    return path.with_name(path.name + '.identity.json')


def _require_identity(path, tenant, registration_authority, context):
    """Receipt is untrusted: require a live, independently injected ledger match."""
    try:
        with _receipt_path(path).open('r', encoding='utf-8') as receipt:
            raw = receipt.read(4097)
        value = json.loads(raw)
        if len(raw) > 4096 or raw != json.dumps(value, sort_keys=True):
            raise ValueError('noncanonical or ambiguous receipt')
        registration_authority.verify(context, _identity(path, tenant), value)
    except (OSError, ValueError, AuthorizationError) as exc:
        raise RecoveryRequiredError('missing, untrusted, edited or revoked registration; recovery refused') from exc


def _publish_receipt(path, record, *, replace=False):
    fd, staged = tempfile.mkstemp(prefix='.research-identity-', dir=path.parent)
    try:
        with os.fdopen(fd, 'w', encoding='utf-8') as receipt:
            json.dump(record, receipt, sort_keys=True)
            receipt.flush()
            os.fsync(receipt.fileno())
        if replace:
            os.replace(staged, _receipt_path(path))
        else:
            try:
                os.link(staged, _receipt_path(path))
            except FileExistsError:
                pass
    finally:
        if os.path.exists(staged):
            os.unlink(staged)


def _trust_provider(registration_authority, production):
    if production or type(registration_authority) is not OfflineRegistrationAuthority:
        raise RecoveryRequiredError('production registration is disabled; explicit offline test authority required')


def register_database(path, tenant, *, registration_authority=None, context=None,
                      replace=False, production=False):
    """Explicit director-authorized registration/replacement of an existing clean file.

    Schema validation must succeed read-only. This operation never recovers hot
    databases, migrates schemas, or initializes arbitrary existing files.
    """
    _trust_provider(registration_authority, production)
    path = Path(path).absolute()
    with registration_authority.guard(context, path, tenant):
        # Check the director grant before schema reads or any registration change.
        registration_authority._scope(context, path, tenant, roles=('director',))
        uri = 'file:' + quote(path.as_posix(), safe='/:')
        with closing(sqlite3.connect(uri + '?mode=ro', uri=True, timeout=5)) as probe:
            validate_schema(probe, tenant)
        record = registration_authority.register(context, _identity(path, tenant), replace=replace)
        _publish_receipt(path, record, replace=replace)
        _require_identity(path, tenant, registration_authority, context)
        return record['registration_id']


def open_database(path, tenant, *, registration_authority=None, context=None, production=False):
    """Use independently authorized registration before any writable recovery.

    Only authorized provisioning of a genuinely new file registers implicitly.
    Existing files need prior ledger registration or explicit register_database.
    """
    _trust_provider(registration_authority, production)
    path = Path(path).absolute()
    with registration_authority.guard(context, path, tenant):
        created = False
        if not path.exists():
            registration_authority._scope(context, path, tenant, roles=('director',))
            created = _initialize_new(path, tenant)
        uri = 'file:' + quote(path.as_posix(), safe='/:')
        probe = sqlite3.connect(uri + '?mode=ro', uri=True, timeout=5)
        try:
            try:
                validate_schema(probe, tenant)
            except sqlite3.Error as exc:
                if getattr(exc, 'sqlite_errorname', None) != 'SQLITE_READONLY_ROLLBACK':
                    raise
        finally:
            probe.close()
        if created:
            record = registration_authority._register_new(context, _identity(path, tenant))
            _publish_receipt(path, record)
        _require_identity(path, tenant, registration_authority, context)
        return _open_registered(uri, path, tenant, registration_authority, context)


def _open_registered(uri, path, tenant, registration_authority, context):
    db = None
    try:
        db = sqlite3.connect(uri + '?mode=rw', uri=True, timeout=5)
        db.execute('PRAGMA foreign_keys=ON')
        db.execute('PRAGMA synchronous=FULL')
        # SQLite owns journal recovery. Validate while holding the write lock,
        # including when a writer crashed between preflight and this open.
        db.execute('BEGIN IMMEDIATE')
        validate_schema(db, tenant)
        _require_identity(path, tenant, registration_authority, context)
        db.commit()
        return db
    except BaseException as exc:
        if db is not None:
            db.rollback()
            db.close()
        if isinstance(exc, (sqlite3.Error, PersistenceError, OSError)):
            raise RecoveryValidationError(
                'SQLite recovery was permitted; database may have changed; '
                'validation/open failed and no application operation was authorized') from exc
        raise
