"""Standard-library offline source packaging; no installer or live adapter.

Build uses an explicit file-type/root allowlist. Verify reads archive members
without extracting or executing them. SHA-256 is integrity, not authorization.
"""
import argparse
import gzip
import hashlib
import io
import json
import os
from pathlib import Path, PurePosixPath
import re
import tarfile
import tempfile

ROOT_FILES = ('.gitignore', 'pyproject.toml', 'README (1).md',
              'alfred_research_v1_codex_master_plan (1).md',
              'Alfred_Memory_Research_Intelligence_Handoff (1).txt')
GENERATED = ('RELEASE_INVENTORY.json', 'FILES.sha256')
MAX_FILE = 20_000_000
MAX_TOTAL = 100_000_000
SECRET_MARKERS = re.compile(rb'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----|'
                            rb'AKIA[0-9A-Z]{16}|sk-[A-Za-z0-9]{32,}')


def require(condition, message):
    if not condition:
        raise ValueError(message)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=False).encode()


def formatted(value):
    return (json.dumps(value, indent=2, ensure_ascii=False) + '\n').encode()


def safe_path(name):
    p = PurePosixPath(name)
    require(not p.is_absolute() and '..' not in p.parts and '\\' not in name and
            str(p) == name and '\n' not in name and '\r' not in name, 'unsafe release path')


def collect(root):
    names = list(ROOT_FILES)
    for directory, extension in (('src', '.py'), ('tests', '.py'), ('docs', '.md'), ('scripts', '.py')):
        for parent, dirs, files in os.walk(root / directory, followlinks=False):
            require(not any((Path(parent) / d).is_symlink() for d in dirs), 'symlink directory in release roots')
            dirs[:] = [d for d in dirs if d != '__pycache__' and not d.startswith('.')]
            for name in files:
                p = Path(parent) / name
                if p.suffix == extension:
                    names.append(p.relative_to(root).as_posix())
    names.append('docs/PHASE6_RELEASE_INVENTORY.json')
    snapshot = {}
    for name in sorted(names):
        safe_path(name)
        p = root / name
        require(all(not part.is_symlink() for part in (p, *p.parents)), 'release symlink forbidden')
        require(p.is_file() and p.stat().st_size <= MAX_FILE, 'missing/oversized release file: ' + name)
        raw = p.read_bytes()
        require(not SECRET_MARKERS.search(raw), 'possible secret marker; manual review required: ' + name)
        snapshot[name] = raw
    require(sum(map(len, snapshot.values())) <= MAX_TOTAL, 'release exceeds size bound')
    return snapshot


def baseline_check(root, snapshot):
    baseline = json.loads((root / 'docs/PHASE6_RELEASE_INVENTORY.json').read_text())
    require(sha(canonical(baseline['files'])) == baseline['entries_sha256'], 'Phase 6 inventory aggregate mismatch')
    for entry in baseline['files']:
        raw = snapshot.get(entry['path'])
        require(raw is not None and len(raw) == entry['bytes'] and sha(raw) == entry['sha256'],
                'accepted baseline changed: ' + entry['path'])
    return len(baseline['files'])


def file_manifest(snapshot):
    return ''.join(f'{sha(raw)}  {name}\n' for name, raw in sorted(snapshot.items())).encode()


def build(root, output, release_id, test_results):
    require(re.fullmatch(r'[a-z0-9][a-z0-9.-]{0,99}', release_id), 'invalid release ID')
    snapshot = collect(root)
    baseline_count = baseline_check(root, snapshot)
    log = test_results.read_bytes()
    match = re.search(rb'^Ran (\d+) tests in ([0-9.]+)s$', log, re.MULTILINE)
    require(match and re.search(rb'^OK$', log, re.MULTILINE) and
            not re.search(rb'^FAILED', log, re.MULTILINE), 'successful unittest transcript required')
    entries = [{'path': name, 'bytes': len(raw), 'sha256': sha(raw)} for name, raw in sorted(snapshot.items())]
    inventory = {'schema': 'mac_source_release_inventory.v1', 'release_id': release_id,
        'status': 'OFFLINE_SIMULATION_ONLY_NOT_DEPLOYED', 'production_enabled': False,
        'linux_accessed': False, 'transfer_performed': False, 'signed': False,
        'payload_file_count': len(entries), 'archive_regular_file_count': len(entries) + 2,
        'generated_metadata': list(GENERATED), 'accepted_phase6_entries_verified': baseline_count,
        'tests': {'count': int(match[1]), 'failures': 0, 'errors': 0,
                  'elapsed_seconds_text': match[2].decode(), 'transcript_sha256': sha(log)},
        'entries_sha256': sha(canonical(entries)), 'files': entries,
        'exclusions': ['.git', 'secrets/credentials/.env', 'runtime databases and registration/journal state',
                       'private company data', 'logs', 'caches/bytecode', 'artifacts and temporary files']}
    snapshot['RELEASE_INVENTORY.json'] = formatted(inventory)
    snapshot['FILES.sha256'] = file_manifest(snapshot)
    output.mkdir(parents=True, exist_ok=True)
    destination = output / release_id
    require(not destination.exists(), 'versioned release already exists; never overwrite it')
    with tempfile.TemporaryDirectory(prefix='.release-stage-', dir=output) as staging:
        stage = Path(staging)
        archive = stage / (release_id + '.tar.gz')
        with archive.open('wb') as stream:
            with gzip.GzipFile(filename='', fileobj=stream, mode='wb', mtime=0, compresslevel=9) as compressed:
                with tarfile.open(fileobj=compressed, mode='w', format=tarfile.PAX_FORMAT) as tar:
                    for name, raw in sorted(snapshot.items()):
                        info = tarfile.TarInfo(release_id + '/' + name)
                        info.size, info.mode, info.mtime = len(raw), 0o644, 0
                        info.uid = info.gid = 0
                        info.uname = info.gname = ''
                        tar.addfile(info, io.BytesIO(raw))
        for name in GENERATED:
            (stage / name).write_bytes(snapshot[name])
        companions = {archive.name: archive.read_bytes(), **{name: snapshot[name] for name in GENERATED}}
        (stage / 'SHA256SUMS').write_bytes(file_manifest(companions))
        verification = verify(archive)
        (stage / 'INTEGRITY_VERIFICATION.json').write_bytes(formatted(verification))
        os.rename(stage, destination)  # Publication only, no install or transfer.
        return destination, verification


