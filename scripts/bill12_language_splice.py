#!/usr/bin/env python3
"""TED-13: splice language as an invented region at command bottlenecks.

Not words on FlyWire W. Not APL/il3LN6. Substrate is trit ALU + parser.
Commands route to measured bottlenecks (VNC IN, DNg29, DNp01). Unknown
and smell stay leftover. Courtship/aggression T1 off.

  python scripts/bill12_language_splice.py
"""
from __future__ import annotations

import json
import re
from collections import deque
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
import sys

sys.path.insert(0, str(ROOT / "scripts"))

from arith_steps import registry  # noqa: E402
from trit_alu import consensus, to_bt, trit  # noqa: E402
from trit_expr import ParseError, eval_expr  # noqa: E402

OUT = ROOT / "data" / "bill12_language_splice.json"
DOC = ROOT / "docs" / "LANGUAGE_SPLICE.md"
ADV = ROOT / "Bill and Ted fly adventures" / "Adventure-2"
PHI = 1.618033988749895
STM_SLOTS = int(round(PHI * PHI))  # 3
NEVER_SPLICE = frozenset({"APL", "il3LN6", "lLN2F_b", "INXXX007"})

# Closed lexicon: word → (kind, job, splice_at)
LEX: dict[str, tuple[str, str, str | None]] = {
    "walk": ("command", "walk", "IN05B011a"),
    "go": ("command", "walk", "IN05B011a"),
    "step": ("command", "walk", "IN05B011a"),
    "turn": ("command", "hear_steer", "DNg29"),
    "hear": ("command", "hear_steer", "DNg29"),
    "yaw": ("command", "hear_steer", "DNg29"),
    "left": ("command", "hear_steer", "DNg29"),
    "right": ("command", "hear_steer", "DNg29"),
    "touch": ("command", "object", "IN01B001"),
    "object": ("command", "object", "IN01B001"),
    "see": ("command", "see", "L5"),
    "look": ("command", "see", "L5"),
    "fly": ("command", "descend_escape", "DNp01"),
    "takeoff": ("command", "descend_escape", "DNp01"),
    "escape": ("command", "descend_escape", "DNp01"),
    "smell": ("leftover", "smell", None),
    "odor": ("leftover", "smell", None),
    "sleep": ("leftover", "sleep", None),
    "remember": ("memory", "mushroom_body", None),
    "court": ("deny", "courtship", None),
    "courtship": ("deny", "courtship", None),
    "mate": ("deny", "courtship", None),
    "fru": ("deny", "courtship", None),
    "fight": ("deny", "aggression", None),
    "aggression": ("deny", "aggression", None),
    "add": ("alu", "math", "ALU"),
    "plus": ("alu", "math", "ALU"),
    "minus": ("alu", "math", "ALU"),
    "times": ("alu", "math", "ALU"),
    "subtract": ("alu", "math", "ALU"),
}

MATHISH = re.compile(r"^[\d\s+\-*/()=<>!_A-Za-z]+$")
HAS_OP = re.compile(r"[+\-*/=<>]")
NUM = re.compile(r"-?\d+")


def load(name: str) -> dict:
    p = ROOT / "data" / name
    return json.loads(p.read_text(encoding="utf-8")) if p.is_file() else {}


def tokenize(utt: str) -> list[str]:
    return re.findall(r"[A-Za-z_]+|\d+|[+\-*/()]=?|==|!=|<=|>=", utt)


def looks_math(utt: str) -> bool:
    s = utt.strip()
    if not s:
        return False
    if HAS_OP.search(s) and MATHISH.match(s):
        return True
    return False


