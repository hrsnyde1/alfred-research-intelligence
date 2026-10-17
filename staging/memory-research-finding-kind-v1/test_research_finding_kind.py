"""research_finding kind: agent-created, auto-approved, searchable by Alfred, exported under Research."""
import secrets
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'deploy' / 'focused-v1'))
from focused_v1.store import MemoryStore
import obsidian_export


class ResearchFindingKind(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.store = MemoryStore(str(self.root / 'memory.sqlite3'), deletion_key=secrets.token_bytes(32), initialize=True)
        self.alfred, self.agent = secrets.token_hex(24), secrets.token_hex(24)
        self.store.provision('alfred', 'alfred', self.alfred)
        self.store.provision('research-line', 'agent', self.agent)
        self.store.assign(self.alfred, 'research-line', 'research-line')

    def tearDown(self):
        self.temp.cleanup()

    def test_agent_research_finding_is_approved_and_searchable(self):
        result = self.store.create(self.agent, task_id='research-line', kind='research_finding',
                                   content='Research finding: retries are safe for idempotent methods.',
                                   source_message_id='research:job:C1')
        self.assertEqual(result['review_state'], 'approved')
        hits = self.store.search(self.alfred, task_id=None, query='idempotent retries', limit=4)
        self.assertEqual([h['kind'] for h in hits], ['research_finding'])

    def test_other_agent_kinds_still_pending(self):
        result = self.store.create(self.agent, task_id='research-line', kind='personal_fact', content='A fact.')
        self.assertEqual(result['review_state'], 'pending')

    def test_export_has_research_category(self):
        self.assertEqual(obsidian_export.CATEGORIES['research_finding'], 'Research')


if __name__ == '__main__':
    unittest.main()
