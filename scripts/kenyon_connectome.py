#!/usr/bin/env python3
"""Mushroom-body Kenyon residual hops — measured hemibrain types only.

Sparse-index analog from the fly plan. Not a new MDS brain.
Seed typed KC on (1) the full hemibrain graph and (2) the measured
MB subgraph (KC + MBON + PAM + PPL1 + APL + DPM). Same residual as
JO / olfactory. 0 free parameters.

  python scripts/kenyon_connectome.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from fly_connectome import residual_cascade, seed_indices, _R_BIO  # noqa: E402
from hemibrain_connectome import load_hemibrain_graph  # noqa: E402

_MB_PREFIX = ("KC", "MBON", "PAM", "PPL1")
_MB_EXACT = frozenset({"APL", "DPM"})


def _is_mb(typ: str) -> bool:
    t = (typ or "").strip()
    return t.startswith(_MB_PREFIX) or t in _MB_EXACT


def _subgraph(graph: dict[str, Any], keep: list[int]) -> dict[str, Any]:
    from scipy.sparse import csr_matrix

    keep_i = np.asarray(sorted(set(keep)), dtype=np.int64)
    old_ids = graph["ids"]
    old_meta = graph["meta"]
    ids = [old_ids[int(i)] for i in keep_i]
    idx = {rid: i for i, rid in enumerate(ids)}
    meta = {rid: old_meta[rid] for rid in ids}
    W = graph["W"].tocsr()
    sub = W[keep_i][:, keep_i]
    if not isinstance(sub, type(W)):
        sub = csr_matrix(sub)
    return {
        "key": graph["key"] + ":mb-subgraph",
        "ids": ids,
        "idx": idx,
        "meta": meta,
        "W": sub,
        "n": len(ids),
        "n_edges": int(sub.nnz),
        "n_gaba": 0,
        "authority": graph["authority"] + "; subgraph = measured KC/MBON/PAM/PPL1/APL/DPM types",
    }


def _trace_row(run: dict[str, Any]) -> list[dict[str, Any]]:
    rows = []
    for snap in run.get("trace") or []:
        tm = snap.get("target_mass") or {}
        cm = snap.get("class_mass") or {}
        top = (snap.get("top") or [{}])[0]
        rows.append(
            {
                "hop": snap.get("hop"),
                "l1": snap.get("l1"),
                "n_active": snap.get("n_active"),
                "descending": tm.get("descending"),
                "vnc_motor": tm.get("vnc_motor"),
                "kenyon": cm.get("kenyon"),
                "mbon": cm.get("mbon"),
                "dan": cm.get("dan"),
                "top": {
                    "cell_type": top.get("cell_type"),
                    "cell_class": top.get("cell_class"),
                    "a": top.get("a"),
                },
            }
        )
    return rows


def _run(graph: dict[str, Any], name: str, gpu: bool) -> dict[str, Any]:
    print(f"== {name} seed=KC how=type_prefix n={graph['n']}", flush=True)
    seed_i = seed_indices(graph, "KC", how="type_prefix")
    run = residual_cascade(
        graph, seed_i, seed="KC", how="type_prefix", gpu=gpu
    )
    return {
        "name": name,
        "seed": "KC",
        "how": "type_prefix",
        "n_seed": run["n_seed"],
        "n_graph": graph["n"],
        "n_edges": graph["n_edges"],
        "gpu": run.get("gpu"),
        "device": run.get("device"),
        "elapsed_s": run.get("elapsed_s"),
        "flow": _trace_row(run),
    }


def main(argv: list[str] | None = None) -> int:
    import argparse

    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--gpu", dest="gpu", action="store_true", default=True)
    ap.add_argument("--cpu", dest="gpu", action="store_false")
    args = ap.parse_args(argv)

    full = load_hemibrain_graph()
    mb_i = [
        full["idx"][rid]
        for rid, m in full["meta"].items()
        if rid in full["idx"] and _is_mb(m.get("cell_type") or "")
    ]
    n_kc = sum(
        1 for m in full["meta"].values() if (m.get("cell_type") or "").startswith("KC")
    )
    n_mbon = sum(
        1 for m in full["meta"].values() if (m.get("cell_type") or "").startswith("MBON")
    )
    n_dan = sum(
        1
        for m in full["meta"].values()
        if (m.get("cell_type") or "").startswith(("PAM", "PPL1"))
    )
    mb = _subgraph(full, mb_i)
    programs = [
        _run(full, "kc_full_hemibrain", args.gpu),
        _run(mb, "kc_mb_subgraph", args.gpu),
    ]
    compare: dict[str, Any] = {}
    for hop in (1, 2, 3):
        row = {}
        for p in programs:
            hit = next((f for f in p["flow"] if f.get("hop") == hop), None)
            if hit:
                row[p["name"]] = {
                    "kenyon": hit.get("kenyon"),
                    "mbon": hit.get("mbon"),
                    "dan": hit.get("dan"),
                    "descending": hit.get("descending"),
                    "n_active": hit.get("n_active"),
                    "top": hit.get("top"),
                }
        compare[f"hop_{hop}"] = row
    report = {
        "dataset": "hemibrain:v1.2.1",
        "pin": "AEB2AD",
        "residual_Biochemistry": _R_BIO,
        "product": "Kenyon residual hops on measured MB types (not a new brain)",
        "n_kc": n_kc,
        "n_mbon": n_mbon,
        "n_dan": n_dan,
        "n_mb_subgraph": mb["n"],
        "n_mb_edges": mb["n_edges"],
        "free_parameters": 0,
        "authority": mb["authority"],
        "programs": programs,
        "compare": compare,
        "note": (
            "Pattern-separation analog = hops on measured KC/MBON/DAN types. "
            "Do not call leftover KC mass a thought. DNg29 is not in this volume."
        ),
    }
    out = ROOT / "data" / "kenyon_connectome_boot.json"
    out.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(f"  wrote {out}", flush=True)
    print(json.dumps(compare, indent=2), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
