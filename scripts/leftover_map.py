#!/usr/bin/env python3
"""Map every leftover we still owe — overlay, hubs, unlabeled, missing dumps.

Leftover in FSOT is not a bug: |x| ≤ 1/φ, unlabeled, unpublished, or cons=0.
We map it. We do not invent a join, a pupal movie, or a wingbeat.

  python scripts/leftover_map.py
"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "leftover_map.json"
PHI = 1.618033988749895
INV_PHI = 1.0 / PHI
INV_PHI2 = 1.0 / (PHI * PHI)


def load(name: str) -> dict:
    p = ROOT / "data" / name
    if not p.is_file():
        return {}
    return json.loads(p.read_text(encoding="utf-8"))


def row(kind: str, name: str, status: str, n, mechanic: str, do: str) -> dict:
    return {
        "kind": kind,
        "name": name,
        "status": status,
        "n": n,
        "mechanic": mechanic,
        "do": do,
    }


def main() -> int:
    male = load("male_cns_boot.json")
    phot = load("phot1_map.json")
    ident = load("type_identity.json")
    dev = load("develop_cycle.json")
    yaw = load("yaw_jo.json")
    func = load("fly_function.json")
    sleep = load("fly_sleep_flow.json")
    arithc = load("arith_count.json")
    steps = load("arith_steps.json")
    stress = load("stress_map.json")
    miss = load("math_first.json")
    hemi = load("hemibrain_connectome_boot.json")

    inv = (dev.get("inventory") or {})
    n_traced = int(male.get("n_neurons") or 165122)
    n_birth = int(inv.get("male_n_with_birthtime") or 0)
    n_truman = int(inv.get("male_truman_hemilineage_n") or 0)
    n_ito = int(inv.get("male_ito_lee_n") or 0)
    truman_tbd = int((inv.get("male_truman_top") or {}).get("TBD") or 0)
    vnc_unlab = 14
    jo_silent = 669
    phot_left = float(phot.get("leftover") or 0)
    frac_sleep = float(((sleep.get("observer") or {}).get("frac_sleep")) or 0)
    hemi_gaba = int(hemi.get("n_gaba") or 0)
    only_male = int(ident.get("only_male_type_names") or 0)
    only_banc = int(ident.get("only_banc_type_names") or 0)
    seed_left = bool(yaw.get("seed_leftover"))
    n_cons0 = int((load("trit_expr.json") or {}).get("consensus_zero_stress") or 0)
    n_mean_left = int((miss.get("miss_audit") or {}).get("n_mean_laterality_leftover") or 0)
    do_not = stress.get("do_not_expand") or []
    n_flight = int(func.get("n_trials_flight_like") or 0)
    types = (func.get("types") or {}).get("counts") or {}

    items = [
        row("overlay", "trial-mean (R−L) laterality", "mapped", n_mean_left,
            "fromS under 1/φ on all 3 clips — do not collapse heading from the mean",
            "use per-frame trit"),
        row("overlay", "JO n_seed L vs R (348 vs 324)", "mapped", seed_left,
            "imbalance 24/336 < 1/φ — do not yaw from cell count",
            "yaw from unilateral ipsi_bias sign"),
        row("consensus", "T001 vs Fly02 heading", "mapped", n_cons0,
            "cons(left, right)=0 superposition",
            "do not vote"),
        row("consensus", "bilateral JO", "mapped", 0,
            "JO_L +1 ∧ JO_R −1 → cons 0 straight",
            "one ear off to yaw"),
        row("hub", "olfactory il3LN6", "mapped", 1319.5,
            "hop-1 collapse leftover LN — not a thought",
            "do not expand"),
        row("hub", "Kenyon APL / KCg-s1 / MBp3", "mapped", 963.5,
            "MB leftover hub / precursor does not light vnc_motor",
            "do not expand"),
        row("hub", "JO hop-1 silent cells", "mapped", jo_silent,
            "672−3=669 below overlay after hop-1; 3 active = DNg29 bottleneck",
            "command bottleneck DNg29 is the expansion candidate"),
        row("unlabeled", "VNC sensory without rootSide", "mapped", vnc_unlab,
            "6365 − (3185+3166) = 14",
            "keep unlabeled; do not impute side"),
        row("unlabeled", "Male traced without birthtime", "mapped", n_traced - n_birth,
            f"{n_traced}−{n_birth} unlabeled birth",
            "hops only on labeled early/late"),
        row("unlabeled", "Male without Truman hemilineage", "mapped", n_traced - n_truman,
            f"{n_traced}−{n_truman}",
            "hops on labeled lineages only"),
        row("unlabeled", "Truman tag TBD", "mapped", truman_tbd,
            "named leftover in the dump, not a lineage",
            "do not treat TBD as 07B"),
        row("unlabeled", "Male without Ito–Lee hemilineage", "mapped", n_traced - n_ito,
            f"{n_traced}−{n_ito}",
            "same"),
        row("unlabeled", "type names only-Male / only-BANC", "mapped",
            {"only_male": only_male, "only_banc": only_banc},
            "Jaccard 0.471 — class identity not a merged graph",
            "do not merge synapses"),
        row("product", "PHOT1 kinase/linker leftover", "mapped", phot_left,
            f"cov 0.29, leftover {phot_left:.3f} > 1/φ²={INV_PHI2:.3f} — domains only",
            "not full-chain product, not MDS"),
        row("product", "Genetics Cα campaign freeze", "sibling", "0.13 Å vs AF 0.47",
            "pack pin AEB2AD; campaign pin D1D38A",
            "do not silently re-run as this pack"),
        row("horizon", "hop leftover round(φ⁵)", "mapped", 11,
            "horizon not a fitted T",
            "stop at 11"),
        row("sleep", "DAM leftover-long inactivity", "mapped", frac_sleep,
            "sleep is leftover rest on measured beams",
            "not a 5-min free cut"),
        row("unsigned", "hemibrain no predictedNt / n_gaba", "mapped", hemi_gaba,
            "unsigned residual; DNg29 absent",
            "do not mix 2.68 desc with 7.77 vnc_motor"),
        row("parked", "tethered wing hinges", "mapped", n_flight,
            "400 Hz clip, peak 4–9 Hz, not 200 Hz band",
            "plant is simulated command→sinusoid"),
        row("missing", "haltere named types", "mapped", int(types.get("haltere_type_substr") or 0),
            "count 0 in Male CNS types",
            "wait for a dump; do not invent"),
        row("missing", "type string 'wing'", "mapped", int(types.get("wing_type_substr") or 0),
            "count 0; hg* MN are the steering muscles",
            "use hg3 / DNp01"),
        row("missing", "free-flight 3D wingbeat", "blocked", None,
            "no time series on disk",
            "do not synthesize a 200 Hz clip and call it measured"),
        row("missing", "embryo→pupa synapse movie", "refused", None,
            "does not exist; two snapshots + hemilineage",
            "do not interpolate metamorphosis synapses"),
        row("missing", "Fly Cell Atlas → bodyId", "refused", None,
            "none published",
            "genes sit on classes, not invented bodyIds"),
        row("missing", "Codex api_token CSV", "blocked", None,
            "local type_counts.json is authority",
            "do not scrape the SPA"),
        row("missing", "Berlin walk / ymaze zip", "blocked", None,
            "unauthorized token / corrupt zip on D:",
            "Harvard 3D remains the body"),
        row("missing", "Iwasaki ball-walk videos", "blocked", None,
            "papers cited; videos not on disk",
            "forelimb share ≥ 1/φ analog"),
        row("sibling", "FSOT-Genetics GitHub pin", "sibling", "D1D38A",
            "this pack is AEB2AD",
            "do not mix pins"),
        row("denied", "courtship / aggression default observer", "mapped", "DENY",
            "labels exist; human-facing seed off",
            "not leftover of data — guardrail"),
        row("language", "LLM / coding tokens", "deferred", None,
            "spatial/trit/φ first; ALU and parser exist",
            "not this pack's next observer"),
    ]

    by_kind: dict[str, int] = {}
    by_status: dict[str, int] = {}
    for it in items:
        by_kind[it["kind"]] = by_kind.get(it["kind"], 0) + 1
        by_status[it["status"]] = by_status.get(it["status"], 0) + 1

    mapped = sum(1 for i in items if i["status"] == "mapped")
    doc = {
        "pin": "AEB2AD",
        "free_parameters": 0,
        "phi": PHI,
        "overlay": INV_PHI,
        "leftover_floor_1_over_phi2": INV_PHI2,
        "n": len(items),
        "n_mapped": mapped,
        "by_kind": by_kind,
        "by_status": by_status,
        "items": items,
        "rule": (
            "Leftover is mapped when we name the mechanic and the do-not. "
            "Missing dumps stay missing. Do not invent joins."
        ),
        "overall_ok": mapped >= 15 and by_status.get("refused", 0) >= 2,
    }
    OUT.write_text(json.dumps(doc, indent=2), encoding="utf-8")
    print(f"  leftover_map n={doc['n']} mapped={mapped}  by_kind={by_kind}")
    print(f"  by_status={by_status}")
    print(f"  wrote {OUT}")
    return 0 if doc["overall_ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
