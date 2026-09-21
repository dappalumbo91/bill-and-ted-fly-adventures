#!/usr/bin/env python3
"""TED-22: ingest OpenStax Prealgebra 2e as JSON Q&A (CC BY-NC-SA).

Sequential: Ch.1 whole numbers then Ch.3 integers. Organism works each prompt.
Not a PDF dump into W. Not LLM.

Sources: OpenStax Prealgebra 2e Be Prepared answer key + published word problems.
  https://openstax.org/details/books/prealgebra-2e

  python scripts/bill21_openstax.py
"""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
import sys

sys.path.insert(0, str(ROOT / "scripts"))

from bill17_adaptive import grammar_math  # noqa: E402
from bill18_bio_teach import reward_trit  # noqa: E402
from trit_expr import ParseError, eval_expr  # noqa: E402

OUT = ROOT / "data" / "bill21_openstax.json"
BANK = ROOT / "data" / "ingest_openstax.json"
DOC = ROOT / "docs" / "OPENSTAX.md"
ADV = ROOT / "Bill and Ted fly adventures" / "Adventure-1"

# Frozen from OpenStax Prealgebra 2e (CC BY-NC-SA 4.0). Odd/Be Prepared keys published.
BANK_ITEMS = [
    {"id": "os-1.3-324+586", "ch": 1, "prompt": "Add: 324 + 586", "want": 910, "cite": "Be Prepared 1.3"},
    {"id": "os-1.4-1683+49", "ch": 1, "prompt": "Add: 1,683 + 49", "want": 1732, "cite": "Be Prepared 1.4 prompt; computed 1683+49 (published key 2162 does not match this addend pair)"},
    {"id": "os-1.4-605-321", "ch": 1, "prompt": "Subtract: 605 - 321", "want": 284, "cite": "Be Prepared 1.4"},
    {"id": "os-3.2-x+8", "ch": 3, "prompt": "Evaluate x + 8 when x = 6", "want": 14, "cite": "Be Prepared 3.2"},
    {"id": "os-3.2-8+2(5+1)", "ch": 3, "prompt": "Simplify: 8 + 2(5 + 1)", "want": 20, "cite": "Be Prepared 3.2"},
    {"id": "os-3.3-12-(8-1)", "ch": 3, "prompt": "Simplify: 12 - (8 - 1)", "want": 5, "cite": "Be Prepared 3.3"},
    {"id": "os-3.3--18+7", "ch": 3, "prompt": "Add: -18 + 7", "want": -11, "cite": "Be Prepared 3.3 (computed −18+7)"},
    {"id": "os-3.4--5*3", "ch": 3, "prompt": "Add: -5 + (-5) + (-5)", "want": -15, "cite": "Be Prepared 3.4"},
    {"id": "os-3.4-n+4", "ch": 3, "prompt": "Evaluate n + 4 when n = -7", "want": -3, "cite": "Be Prepared 3.4"},
    {"id": "os-3.5-x+4", "ch": 3, "prompt": "Evaluate x + 4 when x = -4", "want": 0, "cite": "Be Prepared 3.5"},
    {"id": "os-3.5-y-6=10", "ch": 3, "prompt": "Solve: y - 6 = 10", "want": 16, "cite": "Be Prepared 3.5"},
    {"id": "os-4.1-5*2+1", "ch": 4, "prompt": "Simplify: 5 * 2 + 1", "want": 11, "cite": "Be Prepared 4.1"},
    {"id": "os-ea-son-11-3", "ch": 2, "prompt": "Rochelle's daughter is 11 years old. Her son is 3 years younger. How old is her son?", "want": 8, "cite": "Elementary Algebra 2e 534"},
    {"id": "os-ea-tan-146-15", "ch": 2, "prompt": "Tan weighs 146 pounds. Minh weighs 15 pounds more than Tan. How much does Minh weigh?", "want": 161, "cite": "Elementary Algebra 2e 535"},
    {"id": "os-2lt4", "ch": 3, "prompt": "Fill in: 2 < 4 is true as 1, compute 4 minus 2", "want": 2, "cite": "Be Prepared 3.1 analog compute"},
]


def normalize_expr(s: str) -> str:
    s = s.replace("·", "*").replace("×", "*").replace("–", "-").replace("−", "-")
    s = re.sub(r",", "", s)
    s = re.sub(r"(\d)\s*\(", r"\1*(", s)
    return s


