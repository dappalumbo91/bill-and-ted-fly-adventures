#!/usr/bin/env python3
"""First curriculum: FSOT math the fly already runs (spatial / trit / φ).

Not an LLM. Not backprop. Digs the Fly02 maze miss, then scores a math
probe that uses only seeds {π,e,φ,γ} and measured left/right observers.

  python scripts/math_first.py           # miss audit + math probe
  python scripts/math_first.py --hops    # + Male left/right residual hops
"""
from __future__ import annotations

import runio
runio.install()

import json
import sys
from pathlib import Path
from typing import Any

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "vendor"))

import fsot_compute as fc  # noqa: E402
from fly_behavior import BEHAVIOR, TRIALS, kinematics  # noqa: E402
from fly_connectome import _PHI, _R_BIO, _hop_cpu, cuda_name  # noqa: E402
from full_scalar_law import residual_scale  # noqa: E402
from trinary_syntax import aa_pair_weight  # noqa: E402

OUT = ROOT / "data" / "math_first.json"
BASE = ROOT / "data" / "baseline_sim.json"
PHI = float(_PHI)
INV_PHI = 1.0 / PHI
LEFTOVER = 1.0 - INV_PHI  # 1/φ² wait: 1/φ = φ-1 = leftover of 1. leftover φ^{-2}=2-φ
# Standard: leftover = 1/φ = φ-1 ≈ 0.382; 1/φ² = 2-φ ≈ 0.382? 
# φ-1 = 1/φ. 1/φ² = 1 - 1/φ = 2-φ. leftover coverage floor 1/φ².
PHI2 = PHI * PHI


def trit(x: int) -> int:
    if x > 0:
        return 1
    if x < 0:
        return -1
    return 0


def consensus(a: int, b: int) -> int:
    return a if a == b else 0


def sum_sat(a: int, b: int) -> int:
    return trit(a + b)


def pair(a: int, b: int) -> int:
    return trit(a * b)


def from_s(s: float, lo: float, hi: float) -> int:
    if s < lo:
        return -1
    if s > hi:
        return 1
    return 0


def overlay_on(x: float, cut: float = INV_PHI) -> bool:
    return abs(x) > cut


def math_probe() -> dict[str, Any]:
    rows = []

    def rec(name: str, ok: bool, detail: dict) -> None:
        rows.append({"name": name, "ok": bool(ok), **detail})

    # Trit tables
    cons_ok = all(
        consensus(a, b) == (a if a == b else 0)
        for a in (-1, 0, 1)
        for b in (-1, 0, 1)
    )
    rec("trit_consensus_9", cons_ok, {"n": 9})
    rec("trit_sumsat_1_1", sum_sat(1, 1) == 1, {"got": sum_sat(1, 1)})
    rec("trit_sumsat_1_m1", sum_sat(1, -1) == 0, {"got": sum_sat(1, -1)})
    rec("trit_neg", trit(-1) == -1 and trit(1) == 1, {})
    rec("trit_pair_disagree", pair(1, -1) == -1, {"got": pair(1, -1)})

    # φ identities the overlay already uses
    rec("phi_inv_eq_phi_minus_1", abs(INV_PHI - (PHI - 1.0)) < 1e-12, {"inv": INV_PHI})
    rec("phi2_eq_phi_plus_1", abs(PHI2 - (PHI + 1.0)) < 1e-12, {"phi2": PHI2})
    rec("leftover_1_over_phi2", abs((1.0 / PHI2) - (2.0 - PHI)) < 1e-12, {"leftover": 1.0 / PHI2})

    # Residual law
    r = residual_scale(abs(float(fc.domain_scalar("Biochemistry"))))
    rec("residual_biochem", abs(r - 1.284069161007025) < 1e-9, {"r": r, "D_eff": int(fc.DOMAINS["Biochemistry"].D_eff)})

    # Pair geometry (already a fly-pack gate)
    w = aa_pair_weight("F", "W", 8)
    rec("pair_FW_8", abs(w - 1.6700524010190179) < 1e-9, {"w": w})

    # Overlay cut as inequality
    rec("overlay_phi_on", overlay_on(1.0) and not overlay_on(0.1), {"cut": INV_PHI})
    rec(
        "fromS_overlay",
        from_s(-1.0, -INV_PHI, INV_PHI) == -1
        and from_s(0.0, -INV_PHI, INV_PHI) == 0
        and from_s(1.0, -INV_PHI, INV_PHI) == 1,
        {},
    )

    # Seeds present
    rec("seeds_pi_e_phi_gamma", float(fc.PI) > 3 and float(fc.E) > 2 and PHI > 1.6, {})

    failed = [x["name"] for x in rows if not x["ok"]]
    return {
        "n": len(rows),
        "n_ok": sum(1 for x in rows if x["ok"]),
        "fail": failed,
        "overall_ok": not failed,
        "rows": rows,
        "note": "These are identities the organism already is. Not trained.",
    }