def verify(archive):
    """Verify exact members, per-file hashes, inventory and external checksums."""
    raw_archive = archive.read_bytes()
    require(len(raw_archive) <= MAX_TOTAL, 'oversized archive')
    members = {}
    total = 0
    with tarfile.open(fileobj=io.BytesIO(raw_archive), mode='r:gz') as tar:
        for member in tar:
            safe_path(member.name)
            require(member.isfile() and member.name not in members and member.size <= MAX_FILE,
                    'unsafe/duplicate/nonregular archive member')
            total += member.size
            require(total <= MAX_TOTAL and len(members) < 1000, 'archive exceeds bounds')
            members[member.name] = tar.extractfile(member).read()
    roots = {PurePosixPath(name).parts[0] for name in members}
    require(len(roots) == 1, 'one archive root required')
    release_id = roots.pop()
    require(archive.name == release_id + '.tar.gz', 'archive name/root mismatch')
    snapshot = {name[len(release_id) + 1:]: raw for name, raw in members.items()}
    inventory_raw = snapshot['RELEASE_INVENTORY.json']
    inventory = json.loads(inventory_raw)
    require(inventory['release_id'] == release_id and inventory['production_enabled'] is False and
            inventory['transfer_performed'] is False and inventory['linux_accessed'] is False,
            'release identity/status mismatch')
    entries = inventory['files']
    names = [entry['path'] for entry in entries]
    require(len(set(names)) == len(names) and set(snapshot) == set(names) | set(GENERATED),
            'inventory/member mismatch')
    require(len(names) == inventory['payload_file_count'] and
            len(members) == inventory['archive_regular_file_count'], 'inventory count mismatch')
    require(sha(canonical(entries)) == inventory['entries_sha256'], 'inventory aggregate mismatch')
    for entry in entries:
        safe_path(entry['path'])
        raw = snapshot[entry['path']]
        require(len(raw) == entry['bytes'] and sha(raw) == entry['sha256'], 'payload hash/size mismatch')
    expected_files = file_manifest({name: raw for name, raw in snapshot.items() if name != 'FILES.sha256'})
    require(snapshot['FILES.sha256'] == expected_files, 'per-file checksum manifest mismatch')
    for name in GENERATED:
        require((archive.parent / name).read_bytes() == snapshot[name], 'external metadata differs')
    sums = file_manifest({archive.name: raw_archive, **{name: snapshot[name] for name in GENERATED}})
    require((archive.parent / 'SHA256SUMS').read_bytes() == sums, 'archive/metadata checksum mismatch')
    return {'schema': 'mac_release_integrity_result.v1', 'release_id': release_id, 'result': 'PASS',
        'archive_sha256': sha(raw_archive), 'archive_bytes': len(raw_archive),
        'payload_file_count': len(names), 'archive_regular_file_count': len(members),
        'all_payload_digests_verified': True, 'external_manifests_verified': True,
        'unsafe_members': 0, 'archive_extracted_or_executed': False,
        'signed': False, 'linux_verified': False, 'deployed': False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='operation', required=True)
    b = sub.add_parser('build')
    b.add_argument('--root', type=Path, default=Path('.'))
    b.add_argument('--output', type=Path, default=Path('artifacts/releases'))
    b.add_argument('--release-id', required=True)
    b.add_argument('--test-results', type=Path, required=True)
    v = sub.add_parser('verify')
    v.add_argument('archive', type=Path)
    args = parser.parse_args()
    if args.operation == 'build':
        destination, result = build(args.root.resolve(), args.output.resolve(), args.release_id, args.test_results)
        print('Release directory: ' + str(destination))
    else:
        result = verify(args.archive)
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
