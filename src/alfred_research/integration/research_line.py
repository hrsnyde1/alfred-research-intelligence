"""Dedicated Research Photon line worker: text a link, get cited research, grow Alfred's Memory.

Runs beside the standalone Research Photon connector (same service account).
The connector authenticates the line, accepts only the bound conversation and
sender, and stores each inbound text durably as a ``research.connector.pending/1``
record. This worker polls those records, re-checks the binding, runs the shared
``ResearchDesk`` (intake, verification, Memory publication) and writes replies to
an outbox directory that the connector sends exactly once. No Hermes, no
Personal Alfred conversation, no credentials beyond a Memory token file.
"""
import argparse
import hashlib
import json
import logging
import os
from pathlib import Path
import re
import sys
import time

from ..local.memory import DEFAULT_RESEARCH_TOPIC, RESEARCH_KIND, RESEARCH_TOPICS, MemoryServicePublisher
from .desk import ResearchDesk, short
from .message_intake import detect

log = logging.getLogger(__name__)
PENDING_SCHEMA = 'research.connector.pending/1'
OUTBOX_SCHEMA = 'research.outbox/1'
STATUS = re.compile(r'^\s*(?:research\s+)?(?:status|jobs)(?:\s+(research-[0-9a-f]{32}))?\s*\??\s*$', re.I)
HELP = re.compile(r'^\s*(help|\?|commands)\s*$', re.I)
HELP_TEXT = ('Send me a link (article, PDF, DOCX, GitHub repo, YouTube video with captions, Instagram post) or a '
             'question of at least three words and I\'ll research it and reply with cited findings{memory}. '
             '"status" lists recent jobs; "status <job>" shows one; add "again" to redo a link.')
MEMORY_ON = ' and save verified findings to Alfred\'s Memory'
MEMORY_OFF = ' (findings are kept on the Research server; Memory publishing is off)'
KEY = re.compile(r'^[0-9a-f]{64}$')


