#!/usr/bin/env python3
"""Multi-step trit chains on measured fly integers.

Each chain is a worksheet: name a measured count, then add/sub/mul/div/cmp/abs
using only the balanced-ternary ALU. Later steps read earlier ones.
No trained weights. Not language tokens.

  python scripts/arith_steps.py
"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
import sys

sys.path.insert(0, str(ROOT / "scripts"))

from trit_alu import (  # noqa: E402
    abs_bt,
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

OUT = ROOT / "data" / "arith_steps.json"
COUNT = ROOT / "data" / "arith_count.json"
MATH = ROOT / "data" / "math_first.json"
MALE = ROOT / "data" / "male_cns_boot.json"
BASE = ROOT / "data" / "baseline_sim.json"
COUNTS = ROOT / "data" / "type_counts.json"


def _i(x) -> int:
    return from_bt(x) if isinstance(x, list) else int(x)


def op_add(a, b):
    return add_bt(to_bt(_i(a)), to_bt(_i(b)))


def op_sub(a, b):
    return sub_bt(to_bt(_i(a)), to_bt(_i(b)))


def op_mul(a, b):
    return mul_bt(to_bt(_i(a)), to_bt(_i(b)))


def op_div(a, b):
    q, _r = divmod_bt(to_bt(_i(a)), to_bt(_i(b)))
    return q


def op_abs(a, b=None):
    return abs_bt(to_bt(_i(a)))


def op_cmp(a, b):
    return [cmp_bt(to_bt(_i(a)), to_bt(_i(b)))]


def op_trit(a, b=None):
    return [trit(_i(a))]


def op_cons(a, b):
    return [consensus(trit(_i(a)), trit(_i(b)))]


OPS = {
    "add": op_add,
    "sub": op_sub,
    "mul": op_mul,
    "div": op_div,
    "abs": op_abs,
    "cmp": op_cmp,
    "trit": op_trit,
    "cons": op_cons,
}


def registry() -> dict[str, int]:
    male = json.loads(MALE.read_text(encoding="utf-8"))
    programs = {p["name"]: p for p in (male.get("programs") or [])}
    jo = programs.get("JO") or {}
    vnc = programs.get("vnc_sensory") or {}
    flow_jo = {int(f["hop"]): f for f in (jo.get("flow") or [])}
    lat = {
        p["name"]: int(p.get("n_seed") or 0)
        for p in ((json.loads(MATH.read_text(encoding="utf-8")).get("laterality_hops") or {}).get("programs") or [])
    }
    turns = {
        t["id"]: t.get("turns") or {}
        for t in (json.loads(BASE.read_text(encoding="utf-8")).get("closed_loop_trials") or [])
    }
    tc = json.loads(COUNTS.read_text(encoding="utf-8")) if COUNTS.is_file() else {}
    hemi = tc.get("hemibrain_cache") or {}
    return {
        "JO": int(jo.get("n_seed") or 0),
        "JO_h1": int((flow_jo.get(1) or {}).get("n_active") or 0),
        "VNC": int(vnc.get("n_seed") or 0),
        "JO_L": lat.get("JO_L", 0),
        "JO_R": lat.get("JO_R", 0),
        "VNC_L": lat.get("vnc_sensory_L", 0),
        "VNC_R": lat.get("vnc_sensory_R", 0),
        "GABA": int(male.get("n_gaba") or 0),
        "NEURONS": int(male.get("n_neurons") or 0),
        "DNg29_M": 2,
        "DNg29_B": 2,
        "DNg29_H": int(hemi.get("DNg29") or 0),
        "HOPS": 11,
        "T001_L": int((turns.get("Fly01_T001") or {}).get("left") or 0),
        "T001_R": int((turns.get("Fly01_T001") or {}).get("right") or 0),
        "T002_L": int((turns.get("Fly01_T002") or {}).get("left") or 0),
        "T002_R": int((turns.get("Fly01_T002") or {}).get("right") or 0),
        "T02_L": int((turns.get("Fly02_T002") or {}).get("left") or 0),
        "T02_R": int((turns.get("Fly02_T002") or {}).get("right") or 0),
        "KC": int(hemi.get("KC_type_prefix") or 0),
        "H_JO": int(hemi.get("JO_type_prefix") or 0),
    }


def run_chain(reg: dict[str, int], steps: list[dict]) -> dict:
    env: dict[str, list[int]] = {k: to_bt(v) for k, v in reg.items()}
    trace = []
    last = [0]
    for st in steps:
        op = OPS[st["op"]]
        args = []
        for a in st.get("args") or []:
            if isinstance(a, str):
                args.append(env[a])
            else:
                args.append(to_bt(int(a)))
        if len(args) == 1:
            out = op(args[0])
        else:
            out = op(args[0], args[1])
        env[st["id"]] = out
        last = out
        trace.append(
            {
                "id": st["id"],
                "op": st["op"],
                "args": st.get("args"),
                "value": from_bt(out),
            }
        )
    return {"env_last": from_bt(last), "trace": trace}


def chains() -> list[dict]:
    return [
        {
            "name": "JO laterality then bottleneck",
            "want": 669,
            "steps": [
                {"id": "sum", "op": "add", "args": ["JO_L", "JO_R"]},
                {"id": "check", "op": "sub", "args": ["sum", "JO"]},
                {"id": "silent", "op": "sub", "args": ["sum", "JO_h1"]},
            ],
        },
        {
            "name": "VNC L+R then unlabeled back to n_seed",
            "want": 6365,
            "steps": [
                {"id": "lab", "op": "add", "args": ["VNC_L", "VNC_R"]},
                {"id": "unlab", "op": "sub", "args": ["VNC", "lab"]},
                {"id": "back", "op": "add", "args": ["lab", "unlab"]},
            ],
        },
        {
            "name": "which VNC side is larger?",
            "want": 1,
            "steps": [
                {"id": "c", "op": "cmp", "args": ["VNC_L", "VNC_R"]},
            ],
        },
        {
            "name": "DNg29 two CNS graphs, none in hemibrain",
            "want": 2,
            "steps": [
                {"id": "both", "op": "add", "args": ["DNg29_M", "DNg29_B"]},
                {"id": "per", "op": "div", "args": ["both", 2]},
                {"id": "gap", "op": "sub", "args": ["per", "DNg29_H"]},
            ],
        },
        {
            "name": "three-trial net heading then sign",
            "want": -1,
            "steps": [
                {"id": "L", "op": "add", "args": ["T001_L", "T002_L"]},
                {"id": "Lall", "op": "add", "args": ["L", "T02_L"]},
                {"id": "R", "op": "add", "args": ["T001_R", "T002_R"]},
                {"id": "Rall", "op": "add", "args": ["R", "T02_R"]},
                {"id": "net", "op": "sub", "args": ["Lall", "Rall"]},
                {"id": "sgn", "op": "trit", "args": ["net"]},
            ],
        },
        {
            "name": "T001 and T002 agree left; consensus with Fly02",
            "want": 0,
            "steps": [
                {"id": "h1", "op": "sub", "args": ["T001_L", "T001_R"]},
                {"id": "s1", "op": "trit", "args": ["h1"]},
                {"id": "h2", "op": "sub", "args": ["T002_L", "T002_R"]},
                {"id": "s2", "op": "trit", "args": ["h2"]},
                {"id": "agree", "op": "cons", "args": ["s1", "s2"]},
                {"id": "h3", "op": "sub", "args": ["T02_L", "T02_R"]},
                {"id": "s3", "op": "trit", "args": ["h3"]},
                {"id": "all3", "op": "cons", "args": ["agree", "s3"]},
            ],
        },
        {
            "name": "Fly02 miss magnitude vs leftover hop horizon",
            "want": 1,
            "steps": [
                {"id": "h", "op": "sub", "args": ["T02_L", "T02_R"]},
                {"id": "mag", "op": "abs", "args": ["h"]},
                {"id": "vs", "op": "cmp", "args": ["mag", "HOPS"]},
            ],
        },
        {
            "name": "JO recover: (L+R)÷3×3",
            "want": 672,
            "steps": [
                {"id": "s", "op": "add", "args": ["JO_L", "JO_R"]},
                {"id": "q", "op": "div", "args": ["s", 3]},
                {"id": "back", "op": "mul", "args": ["q", 3]},
            ],
        },
        {
            "name": "non-GABA cells then compare to GABA",
            "want": 1,
            "steps": [
                {"id": "ex", "op": "sub", "args": ["NEURONS", "GABA"]},
                {"id": "c", "op": "cmp", "args": ["ex", "GABA"]},
            ],
        },
        {
            "name": "hemibrain JO+KC vs Male JO seed",
            "want": 1,
            "steps": [
                {"id": "hk", "op": "add", "args": ["H_JO", "KC"]},
                {"id": "c", "op": "cmp", "args": ["hk", "JO"]},
            ],
        },
    ]


def main() -> int:
    reg = registry()
    rows = []
    for ch in chains():
        ran = run_chain(reg, ch["steps"])
        # last step is the answer
        got = ran["trace"][-1]["value"]
        want = ch["want"]
        ok = got == want
        rows.append(
            {
                "name": ch["name"],
                "want": want,
                "got": got,
                "ok": ok,
                "n_steps": len(ch["steps"]),
                "trace": ran["trace"],
            }
        )
        print(f"{'OK' if ok else 'FAIL'}  {ch['name']}: {got} (want {want}) steps={len(ch['steps'])}")
    fail = [r["name"] for r in rows if not r["ok"]]
    doc = {
        "pin": "AEB2AD",
        "free_parameters": 0,
        "n": len(rows),
        "n_ok": len(rows) - len(fail),
        "fail": fail,
        "overall_ok": not fail,
        "n_steps_total": sum(r["n_steps"] for r in rows),
        "registry": reg,
        "chains": rows,
        "note": "Multi-step worksheets. Each step is trit ALU. Inputs are measured counts.",
    }
    OUT.write_text(json.dumps(doc, indent=2), encoding="utf-8")
    print(f"  arith_steps {doc['n_ok']}/{doc['n']}  total_steps={doc['n_steps_total']}")
    print(f"  wrote {OUT}")
    return 0 if doc["overall_ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
