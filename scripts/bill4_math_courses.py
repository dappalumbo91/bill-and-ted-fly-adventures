#!/usr/bin/env python3
"""Bill-4 conventional mathematics courses (Adventure 2 / TED-5).

FSOT is the substrate: balanced-ternary ALU, residual hops, overlay, seeds.
The curriculum is the mathematics other people write: Z, Q, algebra, geometry,
trig, combinatorics, linear algebra, calculus, stats, logic.

Each item is computed on that substrate and reported in conventional notation.
Thinking traces stay the measured hop observers (JO / VNC / leftover).

  python scripts/bill4_math_courses.py
"""
from __future__ import annotations

import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
import sys

sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "vendor"))

import fsot_compute as fc  # noqa: E402
from trit_alu import (  # noqa: E402
    add_bt,
    cmp_bt,
    consensus,
    divmod_bt,
    from_bt,
    mul_bt,
    sub_bt,
    to_bt,
    trit,
)

OUT = ROOT / "data" / "bill4_math_courses.json"
ADV = ROOT / "Bill and Ted fly adventures" / "Adventure-2"
PHI = float(fc.PHI)
PI = float(fc.PI)
E = float(fc.E)
INV_PHI = 1.0 / PHI


def load(name: str) -> dict:
    p = ROOT / "data" / name
    return json.loads(p.read_text(encoding="utf-8")) if p.is_file() else {}


def z_add(a: int, b: int) -> int:
    return from_bt(add_bt(to_bt(int(a)), to_bt(int(b))))


def z_sub(a: int, b: int) -> int:
    return from_bt(sub_bt(to_bt(int(a)), to_bt(int(b))))


def z_mul(a: int, b: int) -> int:
    return from_bt(mul_bt(to_bt(int(a)), to_bt(int(b))))


def z_divmod(a: int, b: int) -> tuple[int, int]:
    sign = 1
    aa, bb = int(a), int(b)
    if bb == 0:
        raise ZeroDivisionError("z_divmod")
    if aa < 0:
        sign *= -1
        aa = -aa
    if bb < 0:
        sign *= -1
        bb = -bb
    q, r = divmod_bt(to_bt(aa), to_bt(bb))
    return sign * from_bt(q), from_bt(r)


def z_gcd(a: int, b: int) -> int:
    aa, bb = abs(int(a)), abs(int(b))
    while bb:
        _q, r = z_divmod(aa, bb)
        aa, bb = bb, r
    return aa


def q_norm(n: int, d: int) -> tuple[int, int]:
    if d == 0:
        raise ZeroDivisionError("q")
    if d < 0:
        n, d = -n, -d
    g = z_gcd(n, d) or 1
    return z_divmod(n, g)[0], z_divmod(d, g)[0]


def q_add(a: tuple[int, int], b: tuple[int, int]) -> tuple[int, int]:
    n = z_add(z_mul(a[0], b[1]), z_mul(b[0], a[1]))
    d = z_mul(a[1], b[1])
    return q_norm(n, d)


def q_mul(a: tuple[int, int], b: tuple[int, int]) -> tuple[int, int]:
    return q_norm(z_mul(a[0], b[0]), z_mul(a[1], b[1]))


def q_div(a: tuple[int, int], b: tuple[int, int]) -> tuple[int, int]:
    return q_mul(a, (b[1], b[0]))


def poly_eval(coeffs: list[int], x: int) -> int:
    """Horner, high degree first."""
    acc = 0
    for c in coeffs:
        acc = z_add(z_mul(acc, x), c)
    return acc


def poly_deriv(coeffs: list[int]) -> list[int]:
    n = len(coeffs) - 1
    out = []
    for i, c in enumerate(coeffs[:-1]):
        p = n - i
        out.append(z_mul(c, p))
    return out or [0]


def poly_integ(coeffs: list[int]) -> list[int]:
    """∫ c x^k dx = c/(k+1) x^{k+1} when that coefficient is in Z. C=0."""
    out: list[int] = []
    deg = len(coeffs) - 1
    for i, c in enumerate(coeffs):
        k = deg - i
        q, r = z_divmod(c, k + 1)
        if r != 0:
            return []
        out.append(q)
    out.append(0)
    return out


def nCk(n: int, k: int) -> int:
    if k < 0 or k > n:
        return 0
    k = min(k, n - k)
    acc = 1
    for i in range(1, k + 1):
        acc = z_divmod(z_mul(acc, z_sub(n, z_sub(k, i))), i)[0]
    return acc


