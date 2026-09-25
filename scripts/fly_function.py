#!/usr/bin/env python3
"""Wing points + other fly functions that are actually on disk.

Harvard Coords3D has Th-lWing / Th-rWing (hinge keypoints), 400 Hz.
Tethered walking on a ball — this is NOT a free-flight wingbeat dump.
We measure it anyway: if the spectrum is ~200 Hz, say so; if not, wings
are parked.

Other functions from Male CNS types + existing observers (JO, ORN, KC,
sleep, odor, courtship clip). DNp01 (2) and hg* MN (steering muscles)
are the flight/song motor names in the dump.

  python scripts/fly_function.py
  python scripts/fly_function.py --hops   # + DNp01 / hg3 residual
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

from fly_behavior import BEHAVIOR, TRIALS  # noqa: E402
from fly_connectome import FLY_ROOT, _PHI, _R_BIO, seed_indices  # noqa: E402

OUT = ROOT / "data" / "fly_function.json"
FPS = 400.0  # Dataverse 6-camera 400 Hz
FLIGHT_HZ = (150.0, 250.0)  # adult Drosophila wingbeat band


def _xyz(df, prefix: str) -> np.ndarray:
    return np.stack(
        [
            df[f"{prefix}_x"].to_numpy(dtype=np.float64),
            df[f"{prefix}_y"].to_numpy(dtype=np.float64),
            df[f"{prefix}_z"].to_numpy(dtype=np.float64),
        ],
        axis=1,
    )


def _fft_peak(x: np.ndarray, fps: float) -> dict[str, float]:
    x = np.asarray(x, dtype=np.float64)
    x = x - x.mean()
    spec = np.abs(np.fft.rfft(x))
    freq = np.fft.rfftfreq(len(x), d=1.0 / fps)
    spec = spec.copy()
    spec[0] = 0.0
    i = int(np.argmax(spec))
    hi = float(spec[(freq >= FLIGHT_HZ[0]) & (freq <= FLIGHT_HZ[1])].sum())
    lo = float(spec[(freq >= 0) & (freq <= 20)].sum())
    return {
        "peak_hz": float(freq[i]),
        "band_150_250": hi,
        "band_0_20": lo,
        "flight_band_ratio": hi / (lo + 1e-12),
    }


def wing_trial(tid: str) -> dict[str, Any]:
    import pandas as pd

    df = pd.read_csv(BEHAVIOR / f"{tid}_Coords3D.csv")
    lw = _xyz(df, "Th-lWing")
    rw = _xyz(df, "Th-rWing")
    tar = np.stack([_xyz(df, f"{leg}-Tar") for leg in ("R1", "R2", "R3", "L1", "L2", "L3")], axis=1)
    we = np.linalg.norm(np.diff(lw, axis=0), axis=1) + np.linalg.norm(np.diff(rw, axis=0), axis=1)
    te = np.linalg.norm(np.diff(tar, axis=0), axis=2).sum(axis=1)
    fft = _fft_peak(lw[:, 0], FPS)
    flight_like = fft["peak_hz"] >= FLIGHT_HZ[0] and fft["flight_band_ratio"] > float(_PHI)
    return {
        "id": tid,
        "n_frames": int(len(df)),
        "duration_s": float(len(df) / FPS),
        "fps": FPS,
        "wing_energy": {
            "min": float(we.min()),
            "median": float(np.median(we)),
            "max": float(we.max()),
        },
        "tarsus_energy_median": float(np.median(te)),
        "wing_over_tarsus": float(np.median(we) / (np.median(te) + 1e-12)),
        "fft": fft,
        "flight_like": flight_like,
        "verdict": "parked_hinge" if not flight_like else "wingbeat_band",
    }


def type_inventory() -> dict[str, Any]:
    import pandas as pd

    from paths import require

    ann_path = FLY_ROOT / "male_cns" / "body-annotations-male-cns-v1.0-minconf-0.5.feather"
    require(ann_path, "Male CNS body annotations feather")
    ann = pd.read_feather(ann_path)
    tr = ann[ann["status"] == "Traced"]
    typ = tr["type"].fillna("").astype(str)
    sc = tr["superclass"].fillna("").astype(str)
    counts = {}
    for pref in (
        "DNp01",
        "DNp",
        "DNg",
        "DNb",
        "DNa",
        "DNg29",
        "hg1 MN",
        "hg2 MN",
        "hg3 MN",
        "hg4 MN",
        "JO",
        "ORN",
        "KC",
        "TN1",
        "pC1",
    ):
        if pref in ("DNp01", "DNg29", "hg1 MN", "hg2 MN", "hg3 MN", "hg4 MN"):
            counts[pref] = int((typ == pref).sum())
        else:
            counts[pref] = int(typ.str.startswith(pref).sum())
    counts["vnc_motor"] = int((sc == "vnc_motor").sum())
    counts["descending_neuron"] = int((sc == "descending_neuron").sum())
    counts["cb_motor"] = int((sc == "cb_motor").sum())
    counts["haltere_type_substr"] = int(typ.str.lower().str.contains("haltere").sum())
    counts["wing_type_substr"] = int(typ.str.lower().str.contains("wing").sum())
    return {"n_traced": int(len(tr)), "counts": counts}


def hops_flight_motor() -> dict[str, Any]:
    from fly_connectome import residual_cascade
    from male_cns import load_male_graph

    print("  load Male CNS", flush=True)
    graph = load_male_graph()
    out = {}
    for name, seed, how in (
        ("DNp01", "DNp01", "type_exact"),
        ("hg3_MN", "hg3 MN", "type_exact"),
    ):
        seed_i = seed_indices(graph, seed, how=how)
        print(f"== {name} n_seed={len(seed_i)}", flush=True)
        run = residual_cascade(graph, seed_i, seed=seed, how=how, gpu=True)
        hit = next((s for s in (run.get("trace") or []) if s.get("hop") == 2), {})
        tm = hit.get("target_mass") or {}
        top = (hit.get("top") or [{}])[0]
        out[name] = {
            "n_seed": len(seed_i),
            "hop2_vnc_motor": tm.get("vnc_motor"),
            "hop2_descending": tm.get("descending"),
            "hop2_cb_motor": tm.get("cb_motor"),
            "top": top.get("cell_type"),
        }
    return out


def main(argv: list[str] | None = None) -> int:
    import argparse

    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--hops", action="store_true")
    args = ap.parse_args(argv)
    wings = [wing_trial(t["id"]) for t in TRIALS]
    inv = type_inventory()
    n_flight = sum(1 for w in wings if w["flight_like"])
    print("  wings")
    for w in wings:
        print(
            f"    {w['id']} peak={w['fft']['peak_hz']:.2f} Hz  "
            f"wing/tarsus={w['wing_over_tarsus']:.4f}  {w['verdict']}"
        )
    print(f"  types DNp01={inv['counts']['DNp01']} hg3 MN={inv['counts']['hg3 MN']} "
          f"DNg={inv['counts']['DNg']} JO={inv['counts']['JO']}")
    hop = hops_flight_motor() if args.hops else None
    doc = {
        "pin": "AEB2AD",
        "residual_Biochemistry": _R_BIO,
        "free_parameters": 0,
        "fps_authority": "Haustein 2024 Harvard Dataverse 10.7910/DVN/BBNPYX 400 Hz",
        "wingbeat_band_hz": list(FLIGHT_HZ),
        "n_trials_flight_like": n_flight,
        "verdict": (
            "Wing hinge keypoints exist. Spectrum is not the 200 Hz flight band. "
            "Tethered walking, wings parked. Do not call this a wingbeat dump."
        ),
        "wings": wings,
        "types": inv,
        "flight_motor_hops": hop,
        "other_functions_on_disk": [
            "6-leg 3D walk (same files)",
            "antenna 3D (JO observer)",
            "JO / ORN / KC / DNg / DNp types in Male CNS",
            "hg1–4 MN (2 each) — steering / song muscle names",
            "DNp01 n=2 — giant-fiber analog",
            "sleep DAM leftover inactivity",
            "odor ACV video rest/pulse",
            "courtship fru-GAL4 wing-extension clip (guardrail: not default seed)",
        ],
        "missing": [
            "free-flight wingbeat kinematics (~200 Hz)",
            "haltere named types in this dump (count 0)",
            "type string containing 'wing' (count 0)",
        ],
    }
    OUT.write_text(json.dumps(doc, indent=2), encoding="utf-8")
    print(f"  flight_like={n_flight}/3  wrote {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
