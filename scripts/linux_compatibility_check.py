"""Read-only interpreter/API probe; not Linux filesystem or live acceptance.

Run only on the Mac now. Later Linux execution requires separate authorization.
No files, services, credentials or networks are opened; SQLite is in-memory.
"""
import argparse
import importlib.metadata
import json
import os
import platform
import sqlite3
import sys


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--require-linux', action='store_true')
    args = parser.parse_args()
    checks = {'python_metadata_minimum_3_10': sys.version_info >= (3, 10),
              'python_recovery_gate_3_11': sys.version_info >= (3, 11),
              'posix': os.name == 'posix', 'O_NOFOLLOW': hasattr(os, 'O_NOFOLLOW'),
              'O_DIRECTORY': hasattr(os, 'O_DIRECTORY'), 'fwalk': hasattr(os, 'fwalk'),
              'open_dir_fd': os.open in os.supports_dir_fd,
              'stat_dir_fd': os.stat in os.supports_dir_fd,
              'stat_no_follow': os.stat in os.supports_follow_symlinks}
    try:
        import fcntl
        checks['flock_api'] = hasattr(fcntl, 'flock')
    except ImportError:
        checks['flock_api'] = False
    with sqlite3.connect(':memory:') as db:
        db.execute('PRAGMA foreign_keys=ON')
        checks['sqlite_foreign_keys'] = db.execute('PRAGMA foreign_keys').fetchone() == (1,)
        db.execute('CREATE TABLE sample (value INTEGER)')
        db.execute("CREATE TRIGGER immutable_sample BEFORE DELETE ON sample BEGIN SELECT RAISE(ABORT, 'blocked'); END")
        checks['sqlite_trigger_api'] = True
        try:
            db.execute('SELECT * FROM absent_table')
        except sqlite3.Error as exc:
            checks['sqlite_errorname_available'] = isinstance(getattr(exc, 'sqlite_errorname', None), str)
    try:
        backend = importlib.metadata.version('setuptools')
    except importlib.metadata.PackageNotFoundError:
        backend = 'NOT_INSTALLED (optional unless a later approved build is required)'
    if args.require_linux:
        checks['linux_host'] = platform.system() == 'Linux'
    result = {'result': 'PASS' if all(checks.values()) else 'BLOCKED', 'checks': checks,
              'python': platform.python_version(), 'implementation': platform.python_implementation(),
              'platform': platform.system(), 'sqlite': sqlite3.sqlite_version,
              'setuptools_version_observed': backend, 'runtime_dependencies': [],
              'production_authorization': 'DISABLED', 'linux_operational_acceptance': 'NOT_ESTABLISHED',
              'filesystem_durability_and_permissions': 'NOT_TESTED_BY_THIS_PROBE'}
    print(json.dumps(result, indent=2))
    return 0 if result['result'] == 'PASS' else 1


if __name__ == '__main__':
    raise SystemExit(main())
