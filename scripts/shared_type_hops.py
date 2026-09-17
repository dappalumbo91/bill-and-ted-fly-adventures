#!/usr/bin/env python3
"""Same type name, two animals — residual hops without merging graphs.

BANC and Male share type strings. Seed each graph independently.
If the type is a walking/descending job, motor/descending should light on
both. If it is optic / Kenyon leftover, it should not. That is FSOT type
identity, not a fused connectome.

  python scripts/shared_type_hops.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "vendor"))

from fly_connectome import residual_cascade, seed_indices, _R_BIO  # noqa: E402

OUT = ROOT / "data" / "shared_type_hops.json"

# Exact type strings that exist on both dumps (type_identity / type_counts).
TYPES = (
    {"name": "DNg29", "expect": "descending_on"},
    {"name": "KCg-m", "expect": "motor_off"},
    {"name": "L5", "expect": "motor_off"},
)


def _hop2(run: dict[str, Any]) -> dict[str, Any]:
    hit = next((s for s in (run.get("trace") or []) if s.get("hop") == 2), None) or {}
    tm = hit.get("target_mass") or {}
    top = (hit.get("top") or [{}])[0]
    return {
        "n_seed": run.get("n_seed"),
        "n_active": hit.get("n_active"),
        "vnc_motor": tm.get("vnc_motor"),
        "descending": tm.get("descending"),
        "top": top.get("cell_type"),
        "gpu": run.get("gpu"),
    }


def main() -> int:
    from male_cns import load_male_graph
    from banc_connectome import load_banc_graph

    print("  load Male CNS", flush=True)
    male = load_male_graph()
    print("  load BANC", flush=True)
    banc = load_banc_graph()
    rows = []
    for spec in TYPES:
        name = spec["name"]
        print(f"== {name}", flush=True)
        rec: dict[str, Any] = {"type": name, "expect": spec["expect"]}
        for label, graph in (("male", male), ("banc", banc)):
            seed_i = seed_indices(graph, name, how="type_exact")
            print(f"  {label} n_seed={len(seed_i)}", flush=True)
            if not seed_i:
                rec[label] = {"n_seed": 0}
                continue
            run = residual_cascade(
                graph, seed_i, seed=name, how="type_exact", gpu=True
            )
            rec[label] = _hop2(run)
        m = rec.get("male") or {}
        b = rec.get("banc") or {}
        if spec["expect"] == "motor_off":
            rec["ok"] = float(m.get("vnc_motor") or 0) < 0.05 and float(
                b.get("vnc_motor") or 0
            ) < 0.05
        else:
            rec["ok"] = float(m.get("descending") or 0) > 1 and float(
                b.get("descending") or 0
            ) > 1
        rows.append(rec)
        print(f"  ok={rec['ok']}", flush=True)

    doc = {
        "pin": "AEB2AD",
        "residual_Biochemistry": _R_BIO,
        "free_parameters": 0,
        "rule": "Same type string on two graphs. Do not merge synapses.",
        "types": rows,
        "overall_ok": all(r.get("ok") for r in rows),
    }
    OUT.write_text(json.dumps(doc, indent=2), encoding="utf-8")
    print(f"  wrote {OUT} overall_ok={doc['overall_ok']}")
    return 0 if doc["overall_ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
