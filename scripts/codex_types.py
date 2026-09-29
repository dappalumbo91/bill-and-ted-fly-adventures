#!/usr/bin/env python3
"""FAFB DNg29 and JO counts from two public measured tables.

The Codex download URL returns the HTML app. fetch_data saves
FLY_ROOT/Supplemental_file1_neuron_annotations.tsv and
FLY_ROOT/fafb/fafb_783_meta.feather. The Schlegel TSV is the committed
FlyWire count in data/type_counts.json. The lee-lab meta table uses
coarser JO names, so its prefix total is recorded beside the TSV.
A portal gzipped CSV still needs CODEX_API_TOKEN or CODEX_TOKEN.
Counts come from the two files. The portal response is only a page check.
"""
from __future__ import annotations

import runio
runio.install()

import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from paths import FLY_ROOT as FLY, need  # noqa: E402

OUT = ROOT / "data" / "codex_types.json"
TYPE_COUNTS = ROOT / "data" / "type_counts.json"
TSV_NAME = "Supplemental_file1_neuron_annotations.tsv"
META_NAME = Path("fafb") / "fafb_783_meta.feather"
PORTAL = "https://codex.flywire.ai/api/download?dataset=fafb"
UA = {"User-Agent": "FSOT-fly-pack (mailto:local)", "Accept": "text/csv, application/json, text/html"}
FLY_KEYS = ("n", "DNg29", "JO_type_prefix")


def _rel(path: Path) -> str:
    try:
        return path.resolve().relative_to(Path(FLY).resolve()).as_posix()
    except ValueError:
        return path.name


def _counts(types) -> dict:
    types = types.fillna("").astype(str)
    jo = types[types.str.startswith("JO")]
    return {
        "n": int(len(types)),
        "DNg29": int((types == "DNg29").sum()),
        "JO_type_prefix": int(len(jo)),
        "jo_lower_prefix": int(types.str.lower().str.startswith("jo").sum()),
        "n_jo_names": int(jo.nunique()),
        "jo_names": sorted(set(jo.tolist())),
    }


def _id_set(series) -> set[str]:
    import pandas as pd

    if pd.api.types.is_numeric_dtype(series):
        out: set[str] = set()
        for value in series.tolist():
            try:
                missing = value is None or bool(pd.isna(value))
            except TypeError:
                missing = value is None
            if missing:
                continue
            out.add(str(int(value)))
        return out
    text = series.fillna("").astype(str).str.strip()
    text = text.str.replace(r"\.0$", "", regex=True)
    return {value for value in text.tolist() if value and value.lower() not in {"nan", "<na>", "none"}}


def _read_tsv(path: Path):
    import pandas as pd

    header = pd.read_csv(path, sep="\t", nrows=0).columns.tolist()
    type_col = "cell_type" if "cell_type" in header else ("type" if "type" in header else "")
    if not type_col:
        raise ValueError(f"{_rel(path)} has no cell_type column")
    dtype = {"root_id": "string"} if "root_id" in header else None
    frame = pd.read_csv(path, sep="\t", low_memory=False, dtype=dtype)
    return frame, type_col, "root_id" if "root_id" in frame.columns else ""


def _read_meta(path: Path):
    import pandas as pd

    frame = pd.read_feather(path)
    type_col = "cell_type" if "cell_type" in frame.columns else ("type" if "type" in frame.columns else "")
    if not type_col:
        raise ValueError(f"{_rel(path)} has no cell_type column")
    id_col = "fafb_783_id" if "fafb_783_id" in frame.columns else ""
    return frame, type_col, id_col


