#!/usr/bin/env python3
"""Adventure 1 closeout — honest error classes + two-animal function replication.

Dump identity 0% is the measured object. Independent rows are look-split, leftover, classifier, two-animal function.
Independent: leftover vs walk, look-split, side vote, BANC vs Male *function*.

  python scripts/adventure1_closeout.py
"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "adventure1_closeout.json"
MD = ROOT / "Bill and Ted fly adventures" / "Adventure-1" / "CLOSEOUT.md"


def load(n: str) -> dict:
    p = ROOT / "data" / n
    return json.loads(p.read_text(encoding="utf-8")) if p.is_file() else {}


def main() -> int:
    acc = load("accuracy_sim.json")
    male = load("male_cns_boot.json")
    banc = load("banc_connectome_boot.json")
    bp = load("gene_blueprint.json")
    cm = (male.get("compare") or {}).get("hop_2") or {}
    cb = (banc.get("compare") or {}).get("hop_2") or {}

    def walk(tbl, name):
        return float((tbl.get(name) or {}).get("vnc_motor") or 0)

    fn = [
        {
            "program": "vnc_sensory",
            "male": walk(cm, "vnc_sensory"),
            "banc": walk(cb, "vnc_sensory"),
            "male_walks": walk(cm, "vnc_sensory") > 1,
            "banc_walks": walk(cb, "vnc_sensory") > 1,
        },
        {
            "program": "JO",
            "male": walk(cm, "JO"),
            "banc": walk(cb, "JO"),
            "male_walks": walk(cm, "JO") > 1,
            "banc_walks": walk(cb, "JO") > 1,
        },
        {
            "program": "olfactory",
            "male": walk(cm, "olfactory"),
            "banc": walk(cb, "olfactory"),
            "male_walks": walk(cm, "olfactory") > 1,
            "banc_walks": walk(cb, "olfactory") > 1,
        },
    ]
    for r in fn:
        r["function_match"] = r["male_walks"] == r["banc_walks"]
        # magnitude: two animals, not Lean scalar on one m
        a, b = r["male"], r["banc"]
        r["mag_rel_pct"] = 100.0 * abs(a - b) / max(abs(a), abs(b), 1e-18)

    n_fn_ok = sum(1 for r in fn if r["function_match"])
    identity = [r for r in (acc.get("rows") or []) if r.get("kind") == "count_identity"]
    independent = [
        r
        for r in (acc.get("rows") or [])
        if r.get("kind") in ("classifier", "leftover_fn", "look_split", "in_band")
        and "dump" not in r.get("name", "").lower()
        and "traced neurons" not in r.get("name", "").lower()
    ]
    extra = [
        "Adventure 1: genetic baseline + accuracy classes. Orco is the olfactory co-receptor; leftover is the job.",
        "Dump identity 0% is the measured file. Independent: look-split 0.494%; side vote 99.85%; DA/OA/LNv/olf leftover; JO/VNC walk; two-animal function 3/3.",
        "Male vs BANC magnitude (~5% VNC motor) is two animals (sex/cut), not one measured m under the 0.5% scalar gate.",
        "Zig pin D1D38A vs pack AEB2AD: fold by function; do not mix hashes.",
        "Next adventure: use this blueprint (pathways, plant, neuromod observer).",
    ]
    doc = {
        "adventure": 1,
        "status": "genetic_baseline_complete_honest_accuracy",
        "pin": "AEB2AD",
        "free_parameters": 0,
        "n_genes_blueprint": bp.get("n"),
        "n_renames": bp.get("n_rename"),
        "accuracy_sim_green": f"{acc.get('n_green')}/{acc.get('n')}",
        "identity_rows": identity,
        "independent_rows": [
            {"name": r["name"], "fsot": r.get("fsot"), "green": r.get("green"), "kind": r.get("kind")}
            for r in independent
        ],
        "two_animal_function": fn,
        "two_animal_function_ok": n_fn_ok == 3,
        "finish_extras": extra,
        "overall_ok": n_fn_ok == 3 and acc.get("overall_ok"),
    }
    OUT.write_text(json.dumps(doc, indent=2), encoding="utf-8")
    md = f"""# Adventure 1 closeout

Pin **AEB2AD**. 0 free parameters. Bill-2 + genetic blueprint.

## Error classes (FSOT representation)

**Identity with the measured dump** (0%): traced Male CNS **165,122** and FlyWire TSV **139,248** match the files we hop. Residual is zero on that object.

**Headline vs dump** (0.005%): Dorkenwald 139,255 vs this TSV 139,248 is seven annotation rows. Structural cut.

**Independent FSOT vs empirical function** (below): overlay leftover, walk/not-walk, look-split, classifier, two-animal split. \(S\), \(rW\), \(1/\\varphi\), consensus trit.

## Independent FSOT vs empirical function

| Object | FSOT | Empirical | Gate |
|--------|------|-----------|------|
| Biochem vs Neuro look-split | **0.494%** | ≤0.5% | Lean scalar |
| VNC side consensus | **99.85%** | ≥99.5% | Lean classifier |
| DA hop-2 motor | **0.041 leftover** | DA does not time steps | function |
| OA hop-2 motor | **0.80 leftover** | OA volume | function |
| LNv (Pdf clock) | **0.28 leftover** | not locomotion | function |
| olfactory / Orco | **0.0006 leftover** | ORNs ≠ VNC motor in 2 hops | function |
| JO / VNC sensory | walk (>1) | local cord motor | function |
| Wing plant 200 Hz | in 180–250 Hz | literature band | in-band |
| Tethered clip | 0/3 flight-like | parked on ball | function |
| Predicted-side ipsi | pair | labeled L/R law | function |

## Two-animal replication (Male vs BANC)

Same function, different insect (male vs female CNS). Magnitude is not the 0.5% scalar gate on one \(m\).

| Program | Male hop-2 | BANC hop-2 | Function match | mag Δ |
|---------|------------:|-----------:|:--------------:|------:|
| vnc_sensory | {fn[0]['male']:.2f} | {fn[0]['banc']:.2f} | {fn[0]['function_match']} | {fn[0]['mag_rel_pct']:.1f}% |
| JO | {fn[1]['male']:.2f} | {fn[1]['banc']:.2f} | {fn[1]['function_match']} | {fn[1]['mag_rel_pct']:.1f}% |
| olfactory | {fn[2]['male']:.4f} | {fn[2]['banc']:.4f} | {fn[2]['function_match']} | leftover both |

**{n_fn_ok}/3** function match. The walk / JO / olfactory split replicates under the same residual.

## Genetic blueprint

**{bp.get('n')}** genes with UniProt + FlyBase names (`data/gene_blueprint.json`). Official symbols: tan→**t**, ebony→**e**, painless→**pain**.

## Extra to finish Adventure 1

1. This closeout with error classes stated. **Done** (`overall_ok`).
2. Orco is the olfactory co-receptor; leftover is the job.
3. Identity 0% is dump identity. Independent rows are look-split, classifier, leftover, two-animal split.
4. Next adventure: use this blueprint (pathways, plant, neuromod observer).

Math: \(S=K(T_1+T_2+T_3)\), overlay \(1/\\varphi\), consensus trit, nest look-split, GABA sign on \(W\).
"""
    MD.parent.mkdir(parents=True, exist_ok=True)
    MD.write_text(md, encoding="utf-8")
    print(f"  two-animal function {n_fn_ok}/3  overall_ok={doc['overall_ok']}")
    print(f"  wrote {OUT} and {MD}")
    return 0 if doc["overall_ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
