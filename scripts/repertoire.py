#!/usr/bin/env python3
"""Fly repertoire beyond walking — same residual, many observers.

Walking was first because the treadmill + vnc_motor is a clean measured
readout. The fly also hears, sees, smells, sleeps, handles objects, and
sends descending commands (flight/escape analog). Courtship/aggression
stay off as default.

Not a trained policy. 0 free parameters.

  python scripts/repertoire.py
"""
from __future__ import annotations

import runio
runio.install()

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "repertoire.json"


def hop2(path: Path, program: str) -> dict:
    d = json.loads(path.read_text(encoding="utf-8"))
    rec = ((d.get("compare") or {}).get("hop_2") or {}).get(program) or {}
    top = rec.get("top") or {}
    if isinstance(top, dict):
        top_n = top.get("cell_type") or top.get("name") or ""
    else:
        top_n = str(top or "")
    return {
        "vnc_motor": float(rec.get("vnc_motor") or 0.0),
        "descending": float(rec.get("descending") or 0.0),
        "n_active": rec.get("n_active"),
        "top": top_n,
    }


def shared(path: Path, typ: str) -> dict:
    d = json.loads(path.read_text(encoding="utf-8"))
    for t in d.get("types") or []:
        if t.get("type") == typ:
            return t.get("male") or {}
    return {}


