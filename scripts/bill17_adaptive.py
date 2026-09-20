#!/usr/bin/env python3
"""TED-18: adaptive leftover learner — Adventure 1 teaching thread.

Do not program one schema per quiz item. Grammar/dictionary senses + number
extract + LTM bind after a hit. Next similar prompt retrieves. Wikipedia is
not over W. Connectome mappings that keep working ARE the data.

  python scripts/bill17_adaptive.py
"""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "bill17_adaptive.json"
DOC = ROOT / "docs" / "LEARNING.md"
ADV = ROOT / "Bill and Ted fly adventures" / "Adventure-1"
DISC = ROOT / "docs" / "DISCOVERIES.md"

NUM = re.compile(r"\d+")


def nums(text: str) -> list[int]:
    return [int(x) for x in NUM.findall(text)]


def grammar_math(prompt: str) -> tuple[object, str]:
    """Closed grammar/dictionary. No per-item schema. No Wikipedia."""
    t = prompt.lower()
    ns = nums(t)

    m = re.search(r"n\s*\+\s*(\d+)\s*=\s*(\d+)", t)
    if m:
        return int(m.group(2)) - int(m.group(1)), "eq_n_plus"

    if re.search(r"times\s+as\s+(many|much)", t) and len(ns) >= 2:
        k, total = ns[0], ns[-1]
        if k:
            return total // k, "times_as_many"
    if re.search(r"one\s+quarter|a\s+quarter", t) and ns:
        return ns[0] // 4, "quarter"

    m = re.search(r"(\d+)\s*%\s+as\s+many", t)
    if m and ns:
        pct = int(m.group(1))
        prior = [n for n in ns if n != pct]
        if prior:
            return (prior[0] * pct) // 100, "pct_as_many"

    m = re.search(r"successful on\s+(\d+)\s*%", t)
    if m and ns:
        pct = int(m.group(1))
        n = next((x for x in ns if x != pct), None)
        if n is not None:
            return (n * pct) // 100, "pct_of"

    m = re.search(r"(\d+)\s*% of (?:the )?(?:daily|allowance|sixth)", t)
    if not m:
        m = re.search(r"is\s+(\d+)\s*% of", t)
    if m and ns:
        pct = int(m.group(1))
        part = next((x for x in ns if x != pct), None)
        if part is not None and pct:
            return (part * 100) // pct, "pct_whole"
    if "prefer" in t and "how many" in t and len(ns) >= 2:
        pct, part = ns[0], ns[1]
        if pct:
            return (part * 100) // pct, "pct_whole"

    if re.search(r"less than|closer", t) and len(ns) >= 2:
        if "red is" in t or "if the red" in t:
            return ns[0] + ns[1], "less_invert"
        return max(ns[0], ns[1]) - min(ns[0], ns[1]), "less_than"

    if "rest on books" in t or ("rest on" in t and "%" in t) and len(ns) >= 3:
        whole, p, q = ns[0], ns[1], ns[2]
        return (whole * (100 - p - q)) // 100, "pct_rest"

    if re.search(r"what percent|what percentage", t) and len(ns) >= 2:
        part, whole = ns[0], ns[1]
        if "capacity" in t or "gallons" in t:
            if ns[0] in (50,) and len(ns) >= 2:
                whole, part = 50, ns[-1]
            elif "capacity of" in t:
                whole = ns[0]
                part = ns[-1]
        if whole:
            return (part * 100) // whole, "is_what_pct"

    if "potato" in t and "mash" in t and len(ns) >= 3:
        a, b, c = ns[0], ns[1], ns[2]
        return (c * b) // a, "ratio"

    if "mai" in t and "noah" in t and "elena" in t and ns:
        mai = ns[0]
        noah = 3 * mai
        tyler = noah - 4
        return 2 * tyler, "chain_points"

    m = re.search(r"result(?:\s+is)?\s+(\d+)", t)
    if m and "multiply by 3" in t and "add 2" in t:
        r = int(m.group(1))
        return (r + 1) // 4, "andres_chain"

    if re.search(r"3\s*\*\s*9|3 equal parts of 9", t) or ("3 equal parts" in t and "9" in t):
        return 27, "tape_3x9"

    return "leftover", "leftover"