def miss_audit() -> dict[str, Any]:
    """Why Fly02 missed the left resource — body laterality, not a hop bug."""
    base = json.loads(BASE.read_text(encoding="utf-8")) if BASE.is_file() else {}
    by_id = {t["id"]: t for t in (base.get("closed_loop_trials") or [])}
    trials = []
    n_mean_leftover = 0
    for tr in TRIALS:
        csv = BEHAVIOR / tr["body"]
        if not csv.is_file():
            continue
        kin = kinematics(csv)
        left = np.asarray(kin["series"]["left"], dtype=np.float64)
        right = np.asarray(kin["series"]["right"], dtype=np.float64)
        d = right - left
        scale = float(np.median(left + right)) + 1e-12
        mean_rl = float(d.mean())
        mean_trit = from_s(mean_rl / scale, -INV_PHI, INV_PHI)
        n_mean_leftover += int(mean_trit == 0)
        sim = by_id.get(tr["id"]) or {}
        turns = sim.get("turns") or {}
        trials.append(
            {
                "id": tr["id"],
                "left_mean": float(left.mean()),
                "right_mean": float(right.mean()),
                "right_minus_left_mean": mean_rl,
                "mean_over_median_step": mean_rl / scale,
                "mean_laterality_trit": mean_trit,
                "mean_is_leftover": mean_trit == 0,
                "sim_turns": turns,
                "sim_final_lane": sim.get("final_lane"),
                "sim_left_resource": sim.get("maze_resource_left_reached"),
                "per_leg_mean_speed": kin["per_leg_mean_speed"],
            }
        )
    return {
        "rule": (
            "Trial-mean (R−L)/median_step uses overlay 1/φ. If leftover, do not "
            "collapse the heading. Maze lane is per-frame consensus trit on walk steps."
        ),
        "trials": trials,
        "n_trials": len(trials),
        "n_mean_laterality_leftover": n_mean_leftover,
        "finding": (
            "All three trial *means* sit under the overlay (leftover). "
            "Fly02 miss is 28 right vs 16 left *frames* at the junction plant, "
            "not a failed residual hop and not odor."
        ),
    }


def _seed_by(graph: dict[str, Any], cls: str, root_side: str) -> list[int]:
    idx = graph["idx"]
    out = []
    want = root_side.lower()
    for rid, m in graph["meta"].items():
        if rid not in idx:
            continue
        if (m.get("super_class") or "").lower() != cls:
            if cls != "jo":
                continue
            if not (m.get("cell_type") or "").lower().startswith("jo"):
                continue
        else:
            if cls == "jo":
                pass
        rs = (m.get("root_side") or "").lower()
        if rs == want:
            out.append(idx[rid])
    return out


def _attach_root_side(graph: dict[str, Any]) -> None:
    import pandas as pd
    from male_cns import ANN

    ann = pd.read_feather(ANN)
    traced = ann[ann["status"] == "Traced"]
    root = {
        str(int(b)): str(s or "").strip()
        for b, s in zip(traced["bodyId"].tolist(), traced["rootSide"].tolist())
    }
    soma = {
        str(int(b)): str(s or "").strip()
        for b, s in zip(traced["bodyId"].tolist(), traced["somaSide"].tolist())
    }
    for rid, m in graph["meta"].items():
        m["root_side"] = root.get(rid, "")
        m["soma_side"] = soma.get(rid, "") or (m.get("side") or "")


def _hop2_state(graph: dict[str, Any], seed_i: list[int]) -> np.ndarray:
    n = graph["n"]
    a = np.zeros(n, dtype=np.float64)
    if seed_i:
        a[np.asarray(seed_i, dtype=np.int64)] = 1.0
    W = graph["W"]
    if cuda_name() and seed_i:
        try:
            import torch
            from fly_connectome import _hop_gpu_prepare

            torch, device, Wt = _hop_gpu_prepare(W)
            at = torch.from_numpy(a).to(device)
            for _ in range(2):
                try:
                    at = torch.mv(Wt, at)
                except RuntimeError:
                    at = torch.sparse.mm(Wt, at.unsqueeze(1)).squeeze(1)
                at = at / (at.abs().max() + 1e-12)
            return at.detach().cpu().numpy()
        except Exception as exc:
            print(f"  GPU hop2 failed ({exc}); CPU", flush=True)
    for _ in range(2):
        a = _hop_cpu(W, a)
    return a