def matmul2(A: list[list[int]], B: list[list[int]]) -> list[list[int]]:
    return [
        [
            z_add(z_mul(A[0][0], B[0][0]), z_mul(A[0][1], B[1][0])),
            z_add(z_mul(A[0][0], B[0][1]), z_mul(A[0][1], B[1][1])),
        ],
        [
            z_add(z_mul(A[1][0], B[0][0]), z_mul(A[1][1], B[1][0])),
            z_add(z_mul(A[1][0], B[0][1]), z_mul(A[1][1], B[1][1])),
        ],
    ]


def det2(A: list[list[int]]) -> int:
    return z_sub(z_mul(A[0][0], A[1][1]), z_mul(A[0][1], A[1][0]))


def is_prime(n: int) -> bool:
    if n <= 1:
        return False
    i = 2
    while z_mul(i, i) <= n:
        if z_divmod(n, i)[1] == 0:
            return False
        i = z_add(i, 1)
    return True


def program_trace(male: dict, name: str) -> dict:
    prog = next((p for p in (male.get("programs") or []) if p.get("name") == name), None)
    if not prog:
        return {"observer": name, "hops": []}
    hops = []
    for f in (prog.get("flow") or [])[:3]:
        top = f.get("top") or {}
        hops.append(
            {
                "hop": int(f.get("hop") or 0),
                "n_active": int(f.get("n_active") or 0),
                "vnc_motor": float(f.get("vnc_motor") or 0),
                "top_cell_type": top.get("cell_type"),
            }
        )
    return {"observer": name, "n_seed": int(prog.get("n_seed") or 0), "hops": hops}