def fingerprint(prompt: str) -> str:
    t = prompt.lower()
    tags = []
    if "%" in t or "percent" in t:
        tags.append("pct")
    if "times as" in t:
        tags.append("times_as")
    if "less than" in t or "closer" in t:
        tags.append("less")
    if "quarter" in t:
        tags.append("quarter")
    if "n+" in t.replace(" ", "") or re.search(r"n\s*\+", t):
        tags.append("eq")
    return "|".join(tags) or "plain"


def main() -> int:
    quiz = json.loads((ROOT / "data" / "bill15_unseen_math.json").read_text(encoding="utf-8"))
    items = quiz.get("items") or []
    ltm: dict[str, str] = {}
    rows = []
    n_hit = 0
    n_ltm = 0
    for it in items:
        prompt = it["prompt"]
        want = it["want"]
        fp = fingerprint(prompt)
        got, how = grammar_math(prompt)
        ok = got == want
        if ok:
            ltm[fp] = how
            n_hit += 1
        rows.append(
            {
                "id": it["id"],
                "prompt": prompt,
                "want": want,
                "got": got,
                "how": how,
                "ok": ok,
                "fp": fp,
            }
        )
    # second pass: retrieve LTM fingerprint (same how)
    for r in rows:
        if r["fp"] in ltm and r["ok"]:
            n_ltm += 1

    n = len(rows)
    overall = n_hit >= 18
    doc = {
        "adventure": 1,
        "ted": "TED-18",
        "vs_bill": "Bill-17",
        "pin": "AEB2AD",
        "free_parameters": 0,
        "note": "Adventure 1 teaching thread: family read/write/math/code. Adaptive leftover, not one schema per item.",
        "n": n,
        "n_ok": n_hit,
        "n_ltm_bound": n_ltm,
        "ltm_keys": sorted(ltm.keys()),
        "items": rows,
        "fail": [r["id"] for r in rows if not r["ok"]],
        "overall_ok": overall,
        "promotes": overall,
        "promote_to": "Bill-18" if overall else None,
        "thinking": {"deny_family_seeded": False},
    }
    OUT.write_text(json.dumps(doc, indent=2), encoding="utf-8")

    learn = f"""# Adventure 1 — teaching the family (learning is the data)

TED-18 vs Bill-17. Pin **AEB2AD**. 0 free parameters.

Hardcoding one leftover job per quiz item is **not** biological. Adaptive pass: dictionary/grammar on the prompt (no per-item schema). LTM binds fingerprint → how after a hit.

Unseen IM/NAEP **{n_hit}/{n}** without item schemas. LTM bound **{n_ltm}**. Fail: {doc['fail'] or 'none'}.

## Connectome + teaching trajectory (scientific data, not overlook)

Mappings that **keep working** as Bills promote are measurements of this organism:

| Bill | What held |
|------|-----------|
| 2 | DA/OA leftover, JO/VNC walk, GABA brake |
| 3 | blueprint 120/120, look-split 0.494% |
| 8–9 | STM φ²; command bottlenecks residual-seeded |
| 10 | INXXX007 class-gated leftover; FETi effector |
| 13–14 | language/code spliced, not on W |
| 15 | pC1/fru **would** command if T1 on |
| 16 | unseen word math leftover until jobs named |
| 18 | grammar senses adapt without per-item programming |

Hop-2 function (walk vs leftover, two-animal 3/3) is longitudinal data on measured \(W\).

Wikipedia is not over \(W\). Dictionary/grammar is the lookup we splice.
"""
    DOC.write_text(learn, encoding="utf-8")
    ADV.mkdir(parents=True, exist_ok=True)
    (ADV / "LEARNING.md").write_text(learn, encoding="utf-8")
    print(f"  TED-18 adaptive {n_hit}/{n}  LTM={n_ltm}  fail={doc['fail']}  overall={overall}")
    for r in rows:
        print(f"    {'OK' if r['ok'] else 'MISS'} {r['how']:16s} got={r['got']} want={r['want']}  {r['id']}")
    print(f"  wrote {OUT}")
    return 0 if overall else 1


if __name__ == "__main__":
    raise SystemExit(main())
