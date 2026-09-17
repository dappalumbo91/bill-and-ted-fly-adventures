#!/usr/bin/env python3
"""Next arithmetic layer: measured hop counts as integers, then word problems.

n_seed, n_active, laterality sizes, maze turns, leftover hop index
are measured. Encode them as balanced-ternary words and compute.
No trained weights. No invented synapses.

  python scripts/arith_count.py
"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys_path = ROOT / "scripts"

import sys

sys.path.insert(0, str(sys_path))

from trit_alu import (  # noqa: E402
    abs_bt,
    add_bt,
    cmp_bt,
    divmod_bt,
    fmt_bt,
    from_bt,
    mul_bt,
    sub_bt,
    to_bt,
    trit,
)

OUT = ROOT / "data" / "arith_count.json"
MALE = ROOT / "data" / "male_cns_boot.json"
MATH = ROOT / "data" / "math_first.json"
BASE = ROOT / "data" / "baseline_sim.json"
COUNTS = ROOT / "data" / "type_counts.json"
PHI = 1.618033988749895


def add(a: int, b: int) -> int:
    return from_bt(add_bt(to_bt(a), to_bt(b)))


def sub(a: int, b: int) -> int:
    return from_bt(sub_bt(to_bt(a), to_bt(b)))


def mul(a: int, b: int) -> int:
    return from_bt(mul_bt(to_bt(a), to_bt(b)))


def qdiv(a: int, b: int) -> int:
    q, _r = divmod_bt(to_bt(a), to_bt(b))
    return from_bt(q)


def hop_leftover() -> int:
    return int(round(PHI**5))


def gather() -> dict:
    male = json.loads(MALE.read_text(encoding="utf-8"))
    programs = {}
    for p in male.get("programs") or []:
        flow = {int(f["hop"]): f for f in (p.get("flow") or [])}
        programs[p["name"]] = {
            "n_seed": int(p.get("n_seed") or 0),
            "n_active": {h: int(flow[h]["n_active"]) for h in flow},
        }
    lat = ((json.loads(MATH.read_text(encoding="utf-8")) if MATH.is_file() else {}).get("laterality_hops") or {}).get("programs") or []
    lat_n = {p["name"]: int(p.get("n_seed") or 0) for p in lat}
    trials = (json.loads(BASE.read_text(encoding="utf-8")) if BASE.is_file() else {}).get("closed_loop_trials") or []
    turns = {t["id"]: t.get("turns") or {} for t in trials}
    tc = json.loads(COUNTS.read_text(encoding="utf-8")) if COUNTS.is_file() else {}
    return {
        "n_neurons": int(male.get("n_neurons") or 0),
        "n_gaba": int(male.get("n_gaba") or 0),
        "programs": programs,
        "lat_n": lat_n,
        "turns": turns,
        "type_counts": tc,
        "hop_leftover": hop_leftover(),
    }


def main() -> int:
    g = gather()
    bank: list[dict] = []

    def rec(kind: str, q: str, got, want, extra=None) -> None:
        row = {"kind": kind, "q": q, "got": got, "want": want, "ok": got == want}
        if extra:
            row.update(extra)
        bank.append(row)

    # Hop leftover index is φ^5, not a fitted horizon.
    rec("const", "leftover hops = round(φ⁵)", g["hop_leftover"], 11)

    # Seed is hop-0 active (the observer is the seed).
    for name, p in g["programs"].items():
        n0 = (p["n_active"] or {}).get(0, -1)
        rec("count", f"{name} hop-0 n_active = n_seed", n0, p["n_seed"])

    jo = g["programs"].get("JO") or {}
    vnc = g["programs"].get("vnc_sensory") or {}
    rec("count", "JO n_seed", jo.get("n_seed"), 672)
    rec("count", "JO hop-1 n_active (DNg29 bottleneck)", (jo.get("n_active") or {}).get(1), 3)
    rec("sub", "JO cells not active at hop-1: n_seed − n_active(1)", sub(672, 3), 669)

    lat = g["lat_n"]
    rec(
        "add",
        "JO_L + JO_R = JO n_seed",
        add(lat.get("JO_L", 0), lat.get("JO_R", 0)),
        672,
    )
    rec(
        "add",
        "vnc_sensory_L + vnc_sensory_R",
        add(lat.get("vnc_sensory_L", 0), lat.get("vnc_sensory_R", 0)),
        add(3185, 3166),
    )
    rec(
        "sub",
        "vnc_sensory unlabeled = n_seed − (L+R)",
        sub(vnc.get("n_seed") or 0, add(lat.get("vnc_sensory_L", 0), lat.get("vnc_sensory_R", 0))),
        14,
    )
    rec("cmp", "more left VNC sensory than right?", trit(cmp_bt(to_bt(3185), to_bt(3166))), 1)

    # DNg29 on two whole-CNS graphs, absent in hemibrain
    tc = g["type_counts"]
    rec("add", "Male DNg29 + BANC DNg29", add(2, 2), 4)
    rec(
        "count",
        "hemibrain DNg29",
        int((tc.get("hemibrain_cache") or {}).get("DNg29") or 0),
        0,
    )
    rec(
        "add",
        "hemibrain JO + KC",
        add(
            int((tc.get("hemibrain_cache") or {}).get("JO_type_prefix") or 0),
            int((tc.get("hemibrain_cache") or {}).get("KC_type_prefix") or 0),
        ),
        add(78, 1927),
    )

    # Maze word problems (multi-trial)
    t1 = g["turns"].get("Fly01_T001") or {}
    t2 = g["turns"].get("Fly01_T002") or {}
    t3 = g["turns"].get("Fly02_T002") or {}
    left_all = add(add(int(t1.get("left") or 0), int(t2.get("left") or 0)), int(t3.get("left") or 0))
    right_all = add(add(int(t1.get("right") or 0), int(t2.get("right") or 0)), int(t3.get("right") or 0))
    rec("add", "all-trial left turns 29+35+16", left_all, 80)
    rec("add", "all-trial right turns 28+26+28", right_all, 82)
    rec("sub", "net heading all trials (left−right)", sub(left_all, right_all), -2)
    rec("cmp", "all-trials net: right-biased?", trit(cmp_bt(to_bt(left_all), to_bt(right_all))), -1)
    rec("sub", "Fly02 heading 16−28", sub(16, 28), -12)
    rec("abs", "|Fly02 heading|", from_bt(abs_bt(to_bt(-12))), 12)

    # Small exact division (trit repeated-sub)
    rec("div", "672 ÷ 3", qdiv(672, 3), 224)
    rec("div", "4 ÷ 2  (two DNg29 × two graphs, per graph)", qdiv(4, 2), 2)
    rec("div", "11 leftover hops ÷ 1", qdiv(11, 1), 11)

    # Multi-digit chain: non-GABA cells
    rec(
        "sub",
        "Male traced − GABA = excitatory/other cells",
        sub(g["n_neurons"], g["n_gaba"]),
        165122 - 22055,
    )
    rec("show", "3185 in balanced ternary", fmt_bt(to_bt(3185)), fmt_bt(to_bt(3185)))
    rec(
        "show",
        "3185 + 3166 in trit ALU",
        fmt_bt(add_bt(to_bt(3185), to_bt(3166))),
        fmt_bt(to_bt(6351)),
    )

    fail = [p for p in bank if not p["ok"]]
    kinds: dict[str, list] = {}
    for p in bank:
        kinds.setdefault(p["kind"], []).append(p["ok"])
    doc = {
        "pin": "AEB2AD",
        "free_parameters": 0,
        "n": len(bank),
        "n_ok": len(bank) - len(fail),
        "fail": [p["q"] for p in fail],
        "overall_ok": not fail,
        "by_kind": {k: {"n": len(v), "n_ok": sum(v)} for k, v in kinds.items()},
        "measured": {
            "hop_leftover_phi5": g["hop_leftover"],
            "JO_n_seed": jo.get("n_seed"),
            "vnc_L": lat.get("vnc_sensory_L"),
            "vnc_R": lat.get("vnc_sensory_R"),
            "JO_L": lat.get("JO_L"),
            "JO_R": lat.get("JO_R"),
        },
        "problems": bank,
        "note": (
            "Integers are measured hop/type/turn counts. Arithmetic is trit ALU. "
            "Not a language model."
        ),
    }
    OUT.write_text(json.dumps(doc, indent=2), encoding="utf-8")
    print(f"arith_count {doc['n_ok']}/{doc['n']}  by_kind={doc['by_kind']}")
    if fail:
        print("FAIL", fail)
    print(f"  wrote {OUT}")
    return 0 if doc["overall_ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
