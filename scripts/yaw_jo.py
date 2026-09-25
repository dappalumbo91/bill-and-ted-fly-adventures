#!/usr/bin/env python3
"""JO_L vs JO_R yaw — next advice item, measured laterality.

Unilateral JO seed already biases motor ipsilateral (math_first hops).
Bilateral JO (both ears) is consensus of those two trits → 0 → straight.
Cell-count 348 vs 324 is leftover under 1/φ — do not yaw from n_seed.

Wing plant: yaw trit ≠ 0 → opposite-phase wings (already in wing_sim).

  python scripts/yaw_jo.py
"""
from __future__ import annotations

import runio
runio.install()

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
import sys

sys.path.insert(0, str(ROOT / "scripts"))

from trit_alu import consensus, trit  # noqa: E402
from trit_expr import eval_expr  # noqa: E402
from wing_sim import plant  # noqa: E402

OUT = ROOT / "data" / "yaw_jo.json"
MATH = ROOT / "data" / "math_first.json"
PHI = 1.618033988749895
INV_PHI = 1.0 / PHI


def main() -> int:
    hops = (json.loads(MATH.read_text(encoding="utf-8")).get("laterality_hops") or {})
    by = {p["name"]: p for p in (hops.get("programs") or [])}
    if "JO_L" not in by or "JO_R" not in by:
        from paths import need

        need("laterality programs JO_L and JO_R in data/math_first.json", MATH)
    jL = by["JO_L"]["hop2"]
    jR = by["JO_R"]["hop2"]
    nL = int(by["JO_L"]["n_seed"])
    nR = int(by["JO_R"]["n_seed"])
    yaw_L = trit(1 if float(jL["ipsi_bias"]) > 0 else -1)
    yaw_R = trit(1 if float(jR["ipsi_bias"]) > 0 else -1)
    both = consensus(yaw_L, yaw_R)
    # n_seed imbalance leftover?
    mid = 0.5 * (nL + nR)
    seed_imbalance = abs(nL - nR) / (mid + 1e-12)
    seed_leftover = seed_imbalance <= INV_PHI
    env = {"JO_L": nL, "JO_R": nR, "HOPS": 11}
    expr = eval_expr("JO_L - JO_R", env)
    expr_trit = trit(expr)
    pL = plant(24.21, 0.835, yaw_trit=yaw_L)  # JO descending scale from repertoire
    pR = plant(24.21, 0.835, yaw_trit=yaw_R)
    pB = plant(24.21, 0.835, yaw_trit=both)

    tests = []

    def rec(q, got, want):
        tests.append({"q": q, "got": got, "want": want, "ok": got == want})

    rec("JO_L ipsi_bias > 0 → yaw trit +1 (left)", yaw_L, 1)
    rec("JO_R ipsi_bias < 0 → yaw trit −1 (right)", yaw_R, -1)
    rec("bilateral consensus 0 (straight)", both, 0)
    rec("n_seed 348 vs 324 is leftover under 1/φ", seed_leftover, True)
    rec("JO_L - JO_R = 24 (count), trit +1 but leftover so do not collapse", expr, 24)
    rec("unilateral L plant yaws", pL["yaw"], True)
    rec("unilateral R plant yaws", pR["yaw"], True)
    rec("bilateral plant no yaw", pB["yaw"], False)
    rec("unilateral still 200 Hz", pL["in_band"] and pR["in_band"], True)
    rec("ipsi signs opposite", (float(jL["ipsi_bias"]) > 0) and (float(jR["ipsi_bias"]) < 0), True)

    fail = [t["q"] for t in tests if not t["ok"]]
    doc = {
        "pin": "AEB2AD",
        "free_parameters": 0,
        "mechanic": (
            "One JO side on → ipsilateral motor → yaw trit. "
            "Both sides on → consensus 0 → straight. "
            "n_seed imbalance is leftover; hop ipsi_bias sign is the command."
        ),
        "JO_L": {"n_seed": nL, "ipsi_bias": jL["ipsi_bias"], "yaw_trit": yaw_L},
        "JO_R": {"n_seed": nR, "ipsi_bias": jR["ipsi_bias"], "yaw_trit": yaw_R},
        "bilateral_consensus": both,
        "seed_imbalance": seed_imbalance,
        "seed_leftover": seed_leftover,
        "expr_JO_L_minus_JO_R": expr,
        "tests": tests,
        "n": len(tests),
        "n_ok": len(tests) - len(fail),
        "fail": fail,
        "overall_ok": not fail,
        "reverse": "Straight flight: both JO observers on. Yaw: one side leftover-off.",
    }
    OUT.write_text(json.dumps(doc, indent=2), encoding="utf-8")
    print(f"  JO_L yaw={yaw_L}  JO_R yaw={yaw_R}  both={both}  seed_leftover={seed_leftover}")
    print(f"  yaw_jo {doc['n_ok']}/{doc['n']}")
    if fail:
        print("  FAIL", fail)
    print(f"  wrote {OUT}")
    return 0 if doc["overall_ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
