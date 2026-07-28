#!/usr/bin/env python3
"""Run the deterministic review receipt gate from an installed hook."""
from __future__ import annotations

import sys
from pathlib import Path

AGENT_ROOT = Path(__file__).resolve().parents[1]
BIN_ROOT = AGENT_ROOT / "bin"
if not (BIN_ROOT / "review_gate.py").is_file():
    BIN_ROOT = Path(__file__).resolve().parents[2] / "bin"
if str(BIN_ROOT) not in sys.path:
    sys.path.insert(0, str(BIN_ROOT))

from review_gate import main  # noqa: E402


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