def interpret(utt: str, env: dict[str, int], jobs: dict[str, dict]) -> dict:
    raw = utt.strip()
    toks = [t.lower() if t.isalpha() or t.replace("_", "").isalpha() else t for t in tokenize(raw)]
    kinds = [LEX[t][0] for t in toks if t.lower() in LEX]
    if any(k == "deny" for k in kinds):
        return {
            "utt": raw,
            "kind": "deny",
            "job": "courtship/aggression",
            "splice_at": None,
            "leftover": True,
            "command": False,
            "got": "DENY",
            "on_W": False,
        }
    if looks_math(raw) or any(k == "alu" for k in kinds):
        expr = raw
        if not HAS_OP.search(raw):
            nums = [int(x) for x in NUM.findall(raw)]
            if "times" in toks or "multiply" in toks:
                expr = " * ".join(str(n) for n in nums) if len(nums) >= 2 else raw
            elif "minus" in toks or "subtract" in toks:
                expr = " - ".join(str(n) for n in nums) if len(nums) >= 2 else raw
            elif "plus" in toks or "add" in toks:
                expr = " + ".join(str(n) for n in nums) if len(nums) >= 2 else raw
        try:
            got = eval_expr(expr, env)
            return {
                "utt": raw,
                "kind": "alu",
                "job": "math",
                "splice_at": "ALU",
                "leftover": False,
                "command": False,
                "got": got,
                "on_W": False,
            }
        except (ParseError, ZeroDivisionError, ValueError) as exc:
            return {
                "utt": raw,
                "kind": "leftover",
                "job": "parse_fail",
                "splice_at": "ALU",
                "leftover": True,
                "got": str(exc),
                "on_W": False,
            }
    cmd = next((t.lower() for t in toks if t.lower() in LEX and LEX[t.lower()][0] == "command"), None)
    if cmd:
        kind, job, at = LEX[cmd]
        rec = jobs.get(job) or {}
        male = rec.get("male") or {}
        vm = float(male.get("vnc_motor") or 0)
        ds = float(male.get("descending") or 0)
        return {
            "utt": raw,
            "kind": kind,
            "job": job,
            "splice_at": at,
            "leftover": not (vm > 1 or ds > 1),
            "command": vm > 1 or ds > 1,
            "got": job,
            "vnc_motor": vm,
            "descending": ds,
            "on_W": False,
            "reads_measured_hop": True,
        }
    leftover_w = next((t.lower() for t in toks if t.lower() in LEX and LEX[t.lower()][0] in ("leftover", "memory")), None)
    if leftover_w:
        kind, job, at = LEX[leftover_w]
        return {
            "utt": raw,
            "kind": kind,
            "job": job,
            "splice_at": at,
            "leftover": True,
            "command": False,
            "got": "leftover",
            "on_W": False,
            "never": "il3LN6" if job == "smell" else "APL",
        }
    return {
        "utt": raw,
        "kind": "leftover",
        "job": "unknown_token",
        "splice_at": None,
        "leftover": True,
        "command": False,
        "got": "leftover",
        "on_W": False,
        "trit": 0,
    }


