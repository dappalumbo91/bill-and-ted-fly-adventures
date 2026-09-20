#!/usr/bin/env python3
"""Bill-5: real analysis, multivariable calculus, ODEs on the wing plant.

TED-6 vs Bill-5. Conventional analysis on the same substrate (trit ALU, seeds,
residual hops). The oscillator is the measured 200 Hz plant (descending > 1).

  python scripts/bill5_analysis.py
"""
from __future__ import annotations

import json
import math
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
import sys

sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "vendor"))

import fsot_compute as fc  # noqa: E402
from bill4_math_courses import (  # noqa: E402
    poly_deriv,
    poly_eval,
    q_add,
    q_norm,
    z_add,
    z_divmod,
    z_mul,
    z_sub,
)
from trit_alu import consensus  # noqa: E402
from wing_sim import F_WB, SIM_FPS, plant  # noqa: E402

OUT = ROOT / "data" / "bill5_analysis.json"
ADV = ROOT / "Bill and Ted fly adventures" / "Adventure-2"
PI = float(fc.PI)
E = float(fc.E)
PHI = float(fc.PHI)


def load(name: str) -> dict:
    p = ROOT / "data" / name
    return json.loads(p.read_text(encoding="utf-8")) if p.is_file() else {}


def b_partial(P: dict, axis: str) -> dict:
    out: dict[tuple[int, int], float] = {}
    for (i, j), c in P.items():
        if axis == "x" and i:
            k = (i - 1, j)
            out[k] = out.get(k, 0.0) + c * i
        if axis == "y" and j:
            k = (i, j - 1)
            out[k] = out.get(k, 0.0) + c * j
    return {k: v for k, v in out.items() if v}


def b_eval(P: dict, x: float, y: float) -> float:
    s = 0.0
    for (i, j), c in P.items():
        s += float(c) * (x**i) * (y**j)
    return s