def main() -> int:
    male = ROOT / "data" / "male_cns_boot.json"
    banc = ROOT / "data" / "banc_connectome_boot.json"
    hemi = ROOT / "data" / "hemibrain_connectome_boot.json"
    ken = ROOT / "data" / "kenyon_connectome_boot.json"
    sh = ROOT / "data" / "shared_type_hops.json"
    sleep = json.loads((ROOT / "data" / "fly_sleep_flow.json").read_text(encoding="utf-8"))
    odor = json.loads((ROOT / "data" / "fly_odor_flow.json").read_text(encoding="utf-8"))
    guard = json.loads((ROOT / "data" / "neural_guardrails.json").read_text(encoding="utf-8"))

    jobs = [
        {
            "job": "rest",
            "observer": "no afferent (odor off, motion under MAD+φ)",
            "allow": True,
            "walks": False,
            "male": {"vnc_motor": 0.0, "descending": 0.0, "top": ""},
            "note": "Rest is leftover, not a neuron class.",
        },
        {
            "job": "walk",
            "observer": "vnc_sensory (tarsus / VNC)",
            "allow": True,
            "walks": True,
            "male": hop2(male, "vnc_sensory"),
            "banc": hop2(banc, "vnc_sensory"),
            "note": "First readout: legs exist on Male/BANC VNC.",
        },
        {
            "job": "hear_steer",
            "observer": "JO (Johnston organ)",
            "allow": True,
            "walks": True,
            "male": hop2(male, "JO"),
            "banc": hop2(banc, "JO"),
            "hemi": hop2(hemi, "JO"),
            "note": "Hearing + antennal wind. Hop-1 peaks DNg29. Descending > vnc_motor.",
        },
        {
            "job": "object",
            "observer": "mechanosensory (forelimb / bristle)",
            "allow": True,
            "walks": True,
            "male": hop2(male, "mechanosensory"),
            "note": "Iwasaki ball analog. Tarsal/bristle afferents.",
        },
        {
            "job": "see",
            "observer": "L5 lamina (optic)",
            "allow": True,
            "walks": False,
            "male": {
                "vnc_motor": float((shared(sh, "L5") or {}).get("vnc_motor") or 0),
                "descending": float((shared(sh, "L5") or {}).get("descending") or 0),
                "top": (shared(sh, "L5") or {}).get("top"),
                "n_seed": (shared(sh, "L5") or {}).get("n_seed"),
            },
            "note": "Legs off at hop-2; descending lights (visual DNs). Not vnc_motor walking.",
        },
        {
            "job": "smell",
            "observer": "olfactory ORN",
            "allow": True,
            "walks": False,
            "male": hop2(male, "olfactory"),
            "banc": hop2(banc, "olfactory"),
            "hemi": hop2(hemi, "olfactory"),
            "note": "Leftover LN hub. Contrast only. Not a thought.",
        },
        {
            "job": "mushroom_body",
            "observer": "KCg-m",
            "allow": True,
            "walks": False,
            "male": {
                "vnc_motor": float((shared(sh, "KCg-m") or {}).get("vnc_motor") or 0),
                "descending": float((shared(sh, "KCg-m") or {}).get("descending") or 0),
                "top": (shared(sh, "KCg-m") or {}).get("top"),
            },
            "hemi_kc": hop2(ken, "kc_full_hemibrain") if ken.is_file() else hop2(hemi, "kenyon"),
            "note": "APL leftover hub. Sparse. Not a thought.",
        },
        {
            "job": "descend_escape",
            "observer": "DNg29 (seed the command type)",
            "allow": True,
            "walks": True,
            "male": {
                "vnc_motor": float((shared(sh, "DNg29") or {}).get("vnc_motor") or 0),
                "descending": float((shared(sh, "DNg29") or {}).get("descending") or 0),
                "top": (shared(sh, "DNg29") or {}).get("top"),
            },
            "note": "Walking/flight-command analog. Giant Fiber is hemibrain JO hop-1. No wingbeat dump.",
        },
        {
            "job": "sleep",
            "observer": "DAM IR beam leftover-long inactivity; LNv/ER/FB named types",
            "allow": True,
            "walks": False,
            "sleep": {
                "frac_sleep": (sleep.get("observer") or {}).get("frac_sleep"),
                "night_over_day": (sleep.get("observer") or {}).get("night_over_day"),
                "n_alive": (sleep.get("observer") or {}).get("n_alive"),
            },
            "note": "Sleep is leftover-long rest on measured beams, not a 5-min free cut.",
        },
        {
            "job": "courtship",
            "observer": "fru/dsx",
            "allow": False,
            "walks": False,
            "note": "Measured labels exist. Default human-facing observer OFF.",
        },
        {
            "job": "aggression",
            "observer": "aggression flow",
            "allow": False,
            "walks": False,
            "note": "Measured labels exist. Default observer OFF.",
        },
    ]

    # Checks: walk lights legs; smell does not; see lights descending not legs; JO descending > smell
    walk_m = jobs[1]["male"]["vnc_motor"]
    smell_m = jobs[5]["male"]["vnc_motor"]
    see_d = jobs[4]["male"]["descending"]
    see_w = jobs[4]["male"]["vnc_motor"]
    jo_d = jobs[2]["male"]["descending"]
    ok = (
        walk_m > 1
        and smell_m < 0.05
        and see_d > 1
        and see_w < 0.05
        and jo_d > 1
        and jobs[9]["allow"] is False
        and jobs[10]["allow"] is False
    )
    why_walk = (
        "Walking was first because Harvard 6-leg 3D + Male/BANC vnc_motor is a "
        "clean measured loop. It is not the whole animal. This table is the rest "
        "of the measured observers under the same law."
    )
    day = {
        "sleep_frac": (sleep.get("observer") or {}).get("frac_sleep"),
        "wake_frac": 1.0 - float((sleep.get("observer") or {}).get("frac_sleep") or 0),
        "odor_video": (odor.get("honesty") or "")[:160],
        "rule": "Sleep leftover; wake uses allow=True observers. Not a trained circadian net.",
    }
    doc = {
        "pin": "AEB2AD",
        "free_parameters": 0,
        "why_walking_first": why_walk,
        "law": "S=K(T1+T2+T3); residual hops; observer from measured class",
        "jobs": jobs,
        "n_jobs": len(jobs),
        "n_allowed": sum(1 for j in jobs if j.get("allow")),
        "n_denied_default": sum(1 for j in jobs if not j.get("allow")),
        "overall_ok": ok,
        "day": day,
        "guardrail_deny": list((guard.get("deny_default_seeds") or {}).keys()),
        "note": (
            "No wingbeat kinematics on disk. Descending mass is the flight/escape analog. "
            "Do not call olfactory LN or APL a thought."
        ),
    }
    OUT.write_text(json.dumps(doc, indent=2), encoding="utf-8")
    print(why_walk)
    print()
    for j in jobs:
        m = j.get("male") or {}
        flag = "allow" if j.get("allow") else "DENY"
        print(
            f"  {j['job']:16s} {flag:5s}  vnc={float(m.get('vnc_motor') or 0):7.3f}  "
            f"desc={float(m.get('descending') or 0):7.3f}  walks={j.get('walks')}"
        )
    print(f"  overall_ok={ok}  wrote {OUT}")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
