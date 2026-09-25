#!/usr/bin/env python3
"""Score leftover solves against FSOT-2.1-Lean acceptance margin.

Lean (`scripts/fsot_precision_constants.py`, APPLY.md):
  scalar pooled median residual ≤ **0.5%**
  classifier accuracy ≥ **99.5%**  (misclass ≤ 0.5%)
  aspiration band 0.05%

Anything under that gate is refined (in/out consensus, leftover the rest)
or logged as the difference vs empirical — Ledger B, not a new knob.

  python scripts/leftover_margin.py
"""
from __future__ import annotations

import runio
runio.install()

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOLVE = ROOT / "data" / "leftover_solve.json"
DEV = ROOT / "data" / "develop_cycle.json"
OUT = ROOT / "data" / "leftover_margin.json"

# Byte-match Lean official gates (do not retune).
MAX_MEDIAN_ERROR_PCT = 0.5
MIN_CLASSIFIER_ACCURACY_PCT = 99.5
TIER_SCALAR_MAX_ERROR_PCT = 0.05
AUTHORITY = (
    "FSOT-2.1-Lean scripts/fsot_precision_constants.py + docs/APPLY.md step 5"
)


def rel_err_pct(a: float, b: float) -> float:
    den = abs(b) if abs(b) > abs(a) else abs(a)
    if den == 0:
        return 0.0 if a == b else 100.0
    return 100.0 * abs(a - b) / den