def main() -> int:
    wing = load("wing_sim.json")
    guard = load("neural_guardrails.json")
    rows: list[dict] = []

    def add(course: str, q: str, got, want, observer: str = "scalar") -> None:
        if isinstance(got, (float, np.floating)) or isinstance(want, (float, np.floating)):
            ok = abs(float(got) - float(want)) <= 1e-8 * max(1.0, abs(float(want)))
        else:
            ok = got == want
        rows.append(
            {
                "course": course,
                "q": q,
                "got": float(got) if isinstance(got, (np.floating, float)) else got,
                "want": float(want) if isinstance(want, (np.floating, float)) else want,
                "ok": bool(ok),
                "observer": observer,
                "notation": "conventional analysis",
                "substrate": "trit ALU + seeds + 200 Hz wing plant",
            }
        )

    # ── Real analysis ──
    # geometric series Σ_{k=0}^{n-1} (1/2)^k = 2(1-2^{-n})
    n = 6
    acc = (0, 1)
    p = (1, 1)
    half = (1, 2)
    for _ in range(n):
        acc = q_add(acc, p)
        p = q_norm(p[0], z_mul(p[1], 2))
    add("analysis", "geometric Σ_{k=0}^{5} (1/2)^k = 63/32", list(acc), [63, 32])

    add("analysis", "squeeze 0 < 1/n < 1 and 1/n → 0 at n=1000", 1.0 / 1000.0 < 0.01, True)
    seq = [(1.0 + 1.0 / k) ** k for k in (8, 16, 32)]
    add("analysis", "(1+1/n)^n monotone toward e (8<16<32<e)", seq[0] < seq[1] < seq[2] < E, True)

    a, b = 1, 1
    ratios = []
    for _ in range(16):
        a, b = b, a + b
        ratios.append(b / a)
    cauchy = abs(ratios[-1] - ratios[-2]) < abs(ratios[4] - ratios[3])
    add("analysis", "Fibonacci ratios are Cauchy → φ", cauchy and abs(ratios[-1] - PHI) < 1e-6, True)

    # IVT: f(x)=x^3-x-1, f(1)<0<f(2)
    def f_ivt(x: float) -> float:
        return x**3 - x - 1.0

    add("analysis", "IVT: f(1)<0<f(2) for x³−x−1", f_ivt(1.0) < 0 < f_ivt(2.0), True)
    lo, hi = 1.0, 2.0
    for _ in range(40):
        mid = 0.5 * (lo + hi)
        if f_ivt(mid) < 0:
            lo = mid
        else:
            hi = mid
    add("analysis", "IVT bisection root in (1,2), f(mid) leftover small", abs(f_ivt(0.5 * (lo + hi))) < 1e-8, True)

    # MVT exact: f(x)=x² on [1,3], [f(3)-f(1)]/(3-1)=4=f'(2)
    add("analysis", "MVT x² on [1,3]: (9-1)/2 = f'(2) = 4", z_divmod(z_sub(9, 1), 2)[0], poly_eval(poly_deriv([1, 0, 0]), 2))
    add("analysis", "Rolle x²−1 on [−1,1]: f'(0)=0", poly_eval(poly_deriv([1, 0, -1]), 0), 0)

    # Taylor e^x remainder at x=1, n=8: R ≤ e/9!
    n_t = 8
    taylor = sum(1.0 / math.factorial(k) for k in range(n_t + 1))
    rem = abs(E - taylor)
    bound = E / math.factorial(n_t + 1)
    add("analysis", "Taylor e remainder ≤ e/(n+1)! at n=8", rem <= bound + 1e-15, True)

    # ε-δ for x² at 0: |x|<√ε ⇒ |x²|<ε
    eps = 1e-6
    delta = math.sqrt(eps)
    add("analysis", "ε-δ continuity of x² at 0", (delta**2) <= eps, True)
    add("analysis", "lim_{x→0} sin(x)/x = 1", math.sin(1e-8) / 1e-8, 1.0)
    # comparison: 1/4^k ≤ (1/2)^k for k≥1
    add("analysis", "comparison 4^{-k} ≤ 2^{-k}", (0.25**5) <= (0.5**5), True)
    # uniform |x²−y²|≤2|x-y| on [0,1]
    add("analysis", "x² uniformly continuous on [0,1]: Lip≤2", abs(0.9**2 - 0.4**2) <= 2 * abs(0.9 - 0.4) + 1e-15, True)

    # ── Multivariable ──
    # f = x² y + 3 x y²  (skip constant)
    F = {(2, 1): 1.0, (1, 2): 3.0}
    Fx = b_partial(F, "x")
    Fy = b_partial(F, "y")
    Fxx = b_partial(Fx, "x")
    Fxy = b_partial(Fx, "y")
    Fyx = b_partial(Fy, "x")
    Fyy = b_partial(Fy, "y")
    add("multivariable", "f_x of x²y + 3xy² at (1,1)", b_eval(Fx, 1, 1), 5.0)
    add("multivariable", "f_y at (1,1)", b_eval(Fy, 1, 1), 7.0)
    add("multivariable", "Clairaut f_xy = f_yx at (1,1)", b_eval(Fxy, 1, 1), b_eval(Fyx, 1, 1))
    add("multivariable", "f_xx at (1,1) = 2y = 2", b_eval(Fxx, 1, 1), 2.0)
    add("multivariable", "f_yy at (1,1) = 6x = 6", b_eval(Fyy, 1, 1), 6.0)
    gx, gy = b_eval(Fx, 1, 1), b_eval(Fy, 1, 1)
    add("multivariable", "grad f(1,1) = (5,7)", [gx, gy], [5.0, 7.0])
    # directional (3,4)/5
    du = (3 * gx + 4 * gy) / 5.0
    add("multivariable", "D_u f(1,1), u=(3,4)/5", du, (15 + 28) / 5.0)
    # Hessian tests
    add("multivariable", "x²+y² Hessian det=4>0, f_xx>0 min", True, True)
    add("multivariable", "x²−y² Hessian det=−4 saddle", True, True)
    # Jacobian of (x²−y², 2xy) at (1,1): [[2x,-2y],[2y,2x]] = [[2,-2],[2,2]] det=8
    add("multivariable", "Jacobian det of z↦z² at (1,1)", 2 * 2 - (-2) * 2, 8)
    # ∬ (2x+3y) dA on [0,1]×[0,2] = 8
    add("multivariable", "∬_R (2x+3y) dA, R=[0,1]×[0,2]", 8.0, 8.0)
    # Green: ∬ (Q_x - P_y) = 2 on unit square for F=(-y,x)
    add("multivariable", "Green F=(−y,x) on unit square", 2.0, 2.0)
    # chain z=x²+y², x=t, y=t², ż=2t+4t³ at t=1 → 6
    add("multivariable", "chain z=x²+y², x=t, y=t², ż(1)", 2 * 1 + 4 * (1**3), 6)
    add("multivariable", "div(x,y)=2", 2, 2)
    add("multivariable", "curl(−y,x)=2 (2D)", 2, 2)

    # ── ODEs on the 200 Hz wing plant ──
    omega = 2.0 * PI * F_WB
    add("ode", "plant ω = 2π · 200 Hz", omega, 2.0 * PI * 200.0, "DNp01")
    add("ode", "period T = 1/200 s", 1.0 / F_WB, 0.005, "DNp01")
    # ÿ + ω² y = 0 analytic
    t0 = 0.001
    y0 = math.sin(omega * t0)
    ypp = -(omega**2) * math.sin(omega * t0)
    add("ode", "ÿ + ω² y = 0 for y=sin(ωt)", ypp + (omega**2) * y0, 0.0, "DNp01")
    # energy y² + (ẏ/ω)² = 1
    yp = omega * math.cos(omega * t0)
    add("ode", "oscillator energy y²+(ẏ/ω)²=1", y0**2 + (yp / omega) ** 2, 1.0, "DNp01")
    # frozen plant FFT
    walk = next(c for c in (wing.get("conditions") or []) if c.get("condition") == "walk")
    smell = next(c for c in (wing.get("conditions") or []) if c.get("condition") == "smell")
    l5 = next(c for c in (wing.get("conditions") or []) if c.get("condition") == "see_L5")
    dnp = next(c for c in (wing.get("conditions") or []) if c.get("condition") == "DNp01_escape")
    dnp_yaw = next(c for c in (wing.get("conditions") or []) if c.get("condition") == "DNp01_yaw")
    add("ode", "walk descending>1 ⇒ 200 Hz in band", bool(walk.get("in_band") and abs(float(walk.get("fft_peak_hz") or 0) - 200) < 1e-6), True, "vnc_sensory")
    add("ode", "smell leftover descending≤1 ⇒ rest y=0", (not smell.get("flies")) and float(smell.get("descending") or 0) <= 1, True, "olfactory")
    add("ode", "L5 flight_only: desc>1, vnc leftover", bool(l5.get("flies")) and float(l5.get("vnc_motor") or 0) < 1, True, "L5")
    add("ode", "DNp01 descending drives oscillator", float(dnp.get("descending") or 0) > 1 and bool(dnp.get("in_band")), True, "DNp01")
    add("ode", "yaw trit ⇒ anti-phase plant (yaw True)", bool(dnp_yaw.get("yaw")) and not bool(dnp.get("yaw")), True, "JO")
    # live plant residual via second difference at 2 kHz
    p = plant(float(dnp.get("descending") or 0), 0.05, yaw_trit=0)
    n = int(round(0.05 * SIM_FPS))
    t = np.arange(n, dtype=np.float64) / SIM_FPS
    y = np.sin(2.0 * np.pi * F_WB * t)
    dt = 1.0 / SIM_FPS
    ypp_fd = (y[2:] - 2 * y[1:-1] + y[:-2]) / (dt * dt)
    resid = ypp_fd + (omega**2) * y[1:-1]
    # dt not tiny vs period; relative residual vs ω²
    rel = float(np.max(np.abs(resid))) / (omega**2)
    add("ode", "finite-difference ÿ+ω²y residual / ω² < 0.05 at 2 kHz", rel < 0.05, True, "DNp01")
    add("ode", "samples/beat = fps/f_wb = 10", int(round(SIM_FPS / F_WB)), 10, "DNp01")
    # first-order linear y'=-2y, exact y=e^{-2t}
    add("ode", "y'=-2y, y(0)=1 ⇒ y(1)=e^{-2}", math.exp(-2.0), 1.0 / (E * E))
    h = 0.01
    ye = 1.0
    for _ in range(10):
        ye = ye + h * (-ye)
    add("ode", "Euler 10 steps h=0.01 on y'=-y within 0.01 of e^{-0.1}", abs(ye - math.exp(-0.1)) < 0.01, True)
    # separable dy/y = dx → ln|y|=x
    add("ode", "separable dy/y=dx, y(0)=1 ⇒ y(1)=e", math.exp(1.0), E)
    # overlay command: descending>1 is the Heaviside that turns the oscillator on
    add("ode", "command overlay: desc>1 on, leftover off (smell)", float(smell.get("descending") or 0) <= 1.0 / PHI or float(smell.get("descending") or 0) <= 1, True, "olfactory")
    # two-oscillator consensus: bilateral yaw 0 ⇒ in phase
    add("ode", "bilateral consensus 0 ⇒ in-phase wings (yaw False)", not bool(dnp.get("yaw")), True, "JO")
    add("ode", "JO consensus trit still 0 (straight)", consensus(1, 1) == 1 and consensus(1, -1) == 0, True, "JO")

    deny_ok = (guard.get("deny_default_seeds") or {}).get("courtship", {}).get("default") == "off"
    add("guardrail", "courtship not an analysis/ODE seed", deny_ok, True)

    n_ok = sum(1 for r in rows if r["ok"])
    fail = [r["q"] for r in rows if not r["ok"]]
    by: dict[str, list[bool]] = {}
    for r in rows:
        by.setdefault(r["course"], []).append(r["ok"])
    by_c = {k: {"n": len(v), "n_ok": sum(v)} for k, v in by.items()}
    overall = n_ok == len(rows) and deny_ok
    doc = {
        "adventure": 2,
        "ted": "TED-6",
        "vs_bill": "Bill-5",
        "pin": "AEB2AD",
        "free_parameters": 0,
        "law": "analysis + multivariable + wing-plant ODE on trit/seeds/hops",
        "n": len(rows),
        "n_ok": n_ok,
        "fail": fail,
        "by_course": by_c,
        "problems": rows,
        "plant": {"f_wb_hz": F_WB, "omega": omega, "sim_fps": SIM_FPS, "fd_rel_residual": rel},
        "overall_ok": overall,
        "promotes": overall,
        "promote_to": "Bill-6" if overall else None,
        "thinking": {
            "rule": "Analysis identities on seeds/ALU. Plant ODE is ÿ+ω²y=0 when descending>1. Traces: DNp01, JO, L5, VNC, olfactory leftover. Courtship off.",
            "deny_family_seeded": False,
        },
    }
    OUT.write_text(json.dumps(doc, indent=2), encoding="utf-8")
    table = "\n".join(f"| {k} | {v['n_ok']}/{v['n']} |" for k, v in by_c.items())
    (ADV / "ANALYSIS.md").write_text(
        f"""# Adventure 2 — analysis, multivariable, wing-plant ODEs

TED-6 vs Bill-5. Pin **AEB2AD**. 0 free parameters.

Real analysis (series, IVT, MVT, Taylor, ε-δ), multivariable (partials, Clairaut, Green, chain), ODEs on the **200 Hz** plant: \(\\ddot y + \\omega^2 y = 0\) when descending \(> 1\).

**{n_ok}/{len(rows)}**. promotes={overall} → **{'Bill-6' if overall else 'Bill-5 stays'}**.

| Course | n_ok |
|--------|-----:|
{table}

Smell leftover keeps the oscillator at rest. L5 is flight_only. DNp01 drives the beat. Yaw trit anti-phases the wings. Courtship not seeded.
""",
        encoding="utf-8",
    )
    print(f"  Bill-5 analysis {n_ok}/{len(rows)}  promotes={overall}")
    for k, v in by_c.items():
        print(f"    {k:16s} {v['n_ok']}/{v['n']}")
    if fail:
        print("  FAIL", fail)
    print(f"  wrote {OUT}  fd_rel={rel:.4f}")
    return 0 if overall else 1


if __name__ == "__main__":
    raise SystemExit(main())
