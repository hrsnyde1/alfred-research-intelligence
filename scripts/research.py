#!/usr/bin/env python3
"""Run local Research directly from a checkout; installation is optional."""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
from alfred_research.local.cli import main

raise SystemExit(main())
