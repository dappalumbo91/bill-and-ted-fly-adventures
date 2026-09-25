#!/usr/bin/env python3
"""Hop Male CNS using the 9 predicted VNC sides as observers.

Labels are FSOT predictions (in/out |W| consensus), not EM.
Function test: predicted-L should bias motor L, predicted-R motor R
(same ipsi law as labeled VNC laterality). Leftover five should not
collapse a side (|ipsi|<1/φ).

  python scripts/predicted_side_hops.py
"""
from __future__ import annotations

import runio
runio.install()

import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "vendor"))

from fly_connectome import _PHI, _R_BIO  # noqa: E402
from math_first import _hop2_state, _motor_by_side  # noqa: E402
from trit_alu import trit  # noqa: E402

PRED = ROOT / "data" / "vnc_side_predicted.json"
OUT = ROOT / "data" / "predicted_side_hops.json"
INV_PHI = 1.0 / float(_PHI)


def main() -> int:
    from male_cns import load_male_graph

    pred_doc = json.loads(PRED.read_text(encoding="utf-8"))
    L = [p["bodyId"] for p in pred_doc["predicted"] if p["predict_consensus"] == "L"]
    R = [p["bodyId"] for p in pred_doc["predicted"] if p["predict_consensus"] == "R"]
    Z = [p["bodyId"] for p in pred_doc["leftover"]]
    print("  load Male CNS", flush=True)
    graph = load_male_graph()
    idx = graph["idx"]

    def seed(ids: list[str]) -> list[int]:
        return [idx[i] for i in ids if i in idx]

    programs = []
    for name, ids, expect in (
        ("predicted_L", L, 1),
        ("predicted_R", R, -1),
        ("leftover_5", Z, 0),
        ("predicted_all_9", L + R, 0),
    ):
        si = seed(ids)
        print(f"== {name} n_seed={len(si)} ids={ids}", flush=True)
        a = _hop2_state(graph, si)
        mass = _motor_by_side(a, graph)
        bias = float(mass["ipsi_bias"])
        sgn = trit(1 if bias > 0 else (-1 if bias < 0 else 0))
        leftover = abs(bias) <= INV_PHI
        if expect == 0:
            ok = leftover
        else:
            ok = (sgn == expect) or leftover
        programs.append(
            {
                "name": name,
                "n_seed": len(si),
                "bodyIds": ids,
                "expect_yaw_trit": expect,
                "hop2": mass,
                "yaw_trit": 0 if leftover else sgn,
                "ipsi_leftover": leftover,
                "function_ok": ok,
                "label": "predicted_not_EM",
            }
        )
        print(
            f"  vnc_motor={mass['vnc_motor']:.3f} L={mass['vnc_motor_L']:.3f} "
            f"R={mass['vnc_motor_R']:.3f} ipsi={bias:.3f} leftover={leftover} ok={ok}",
            flush=True,
        )
    pL = next(p for p in programs if p["name"] == "predicted_L")
    pR = next(p for p in programs if p["name"] == "predicted_R")
    ipsi_pair = (float(pL["hop2"]["ipsi_bias"]) > 0) and (float(pR["hop2"]["ipsi_bias"]) < 0)
    overall = all(p["function_ok"] for p in programs) and ipsi_pair
    doc = {
        "pin": "AEB2AD",
        "residual_Biochemistry": _R_BIO,
        "free_parameters": 0,
        "mechanic": (
            "Predicted VNC sides as hop seeds. Same ipsi law as labeled "
            "vnc_sensory_L/R. Not EM labels."
        ),
        "n_predicted_L": len(L),
        "n_predicted_R": len(R),
        "n_leftover": len(Z),
        "programs": programs,
        "ipsi_pair": ipsi_pair,
        "overall_ok": overall,
        "compare_labeled": {
            "vnc_sensory_L_ipsi": 0.342,
            "vnc_sensory_R_ipsi": -0.362,
        },
    }
    OUT.write_text(json.dumps(doc, indent=2), encoding="utf-8")
    print(f"  ipsi_pair={ipsi_pair} overall_ok={overall}")
    print(f"  wrote {OUT}")
    return 0 if overall else 1


if __name__ == "__main__":
    raise SystemExit(main())
