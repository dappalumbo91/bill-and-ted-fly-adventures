#!/usr/bin/env python3
"""BANC ↔ Male CNS cell-type identity — measured columns, two graphs.

BANC v888 already annotates `malecns_cell_type` and `malecns_match`.
This script reads those columns. It does **not** merge the two synapse
graphs into one fake animal.

  python scripts/type_identity.py
"""
from __future__ import annotations

import runio
runio.install()

import json
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from paths import FLY_ROOT as FLY  # noqa: E402
from paths import require  # noqa: E402
OUT = ROOT / "data" / "type_identity.json"


def _norm(s: str) -> str:
    t = str(s or "").strip()
    if t.lower() in {"", "nan", "none", "null"}:
        return ""
    if t.lower().startswith("auto:"):
        t = t[5:]
    return t


def main() -> int:
    male_path = FLY / "male_cns" / "body-annotations-male-cns-v1.0-minconf-0.5.feather"
    banc_path = FLY / "banc" / "banc_888_meta.feather"
    require(male_path, "Male CNS body annotations feather")
    require(banc_path, "BANC meta feather")
    male = pd.read_feather(male_path)
    traced = male[male["status"] == "Traced"]
    male_types = {_norm(x) for x in traced["type"].tolist() if _norm(x)}
    banc = pd.read_feather(banc_path)
    banc_types = {_norm(x) for x in banc["cell_type"].tolist() if _norm(x)}
    banc_male_ann = [_norm(x) for x in banc["malecns_cell_type"].tolist()]
    banc_male_set = {x for x in banc_male_ann if x}
    match = banc["malecns_match"].fillna("").astype(str)
    n_match = int(((match != "") & (match.str.lower() != "nan") & (match.str.lower() != "none")).sum())

    shared_type = sorted(male_types & banc_types)
    shared_ann = sorted(male_types & banc_male_set)
    only_male = len(male_types - banc_types)
    only_banc = len(banc_types - male_types)

    # Frequency of shared names on each graph (still two animals).
    male_vc = traced["type"].map(_norm).value_counts()
    banc_vc = banc["cell_type"].map(_norm).value_counts()
    top_shared = []
    for t in shared_type:
        top_shared.append(
            {
                "type": t,
                "male_n": int(male_vc.get(t, 0)),
                "banc_n": int(banc_vc.get(t, 0)),
            }
        )
    top_shared.sort(key=lambda r: -(r["male_n"] + r["banc_n"]))

    doc = {
        "pin": "AEB2AD",
        "free_parameters": 0,
        "rule": "Same type name is identity of a class, not a license to merge synapses. Two animals.",
        "male_traced": int(len(traced)),
        "male_n_types": len(male_types),
        "banc_n_cells": int(len(banc)),
        "banc_n_types": len(banc_types),
        "banc_n_with_malecns_cell_type": len([x for x in banc_male_ann if x]),
        "banc_n_malecns_type_names": len(banc_male_set),
        "banc_n_with_malecns_match": n_match,
        "shared_cell_type_names": len(shared_type),
        "shared_malecns_annotation_in_male_types": len(shared_ann),
        "only_male_type_names": only_male,
        "only_banc_type_names": only_banc,
        "jaccard_type_names": (
            len(shared_type) / max(1, len(male_types | banc_types))
        ),
        "top_shared": top_shared[:40],
        "do_not": "merge BANC and Male CNS edge lists into one graph",
    }
    OUT.write_text(json.dumps(doc, indent=2), encoding="utf-8")
    print(
        f"shared type names {doc['shared_cell_type_names']} / "
        f"male {doc['male_n_types']} banc {doc['banc_n_types']}  "
        f"jaccard={doc['jaccard_type_names']:.3f}  "
        f"BANC malecns_match cells={n_match}"
    )
    print(f"  wrote {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
