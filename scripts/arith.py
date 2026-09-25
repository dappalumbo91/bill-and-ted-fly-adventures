#!/usr/bin/env python3
"""Actual arithmetic on FSOT trits — balanced ternary, then spatial problems.

The fly's native word is {-1,0,+1}. Integers are finite trit strings.
Add/sub/mul/compare use only trit ops + trit carry. No trained weights.

Spatial problems reuse the maze laterality counts (left = +1, right = −1).

  python scripts/arith.py
"""
from __future__ import annotations

import runio
runio.install()

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from trit_alu import (  # noqa: E402
    add_bt,
    cmp_bt,
    fmt_bt,
    from_bt,
    mul_bt,
    sub_bt,
    to_bt,
    trit,
)

OUT = ROOT / "data" / "arith.json"
MATH = ROOT / "data" / "math_first.json"
PHI = 1.618033988749895
INV_PHI = 1.0 / PHI


def solve_add(a: int, b: int) -> int:
    return from_bt(add_bt(to_bt(a), to_bt(b)))


def solve_sub(a: int, b: int) -> int:
    return from_bt(sub_bt(to_bt(a), to_bt(b)))


def solve_mul(a: int, b: int) -> int:
    return from_bt(mul_bt(to_bt(a), to_bt(b)))


def solve_cmp(a: int, b: int) -> int:
    return cmp_bt(to_bt(a), to_bt(b))


def problems() -> list[dict]:
    bank: list[dict] = []

    def add(kind: str, q: str, got, want, extra: dict | None = None) -> None:
        rec = {
            "kind": kind,
            "q": q,
            "got": got,
            "want": want,
            "ok": got == want,
        }
        if extra:
            rec.update(extra)
        bank.append(rec)

    # Roundtrip
    for n in range(-40, 41):
        enc = to_bt(n)
        add(
            "roundtrip",
            f"encode {n}",
            from_bt(enc),
            n,
            {"bt": fmt_bt(enc)},
        )

    # Addition
    for a, b in (
        (0, 0),
        (1, 1),
        (1, 2),
        (2, 2),
        (3, 4),
        (5, 8),
        (7, -3),
        (-4, -5),
        (12, 13),
        (20, -7),
        (-19, 19),
        (9, 9),
        (2, -2),
        (15, 16),
        (-8, 3),
    ):
        add("add", f"{a} + {b}", solve_add(a, b), a + b)

    # Subtraction
    for a, b in (
        (5, 3),
        (3, 5),
        (0, 1),
        (10, 10),
        (-4, 2),
        (8, -8),
        (13, 6),
        (1, 0),
    ):
        add("sub", f"{a} − {b}", solve_sub(a, b), a - b)

    # Multiplication
    for a, b in (
        (0, 7),
        (1, 9),
        (2, 3),
        (4, 4),
        (5, -3),
        (-6, -6),
        (7, 8),
        (3, 0),
        (-2, 5),
    ):
        add("mul", f"{a} × {b}", solve_mul(a, b), a * b)

    # Compare
    for a, b in ((3, 5), (5, 3), (4, 4), (-2, -2), (-7, 1), (0, -1), (12, 11)):
        add("cmp", f"cmp({a},{b})", solve_cmp(a, b), trit(a - b))

    # Overlay leftover (φ) as a decision problem
    add(
        "overlay",
        "|0.034|/0.49 ≟ > 1/φ  (Fly02 trial mean)",
        abs(0.0343) / 0.49 > INV_PHI,
        False,
    )
    add(
        "overlay",
        "1 ≟ > 1/φ",
        1.0 > INV_PHI,
        True,
    )

    # Spatial word problems from the maze (left=+1, right=−1)
    # Net heading = n_left − n_right (superpose contributes 0).
    spatial = [
        ("Fly01_T001", 29, 28, True),
        ("Fly01_T002", 35, 26, True),
        ("Fly02_T002", 16, 28, False),
    ]
    for name, nl, nr, reached_left in spatial:
        net = solve_sub(nl, nr)
        sign = trit(net)
        add(
            "spatial",
            f"{name}: {nl} left − {nr} right → heading, resource-left?",
            (sign, sign == 1),
            (trit(nl - nr), reached_left),
            {"net": net, "heading_trit": sign},
        )

    # Resource: left arm is +1. Did heading match resource?
    add(
        "spatial",
        "If heading trit is +1, take left resource",
        solve_cmp(29, 28) == 1,
        True,
    )
    add(
        "spatial",
        "If heading trit is −1, left resource is a miss",
        solve_cmp(16, 28) == -1,
        True,
    )

    # Two-digit example shown as trit words
    add(
        "show",
        "2 + 2 in balanced ternary",
        fmt_bt(add_bt(to_bt(2), to_bt(2))),
        fmt_bt(to_bt(4)),
    )
    return bank


def main() -> int:
    # Encoder self-check before the bank
    bad_rt = [n for n in range(-80, 81) if from_bt(to_bt(n)) != n]
    bank = problems()
    fail = [p for p in bank if not p["ok"]]
    doc = {
        "pin": "AEB2AD",
        "free_parameters": 0,
        "alu": "balanced ternary on FSOT trits; carry is a trit",
        "encoder_roundtrip_fail": bad_rt,
        "n": len(bank),
        "n_ok": len(bank) - len(fail),
        "fail": [p["q"] for p in fail],
        "overall_ok": not fail and not bad_rt,
        "by_kind": {},
        "problems": bank,
        "note": (
            "This is exact integer arithmetic on the native trit word. "
            "Not a transformer. Spatial items are the maze counts, not new synapses."
        ),
    }
    kinds: dict[str, list] = {}
    for p in bank:
        kinds.setdefault(p["kind"], []).append(p["ok"])
    doc["by_kind"] = {
        k: {"n": len(v), "n_ok": sum(v)} for k, v in kinds.items()
    }
    OUT.write_text(json.dumps(doc, indent=2), encoding="utf-8")
    print(f"encoder roundtrip fails: {bad_rt[:8]} n={len(bad_rt)}")
    print(f"arith {doc['n_ok']}/{doc['n']}  by_kind={doc['by_kind']}")
    if fail:
        print("FAIL", fail[:8])
    print(f"  wrote {OUT}")
    return 0 if doc["overall_ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
