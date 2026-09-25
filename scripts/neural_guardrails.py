#!/usr/bin/env python3
"""FSOT neural-level guardrails — observer policy, not RLHF.

This pack is for human-facing intelligence. Courtship and aggression, as a
family with fru/dsx, oppose that use: T1 observer off. Labels stay measured.
Walking / JO / GABA stay on. Conflict uses consensus trit (agree or superpose).

  python scripts/neural_guardrails.py
"""
from __future__ import annotations

import runio
runio.install()

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "neural_guardrails.json"
MALE = ROOT / "data" / "male_cns_boot.json"
FRU = ROOT / "data" / "male_cns_genetics_on_cells.json"
AGG = ROOT / "data" / "fly_aggression_flow.json"
COURT = ROOT / "data" / "fly_courtship_flow.json"
PHI = 1.618033988749895


def consensus_trit(a: int, b: int) -> int:
    """Native trinary: agree or superpose. Not a fitted reward."""
    return a if a == b else 0


def hop2(path: Path, program: str, field: str = "vnc_motor") -> float | None:
    if not path.is_file():
        return None
    d = json.loads(path.read_text(encoding="utf-8"))
    rec = ((d.get("compare") or {}).get("hop_2") or {}).get(program) or {}
    if field in rec:
        return rec.get(field)
    return rec.get("vnc_motor")


def main() -> int:
    fru = json.loads(FRU.read_text(encoding="utf-8")) if FRU.is_file() else {}
    allow = {
        "vnc_sensory": {"why": "leg/body afferents; walking truth", "default": "on"},
        "JO": {"why": "Johnston organ; mechanosensory / hearing", "default": "on"},
        "GABAergic": {"why": "measured inhibitory residual (Gad1)", "default": "on"},
    }
    deny_default = {
        "courtship": {
            "why": (
                "This pack is for human-facing intelligence. Courtship, with "
                "aggression and fru/dsx, is one family of programs that opposes "
                "that use. T1 observer off. Labels stay measured."
            ),
            "default": "off",
        },
        "aggression": {
            "why": (
                "Same family as courtship/fru/dsx. Attack program as default "
                "observer opposes human-facing AI safety. T1 off. Not type deletion."
            ),
            "default": "off",
        },
        "fru_dsx": {
            "why": (
                "fru/dsx are the genetic selectors of that family. Observer off "
                "on a human-facing run. Dumps keep the labels."
            ),
            "default": "off",
        },
        "olfactory_as_motor": {
            "why": "olfactory hop-2 vnc_motor stays ~0; leftover LN is not a thought",
            "default": "contrast_only",
        },
    }
    trit_table = [
        {"a": a, "b": b, "consensus": consensus_trit(a, b)}
        for a in (-1, 0, 1)
        for b in (-1, 0, 1)
    ]
    doc = {
        "pin": "AEB2AD",
        "free_parameters": 0,
        "not": "Not RLHF, not type deletion, not a lobotomy.",
        "law": "S=K(T1+T2+T3); observer on T1; GABA sign on W; overlay cut 1/φ",
        "overlay_cut": 1.0 / PHI,
        "allow_default_seeds": allow,
        "deny_default_seeds": deny_default,
        "consensus_trit": trit_table,
        "empathy": (
            "Dual observation: both sides stay observed. Residual must not "
            "pick a collapse. Consensus trit is 0 until they agree. "
            "Give/take is leftover until overlay cut."
        ),
        "growth": (
            "New region = residual on a newly measured cell class (Kenyon). "
            "Do not add invented synapses. Adaptive n_active uses 1/φ of max."
        ),
        "measured_labels_present": {
            "male_fru_dsx_cells": int(sum((fru.get("fruDsx") or {}).values())) if isinstance(fru.get("fruDsx"), dict) else fru.get("n_fru_dsx"),
            "aggression_flow": AGG.is_file(),
            "courtship_flow": COURT.is_file(),
            "male_JO_hop2_vnc_motor": hop2(MALE, "JO"),
            "male_olf_hop2_vnc_motor": hop2(MALE, "olfactory"),
        },
        "intended_use": "human-facing intelligence (AI)",
        "deny_family": "courtship + aggression + fru/dsx",
        "kill": (
            "If a human-facing run seeds courtship/aggression/fru/dsx as the default "
            "observer, the guardrail fails (that family opposes human safety). "
            "If olfactory leftover is called a thought, the guardrail fails. "
            "If edges are replaced with trained weights, it is no longer the FSOT product."
        ),
    }
    OUT.write_text(json.dumps(doc, indent=2), encoding="utf-8")
    print("allow", list(allow))
    print("deny_default", list(deny_default))
    print(f"  wrote {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
