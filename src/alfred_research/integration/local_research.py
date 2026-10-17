"""Callable Research entry point for a future authenticated Hermes tool.

Never register automatically in Personal Hermes. Caller authentication belongs
to the existing host; this local method is not a network authorization boundary.
"""
from ..local.engine import ResearchEngine
from ..local.cli import summary


class LocalResearchEntryPoint:
    def __init__(self, working_directory):
        self.engine = ResearchEngine(working_directory)

    def submit(self, request_id, objective, sources=(), *, article=None, provider='auto'):
        if not isinstance(request_id, str) or not 1 <= len(request_id) <= 256:
            raise ValueError('Bounded host-issued request ID required')
        job_id = self.engine.submit(objective, sources, article=article, provider=provider,
                                    request_key='hermes:' + request_id)
        return summary(self.engine.store.get(job_id))

    def execute(self, job_id):
        return summary(self.engine.run(job_id))

    def retrieve(self, job_id):
        job = self.engine.store.get(job_id)
        return {**summary(job), 'report': job['artifacts'].get('report', {}).get('text'),
                'authority': 'Research report; not authoritative Memory retrieval'}
