#!/usr/bin/env python3
"""Run the Research line worker from a checkout or install directory."""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
from alfred_research.integration.research_line import main

raise SystemExit(main())
