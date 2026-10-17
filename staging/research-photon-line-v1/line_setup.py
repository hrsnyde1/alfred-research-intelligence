#!/usr/bin/env python3
"""Owner-run (sudo) setup helper for the Research line. Standard library only.

  line_setup.py challenge   -> prints a fresh challenge to text from your phone and
                               writes /etc/alfred-research-photon/discovery-policy.json
  line_setup.py configure   -> reads the discovery report and writes policy.json and the
                               worker config (line enabled, Memory publishing OFF)

Never prints or copies credential secrets. The project ID is read from its credential
file only to bind the policy; the secret file is never opened.
"""
import grp
import hashlib
import json
import os
import secrets
import sys
from pathlib import Path

PHOTON_ETC = Path('/etc/alfred-research-photon')
LINE_ETC = Path('/etc/alfred-research-line')
STATE = Path('/var/lib/alfredresearch-photon')
GROUP = 'alfredresearchphoton'


def write(path, value):
    """root:GROUP 0640, atomic."""
    gid = grp.getgrnam(GROUP).gr_gid
    temporary = path.with_name('.' + path.name + '.tmp')
    descriptor = os.open(temporary, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o640)
    try:
        os.write(descriptor, (json.dumps(value, indent=1) + '\n').encode())
        os.fsync(descriptor)
    finally:
        os.close(descriptor)
    os.chown(temporary, 0, gid)
    os.chmod(temporary, 0o640)
    os.replace(temporary, path)
    print('wrote', path)


def project_id():
    value = (PHOTON_ETC / 'credentials' / 'research-project-id').read_text().strip()
    if not value or len(value) > 256:
        sys.exit('Research project ID credential missing or invalid')
    return value


def challenge():
    phrase = ''.join(secrets.choice('0123456789') for _ in range(16))  # digits survive iPhone autocorrect
    write(PHOTON_ETC / 'discovery-policy.json', {
        'project_id': project_id(), 'state_dir': str(STATE),
        'discovery_challenge_sha256': hashlib.sha256(phrase.encode()).hexdigest()})
    print('\nText exactly these 16 digits to the Research line within 2 minutes of starting discovery:\n\n    ' + phrase + '\n')


def configure():
    report = json.loads((STATE / 'discovery.json').read_text())
    if report.get('shared_line') or not report.get('usable'):
        sys.exit('STOP: discovery shows the line is shared or the identity is incomplete; do not enable. ' + json.dumps(
            {k: report.get(k) for k in ('shared_line', 'usable', 'space_type')}))
    binding = {'line': report['line'], 'space': report['space'], 'sender': report['sender']}
    write(PHOTON_ETC / 'policy.json', {
        'role': 'research', 'enabled': True, 'intake_enabled': False, 'outbox_enabled': True,
        'project_id': project_id(), **binding, 'profile': 'research',
        'connection_ref': 'research-connection-v1', 'state_dir': str(STATE)})
    LINE_ETC.mkdir(mode=0o750, exist_ok=True)
    os.chown(LINE_ETC, 0, grp.getgrnam(GROUP).gr_gid)
    os.chmod(LINE_ETC, 0o750)
    write(LINE_ETC / 'config.json', {
        'enabled': True, 'data_dir': '/var/lib/alfred-research-line', 'ledger_dir': str(STATE),
        'outbox_dir': str(STATE / 'outbox'), 'binding': binding, 'provider': 'extractive', 'poll_seconds': 3,
        'memory': {'enabled': False, 'url': 'http://127.0.0.1:<MEMORY_PORT>/v1/memory',
                   'token_file': '${CREDENTIALS_DIRECTORY}/memory-token', 'task_id': 'research-line',
                   'kind': 'development_lesson'}})
    print('\nBinding: line', binding['line'], '| conversation and sender recorded (not printed). Memory publishing: OFF.')


if __name__ == '__main__':
    if os.geteuid() != 0 or len(sys.argv) != 2 or sys.argv[1] not in ('challenge', 'configure'):
        sys.exit('usage: sudo python3 line_setup.py challenge|configure')
    {'challenge': challenge, 'configure': configure}[sys.argv[1]]()
