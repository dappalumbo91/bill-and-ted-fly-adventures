#!/usr/bin/env python3
"""Keep committed results in place.

A rerun writes under out/. --check compares score fields to the committed
JSON and does not write it. FSOT_COMMIT_OUT=1, or python scripts/bill_ted.py,
writes the tracked path. That is the promotion step.
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

from paths import OUT_DIR, ROOT

_INSTALLED = False
_ORIG_TEXT = None
_ORIG_BYTES = None
_SKIP = object()
_SCORE_KEYS = (
    "overall_ok",
    "n",
    "n_ok",
    "n_trials",
    "correct",
    "wrong",
    "leftover",
    "free_parameters",
    "promotes",
    "pin",
)


def offline() -> bool:
    return "--offline" in sys.argv or os.environ.get("FSOT_OFFLINE") == "1"


def checking() -> bool:
    return "--check" in sys.argv


def committing() -> bool:
    if os.environ.get("FSOT_COMMIT_OUT") == "1":
        return True
    return Path(sys.argv[0]).name == "bill_ted.py"


def offline_exit(committed: Path) -> int | None:
    """Return an exit code when --offline should use the cached JSON."""
    if not offline():
        return None
    if not committed.is_file():
        print(
            f"needs cached {committed.name} from a previous run "
            f"(python scripts/fetch_data.py, then run once without --offline)",
            file=sys.stderr,
        )
        return 2
    doc = json.loads(committed.read_text(encoding="utf-8"))
    ok = doc.get("overall_ok", True)
    print(f"offline {committed.name} overall_ok={ok}")
    return 0 if ok else 1


def _rel(path: Path) -> Path | None:
    try:
        return path.resolve().relative_to(ROOT.resolve())
    except ValueError:
        return None


def _guarded(path: Path) -> bool:
    rel = _rel(path)
    if rel is None or not rel.parts:
        return False
    top = rel.parts[0]
    if top in {"out", "data_external", ".git"}:
        return False
    if top in {"data", "docs"}:
        return True
    if top == "Bill and Ted fly adventures":
        return True
    if path.suffix.lower() == ".pdf" and path.name.startswith("Bio-Neuromorphic"):
        return True
    return False


def _score_mismatch(committed: Path, text: str) -> str | None:
    if not committed.is_file():
        return f"check FAIL {committed}: no committed result"
    try:
        new = json.loads(text)
        old = json.loads(committed.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return None
    if not isinstance(new, dict) or not isinstance(old, dict):
        return None
    for key in _SCORE_KEYS:
        if key in new and key in old and new[key] != old[key]:
            return f"check FAIL {committed.name}: {key} committed={old[key]!r} rerun={new[key]!r}"
    return None


def _route(path: Path, text: str | None):
    if not _guarded(path) or committing():
        return None
    if checking() and text is not None and path.suffix.lower() == ".json":
        mismatch = _score_mismatch(path, text)
        if mismatch:
            print(mismatch, file=sys.stderr)
            raise SystemExit(1)
        print(f"check OK {path.name}")
        return _SKIP
    if checking():
        return _SKIP
    rel = _rel(path)
    assert rel is not None
    dest = OUT_DIR / rel
    dest.parent.mkdir(parents=True, exist_ok=True)
    return dest


def install() -> None:
    global _INSTALLED, _ORIG_TEXT, _ORIG_BYTES
    if _INSTALLED:
        return
    _ORIG_TEXT = Path.write_text
    _ORIG_BYTES = Path.write_bytes

    def write_text(self, data, *args, **kwargs):
        text = data if isinstance(data, str) else None
        routed = _route(self, text)
        if routed is _SKIP:
            return len(data) if isinstance(data, str) else 0
        if isinstance(routed, Path):
            return _ORIG_TEXT(routed, data, *args, **kwargs)
        return _ORIG_TEXT(self, data, *args, **kwargs)

    def write_bytes(self, data, *args, **kwargs):
        routed = _route(self, None)
        if routed is _SKIP:
            return len(data)
        if isinstance(routed, Path):
            return _ORIG_BYTES(routed, data, *args, **kwargs)
        return _ORIG_BYTES(self, data, *args, **kwargs)

    Path.write_text = write_text  # type: ignore[method-assign]
    Path.write_bytes = write_bytes  # type: ignore[method-assign]
    _INSTALLED = True
