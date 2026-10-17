"""Owner-local CLI, no Photon, Hermes or production activation required."""
import argparse
import json
from pathlib import Path
import sys

from .engine import ResearchEngine
from .memory import AuthoritativeMemoryAdapter, MemoryBlocked


def main(argv=None):
    parser = argparse.ArgumentParser(description='Alfred Research & Intelligence local V1')
    parser.add_argument('--data', default='data/research-v1', help='Private Research working directory (not Memory)')
    commands = parser.add_subparsers(dest='command', required=True)
    submit = commands.add_parser('submit', help='Submit a URL, document, or question')
    submit.add_argument('input')
    submit.add_argument('--question', help='Objective for submitted URL/document/article')
    submit.add_argument('--source', action='append', default=[], help='Supporting URL or file; at most four')
    submit.add_argument('--text', help='Owner-supplied article text')
    submit.add_argument('--provider', choices=['auto', 'claude', 'codex', 'extractive'], default='auto')
    submit.add_argument('--request-key', help='Idempotency key for host/CLI submission')
    submit.add_argument('--run', action='store_true', help='Execute now instead of leaving queued')
    for name in ('run', 'recover', 'show', 'report', 'candidate', 'promote'):
        command = commands.add_parser(name)
        command.add_argument('job_id')
    commands.add_parser('list')
    commands.add_parser('provider-status', help='Check Claude provider configuration (no API call)')
    args = parser.parse_args(argv)
    try:
        engine = ResearchEngine(args.data)
        if args.command == 'submit':
            sources = list(args.source)
            objective = args.question or args.input
            if args.input.startswith(('https://', 'http://')) or Path(args.input).expanduser().is_file():
                sources.insert(0, args.input)
                objective = args.question or 'Analyze this source and summarize its important findings and implications.'
            job_id = engine.submit(objective, sources, article=args.text, provider=args.provider, request_key=args.request_key)
            if args.run:
                job = engine.run(job_id)
                print(json.dumps(summary(job), indent=2))
                return 0 if job['status'] == 'completed' else 2
            print(json.dumps({'job_id': job_id, 'status': engine.store.get(job_id)['status']}))
        elif args.command == 'run':
            job = engine.run(args.job_id)
            print(json.dumps(summary(job), indent=2))
            return 0 if job['status'] == 'completed' else 2
        elif args.command == 'recover':
            print(json.dumps(summary(engine.recover(args.job_id)), indent=2))
        elif args.command == 'provider-status':
            print(json.dumps(engine.claude_status(), indent=2))
        elif args.command == 'list':
            print(json.dumps(engine.store.list(), indent=2))
        else:
            job = engine.store.get(args.job_id)
            if args.command == 'show':
                print(json.dumps(job, indent=2, ensure_ascii=False))
            elif args.command == 'report':
                if 'report' not in job['artifacts']:
                    raise ValueError('This job has no report; inspect status/error with show')
                print(job['artifacts']['report']['text'], end='')
            else:
                candidate = job['artifacts'].get('memory-candidate')
                if candidate is None:
                    raise ValueError('This job has no source-supported Memory candidate')
                if args.command == 'promote':
                    AuthoritativeMemoryAdapter().promote(candidate)
                print(json.dumps(candidate, indent=2, ensure_ascii=False))
        return 0
    except (ValueError, KeyError, MemoryBlocked, OSError) as error:
        print(json.dumps({'error': str(error)}), file=sys.stderr)
        return 2


def summary(job):
    return {'job_id': job['id'], 'status': job['status'], 'report': job['report_path'],
            'error': job['error'], 'provider': job['artifacts'].get('plan', {}).get('mode'),
            'memory_candidate': job['artifacts'].get('memory-candidate', {}).get('status', 'NONE'),
            'memory_promotion': 'BLOCKED; no authoritative Memory write attempted'}


if __name__ == '__main__':
    sys.exit(main())
