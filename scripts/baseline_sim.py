#!/usr/bin/env python3
"""Baseline FSOT fly simulation — print first, no LLM.

Closed loop: measured treadmill kinematics (fly walking on a ball) gate
observers. Observers read **frozen** residual hop-2 fields from Male CNS
(measured W). Motor mass drives a Y-maze plant. Ball-contact analog =
forelimb share of tarsus energy (Iwasaki et al. PNAS 2025 / Curr Biol 2025).

Not a trained policy. Not language. Not invented synapses.
0 free parameters. Pin AEB2AD.

  python scripts/baseline_sim.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "vendor"))

from fly_behavior import BEHAVIOR, TRIALS, kinematics  # noqa: E402
from fly_connectome import _PHI, _R_BIO  # noqa: E402

MALE = ROOT / "data" / "male_cns_boot.json"
BANC = ROOT / "data" / "banc_connectome_boot.json"
GUARD = ROOT / "data" / "neural_guardrails.json"
OUT = ROOT / "data" / "baseline_sim.json"
MAZE_STEM = 8.0
MAZE_ARM = 8.0
BALL_FORE_SHARE = 1.0 / float(_PHI)


def hop2_table(path: Path) -> dict[str, dict[str, float]]:
    d = json.loads(path.read_text(encoding="utf-8"))
    rec = (d.get("compare") or {}).get("hop_2") or {}
    out: dict[str, dict[str, float]] = {}
    for name, row in rec.items():
        top = row.get("top") or {}
        out[name] = {
            "vnc_motor": float(row.get("vnc_motor") or 0.0),
            "descending": float(row.get("descending") or 0.0),
            "top": str(top.get("cell_type") or ""),
        }
    return out


def consensus_turn(left: float, right: float, thr: float) -> int:
    """+1 left, -1 right, 0 superpose (straight). Trit consensus."""
    l_on = left >= thr
    r_on = right >= thr
    if l_on and r_on:
        return 0
    if l_on:
        return 1
    if r_on:
        return -1
    return 0


def command_for_seeds(
    seeds: list[str], table: dict[str, dict[str, float]]
) -> dict[str, Any]:
    if not seeds:
        return {"seeds": [], "vnc_motor": 0.0, "descending": 0.0, "walks": False}
    use = [s for s in seeds if s in table]
    if not use:
        return {"seeds": seeds, "vnc_motor": 0.0, "descending": 0.0, "walks": False}
    motor = max(table[s]["vnc_motor"] for s in use)
    desc = max(table[s]["descending"] for s in use)
    return {
        "seeds": seeds,
        "vnc_motor": motor,
        "descending": desc,
        "walks": motor > 1.0,
    }


def _lr_threshold(left: np.ndarray, right: np.ndarray) -> float:
    d = np.abs(left - right)
    med = float(np.median(d))
    mad = float(np.median(np.abs(d - med))) + 1e-12
    return med + float(_PHI) * mad


def run_trial(
    trial: dict[str, str], table: dict[str, dict[str, float]]
) -> dict[str, Any]:
    csv = BEHAVIOR / trial["body"]
    kin = kinematics(csv)
    energy = np.asarray(kin["series"]["tarsus_energy"], dtype=np.float64)
    antenna = np.asarray(kin["series"]["antenna_energy"], dtype=np.float64)
    left = np.asarray(kin["series"]["left"], dtype=np.float64)
    right = np.asarray(kin["series"]["right"], dtype=np.float64)
    r1 = np.asarray(kin["per_leg_series"]["R1"], dtype=np.float64)
    l1 = np.asarray(kin["per_leg_series"]["L1"], dtype=np.float64)
    t_thr = float(kin["tarsus_gate"]["threshold"])
    a_thr = float(kin["antenna_gate"]["threshold"])
    lr_thr = _lr_threshold(left, right)

    n = int(energy.size)
    x = 0.0
    lane = 0
    reached = False
    n_walk = n_rest = n_ball = n_jo = n_vnc = 0
    turns: list[int] = []
    seed_hist: dict[str, int] = {}

    for t in range(n):
        tarsus_on = bool(energy[t] >= t_thr)
        ant_on = bool(antenna[t] >= a_thr)
        tot = float(energy[t]) + 1e-12
        ball = bool(tarsus_on and ((r1[t] + l1[t]) / tot) >= BALL_FORE_SHARE)
        seeds: list[str] = []
        if tarsus_on:
            seeds.append("vnc_sensory")
            n_vnc += 1
        if ant_on:
            seeds.append("JO")
            n_jo += 1
        if ball:
            seeds.append("mechanosensory")
            n_ball += 1
        key = "+".join(seeds) if seeds else "rest"
        seed_hist[key] = seed_hist.get(key, 0) + 1
        cmd = command_for_seeds(seeds, table)
        if cmd["walks"]:
            n_walk += 1
            step = float(energy[t])
            turn = consensus_turn(float(left[t]), float(right[t]), lr_thr)
            turns.append(turn)
            if lane == 0:
                x += step
                if x >= MAZE_STEM:
                    if turn == 0:
                        x = MAZE_STEM
                    else:
                        lane = turn
                        x = 0.0
            else:
                x += step
                if lane == 1 and x >= MAZE_ARM:
                    reached = True
        else:
            n_rest += 1

    return {
        "id": trial["id"],
        "n_frames": n,
        "tarsus_gate": t_thr,
        "antenna_gate": a_thr,
        "n_walk_frames": n_walk,
        "n_rest_frames": n_rest,
        "n_vnc_sensory_on": n_vnc,
        "n_JO_on": n_jo,
        "n_ball_forelimb": n_ball,
        "seed_histogram": seed_hist,
        "turns": {
            "left": int(sum(1 for u in turns if u == 1)),
            "right": int(sum(1 for u in turns if u == -1)),
            "superpose": int(sum(1 for u in turns if u == 0)),
        },
        "maze_resource_left_reached": reached,
        "final_lane": lane,
        "per_leg_mean_speed": kin["per_leg_mean_speed"],
        "whole_clip_is_walking": kin["whole_clip_is_walking"],
    }


def brain_print(
    male: dict[str, dict[str, float]], banc: dict[str, dict[str, float]]
) -> list[dict[str, Any]]:
    catalog = [
        {"condition": "rest", "seeds": [], "body": "no afferent", "allow": True},
        {
            "condition": "walk_legs",
            "seeds": ["vnc_sensory"],
            "body": "tarsus / VNC sensory",
            "allow": True,
        },
        {
            "condition": "walk_JO",
            "seeds": ["JO"],
            "body": "antenna / Johnston organ",
            "allow": True,
        },
        {
            "condition": "ball_contact",
            "seeds": ["mechanosensory"],
            "body": "forelimb object analog (Iwasaki ball)",
            "allow": True,
        },
        {
            "condition": "walk_plus_ball",
            "seeds": ["vnc_sensory", "mechanosensory"],
            "body": "legs + object",
            "allow": True,
        },
        {
            "condition": "odor_contrast",
            "seeds": ["olfactory"],
            "body": "olfactory ORN (must NOT walk)",
            "allow": True,
        },
        {
            "condition": "courtship_DENIED",
            "seeds": [],
            "body": "fru/courtship observer",
            "allow": False,
        },
        {
            "condition": "aggression_DENIED",
            "seeds": [],
            "body": "aggression observer",
            "allow": False,
        },
    ]
    rows = []
    for row in catalog:
        if not row["allow"]:
            rows.append(
                {
                    **row,
                    "male": {"vnc_motor": 0.0, "descending": 0.0, "walks": False, "blocked": True},
                    "banc": {"vnc_motor": 0.0, "descending": 0.0, "walks": False, "blocked": True},
                    "ok": True,
                }
            )
            continue
        m = command_for_seeds(row["seeds"], male)
        b = command_for_seeds(row["seeds"], banc)
        if row["condition"] == "odor_contrast":
            ok = (not m["walks"]) and (float(m["vnc_motor"]) < 0.05)
        elif row["condition"] == "rest":
            ok = not m["walks"]
        else:
            ok = bool(m["walks"])
        rows.append({**row, "male": m, "banc": b, "ok": ok})
    return rows


def main() -> int:
    male = hop2_table(MALE)
    banc = hop2_table(BANC)
    catalog = brain_print(male, banc)
    sys.stdout.write("  brain print\n")
    for row in catalog:
        m = row["male"]
        sys.stdout.write(
            f"    {row['condition']:18s} walks={m.get('walks')}  "
            f"vnc_motor={float(m.get('vnc_motor') or 0):.3f}  "
            f"desc={float(m.get('descending') or 0):.3f}  ok={row['ok']}\n"
        )
        sys.stdout.flush()
    trials = []
    for tr in TRIALS:
        csv = BEHAVIOR / tr["body"]
        if not csv.is_file():
            continue
        sys.stdout.write(f"  trial {tr['id']}\n")
        sys.stdout.flush()
        trials.append(run_trial(tr, male))
    n_reach = sum(1 for t in trials if t.get("maze_resource_left_reached"))
    doc = {
        "pin": "AEB2AD",
        "residual_Biochemistry": _R_BIO,
        "phi": float(_PHI),
        "free_parameters": 0,
        "not": (
            "Not an LLM. Not a trained walking policy. Not Iwasaki video "
            "(not on disk). Not Berlin/ymaze files (those dumps are unauthorized/corrupt). "
            "Language/coding is not this baseline."
        ),
        "law": "S=K(T1+T2+T3); a <- r W a; inf-norm; observer from measured limbs",
        "body": (
            "Harvard Dataverse 10.7910/DVN/BBNPYX tethered fly on a ball, "
            "6-leg 3D tarsus + antenna. MAD+φ gates."
        ),
        "brain": "Male CNS hop-2 frozen fields (measured synapses). BANC listed for split check.",
        "object_papers": [
            "Iwasaki et al. PNAS 2025 e2426180122 (microrobotics / ball cargo)",
            "Iwasaki et al. Curr Biol 2025 35:5475 (immobile sphere preference; hΔ FB)",
        ],
        "guardrail": "courtship/aggression/fru never seeded. olfactory is contrast only.",
        "brain_print": catalog,
        "brain_print_ok": all(r.get("ok") for r in catalog),
        "closed_loop_trials": trials,
        "n_trials": len(trials),
        "n_resource_reached": n_reach,
        "maze": {
            "stem": MAZE_STEM,
            "arm": MAZE_ARM,
            "resource": "left",
            "choice": "left/right tarsus consensus trit; 0 = no collapse",
        },
        "ball_rule": "forelimb (R1+L1) share of tarsus energy ≥ 1/φ → mechanosensory seed",
        "next_not_this_file": (
            "Language, coding, LLM-style tokens wait until this baseline holds. "
            "Teach by adding measured observers, not trained weights."
        ),
    }
    OUT.write_text(json.dumps(doc, indent=2), encoding="utf-8")
    sys.stdout.write(
        f"  brain_print_ok={doc['brain_print_ok']}  "
        f"trials={len(trials)} resource_reached={n_reach}\n"
        f"  wrote {OUT}\n"
    )
    sys.stdout.flush()
    return 0 if doc["brain_print_ok"] and trials else 1


if __name__ == "__main__":
    raise SystemExit(main())
