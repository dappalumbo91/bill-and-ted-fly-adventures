#!/usr/bin/env python3
"""Fly life-cycle identity that is actually measured.

No embryo→pupa synapse movie exists. We use:

  - first-instar larva CNS (Winding 2023)
  - adult Male CNS / BANC / FlyWire
  - Truman + Ito–Lee hemilineage on adult cells
  - Male `birthtime` (early / late)

Named class persistence (KC, MBON, DN, sensory) is a **job name**,
not a 1:1 cell. Residual hops on a birth/lineage seed are growth on
measured cells. Do not invent metamorphosis synapses.

  python scripts/develop_cycle.py              # inventory
  python scripts/develop_cycle.py --hops       # + Male residual on birth/lineage
"""
from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "vendor"))

FLY = Path(r"D:\FlyWire_Connectome")
OUT = ROOT / "data" / "develop_cycle.json"
LARVA_BOOT = ROOT / "data" / "larva_connectome_boot.json"
MALE_BOOT = ROOT / "data" / "male_cns_boot.json"


def _norm(s: Any) -> str:
    t = str(s or "").strip()
    if t.lower() in {"", "nan", "none", "null"}:
        return ""
    return t


def inventory() -> dict[str, Any]:
    import pandas as pd

    male = pd.read_feather(
        FLY / "male_cns" / "body-annotations-male-cns-v1.0-minconf-0.5.feather"
    )
    traced = male[male["status"] == "Traced"]
    birth = traced["birthtime"].map(_norm)
    truman = traced["trumanHl"].map(_norm)
    ito = traced["itoleeHl"].map(_norm)
    banc = pd.read_feather(FLY / "banc" / "banc_888_meta.feather")
    bhl = banc["hemilineage"].map(_norm)
    fw = pd.read_csv(
        FLY / "Supplemental_file1_neuron_annotations.tsv",
        sep="\t",
        low_memory=False,
        usecols=["ito_lee_hemilineage", "hartenstein_hemilineage", "cell_type"],
    )
    lar = pd.read_csv(FLY / "larva" / "Supplementary-Data-S1" / "annotations.csv")
    larva_types = Counter(_norm(x) for x in lar["celltype"].tolist() if _norm(x))
    extra = Counter(
        _norm(x) for x in lar["additional_annotations"].tolist() if _norm(x) and _norm(x) != "no official annotation"
    )

    # Named jobs that exist as strings at both stages (not 1:1 cells).
    adult_types = traced["type"].map(_norm)
    persist = []
    for larva_name, prefixes in (
        ("KC", ("KC",)),
        ("MBON", ("MBON",)),
        ("DN-VNC", ("DN", "DNg", "DNp", "DNb")),
        ("ascending", ("AN",)),
        ("sensory", ("JO", "ORN", "SN")),
        ("LN", ("LN", "lLN", "il3LN")),
    ):
        n_larva = int(larva_types.get(larva_name, 0))
        n_adult = int(
            sum(adult_types.str.startswith(p).sum() for p in prefixes)
            if larva_name != "sensory"
            else (
                (traced["superclass"].fillna("").str.lower().str.contains("sensory")).sum()
            )
        )
        persist.append(
            {
                "larva_class": larva_name,
                "n_larva_rows": n_larva,
                "adult_prefixes": list(prefixes),
                "n_adult_traced_matching": int(n_adult),
                "persistent_job": n_larva > 0 and n_adult > 0,
            }
        )

    return {
        "male_traced": int(len(traced)),
        "male_birthtime": dict(Counter(x for x in birth if x)),
        "male_n_with_birthtime": int((birth != "").sum()),
        "male_truman_hemilineage_n": int((truman != "").sum()),
        "male_truman_nunique": int(truman[truman != ""].nunique()),
        "male_truman_top": truman[truman != ""].value_counts().head(12).to_dict(),
        "male_ito_lee_n": int((ito != "").sum()),
        "male_ito_lee_nunique": int(ito[ito != ""].nunique()),
        "banc_hemilineage_n": int((bhl != "").sum()),
        "banc_hemilineage_nunique": int(bhl[bhl != ""].nunique()),
        "flywire_ito_lee_n": int(fw["ito_lee_hemilineage"].fillna("").astype(str).str.len().gt(0).sum()),
        "larva_n_rows": int(len(lar)),
        "larva_celltypes": dict(larva_types),
        "larva_extra_top": extra.most_common(12),
        "named_job_persistence": persist,
        "missing": (
            "No published complete synapse time series embryo→pupa→adult. "
            "Two measured snapshots + hemilineage/birthtime. "
            "C. elegans remains the only complete cell lineage."
        ),
    }


