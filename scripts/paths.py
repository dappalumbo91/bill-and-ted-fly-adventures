#!/usr/bin/env python3
"""Where external measured files live.

Defaults are under ./data_external/. Override with FLY_ROOT, DATASETS_ROOT,
or CACHE_DIR. A directory that is already present at the old drive letter is
used when the env var is unset, so an existing local dump still resolves.
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class MissingData(FileNotFoundError):
    """Raised when a measured dump is not on disk. Caught by live loaders."""


def _pick(env: str, default: Path, legacy: Path | None = None) -> Path:
    raw = os.environ.get(env)
    if raw:
        return Path(raw)
    if legacy is not None and legacy.is_dir():
        return legacy
    return default


FLY_ROOT = _pick("FLY_ROOT", ROOT / "data_external" / "FlyWire_Connectome", Path(r"D:\FlyWire_Connectome"))
DATASETS_ROOT = _pick("DATASETS_ROOT", ROOT / "data_external" / "AI_Datasets", Path(r"G:\AI_Datasets"))
CACHE_DIR = _pick("CACHE_DIR", ROOT / "data_external" / "cache", None)
OUT_DIR = Path(os.environ["FSOT_OUT"]) if os.environ.get("FSOT_OUT") else ROOT / "out"


def _msg(what: str, path: Path | None) -> str:
    where = f" Missing {path}." if path is not None else ""
    return f"needs {what} from fetch_data (python scripts/fetch_data.py).{where}"


def need(what: str, path: Path | None = None) -> None:
    print(_msg(what, path), file=sys.stderr)
    raise SystemExit(2)


def require(path: Path, what: str) -> Path:
    path = Path(path)
    if not path.is_file():
        msg = _msg(what, path)
        print(msg, file=sys.stderr)
        raise MissingData(msg)
    return path