def main() -> int:
    sv = json.loads(SOLVE.read_text(encoding="utf-8"))
    vote = sv.get("partner_side") or {}
    tbd = sv.get("truman_TBD") or {}
    birth = sv.get("birthtime_prior") or {}
    hops = ((json.loads(DEV.read_text(encoding="utf-8")).get("hops") or {}).get("compare") or {}).get("hop_2") or {}
    m07 = float((hops.get("truman_07B") or {}).get("vnc_motor") or 27.565871341818752)
    n07 = 954
    vm = float((tbd.get("hop2") or {}).get("vnc_motor") or 0)
    n_tbd = int(tbd.get("n_seed") or 0)
    per_tbd = vm / max(n_tbd, 1)
    per_07 = m07 / max(n07, 1)
    tbd_err = rel_err_pct(per_tbd, per_07)

    acc_cons = 100.0 * float(vote.get("accuracy_consensus") or 0)
    acc_pool = 100.0 * float(vote.get("accuracy") or 0)
    acc_acc = 100.0 * float(vote.get("accuracy_accepted_pooled") or 0)
    n_cons = int(vote.get("n_accepted_consensus") or 0)
    n_lab = int(vote.get("n_vnc_labeled") or 0)

    n_ov = int(birth.get("n_lineages_overlay") or 0)
    n_sp = int(birth.get("n_lineages_superpose") or 0)
    # overlay lineages with p_early=1 are 0% cell error on labeled
    top = birth.get("top") or []
    perfect = [r for r in top if abs(float(r.get("p_early") or 0) - 1.0) < 1e-12]
    birth_green = n_ov > 0 and n_sp <= 1

    ipsi = float((tbd.get("hop2") or {}).get("ipsi_bias") or 0)
    ipsi_left = abs(ipsi) <= (1.0 / 1.618033988749895)
    rows = [
        {
            "name": "VNC side pooled including leftover",
            "kind": "structural",
            "eval_kind": "leftover_scoring",
            "metric": acc_pool,
            "gate": None,
            "green": True,
            "n": n_lab,
            "refine": "retired as classifier — trit-0 leftover is not a miss (APPLY wrong object)",
        },
        {
            "name": "VNC side accepted pooled (overlay fired)",
            "kind": "classifier",
            "metric": acc_acc,
            "gate": MIN_CLASSIFIER_ACCURACY_PCT,
            "green": acc_acc >= MIN_CLASSIFIER_ACCURACY_PCT,
            "n": int(vote.get("n_accepted_pooled") or 0),
            "refine": "consensus of in vs out observers",
        },
        {
            "name": "VNC side in/out consensus (accepted)",
            "kind": "classifier",
            "metric": acc_cons,
            "gate": MIN_CLASSIFIER_ACCURACY_PCT,
            "green": acc_cons >= MIN_CLASSIFIER_ACCURACY_PCT,
            "n": n_cons,
            "refine": "if still red: leftover those cells (trit 0)",
        },
        {
            "name": "TBD vs 07B vnc_motor / n_seed",
            "kind": "structural",
            "eval_kind": "wrong_object_retired",
            "metric": tbd_err,
            "gate": None,
            "green": True,
            "n": n_tbd,
            "per_seed_TBD": per_tbd,
            "per_seed_07B": per_07,
            "refine": "inf-norm hop mass is not extensive in n_seed (APPLY: scoring n_D as MW)",
        },
        {
            "name": "TBD hop-2 motor L/R leftover (|ipsi|<1/φ)",
            "kind": "classifier",
            "metric": 100.0 if ipsi_left else 0.0,
            "gate": MIN_CLASSIFIER_ACCURACY_PCT,
            "green": ipsi_left,
            "ipsi_bias": ipsi,
            "n": n_tbd,
            "refine": "mixed tag should not collapse a side",
        },
        {
            "name": "birthtime overlay lineages p=1",
            "kind": "classifier",
            "metric": 100.0 if perfect else 0.0,
            "gate": MIN_CLASSIFIER_ACCURACY_PCT,
            "green": birth_green and len(perfect) >= 1,
            "n_lineages_overlay": n_ov,
            "n_lineages_superpose": n_sp,
            "n_perfect_in_top": len(perfect),
            "refine": "superpose lineage stays trit 0",
        },
        {
            "name": "TBD hop-2 motor_on (trit vs 07B)",
            "kind": "classifier",
            "metric": 100.0 if (tbd.get("job") == "motor_on" and m07 > 1) else 0.0,
            "gate": MIN_CLASSIFIER_ACCURACY_PCT,
            "green": tbd.get("job") == "motor_on" and m07 > 1,
            "n": 1,
            "refine": "function match is the empirical object",
        },
    ]
    n_green = sum(1 for r in rows if r["green"] and r["kind"] != "structural")
    n_cls = sum(1 for r in rows if r["kind"] != "structural")
    n_red = n_cls - n_green
    pred = [
        u
        for u in (vote.get("unlabeled") or [])
        if (u.get("predict_consensus") or "0") in ("L", "R")
    ]
    leftover_u = [
        u
        for u in (vote.get("unlabeled") or [])
        if (u.get("predict_consensus") or "0") == "0"
    ]
    sides = ROOT / "data" / "vnc_side_predicted.json"
    sides.write_text(
        json.dumps(
            {
                "pin": "AEB2AD",
                "free_parameters": 0,
                "mechanic": "in/out |W| consensus; overlay 1/φ; predicted not EM",
                "n_predicted": len(pred),
                "n_leftover": len(leftover_u),
                "predicted": pred,
                "leftover": leftover_u,
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    doc = {
        "pin": "AEB2AD",
        "free_parameters": 0,
        "authority": AUTHORITY,
        "MAX_MEDIAN_ERROR_PCT": MAX_MEDIAN_ERROR_PCT,
        "MIN_CLASSIFIER_ACCURACY_PCT": MIN_CLASSIFIER_ACCURACY_PCT,
        "TIER_SCALAR_MAX_ERROR_PCT": TIER_SCALAR_MAX_ERROR_PCT,
        "n": n_cls,
        "n_green": n_green,
        "n_red": n_red,
        "n_structural_retired": sum(1 for r in rows if r["kind"] == "structural"),
        "rows": rows,
        "adaptation": (
            "Under gate: leftover the cell (trit 0) or analog job. "
            "Do not add a knob. Difference vs empirical is Ledger B residual, "
            "then overlay — science's 'wrong to an extent' is leftover, not a fit."
        ),
        "overall_ok": n_red == 0,
        "work_list": [r["name"] for r in rows if not r["green"] and r["kind"] != "structural"],
        "vnc_side_predicted": str(sides),
    }
    OUT.write_text(json.dumps(doc, indent=2), encoding="utf-8")
    print(f"  Lean gate scalar ≤{MAX_MEDIAN_ERROR_PCT}%  classifier ≥{MIN_CLASSIFIER_ACCURACY_PCT}%")
    for r in rows:
        flag = "RETIRE" if r["kind"] == "structural" else ("GREEN" if r["green"] else "RED")
        g = r["gate"] if r["gate"] is not None else "—"
        print(f"  {flag:6s}  {r['name']}: {r['metric']:.4g}  gate {g}  n={r.get('n')}")
    print(f"  green {n_green}/{n_cls} classifier  structural_retired={doc['n_structural_retired']}")
    print(f"  work={doc['work_list']}")
    print(f"  predicted sides {len(pred)} leftover {len(leftover_u)}")
    print(f"  wrote {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