def _rows_for(frame, id_col: str, type_col: str, wanted: set[str]) -> list[dict]:
    if not id_col or not wanted:
        return []
    rows = []
    ids = frame[id_col]
    types = frame[type_col].fillna("").astype(str)
    super_col = frame["super_class"] if "super_class" in frame.columns else None
    seen: set[str] = set()
    id_values = _id_list(ids)
    for i, root in enumerate(id_values):
        if root not in wanted or root in seen:
            continue
        seen.add(root)
        rec = {"root_id": root, "cell_type": types.iloc[i]}
        if super_col is not None:
            value = super_col.iloc[i]
            rec["super_class"] = "" if value is None or str(value) == "nan" else str(value)
        rows.append(rec)
    rows.sort(key=lambda rec: rec["root_id"])
    return rows


def _id_list(series) -> list[str]:
    import pandas as pd

    if pd.api.types.is_numeric_dtype(series):
        out = []
        for value in series.tolist():
            try:
                missing = value is None or bool(pd.isna(value))
            except TypeError:
                missing = value is None
            out.append("" if missing else str(int(value)))
        return out
    text = series.fillna("").astype(str).str.strip()
    return text.str.replace(r"\.0$", "", regex=True).tolist()


def _load_type_counts() -> dict | None:
    if not TYPE_COUNTS.is_file():
        return None
    try:
        doc = json.loads(TYPE_COUNTS.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return None
    return doc if isinstance(doc, dict) else None


def _ints(block, keys: tuple[str, ...]) -> dict | None:
    if not isinstance(block, dict):
        return None
    out = {}
    for key in keys:
        value = block.get(key)
        if isinstance(value, bool) or not isinstance(value, int):
            return None
        out[key] = value
    return out


def _probe(token: str) -> dict:
    headers = dict(UA)
    present = bool(token)
    if present:
        headers["Authorization"] = f"Bearer {token}"
    rec: dict = {"token_present": present, "is_table": False}
    req = urllib.request.Request(PORTAL, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=20) as fh:
            ctype = fh.headers.get("Content-Type") or ""
            prefix = fh.read(512)
            rec["status"] = fh.status
            rec["content_type"] = ctype
            html = "html" in ctype.lower() or prefix.lstrip()[:1] == b"<"
            rec["is_table"] = (not html) and fh.status == 200
    except urllib.error.HTTPError as exc:
        rec["status"] = exc.code
        rec["content_type"] = exc.headers.get("Content-Type") if exc.headers else None
        rec["error"] = f"HTTP {exc.code}"
    except (urllib.error.URLError, TimeoutError, OSError) as exc:
        rec["error"] = str(exc)
    return rec


def _portal_label(probe: dict) -> str:
    if probe.get("is_table"):
        return "table"
    ctype = str(probe.get("content_type") or "")
    if "html" in ctype.lower() or probe.get("status") == 200:
        return "html"
    return "unreachable"


def main() -> int:
    tsv_path = FLY / TSV_NAME
    meta_path = FLY / META_NAME
    if not tsv_path.is_file():
        need("FlyWire annotation TSV", tsv_path)
    if not meta_path.is_file():
        need("FAFB 783 meta feather", meta_path)

    try:
        tsv, tsv_type, tsv_id = _read_tsv(tsv_path)
        meta, meta_type, meta_id = _read_meta(meta_path)
    except (OSError, ValueError) as exc:
        rec = {
            "pin": "AEB2AD",
            "free_parameters": 0,
            "want": ["DNg29", "JO"],
            "overall_ok": False,
            "error": str(exc),
        }
        OUT.write_text(json.dumps(rec, indent=2) + "\n", encoding="utf-8")
        print(str(exc), file=sys.stderr)
        return 1

    sch = _counts(tsv[tsv_type])
    sch["source"] = _rel(tsv_path)
    sch["type_column"] = tsv_type
    sch["id_column"] = tsv_id or None
    meta_counts = _counts(meta[meta_type])
    meta_counts["source"] = _rel(meta_path)
    meta_counts["type_column"] = meta_type
    meta_counts["id_column"] = meta_id or None

    jo_only_meta: list[str] = []
    jo_only_tsv: list[str] = []
    meta_rows: list[dict] = []
    if tsv_id and meta_id:
        tsv_types = tsv[tsv_type].fillna("").astype(str)
        meta_types = meta[meta_type].fillna("").astype(str)
        tsv_all = _id_set(tsv[tsv_id])
        meta_all = _id_set(meta[meta_id])
        tsv_jo = _id_set(tsv.loc[tsv_types.str.startswith("JO"), tsv_id])
        meta_jo = _id_set(meta.loc[meta_types.str.startswith("JO"), meta_id])
        jo_only_meta = sorted(meta_jo - tsv_all)
        jo_only_tsv = sorted(tsv_jo - meta_all)
        meta_rows = _rows_for(meta, meta_id, meta_type, set(jo_only_meta))

    committed = _load_type_counts()
    flywire = (committed or {}).get("flywire_annotations")
    fly_ints = _ints(flywire, FLY_KEYS)
    matches = bool(fly_ints) and all(fly_ints[key] == sch[key] for key in FLY_KEYS)

    other = {"source": "data/type_counts.json"}
    if committed is None:
        other["missing"] = True
    else:
        other["male_cns"] = _ints(committed.get("male_cns"), ("n_traced", "DNg29", "JO_type_prefix"))
        other["banc"] = _ints(committed.get("banc"), ("n", "DNg29", "JO_type_prefix"))
        other["hemibrain_cache"] = _ints(
            committed.get("hemibrain_cache"),
            ("n_typed", "DNg29", "JO_type_prefix"),
        )

    token = os.environ.get("CODEX_API_TOKEN") or os.environ.get("CODEX_TOKEN") or ""
    anonymous = _probe("")
    portal = {
        "url": PORTAL,
        "anonymous": anonymous,
        "with_token": _probe(token) if token else {"token_present": False},
    }

    rec = {
        "pin": "AEB2AD",
        "free_parameters": 0,
        "want": ["DNg29", "JO"],
        "authority": (
            "Supplemental_file1_neuron_annotations.tsv and fafb/fafb_783_meta.feather. "
            "The Schlegel TSV is the committed FlyWire count. "
            "The Codex download URL is the HTML app. "
            "A portal gzipped CSV still needs CODEX_API_TOKEN."
        ),
        "nomenclature": (
            "Schlegel cell_type names are the split JO labels in schlegel_tsv.jo_names. "
            "lee-lab fafb_783_meta cell_type names are the coarser labels in fafb_783_meta.jo_names. "
            "Each table keeps its own JO prefix total. "
            "jo_only_in_meta lists meta JO root ids absent from the TSV root_id column. "
            "jo_only_in_tsv lists TSV JO root ids absent from the meta id column."
        ),
        "schlegel_tsv": sch,
        "fafb_783_meta": meta_counts,
        "dng29_same": sch["DNg29"] == meta_counts["DNg29"],
        "jo_only_in_meta": jo_only_meta,
        "n_jo_only_in_meta": len(jo_only_meta),
        "jo_only_in_meta_rows": meta_rows,
        "jo_only_in_tsv": jo_only_tsv,
        "n_jo_only_in_tsv": len(jo_only_tsv),
        "type_counts_flywire": {"source": "data/type_counts.json", **(fly_ints or {})},
        "matches_type_counts": matches,
        "overall_ok": matches,
        "other_graphs": other,
        "codex_portal": portal,
    }
    OUT.write_text(json.dumps(rec, indent=2) + "\n", encoding="utf-8")
    print(
        f"FAFB TSV n={sch['n']} DNg29={sch['DNg29']} JO={sch['JO_type_prefix']}; "
        f"meta n={meta_counts['n']} DNg29={meta_counts['DNg29']} JO={meta_counts['JO_type_prefix']}; "
        f"JO roots only in meta={len(jo_only_meta)}; "
        f"codex portal {_portal_label(anonymous)}"
    )
    return 0 if matches else 1


if __name__ == "__main__":
    raise SystemExit(main())