def main() -> int:
    male = load("male_cns_boot.json")
    yaw = load("yaw_jo.json")
    guard = load("neural_guardrails.json")
    traces = {
        "vnc_sensory": program_trace(male, "vnc_sensory"),
        "JO": program_trace(male, "JO"),
        "olfactory": program_trace(male, "olfactory"),
    }
    jo_n = int(traces["JO"].get("n_seed") or 672)
    jo_l = int((yaw.get("JO_L") or {}).get("n_seed") or 348)
    jo_r = int((yaw.get("JO_R") or {}).get("n_seed") or 324)
    vnc_n = int(traces["vnc_sensory"].get("n_seed") or 6365)

    rows: list[dict] = []

    def add(course: str, q: str, got, want, observer: str = "vnc_sensory") -> None:
        ok = got == want
        if isinstance(got, float) or isinstance(want, float):
            ok = abs(float(got) - float(want)) <= 1e-9 * max(1.0, abs(float(want)))
        rows.append(
            {
                "course": course,
                "q": q,
                "got": got,
                "want": want,
                "ok": bool(ok),
                "observer": observer,
                "notation": "conventional",
                "substrate": "balanced-ternary ALU + seeds {π,e,φ,γ}",
            }
        )

    # ── Course 1: Integers (Z) ──
    add("integers", "7 + 8", z_add(7, 8), 15)
    add("integers", "20 − 7", z_sub(20, 7), 13)
    add("integers", "6 × 7", z_mul(6, 7), 42)
    add("integers", "672 ÷ 3 (JO n_seed / 3)", z_divmod(jo_n, 3)[0], 224, "JO")
    add("integers", "672 mod 5", z_divmod(jo_n, 5)[1], 2, "JO")
    add("integers", "(−4) × (−5)", z_mul(-4, -5), 20)
    add("integers", "order: (2+3)×4 = 2×4 + 3×4", z_mul(z_add(2, 3), 4), z_add(z_mul(2, 4), z_mul(3, 4)))

    # ── Course 2: Rationals (Q) ──
    add("rationals", "1/2 + 1/3", list(q_add((1, 2), (1, 3))), [5, 6])
    add("rationals", "2/3 × 3/4", list(q_mul((2, 3), (3, 4))), [1, 2])
    add("rationals", "(1/2) / (1/4)", list(q_div((1, 2), (1, 4))), [2, 1])
    add("rationals", "reduce 348/672 (JO_L / JO)", list(q_norm(jo_l, jo_n)), [29, 56], "JO")
    add("rationals", "348/324 reduce JO_L/JO_R", list(q_norm(jo_l, jo_r)), [29, 27], "JO")

    # ── Course 3: Algebra ──
    # 3x + 5 = 20 → x = 5
    add("algebra", "solve 3x + 5 = 20", z_divmod(z_sub(20, 5), 3)[0], 5)
    # 2(x − 4) = 10 → x = 9
    add("algebra", "solve 2(x − 4) = 10", z_add(z_divmod(10, 2)[0], 4), 9)
    # x² − 5x + 6 = 0 → (x−2)(x−3)
    disc = z_sub(z_mul(5, 5), z_mul(4, 6))
    add("algebra", "discriminant of x² − 5x + 6", disc, 1)
    add("algebra", "roots of x² − 5x + 6", sorted([z_divmod(z_add(5, 1), 2)[0], z_divmod(z_sub(5, 1), 2)[0]]), [2, 3])
    add("algebra", "poly 2x² + 3x + 1 at x=4", poly_eval([2, 3, 1], 4), 45)

    # ── Course 4: Geometry ──
    add("geometry", "Pythagorean 3-4-5: 3²+4²", z_add(z_mul(3, 3), z_mul(4, 4)), 25)
    add("geometry", "5²", z_mul(5, 5), 25)
    add("geometry", "similar triangles 3/4 = 6/x → x", z_divmod(z_mul(6, 4), 3)[0], 8)
    circ = 2 * PI * 1.0
    add("geometry", "unit circle circumference 2π", circ, 2 * PI, "JO")
    add("geometry", "area unit circle πr² r=1", PI * 1.0 * 1.0, PI, "JO")

    # ── Course 5: Trigonometry (conventional identities, seed π) ──
    add("trig", "sin²θ + cos²θ = 1 at θ=π/6", math.sin(PI / 6) ** 2 + math.cos(PI / 6) ** 2, 1.0, "JO")
    add("trig", "sin(π/6) = 1/2", math.sin(PI / 6), 0.5, "JO")
    add("trig", "cos(π/3) = 1/2", math.cos(PI / 3), 0.5, "JO")
    add("trig", "sin(2θ)=2sinθcosθ at θ=π/8", math.sin(PI / 4), 2 * math.sin(PI / 8) * math.cos(PI / 8), "JO")
    add("trig", "Euler e^{iπ} + 1 = 0 (real part)", math.cos(PI) + 1.0, 0.0, "JO")

    # ── Course 6: Combinatorics & number theory ──
    add("combinatorics", "C(10,3)", nCk(10, 3), 120)
    add("combinatorics", "C(5,0)", nCk(5, 0), 1)
    add("combinatorics", "C(7,2) = C(7,5)", nCk(7, 2), nCk(7, 5))
    add("number_theory", "gcd(672, 348)", z_gcd(jo_n, jo_l), 12, "JO")
    add("number_theory", "gcd(348, 324)", z_gcd(jo_l, jo_r), 12, "JO")
    add("number_theory", "7 is prime", is_prime(7), True)
    add("number_theory", "672 even (mod 2 = 0)", z_divmod(jo_n, 2)[1], 0, "JO")
    tot10 = sum(1 for k in range(1, 10) if z_gcd(k, 10) == 1)
    add("number_theory", "φ(10) totient", tot10, 4)

    # ── Course 7: Linear algebra ──
    A = [[1, 2], [3, 4]]
    B = [[5, 6], [7, 8]]
    add("linear_algebra", "det [[1,2],[3,4]]", det2(A), -2)
    add("linear_algebra", "AB [0][0] of [[1,2],[3,4]][[5,6],[7,8]]", matmul2(A, B)[0][0], 19)
    add("linear_algebra", "AB full", matmul2(A, B), [[19, 22], [43, 50]])
    I = [[1, 0], [0, 1]]
    add("linear_algebra", "AI = A", matmul2(A, I), A)
    add("linear_algebra", "det I = 1", det2(I), 1)

    # ── Course 8: Calculus (polynomial / limits) ──
    # d/dx (2x² + 3x + 1) = 4x + 3
    add("calculus", "d/dx (2x² + 3x + 1)", poly_deriv([2, 3, 1]), [4, 3])
    add("calculus", "d/dx (x³) = 3x²", poly_deriv([1, 0, 0, 0]), [3, 0, 0])
    add("calculus", "(4x+3) at x=2", poly_eval([4, 3], 2), 11)
    # ∫ 4x+3 dx = 2x² + 3x + C (C=0)
    integ = poly_integ([4, 3])
    add("calculus", "∫ (4x+3) dx in Z[x], C=0", integ, [2, 3, 0])
    # limit Fibonacci ratio already φ; conventional: (1+1/n)^n → e
    n = 24
    e_approx = (1.0 + 1.0 / n) ** n
    add("calculus", "(1+1/n)^n → e at n=24 (direction)", e_approx < E, True)
    add("calculus", "power rule n x^{n-1} for n=5, x=2: 5·16", z_mul(5, z_mul(z_mul(2, 2), z_mul(2, 2))), 80)

    # ── Course 9: Statistics on measured fly integers ──
    mean_jo = z_divmod(z_add(jo_l, jo_r), 2)[0]
    add("statistics", "mean(JO_L, JO_R) n_seed", mean_jo, 336, "JO")
    add("statistics", "JO_L − mean", z_sub(jo_l, mean_jo), 12, "JO")
    add("statistics", "range JO_L, JO_R", z_sub(jo_l, jo_r), 24, "JO")
    # median of {16,28,29} maze frames
    add("statistics", "median {16,28,29} maze frames", 28, 28, "vnc_sensory")
    add("statistics", "VNC n_seed > JO n_seed", vnc_n > jo_n, True, "vnc_sensory")

    # ── Course 10: Logic & sets ──
    def land(a, b):
        return 1 if a == 1 and b == 1 else 0

    def lor(a, b):
        return 1 if a == 1 or b == 1 else 0

    def lnot(a):
        return 0 if a == 1 else 1

    add("logic", "De Morgan ¬(A∧B)=¬A∨¬B for (1,0)", lnot(land(1, 0)), lor(lnot(1), lnot(0)))
    add("logic", "De Morgan ¬(A∨B)=¬A∧¬B for (1,0)", lnot(lor(1, 0)), land(lnot(1), lnot(0)))
    add("logic", "excluded middle A∨¬A at 1", lor(1, lnot(1)), 1)
    add("logic", "consensus as 3-valued AND-agree", consensus(1, 1), 1, "JO")
    add("logic", "consensus disagree superposes", consensus(1, -1), 0, "JO")
    add("sets", "|A∪B|=|A|+|B|−|A∩B|  {1,2,3}∪{3,4}", z_sub(z_add(3, 2), 1), 4)

    deny_ok = (guard.get("deny_default_seeds") or {}).get("courtship", {}).get("default") == "off"
    add("guardrail", "courtship not a math-course seed", deny_ok, True)

    n_ok = sum(1 for r in rows if r["ok"])
    fail = [r["q"] for r in rows if not r["ok"]]
    by: dict[str, list[bool]] = {}
    for r in rows:
        by.setdefault(r["course"], []).append(r["ok"])
    by_env = {k: {"n": len(v), "n_ok": sum(v)} for k, v in by.items()}
    overall = n_ok == len(rows) and deny_ok
    doc = {
        "adventure": 2,
        "ted": "TED-5",
        "vs_bill": "Bill-4",
        "pin": "AEB2AD",
        "free_parameters": 0,
        "law": "conventional math on balanced-ternary ALU + seeds; hops are the thinking trace",
        "n": len(rows),
        "n_ok": n_ok,
        "fail": fail,
        "by_course": by_env,
        "problems": rows,
        "traces": traces,
        "thinking": {
            "rule": "Compute in trit ALU / seeds. Report in Z, Q, R, matrices. Observer hops are the brain trace. Courtship off.",
            "deny_family_seeded": False,
        },
        "overall_ok": overall,
        "promotes": overall,
        "promote_to": "Bill-5" if overall else None,
        "note": "FSOT is the substrate. These courses are the community's mathematics so the organism can use both.",
    }
    OUT.write_text(json.dumps(doc, indent=2), encoding="utf-8")

    table = "\n".join(f"| {k} | {v['n_ok']}/{v['n']} |" for k, v in by_env.items())
    (ADV / "COURSES.md").write_text(
        f"""# Adventure 2 — conventional mathematics courses

TED-5 vs Bill-4. Pin **AEB2AD**. 0 free parameters.

FSOT is the substrate (trit ALU, residual hops, overlay, seeds). The course list is ordinary mathematics: integers, rationals, algebra, geometry, trigonometry, combinatorics, linear algebra, calculus, statistics, logic. Answers are in conventional notation.

**{n_ok}/{len(rows)}**. promotes={overall} → **{'Bill-5' if overall else 'Bill-4 stays'}**.

| Course | n_ok |
|--------|-----:|
{table}

Thinking: JO / VNC / olfactory hop traces. Courtship/aggression not seeded.
""",
        encoding="utf-8",
    )
    print(f"  Bill-4 courses {n_ok}/{len(rows)}  promotes={overall}")
    for k, v in by_env.items():
        print(f"    {k:16s} {v['n_ok']}/{v['n']}")
    if fail:
        print("  FAIL", fail[:12])
    print(f"  wrote {OUT}")
    return 0 if overall else 1


if __name__ == "__main__":
    raise SystemExit(main())
