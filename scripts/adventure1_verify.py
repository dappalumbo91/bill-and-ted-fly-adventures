#!/usr/bin/env python3
"""Adventure 1 blueprint verification — TED vs Bill, not a new adventure.

TED-3 is the genetic/FSOT blueprint on the same Adventure 1 organism.
A Bill promotes only if this TED keeps Bill-2 hop function, Lean gates,
and 0 free parameters.

  python scripts/adventure1_verify.py
  python scripts/bill_ted.py ted-3
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "adventure1_verify.json"
TED = ROOT / "Bill and Ted fly adventures" / "TED-3" / "EXPERIMENT.json"
MD = ROOT / "Bill and Ted fly adventures" / "Adventure-1" / "CLOSEOUT.md"
PIN = ROOT / "vendor" / "fsot_compute.py"

MAX_MEDIAN = 0.5
MIN_CLS = 99.5
PHI = 1.618033988749895


def load(name: str) -> dict:
    p = ROOT / "data" / name
    return json.loads(p.read_text(encoding="utf-8")) if p.is_file() else {}


def hop2(d: dict, program: str, field: str = "vnc_motor") -> float:
    rec = ((d.get("compare") or {}).get("hop_2") or {}).get(program) or {}
    return float(rec.get(field) or 0.0)


def near(a: float, b: float, eps: float) -> bool:
    return abs(float(a) - float(b)) <= eps


def main() -> int:
    male = load("male_cns_boot.json")
    banc = load("banc_connectome_boot.json")
    a1 = load("adventure1.json")
    fold = load("adventure1_fold.json")
    acc = load("accuracy_sim.json")
    mg = load("leftover_margin.json")
    a1c = load("adventure1_closeout.json")
    a1f = load("adventure1_fsot_apply.json")
    a1b = load("adventure1_fsot_blueprint.json")
    guard = load("neural_guardrails.json")
    pep = load("peptide_leftovers.json")
    bp = load("gene_blueprint.json")

    pin_sha = hashlib.sha256(PIN.read_bytes()).hexdigest().upper()
    nt = {h["nt"]: h for h in (a1.get("neuromod_hops") or [])}
    walk = hop2(male, "vnc_sensory")
    walk_phi = walk / PHI
    da = float(((nt.get("dopamine") or {}).get("hop2") or {}).get("vnc_motor") or 9)
    oa = float(((nt.get("octopamine") or {}).get("hop2") or {}).get("vnc_motor") or 9)
    ht = float(((nt.get("serotonin") or {}).get("hop2") or {}).get("vnc_motor") or 9)
    gaba = float(((nt.get("gaba") or {}).get("hop2") or {}).get("vnc_motor") or 0)
    ln = float((((pep.get("LNv_hop") or {}).get("hop2") or {}).get("vnc_motor") or 9))
    look = float((a1b.get("scalar") or fold).get("look_split_pct") or fold.get("look_split_pct") or 99)
    orco = a1b.get("orco") or {}

    checks = []

    def add(name: str, ok: bool, detail, kind: str) -> None:
        checks.append({"name": name, "ok": bool(ok), "detail": detail, "kind": kind})

    add("pin AEB2AD", pin_sha.startswith("AEB2AD"), pin_sha[:16], "pin")
    add("0 free parameters", male.get("free_parameters") == 0 and a1b.get("free_parameters") == 0, 0, "law")
    add("Male VNC walk (Bill-2)", near(hop2(male, "vnc_sensory"), 10.74, 0.02) and hop2(male, "vnc_sensory") > 1, hop2(male, "vnc_sensory"), "bill_function")
    add("Male JO walk (Bill-2)", near(hop2(male, "JO"), 7.77, 0.02) and hop2(male, "JO") > 1, hop2(male, "JO"), "bill_function")
    add("Male olfactory leftover (Bill-2)", hop2(male, "olfactory") < 0.01, hop2(male, "olfactory"), "bill_function")
    add("BANC VNC walk", hop2(banc, "vnc_sensory") > 1 and near(hop2(banc, "vnc_sensory"), 10.16, 0.02), hop2(banc, "vnc_sensory"), "bill_function")
    add("BANC JO walk", hop2(banc, "JO") > 1, hop2(banc, "JO"), "bill_function")
    add("BANC olfactory leftover", hop2(banc, "olfactory") < 0.01, hop2(banc, "olfactory"), "bill_function")
    add("DA volume leftover", da < 1.0, da, "bill_function")
    add("OA volume leftover", oa < 1.0, oa, "bill_function")
    add("5HT < walk/φ", ht < walk_phi, {"ht": ht, "walk_phi": walk_phi}, "bill_function")
    add("GABA signed brake on W", gaba > 1.0, gaba, "bill_function")
    add("LNv leftover", ln < 1.0, ln, "bill_function")
    add("volume leftover vs VNC walk", bool(a1.get("volume_weaker_than_vnc_walk")), True, "bill_function")
    add("two-animal function 3/3", bool(a1c.get("two_animal_function_ok")), a1c.get("two_animal_function_ok"), "bill_function")
    add("Lean leftover_margin", bool(mg.get("overall_ok")) and float(mg.get("MAX_MEDIAN_ERROR_PCT") or 0) == MAX_MEDIAN and float(mg.get("MIN_CLASSIFIER_ACCURACY_PCT") or 0) == MIN_CLS, mg.get("n_green"), "lean")
    add("look-split ≤0.5%", look <= MAX_MEDIAN, look, "lean")
    add("accuracy_sim", bool(acc.get("overall_ok")), acc.get("n_green"), "lean")
    add("Ledger B median ≤0.5%", bool(a1f.get("overall_ok")) and float(a1f.get("median_error_pct") or 9) <= MAX_MEDIAN, a1f.get("median_error_pct"), "lean")
    add("blueprint 120/120", int(a1b.get("n_genes_ok") or 0) == int(a1b.get("n_genes") or 0) and int(a1b.get("n_genes") or 0) >= 120, f"{a1b.get('n_genes_ok')}/{a1b.get('n_genes')}", "ted_extend")
    add("pathways 5/5", int(a1b.get("n_pathways_ok") or 0) >= 5 and bool(a1b.get("overall_ok")), a1b.get("n_pathways_ok"), "ted_extend")
    add("Orco leftover hop", bool(orco.get("ok")) and float(orco.get("vnc_motor") or 9) < 1.0, orco.get("vnc_motor"), "ted_extend")
    add("F02 transmitter AA unique opcodes", bool(a1b.get("trinary_unique")), True, "ted_extend")
    add("innexin consensus trit", int(a1b.get("n_innexin_consensus") or 0) >= 3, a1b.get("n_innexin_consensus"), "ted_extend")
    add("fru/dsx DENY T1 off", bool(a1b.get("deny_fru_dsx")), True, "guardrail")
    add(
        "human-facing intended use",
        (guard.get("intended_use") or "").startswith("human-facing")
        and (guard.get("deny_default_seeds") or {}).get("courtship", {}).get("default") == "off",
        guard.get("deny_family"),
        "guardrail",
    )
    add("gene blueprint n=120", int(bp.get("n") or 0) >= 120, bp.get("n"), "ted_extend")
    add("fold 9/9 enzymes", bool(fold.get("overall_ok")) and int(fold.get("n_ok") or 0) >= 9, fold.get("n_ok"), "ted_extend")

    n_ok = sum(1 for c in checks if c["ok"])
    n_fail = [c["name"] for c in checks if not c["ok"]]
    promotes = n_ok == len(checks)
    doc = {
        "adventure": 1,
        "ted": "TED-3",
        "vs_bill": "Bill-2",
        "promote_to": "Bill-3" if promotes else None,
        "role": "verification_not_new_adventure",
        "pin": "AEB2AD",
        "pin_sha256_16": pin_sha[:16],
        "free_parameters": 0,
        "law": "S=K(T1+T2+T3); r=1+|S|P_NEW; overlay 1/φ; consensus trit; F02; Ledger B",
        "n": len(checks),
        "n_ok": n_ok,
        "fail": n_fail,
        "checks": checks,
        "bill_function_ok": all(c["ok"] for c in checks if c["kind"] == "bill_function"),
        "lean_ok": all(c["ok"] for c in checks if c["kind"] == "lean"),
        "ted_extend_ok": all(c["ok"] for c in checks if c["kind"] == "ted_extend"),
        "promotes": promotes,
        "overall_ok": promotes,
        "why": (
            "Blueprint through FSOT extends Bill-2 without new knobs. "
            "Hop function (walk/JO on, olf/DA/OA leftover) holds. Lean 0.5%/99.5% hold. "
            "Not Adventure 2."
            if promotes
            else f"TED-3 does not promote; fail={n_fail}"
        ),
    }
    OUT.write_text(json.dumps(doc, indent=2), encoding="utf-8")
    TED.parent.mkdir(parents=True, exist_ok=True)
    TED.write_text(
        json.dumps(
            {
                "id": "TED-3",
                "role": "ted",
                "adventure": 1,
                "change": "genetic blueprint through FSOT (F02, residual hops, overlay, trit) as verification of Adventure 1",
                "vs_bill": "Bill-2 neuromod volume leftover + VNC/JO walk",
                "promotes": promotes,
                "promote_to": "Bill-3" if promotes else None,
                "n_ok": n_ok,
                "n": len(checks),
                "fail": n_fail,
                "why": doc["why"],
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    print(f"  TED-3 vs Bill-2  {n_ok}/{len(checks)}  promotes={promotes}")
    for c in checks:
        flag = "OK" if c["ok"] else "FAIL"
        print(f"  {flag:4s}  {c['name']}: {c['detail']}")
    print(f"  wrote {OUT}")
    print(f"  wrote {TED}")

    section = "## TED-3 verification (still Adventure 1)"
    extra = [
        "",
        section,
        "",
        f"Blueprint is **not** Adventure 2. It is TED-3 vs Bill-2: same law, 0 free parameters.",
        "",
        f"Checks **{n_ok}/{len(checks)}**. Bill function hold. Lean 0.5%/99.5% hold. **promotes={promotes}** → **{'Bill-3' if promotes else 'Bill-2 stays'}**.",
        "",
        doc["why"],
        "",
    ]
    if MD.is_file():
        prev = MD.read_text(encoding="utf-8")
        if section in prev:
            prev = prev.split(section)[0].rstrip()
        MD.write_text(prev + "\n" + "\n".join(extra), encoding="utf-8")
    return 0 if promotes else 1


if __name__ == "__main__":
    raise SystemExit(main())