def _seed_from_col(traced, graph: dict[str, Any], col: str, want: str) -> list[int]:
    idx = graph["idx"]
    out = []
    for body, val in zip(traced["bodyId"].tolist(), traced[col].tolist()):
        if _norm(val).lower() == want.lower():
            rid = str(int(body))
            if rid in idx:
                out.append(idx[rid])
    return out


def hops(inv: dict[str, Any]) -> dict[str, Any]:
    import pandas as pd
    from fly_connectome import residual_cascade
    from male_cns import load_male_graph

    traced = pd.read_feather(
        FLY / "male_cns" / "body-annotations-male-cns-v1.0-minconf-0.5.feather"
    )
    traced = traced[traced["status"] == "Traced"]
    graph = load_male_graph()
    programs = []
    specs = [
        ("birth_early", "birthtime", "early"),
        ("truman_07B", "trumanHl", "07B"),
        ("ito_MBp3", "itoleeHl", "MBp3"),
    ]
    for name, col, want in specs:
        seed_i = _seed_from_col(traced, graph, col, want)
        print(f"== {name} n_seed={len(seed_i)}", flush=True)
        if not seed_i:
            programs.append({"name": name, "n_seed": 0, "flow": []})
            continue
        run = residual_cascade(graph, seed_i, seed=name, how="class", gpu=True)
        flow = []
        for snap in run.get("trace") or []:
            if snap.get("hop") in (0, 1, 2, 3):
                tm = snap.get("target_mass") or {}
                top = (snap.get("top") or [{}])[0]
                flow.append(
                    {
                        "hop": snap.get("hop"),
                        "n_active": snap.get("n_active"),
                        "vnc_motor": tm.get("vnc_motor"),
                        "descending": tm.get("descending"),
                        "top": top.get("cell_type"),
                    }
                )
        programs.append(
            {
                "name": name,
                "column": col,
                "want": want,
                "n_seed": len(seed_i),
                "gpu": run.get("gpu"),
                "flow": flow,
            }
        )
    compare = {}
    for hop in (1, 2):
        row = {}
        for p in programs:
            hit = next((f for f in p.get("flow") or [] if f.get("hop") == hop), None)
            if hit:
                row[p["name"]] = {
                    "vnc_motor": hit.get("vnc_motor"),
                    "descending": hit.get("descending"),
                    "top": hit.get("top"),
                    "n_active": hit.get("n_active"),
                }
        compare[f"hop_{hop}"] = row
    larva = {}
    if LARVA_BOOT.is_file():
        lb = json.loads(LARVA_BOOT.read_text(encoding="utf-8"))
        larva = (lb.get("compare") or {}).get("hop_2") or {}
    return {
        "programs": programs,
        "compare": compare,
        "larva_hop2": larva,
        "note": (
            "Birth/lineage seeds are adult cells that still carry a measured "
            "developmental tag. Residual does not replay metamorphosis."
        ),
    }


def main(argv: list[str] | None = None) -> int:
    import argparse

    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--hops", action="store_true", help="Male residual on birth/lineage seeds")
    args = ap.parse_args(argv)
    print("  inventory", flush=True)
    inv = inventory()
    hop = hops(inv) if args.hops else None
    doc = {
        "pin": "AEB2AD",
        "free_parameters": 0,
        "law": "S=K(T1+T2+T3); residual on measured cells; no invented metamorphosis synapses",
        "inventory": inv,
        "hops": hop,
    }
    OUT.write_text(json.dumps(doc, indent=2), encoding="utf-8")
    print(
        f"  birthtime {inv['male_birthtime']}  "
        f"truman n={inv['male_truman_hemilineage_n']}  "
        f"persist {[p['larva_class'] for p in inv['named_job_persistence'] if p['persistent_job']]}"
    )
    print(f"  wrote {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