def private_write(path, payload):
    """Atomic, exclusive, owner-only JSON write. Returns False if it already exists."""
    if path.exists():
        return False
    temporary = path.with_name(path.name + '.' + os.urandom(6).hex() + '.tmp')
    descriptor = os.open(temporary, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    try:
        os.write(descriptor, json.dumps(payload, ensure_ascii=False).encode())
        os.fsync(descriptor)
    finally:
        os.close(descriptor)
    try:
        os.link(temporary, path)  # fails if another writer won the race
    except FileExistsError:
        return False
    finally:
        os.unlink(temporary)
    return True


def protected_directory(path, *, create=False):
    path = Path(path)
    if create:
        path.mkdir(mode=0o700, parents=True, exist_ok=True)
    info = path.lstat()
    if not path.is_dir() or path.is_symlink() or info.st_mode & 0o077 or info.st_uid != os.getuid():
        raise ValueError('Protected owner-only directory required: ' + str(path))
    return path


class ResearchLine(ResearchDesk):
    def __init__(self, config, **options):
        binding = config.get('binding') or {}
        if not all(isinstance(binding.get(k), str) and binding[k].strip() for k in ('line', 'space', 'sender')):
            raise ValueError('Exact line/space/sender binding required')
        if binding['line'] == 'shared':
            raise ValueError('Shared Photon line cannot carry Research')
        self.binding = binding
        self.ledger = protected_directory(config['ledger_dir'])
        self.outbox = protected_directory(config['outbox_dir'], create=True)
        data = protected_directory(config['data_dir'], create=True)
        self.processed = protected_directory(data / 'processed', create=True)
        publisher = None
        memory = config.get('memory') or {}
        if memory.get('enabled') is True:
            if 'task_id' in memory or memory.get('kind', RESEARCH_KIND) != RESEARCH_KIND:
                raise ValueError('Memory task is per topic (research-line/<topic>) and kind is ' + RESEARCH_KIND +
                                 '; remove memory.task_id and memory.kind from the config')
            token_file = memory['token_file'].replace('${CREDENTIALS_DIRECTORY}', os.environ.get('CREDENTIALS_DIRECTORY', ''))
            publisher = MemoryServicePublisher(memory['url'], token_file)
        super().__init__(data / 'research', deliver=self.send, provider=config.get('provider', 'auto'),
                         publisher=publisher, publish_extractive=memory.get('allow_extractive') is True,
                         claude=config.get('claude'), **options)

    # ------------------------------------------------------------ transport

    def send(self, route, text):
        # One final reply per inbound message; a restart retry reuses the same operation id.
        self.enqueue('final:' + route['ledger_key'], text)

    def enqueue(self, operation_id, text):
        name = hashlib.sha256(operation_id.encode()).hexdigest() + '.json'
        payload = {'schema': OUTBOX_SCHEMA, 'operationId': operation_id, 'text': text[:60000],
                   'sequence': time.time_ns(), 'created_at': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())}
        private_write(self.outbox / name, payload)

    # ------------------------------------------------------------ intake

    def pending(self):
        """Unprocessed inbound records in arrival order (message timestamp, then write time)."""
        found = []
        for path in self.ledger.glob('*.json'):
            if not KEY.match(path.stem) or (self.processed / path.name).exists():
                continue
            try:
                record = json.loads(path.read_text())
                written = path.stat().st_mtime_ns
            except (OSError, ValueError):
                continue
            if isinstance(record, dict) and record.get('schema') == PENDING_SCHEMA and record.get('status') == 'PENDING_INTAKE':
                stamp = (record.get('event') or {}).get('timestamp')
                found.append((stamp if isinstance(stamp, str) else '', written, path.stem, record))
        return [(key, record) for _, _, key, record in sorted(found)]

    def poll_once(self):
        handled = 0
        for key, record in self.pending():
            try:
                self.handle(key, record)
            except Exception:
                log.exception('Research line message %s could not be handled', key[:12])
                self.enqueue('error:' + key, 'I couldn\'t start research on that message. Nothing was researched.')
            private_write(self.processed / (key + '.json'), {'at': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())})
            handled += 1
        return handled

    def handle(self, key, record):
        event = record.get('event') or {}
        research = event.get('research') or {}
        if (research.get('line'), research.get('space'), research.get('sender')) != \
                (self.binding['line'], self.binding['space'], self.binding['sender']) or event.get('project') != 'research':
            log.warning('Research line record %s ignored: binding mismatch', key[:12])
            return
        text = ((event.get('content') or {}).get('text') or '')[:20000]
        # The connector already stripped the prefix; anything unrecognised files under General.
        topic = research.get('topic') if research.get('topic') in RESEARCH_TOPICS else DEFAULT_RESEARCH_TOPIC
        reply = 'reply:' + key
        status = STATUS.match(text)
        if status:
            return self.enqueue(reply, self.status_reply(status.group(1)))
        if HELP.match(text):
            return self.enqueue(reply, self.help_text())
        intent = detect(text, dedicated=True)
        if intent is None:
            return self.enqueue(reply, 'Nothing to research in that message. ' + self.help_text())
        route = {'project': 'research', 'line': self.binding['line'], 'space': self.binding['space'],
                 'sender': self.binding['sender'], 'message_id': research.get('originalMessageId'),
                 'ledger_key': key, 'environment': 'personal', 'topic': topic}
        # Queue the acknowledgement before any job starts so it always precedes the result.
        self.deferred = []
        try:
            acknowledgement = self.accept(intent, route, 'line:' + key)
        finally:
            started, self.deferred = self.deferred, None
        self.enqueue(reply, acknowledgement)
        for job_id in started:
            super().start(job_id)

    def help_text(self):
        return HELP_TEXT.format(memory=MEMORY_ON if self.publisher is not None else MEMORY_OFF)

    def start(self, job_id):
        if getattr(self, 'deferred', None) is not None:
            self.deferred.append(job_id)
        else:
            super().start(job_id)

    # ------------------------------------------------------------ service loop

    def run_forever(self, poll_seconds=3):
        self.resume()
        while True:
            self.poll_once()
            time.sleep(poll_seconds)


def load_config(path):
    path = Path(path)
    info = path.lstat()
    if not path.is_file() or path.is_symlink() or info.st_mode & 0o022 or info.st_size > 65536:
        raise ValueError('Config must be a regular file, not group/world writable')
    return json.loads(path.read_text())


def main(argv=None):
    parser = argparse.ArgumentParser(description='Alfred Research line worker')
    parser.add_argument('command', choices=('run', 'once', 'check'))
    parser.add_argument('config')
    args = parser.parse_args(argv)
    logging.basicConfig(level=logging.INFO, format='%(levelname)s %(name)s %(message)s')
    config = load_config(args.config)
    if config.get('enabled') is not True:
        print(json.dumps({'state': 'DISABLED'}))
        return 0
    # `once` exits after one poll, so its jobs must finish in the foreground, not on daemon threads.
    line = ResearchLine(config, runner='inline' if args.command == 'once' else 'thread')
    if args.command == 'check':
        print(json.dumps({'state': 'READY', 'memory_publishing': line.publisher is not None,
                          'pending': sum(1 for _ in line.pending())}))
        return 0
    if args.command == 'once':
        line.resume()
        print(json.dumps({'handled': line.poll_once()}))
        return 0
    line.run_forever(int(config.get('poll_seconds', 3)))
    return 0


if __name__ == '__main__':
    sys.exit(main())
