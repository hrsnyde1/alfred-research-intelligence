# Alfred Research & Intelligence

Source of the Alfred Research worker (`src/alfred_research`), its scripts and tests.
Lucius Fox runs this worker on the Alfred VM over Telegram; the live copy, with Fox's
fixes, is in `hrsnyde1/alfred-fox` under `worker/`.

## Layout

- `src/alfred_research/`: the research pipeline, integrations and Memory contracts.
- `scripts/`: `research.py` (local CLI), `research_line.py`, `linux_compatibility_check.py`.
- `tests/`: unit and contract tests.
- `staging/`: reviewed Photon patches and the research line template used by the tests.
- `docs/`: phase reports and design notes. The original 2026-10-15 design handoffs are in
  `docs/history/`.

## Tests

```bash
PYTHONPATH=src python3 -m unittest discover -s tests
```