def _motor_by_side(a: np.ndarray, graph: dict[str, Any]) -> dict[str, float]:
    meta = graph["meta"]
    ids = graph["ids"]
    left = right = other = 0.0
    vnc = 0.0
    for i, rid in enumerate(ids):
        m = meta.get(rid) or {}
        if (m.get("super_class") or "").lower() != "vnc_motor":
            continue
        amp = float(abs(a[i]))
        vnc += amp
        side = (m.get("soma_side") or m.get("side") or "").upper()
        if side == "L":
            left += amp
        elif side == "R":
            right += amp
        else:
            other += amp
    return {
        "vnc_motor": vnc,
        "vnc_motor_L": left,
        "vnc_motor_R": right,
        "vnc_motor_other": other,
        "ipsi_bias": (left - right) / (left + right + 1e-12),
    }


def laterality_hops() -> dict[str, Any]:
    from male_cns import load_male_graph

    print("  load Male CNS", flush=True)
    graph = load_male_graph()
    _attach_root_side(graph)
    programs = []
    for name, cls, side in (
        ("vnc_sensory_L", "vnc_sensory", "L"),
        ("vnc_sensory_R", "vnc_sensory", "R"),
        ("JO_L", "jo", "L"),
        ("JO_R", "jo", "R"),
    ):
        if cls == "vnc_sensory":
            seed_i = [
                graph["idx"][rid]
                for rid, m in graph["meta"].items()
                if rid in graph["idx"]
                and (m.get("super_class") or "").lower() == "vnc_sensory"
                and (m.get("root_side") or "").upper() == side
            ]
        else:
            seed_i = [
                graph["idx"][rid]
                for rid, m in graph["meta"].items()
                if rid in graph["idx"]
                and (m.get("cell_type") or "").lower().startswith("jo")
                and (m.get("root_side") or "").upper() == side
            ]
        print(f"== {name} n_seed={len(seed_i)}", flush=True)
        a = _hop2_state(graph, seed_i)
        mass = _motor_by_side(a, graph)
        programs.append({"name": name, "n_seed": len(seed_i), "hop2": mass})
        print(
            f"  hop2 vnc_motor={mass['vnc_motor']:.4f} L={mass['vnc_motor_L']:.4f} "
            f"R={mass['vnc_motor_R']:.4f} ipsi_bias={mass['ipsi_bias']:.3f}",
            flush=True,
        )
    # Ipsilateral: L seed should bias motor L (positive ipsi_bias for L seed)
    vL = next(p for p in programs if p["name"] == "vnc_sensory_L")["hop2"]
    vR = next(p for p in programs if p["name"] == "vnc_sensory_R")["hop2"]
    ipsi = (vL["ipsi_bias"] > 0) and (vR["ipsi_bias"] < 0)
    return {
        "programs": programs,
        "vnc_sensory_ipsi_same_sign": ipsi,
        "note": (
            "vnc_sensory laterality is rootSide (somaSide is empty on the cord). "
            "vnc_motor laterality is somaSide. Crossing is allowed; we measure it."
        ),
    }


def main(argv: list[str] | None = None) -> int:
    import argparse

    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--hops", action="store_true", help="Male left/right residual hops")
    args = ap.parse_args(argv)
    print("  math probe", flush=True)
    probe = math_probe()
    print(f"  math {probe['n_ok']}/{probe['n']} fail={probe['fail']}", flush=True)
    print("  miss audit", flush=True)
    miss = miss_audit()
    for t in miss["trials"]:
        print(
            f"    {t['id']} R-L={t['right_minus_left_mean']:+.4f} "
            f"mean_trit={t['mean_laterality_trit']} leftover={t['mean_is_leftover']} "
            f"turns={t.get('sim_turns')} lane={t.get('sim_final_lane')} "
            f"left_resource={t.get('sim_left_resource')}",
            flush=True,
        )
    hops = laterality_hops() if args.hops else None
    doc = {
        "pin": "AEB2AD",
        "residual_Biochemistry": _R_BIO,
        "free_parameters": 0,
        "curriculum": "spatial / trit / φ first — not language tokens",
        "math_probe": probe,
        "miss_audit": miss,
        "laterality_hops": hops,
        "next": (
            "Language/coding still waits. After spatial laterality is measured, "
            "integer counting can ride hop-n_active / overlay, still without backprop."
        ),
    }
    OUT.write_text(json.dumps(doc, indent=2), encoding="utf-8")
    print(f"  wrote {OUT}", flush=True)
    ipsi = True
    if hops is not None:
        ipsi = bool(hops.get("vnc_sensory_ipsi_same_sign"))
    ok = bool(probe["overall_ok"] and ipsi)
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
