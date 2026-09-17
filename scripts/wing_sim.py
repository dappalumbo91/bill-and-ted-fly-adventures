#!/usr/bin/env python3
"""Untethered wing plant driven by *measured* descending hops.

The Harvard clip is a fly glued to a ball: hinges exist, spectrum is not
200 Hz. On a computer that mechanical lock is gone. We do **not** rewrite
the clip. We drive a plant from residual descending mass already measured
on Male CNS (DNp01, JO, L5, vnc_sensory, olfactory).

Species wingbeat ~200 Hz is the band center already used in fly_function.py
(literature adult *D. melanogaster*, not fitted to this clip).
Amplitude: 0 if descending ≤ 1 (leftover command); else 1 (overlay).
No trained policy. 0 free parameters.

  python scripts/wing_sim.py
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
import sys

sys.path.insert(0, str(ROOT / "scripts"))

from trit_alu import add_bt, from_bt, to_bt  # noqa: E402

OUT = ROOT / "data" / "wing_sim.json"
FUNC = ROOT / "data" / "fly_function.json"
REP = ROOT / "data" / "repertoire.json"
PHI = 1.618033988749895
F_WB = 200.0  # Hz, center of documented 150–250 band
# Camera was 400 Hz (Nyquist = 200 Hz — exactly the beat, aliases to nothing).
# The computer is not a camera: sample the plant well above the beat.
SIM_FPS = 2000.0


def plant(descending: float, duration_s: float, yaw_trit: int = 0) -> dict:
    """Sinusoid at F_WB when command clears overlay (descending > 1)."""
    flies = float(descending) > 1.0
    n = max(int(round(duration_s * SIM_FPS)), 1)
    t = np.arange(n, dtype=np.float64) / SIM_FPS
    if not flies:
        left = np.zeros(n)
        right = np.zeros(n)
        n_beats = 0
        peak = 0.0
    else:
        left = np.sin(2 * np.pi * F_WB * t)
        phase = np.pi if yaw_trit != 0 else 0.0
        right = np.sin(2 * np.pi * F_WB * t + phase)
        n_beats = int(round(F_WB * duration_s))
        spec = np.abs(np.fft.rfft(left - left.mean()))
        freq = np.fft.rfftfreq(n, d=1.0 / SIM_FPS)
        spec[0] = 0.0
        peak = float(freq[int(np.argmax(spec))])
    return {
        "flies": flies,
        "n_beats": n_beats,
        "fft_peak_hz": peak,
        "in_band": flies and 150.0 <= peak <= 250.0,
        "yaw": yaw_trit != 0,
        "n_samples": n,
    }


def main() -> int:
    func = json.loads(FUNC.read_text(encoding="utf-8"))
    rep = json.loads(REP.read_text(encoding="utf-8"))
    jobs = {j["job"]: j for j in rep.get("jobs") or []}
    dnp = (func.get("flight_motor_hops") or {}).get("DNp01") or {}
    duration = float((func.get("wings") or [{}])[0].get("duration_s") or 0.835)
    parked = int(func.get("n_trials_flight_like") or 0)

    def desc(job: str) -> float:
        return float((jobs.get(job) or {}).get("male", {}).get("descending") or 0.0)

    def vnc(job: str) -> float:
        return float((jobs.get(job) or {}).get("male", {}).get("vnc_motor") or 0.0)

    conditions = [
        ("rest", 0.0, 0.0, 0),
        ("walk", vnc("walk"), desc("walk"), 0),
        ("hear_JO", vnc("hear_steer"), desc("hear_steer"), 0),
        ("see_L5", vnc("see"), desc("see"), 0),
        ("smell", vnc("smell"), desc("smell"), 0),
        ("DNp01_escape", float(dnp.get("hop2_vnc_motor") or 0), float(dnp.get("hop2_descending") or 0), 0),
        ("DNp01_yaw", float(dnp.get("hop2_vnc_motor") or 0), float(dnp.get("hop2_descending") or 0), 1),
        ("object", vnc("object"), desc("object"), 0),
    ]
    rows = []
    for name, vn, ds, yaw in conditions:
        p = plant(ds, duration, yaw_trit=yaw)
        walks = vn > 1.0
        cons = 1 if walks == p["flies"] else 0
        if walks and p["flies"]:
            mode = "takeoff_both"
        elif p["flies"] and not walks:
            mode = "flight_only"
        elif walks and not p["flies"]:
            mode = "walk_only"
        else:
            mode = "rest"
        rows.append(
            {
                "condition": name,
                "vnc_motor": vn,
                "descending": ds,
                "walks": walks,
                "mode": mode,
                "effectors_agree": bool(cons),
                **p,
            }
        )

    # Trit: beats in the clip window vs leftover hop horizon
    n_beats_on = int(round(F_WB * duration))
    beats_bt = from_bt(add_bt(to_bt(0), to_bt(n_beats_on)))
    tests = []

    def rec(q: str, got, want) -> None:
        tests.append({"q": q, "got": got, "want": want, "ok": got == want})

    rec("parked clip is not flight", parked == 0, True)
    rec("rest plant does not beat", rows[0]["n_beats"] == 0, True)
    rec("smell leftover does not beat", next(r["n_beats"] == 0 for r in rows if r["condition"] == "smell"), True)
    rec("see (L5) flight_only", next(r["mode"] == "flight_only" for r in rows if r["condition"] == "see_L5"), True)
    rec("DNp01 in 200 Hz band", next(r["in_band"] for r in rows if r["condition"] == "DNp01_escape"), True)
    rec("walk also has descending > 1 so untethered takeoff_both", next(r["mode"] == "takeoff_both" for r in rows if r["condition"] == "walk"), True)
    rec("JO hear takeoff_both (desc 24)", next(r["mode"] == "takeoff_both" for r in rows if r["condition"] == "hear_JO"), True)
    rec("yaw plant marks yaw", next(r["yaw"] for r in rows if r["condition"] == "DNp01_yaw"), True)
    rec("beat count in clip window", beats_bt, n_beats_on)
    rec("beats > leftover hops 11", n_beats_on > 11, True)

    fail = [t["q"] for t in tests if not t["ok"]]
    advice = [
        "Untethered, walking's own descending (11.4) already clears overlay — the ball was hiding a takeoff command. Dual-effector takeoff is a feature, not a bug.",
        "Vision (L5) is the clean flight_only test: descending 1.92, legs off. That is the visual-flight analog without inventing wing MNs.",
        "DNp01 descending 15.8 is the escape plant; hg3 MN stays local VNC (song/steering muscle), do not swap them.",
        "Thought stress cons(T001, Fly02)=0 is heading leftover. Do not grow tissue on olfactory il3LN6 / Kenyon APL.",
        "Next learning pressure: L/R yaw from laterality trit on L5 or JO_L vs JO_R, still measured cells.",
        "Still missing: free-flight 3D. This plant is command→sinusoid, labeled simulated, not a reconstructed wingbeat.",
    ]
    doc = {
        "pin": "AEB2AD",
        "free_parameters": 0,
        "f_wb_hz": F_WB,
        "sim_fps": SIM_FPS,
        "f_wb_note": "Species band center 150–250 Hz (already in fly_function). Not fitted to the parked clip.",
        "duration_s": duration,
        "n_beats_if_on": n_beats_on,
        "parked_clip_flight_like": parked,
        "conditions": rows,
        "tests": tests,
        "n_ok": len(tests) - len(fail),
        "n": len(tests),
        "fail": fail,
        "overall_ok": not fail,
        "advice": advice,
        "note": "Computer removes the glue. Residual descending is still the measured command.",
    }
    OUT.write_text(json.dumps(doc, indent=2), encoding="utf-8")
    print(f"  f={F_WB} Hz  window={duration:.3f}s  beats_if_on={n_beats_on}")
    for r in rows:
        print(
            f"    {r['condition']:16s} {r['mode']:14s}  "
            f"walks={r['walks']} flies={r['flies']}  peak={r['fft_peak_hz']:.1f} Hz"
        )
    print(f"  tests {doc['n_ok']}/{doc['n']}")
    if fail:
        print("  FAIL", fail)
    print(f"  wrote {OUT}")
    return 0 if doc["overall_ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