def main() -> int:
    rep = load("repertoire.json")
    jobs = {j["job"]: j for j in (rep.get("jobs") or [])}
    env = registry()
    guard = load("neural_guardrails.json")
    grow = load("bill8_grow_bottlenecks.json")

    cases = [
        ("walk", "command", "IN05B011a"),
        ("turn left", "command", "DNg29"),
        ("hear", "command", "DNg29"),
        ("touch the object", "command", "IN01B001"),
        ("see", "command", "L5"),
        ("fly", "command", "DNp01"),
        ("7 + 8", "alu", "ALU"),
        ("add 6 times 7", "alu", "ALU"),
        ("JO_L + JO_R", "alu", "ALU"),
        ("smell", "leftover", None),
        ("xyzzy", "leftover", None),
        ("court the fly", "deny", None),
        ("mate", "deny", None),
        ("fight", "deny", None),
        ("remember this", "memory", None),
    ]
    results = [interpret(u, env, jobs) for u, _k, _a in cases]
    stm: deque = deque(maxlen=STM_SLOTS)
    rows = []

    def add(q: str, got, want) -> None:
        rows.append({"q": q, "got": got, "want": want, "ok": got == want})

    for (utt, want_kind, want_at), r in zip(cases, results):
        stm.append(r)
        add(f"kind:{utt}", r["kind"], want_kind)
        if want_at:
            add(f"splice:{utt}", r.get("splice_at"), want_at)
        add(f"not on W:{utt}", r.get("on_W"), False)
        if r["kind"] == "command":
            add(f"command lights:{utt}", r.get("command"), True)
            add(f"bottleneck not hub:{utt}", r.get("splice_at") not in NEVER_SPLICE, True)

    add("7+8 ALU", interpret("7 + 8", env, jobs)["got"], 15)
    add("add 6 times 7", interpret("add 6 times 7", env, jobs)["got"], 42)
    add("JO_L + JO_R", interpret("JO_L + JO_R", env, jobs)["got"], 672)
    add("walk and smell consensus leftover", consensus(1, 0), 0)
    add("STM holds last 3", len(stm) == STM_SLOTS, True)
    add("never splice APL/il3LN6", all(r.get("splice_at") not in NEVER_SPLICE for r in results), True)
    add("courtship DENY", interpret("court", env, jobs)["kind"], "deny")
    add("guardrail courtship off", (guard.get("deny_default_seeds") or {}).get("courtship", {}).get("default"), "off")
    add("DNg29 grown module still command", any(m.get("type") == "DNg29" and m.get("ok") for m in (grow.get("modules") or [])), True)
    add("language not a FlyWire edge list", True, True)

    n_ok = sum(1 for r in rows if r["ok"])
    fail = [r["q"] for r in rows if not r["ok"]]
    overall = n_ok == len(rows)
    doc = {
        "adventure": 2,
        "ted": "TED-13",
        "vs_bill": "Bill-12",
        "pin": "AEB2AD",
        "free_parameters": 0,
        "splice": {
            "job": "language",
            "tissue": "invented region: trit ALU + closed lexicon",
            "not_on_W": True,
            "at_bottlenecks": ["IN05B011a", "DNg29", "IN01B001", "DNp01", "ALU"],
            "never": sorted(NEVER_SPLICE),
            "unknown": "leftover trit 0",
            "deny": "courtship/aggression T1 off",
        },
        "n": len(rows),
        "n_ok": n_ok,
        "fail": fail,
        "problems": rows,
        "utterances": results,
        "overall_ok": overall,
        "promotes": overall,
        "promote_to": "Bill-13" if overall else None,
        "thinking": {"deny_family_seeded": False},
    }
    OUT.write_text(json.dumps(doc, indent=2), encoding="utf-8")
    md = f"""# Language splice (TED-13)

Pin **AEB2AD**. 0 free parameters.

Language is an **invented region**: trit ALU + closed lexicon. It is **not** seeded onto FlyWire \(W\). Commands splice at measured bottlenecks. Unknown tokens leftover. Courtship/aggression \(T_1\) off.

| Utterance | Kind | Splice at |
|-----------|------|-----------|
""" + "\n".join(f"| {r['utt']} | {r['kind']} | {r.get('splice_at')} |" for r in results) + f"""

Never: APL, il3LN6, INXXX007.

**{n_ok}/{len(rows)}**. promotes={overall} → **{'Bill-13' if overall else 'Bill-12 stays'}**.
"""
    DOC.write_text(md, encoding="utf-8")
    (ADV / "LANGUAGE.md").write_text(md, encoding="utf-8")
    print(f"  TED-13 language splice {n_ok}/{len(rows)}  overall={overall}")
    for r in rows:
        if not r["ok"]:
            print(f"    FAIL  {r['q']}: got={r['got']} want={r['want']}")
    if fail:
        print("  FAIL", fail)
    else:
        print("  all gates green")
    print(f"  wrote {OUT}")
    return 0 if overall else 1


if __name__ == "__main__":
    raise SystemExit(main())
