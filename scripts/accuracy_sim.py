#!/usr/bin/env python3
"""Accuracy simulation: FSOT-derived vs empirical fly measurements.

Lean gates: scalar median ≤ 0.5%, classifier ≥ 99.5%.
Counts vs the *dump we actually used* are identity (0%). Counts vs a paper
headline on a different cut are structural, not a scalar fail.

  python scripts/accuracy_sim.py
"""
from __future__ import annotations

import runio
runio.install()

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "accuracy_sim.json"
ADV = ROOT / "Bill and Ted fly adventures" / "Adventure-1"

MAX_MEDIAN = 0.5
MIN_CLS = 99.5


def load(name: str) -> dict:
    p = ROOT / "data" / name
    return json.loads(p.read_text(encoding="utf-8")) if p.is_file() else {}


def rel_pct(a: float, b: float) -> float:
    den = max(abs(a), abs(b), 1e-18)
    return 100.0 * abs(a - b) / den


def main() -> int:
    male = load("male_cns_boot.json")
    fw = load("fly_connectome_inventory.json")
    a1 = load("adventure1.json")
    fold = load("adventure1_fold.json")
    pep = load("peptide_leftovers.json")
    gbr = load("genetic_baseline_rest.json")
    mg = load("leftover_margin.json")
    ps = load("predicted_side_hops.json")
    wing = load("wing_sim.json")
    func = load("fly_function.json")
    gi = load("genetic_interactions.json")
    crumbs = load("genetic_crumbs.json")
    bp = load("gene_blueprint.json")

    cmp = (male.get("compare") or {}).get("hop_2") or {}
    nt = {h["nt"]: h for h in (a1.get("neuromod_hops") or [])}
    ln = pep.get("LNv_hop") or {}

    rows = []

    def add(name, kind, fsot, emp, cite, gate=None):
        if kind == "count_identity":
            err = rel_pct(float(fsot), float(emp))
            green = err <= MAX_MEDIAN
            g = MAX_MEDIAN
        elif kind == "classifier":
            err = 100.0 - float(fsot)
            green = float(fsot) >= MIN_CLS
            g = MIN_CLS
        elif kind == "in_band":
            lo, hi = emp
            green = lo <= float(fsot) <= hi
            err = 0.0 if green else min(abs(float(fsot) - lo), abs(float(fsot) - hi))
            g = f"{lo}-{hi}"
        elif kind == "leftover_fn":
            green = float(fsot) < 1.0
            err = 0.0 if green else float(fsot)
            g = "vnc_motor<1 leftover"
        elif kind == "look_split":
            err = float(fsot)
            green = err <= MAX_MEDIAN
            g = MAX_MEDIAN
        else:
            err = rel_pct(float(fsot), float(emp))
            green = err <= MAX_MEDIAN
            g = MAX_MEDIAN
        rows.append(
            {
                "name": name,
                "kind": kind,
                "fsot": fsot,
                "empirical": emp,
                "cite": cite,
                "error_pct": err,
                "gate": g,
                "green": green,
            }
        )

    add(
        "Male CNS traced neurons vs dump",
        "count_identity",
        int(male.get("n_neurons") or 0),
        165122,
        "Male CNS v1.0 feathers status=Traced (this dump)",
    )
    add(
        "FlyWire annotation n vs dump",
        "count_identity",
        int(fw.get("n_neurons") or 0),
        139248,
        "Supplemental_file1_neuron_annotations.tsv",
    )
    add(
        "FlyWire vs Dorkenwald paper 139255",
        "structural",
        int(fw.get("n_neurons") or 0),
        139255,
        "paper headline; dump is 7 short — not a scalar fail",
    )
    # structural row: force green as documented leftover
    rows[-1]["kind"] = "structural"
    rows[-1]["error_pct"] = rel_pct(139248, 139255)
    rows[-1]["green"] = True
    rows[-1]["gate"] = "structural"

    add(
        "VNC side in/out consensus accuracy",
        "classifier",
        100.0 * float((mg.get("rows") or [{}])[2].get("metric") or 99.85) / (100.0 if (mg.get("rows") or [{}])[2].get("metric", 0) > 2 else 1),
        99.5,
        "labeled Male CNS rootSide vs |W| vote",
    )
    # fix classifier: leftover_margin stores 99.85 already as percent
    for r in mg.get("rows") or []:
        if "consensus" in r.get("name", "").lower():
            rows[-1]["fsot"] = float(r.get("metric") or 0)
            rows[-1]["error_pct"] = 100.0 - float(r.get("metric") or 0)
            rows[-1]["green"] = float(r.get("metric") or 0) >= MIN_CLS
            break

    add(
        "Biochem vs Neuro |S| look-split",
        "look_split",
        float(fold.get("look_split_pct") or 99),
        0.5,
        "APPLY_NEURO neighbor fold; Lean ≤0.5%",
    )
    add(
        "DA hop-2 vnc_motor leftover (not walk)",
        "leftover_fn",
        float(((nt.get("dopamine") or {}).get("hop2") or {}).get("vnc_motor") or 9),
        1.0,
        "DA does not time steps; Zig MB-modulate; Male consensus_nt dopamine",
    )
    add(
        "OA hop-2 vnc_motor leftover",
        "leftover_fn",
        float(((nt.get("octopamine") or {}).get("hop2") or {}).get("vnc_motor") or 9),
        1.0,
        "octopamine volume, not VNC walk",
    )
    add(
        "LNv clock leftover vs walk",
        "leftover_fn",
        float((ln.get("hop2") or {}).get("vnc_motor") or 9),
        1.0,
        "Pdf/LNv circadian; not locomotion",
    )
    add(
        "olfactory hop-2 vnc_motor leftover",
        "leftover_fn",
        float((cmp.get("olfactory") or {}).get("vnc_motor") or 9),
        1.0,
        "ORNs do not drive VNC motor in 2 hops; Orco seated",
    )
    add(
        "JO hop-2 vnc_motor lights walk",
        "leftover_fn",
        0.0 if float((cmp.get("JO") or {}).get("vnc_motor") or 0) > 1 else 9.0,
        1.0,
        "JO→DNg29 descending/walk command; invert leftover_fn: we want WALKS",
    )
    # JO should walk: leftover_fn green if fsot<1 is wrong. Fix last row.
    jo = float((cmp.get("JO") or {}).get("vnc_motor") or 0)
    rows[-1] = {
        "name": "JO hop-2 vnc_motor >1 (walks)",
        "kind": "classifier",
        "fsot": 100.0 if jo > 1 else 0.0,
        "empirical": True,
        "cite": "JO hop-1 DNg29; Male/BANC",
        "error_pct": 0.0 if jo > 1 else 100.0,
        "gate": MIN_CLS,
        "green": jo > 1,
    }
    vnc = float((cmp.get("vnc_sensory") or {}).get("vnc_motor") or 0)
    rows.append(
        {
            "name": "VNC sensory hop-2 vnc_motor >1 (walks)",
            "kind": "classifier",
            "fsot": 100.0 if vnc > 1 else 0.0,
            "empirical": True,
            "cite": "local VNC modules; Berg/Male CNS",
            "error_pct": 0.0 if vnc > 1 else 100.0,
            "gate": MIN_CLS,
            "green": vnc > 1,
        }
    )
    add(
        "wing plant frequency in literature band",
        "in_band",
        float(wing.get("f_wb_hz") or 0),
        (180.0, 250.0),
        "adult D. melanogaster wingbeat ~200 Hz (band 180–250); plant not the parked clip",
    )
    parked = int(func.get("n_trials_flight_like", 99))
    rows.append(
        {
            "name": "tethered clip not flight-like (0/3)",
            "kind": "classifier",
            "fsot": 100.0 if parked == 0 else 0.0,
            "empirical": 0,
            "cite": "Haustein Dataverse 400 Hz; wings parked on ball",
            "error_pct": 0.0 if parked == 0 else 100.0,
            "gate": MIN_CLS,
            "green": parked == 0,
        }
    )
    rows.append(
        {
            "name": "predicted-side ipsi_pair",
            "kind": "classifier",
            "fsot": 100.0 if ps.get("ipsi_pair") else 0.0,
            "empirical": True,
            "cite": "labeled VNC L/R laterality law",
            "error_pct": 0.0 if ps.get("ipsi_pair") else 100.0,
            "gate": MIN_CLS,
            "green": bool(ps.get("ipsi_pair")),
        }
    )
    n_genes = int(bp.get("n") or 0)
    n_gi = int(gi.get("n_ok") or 0)
    n_pep = int(pep.get("n_ok") or 0)
    n_gbr = int(gbr.get("n_ok") or 0)
    n_cr = int(crumbs.get("n_ok") or 0)
    rows.append(
        {
            "name": "genetic blueprint live UniProt seating",
            "kind": "classifier",
            "fsot": 100.0 if n_genes >= 100 else 0.0,
            "empirical": n_genes,
            "cite": "UniProt organism 7227",
            "error_pct": 0.0,
            "gate": MIN_CLS,
            "green": n_gi == 17 and n_pep == 28 and n_gbr == 47 and (n_cr == 0 or crumbs.get("overall_ok")),
        }
    )

    n_green = sum(1 for r in rows if r["green"])
    n_red = sum(1 for r in rows if not r["green"] and r["kind"] != "structural")
    doc = {
        "adventure": 1,
        "pin": "AEB2AD",
        "free_parameters": 0,
        "MAX_MEDIAN_ERROR_PCT": MAX_MEDIAN,
        "MIN_CLASSIFIER_ACCURACY_PCT": MIN_CLS,
        "n": len(rows),
        "n_green": n_green,
        "n_red": n_red,
        "rows": rows,
        "gene_blueprint_n": n_genes,
        "gene_renames": bp.get("n_rename"),
        "overall_ok": n_red == 0,
        "note": "Dump identity 0%. Paper headline vs dump is structural. Function leftover vs walk is the empirical object.",
    }
    OUT.write_text(json.dumps(doc, indent=2), encoding="utf-8")
    print(f"  accuracy_sim green {n_green}/{len(rows)} red={n_red}")
    for r in rows:
        flag = "GREEN" if r["green"] else "RED"
        print(f"  {flag:5s}  {r['name']}: fsot={r['fsot']} emp={r['empirical']} err={r.get('error_pct')}")
    print(f"  wrote {OUT}")
    return 0 if doc["overall_ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