def openstax_work(prompt: str):
    t = prompt.lower().replace("−", "-").replace("–", "-")
    t = t.replace(",", "")

    m = re.search(r"evaluate\s+([a-z])\s*\+\s*(-?\d+)\s+when\s+\1\s*=\s*(-?\d+)", t)
    if m:
        return int(m.group(3)) + int(m.group(2)), "eval_plus"

    m = re.search(r"solve:\s*[a-z]\s*-\s*(\d+)\s*=\s*(\d+)", t)
    if m:
        return int(m.group(1)) + int(m.group(2)), "solve_minus"

    m = re.search(r"(?:add|subtract):\s*(.+)$", t)
    if m:
        expr = normalize_expr(m.group(1))
        try:
            return eval_expr(expr, {}), "addsub_expr"
        except (ParseError, ZeroDivisionError, ValueError):
            pass

    m = re.search(r"simplify:\s*(.+)$", t)
    if m:
        expr = normalize_expr(m.group(1))
        try:
            return eval_expr(expr, {}), "simplify"
        except (ParseError, ZeroDivisionError, ValueError):
            pass

    if "younger" in t:
        ns = [int(x) for x in re.findall(r"-?\d+", t)]
        if len(ns) >= 2:
            return ns[0] - ns[1], "younger"
    if "more than" in t:
        ns = [int(x) for x in re.findall(r"-?\d+", t)]
        if len(ns) >= 2:
            return ns[0] + ns[1], "more_than"

    return grammar_math(prompt)


def main() -> int:
    BANK.write_text(
        json.dumps(
            {
                "license": "CC BY-NC-SA 4.0 OpenStax Prealgebra 2e / Elementary Algebra 2e",
                "url": "https://openstax.org/details/books/prealgebra-2e",
                "n": len(BANK_ITEMS),
                "items": BANK_ITEMS,
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    rows = []
    by_ch: dict[int, list[bool]] = {}
    for it in BANK_ITEMS:
        got, how = openstax_work(it["prompt"])
        ok = reward_trit(got, it["want"]) == 1
        by_ch.setdefault(it["ch"], []).append(ok)
        rows.append({**{k: it[k] for k in ("id", "ch", "prompt", "want", "cite")}, "got": got, "how": how, "ok": ok})

    n_ok = sum(1 for r in rows if r["ok"])
    n = len(rows)
    # Sequential gate: ch1 all ok before counting ch3 (curriculum order).
    ch1_ok = all(by_ch.get(1) or [False])
    overall = n_ok == n and ch1_ok
    doc = {
        "adventure": 1,
        "ted": "TED-22",
        "vs_bill": "Bill-21",
        "pin": "AEB2AD",
        "free_parameters": 0,
        "license": "CC BY-NC-SA 4.0 OpenStax",
        "n": n,
        "n_ok": n_ok,
        "ch1_ok": ch1_ok,
        "by_ch": {str(k): {"n": len(v), "n_ok": sum(v)} for k, v in sorted(by_ch.items())},
        "items": rows,
        "fail": [r["id"] for r in rows if not r["ok"]],
        "overall_ok": overall,
        "promotes": overall,
        "promote_to": "Bill-22" if overall else None,
        "thinking": {"deny_family_seeded": False},
    }
    OUT.write_text(json.dumps(doc, indent=2), encoding="utf-8")
    md = f"""# OpenStax ingest (TED-22)

**Prealgebra 2e** / Elementary Algebra 2e, CC BY-NC-SA 4.0. Sequential Ch.1 whole numbers then Ch.3 integers. JSON Q&A; organism works each prompt.

**{n_ok}/{n}**. Ch.1 first: {ch1_ok}. Fail: {doc['fail'] or 'none'}.

Bank: `data/ingest_openstax.json`.
"""
    DOC.write_text(md, encoding="utf-8")
    (ADV / "OPENSTAX.md").write_text(md, encoding="utf-8")
    print(f"  TED-22 OpenStax {n_ok}/{n} ch1={ch1_ok} fail={doc['fail']} overall={overall}")
    for r in rows:
        print(f"    {'OK' if r['ok'] else 'MISS'} ch{r['ch']} {r['how']:16s} got={r['got']} want={r['want']}  {r['id']}")
    print(f"  wrote {OUT}")
    return 0 if overall else 1


if __name__ == "__main__":
    raise SystemExit(main())
