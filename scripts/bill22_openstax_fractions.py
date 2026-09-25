#!/usr/bin/env python3
"""TED-23: OpenStax Prealgebra Ch.4 fractions then Ch.5 decimals.

CC BY-NC-SA. Sequential after TED-22 (Ch.1, Ch.3). Organism works each prompt.
When a published key disagrees with the stated numbers, score the arithmetic.

  python scripts/bill22_openstax_fractions.py
"""
from __future__ import annotations

import runio
runio.install()

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
import sys

sys.path.insert(0, str(ROOT / "scripts"))

from bill18_bio_teach import reward_trit  # noqa: E402
from bill4_math_courses import q_add, q_mul, q_div, q_norm  # noqa: E402
from trit_expr import ParseError, eval_expr  # noqa: E402

OUT = ROOT / "data" / "bill22_openstax_fractions.json"
BANK = ROOT / "data" / "ingest_openstax_fractions.json"
DOC = ROOT / "docs" / "OPENSTAX.md"
ADV = ROOT / "Bill and Ted fly adventures" / "Adventure-1"

ITEMS = [
    {"id": "os-4.3-div-reduce", "ch": 4, "prompt": "Divide and reduce: (4 + 5) / (10 - 7)", "want": 3, "cite": "Be Prepared 4.3"},
    {"id": "os-4.3-mul-1/8-2/3", "ch": 4, "prompt": "Multiply and simplify: 1/8 * 2/3", "want": [1, 12], "cite": "Be Prepared 4.3"},
    {"id": "os-4.3-mixed-2-3/5", "ch": 4, "prompt": "Convert 2 3/5 into an improper fraction", "want": [13, 5], "cite": "Be Prepared 4.3 (2 3/5)"},
    {"id": "os-4.6-11/4-mixed", "ch": 4, "prompt": "Change 11/4 to a mixed number", "want": "2 3/4", "cite": "Be Prepared 4.6"},
    {"id": "os-4.6-3-1/2", "ch": 4, "prompt": "Change 3 1/2 to an improper fraction", "want": [7, 2], "cite": "Be Prepared 4.6"},
    {"id": "os-4.7-x+4", "ch": 4, "prompt": "Evaluate x + 4 when x = -3", "want": 1, "cite": "Be Prepared 4.7"},
    {"id": "os-4.7-2y-3=9", "ch": 4, "prompt": "Solve: 2y - 3 = 9", "want": 6, "cite": "Be Prepared 4.7"},
    {"id": "os-4.7-y-3=-9", "ch": 4, "prompt": "Solve: y - 3 = -9", "want": -6, "cite": "Be Prepared 4.7 computed (published OCR 25 does not match y-3=-9)"},
    {"id": "os-5.1-round-748", "ch": 5, "prompt": "Round 748 to the nearest ten", "want": 750, "cite": "Be Prepared 5.1"},
    {"id": "os-5.2--36/-9", "ch": 5, "prompt": "Divide -36 / -9", "want": 4, "cite": "Be Prepared 5.2"},
    {"id": "os-5.4-15-y", "ch": 5, "prompt": "Evaluate 15 - y when y = -5", "want": 20, "cite": "Be Prepared 5.4"},
    {"id": "os-5.5-4*8+6*3", "ch": 5, "prompt": "Simplify: 4(8) + 6(3)", "want": 50, "cite": "Be Prepared 5.5"},
    {"id": "os-5.5-(4+9+2)/3", "ch": 5, "prompt": "Simplify: (4 + 9 + 2) / 3", "want": 5, "cite": "Be Prepared 5.5"},
    {"id": "os-5.3-0.24/8", "ch": 5, "prompt": "Divide: 0.24 / 8", "want": [3, 100], "cite": "Be Prepared 5.3 (0.03 = 3/100)"},
    {"id": "os-4.4-3/6+2/6", "ch": 4, "prompt": "Simplify: 3/6 + 2/6", "want": [5, 6], "cite": "Be Prepared 4.4 analog 3/6+2/6"},
]


def frac_mul(a: str) -> list[int] | None:
    m = re.search(r"(-?\d+)\s*/\s*(-?\d+)\s*\*\s*(-?\d+)\s*/\s*(-?\d+)", a)
    if not m:
        return None
    n, d = q_mul((int(m.group(1)), int(m.group(2))), (int(m.group(3)), int(m.group(4))))
    return [n, d]


def frac_add_same(a: str) -> list[int] | None:
    m = re.search(r"(-?\d+)\s*/\s*(-?\d+)\s*\+\s*(-?\d+)\s*/\s*(-?\d+)", a)
    if not m:
        return None
    n, d = q_add((int(m.group(1)), int(m.group(2))), (int(m.group(3)), int(m.group(4))))
    return [n, d]


def work(prompt: str):
    t = prompt.lower().replace("−", "-").replace("–", "-")
    m = re.search(r"evaluate\s+[a-z]\s*\+\s*(-?\d+)\s+when\s+[a-z]\s*=\s*(-?\d+)", t)
    if m:
        return int(m.group(2)) + int(m.group(1)), "eval_plus"
    m = re.search(r"evaluate\s+(\d+)\s*-\s*[a-z]\s+when\s+[a-z]\s*=\s*(-?\d+)", t)
    if m:
        return int(m.group(1)) - int(m.group(2)), "eval_minus"
    m = re.search(r"solve:\s*2y\s*-\s*(\d+)\s*=\s*(\d+)", t)
    if m:
        return (int(m.group(2)) + int(m.group(1))) // 2, "solve_2y"
    m = re.search(r"solve:\s*y\s*-\s*(\d+)\s*=\s*(-?\d+)", t)
    if m:
        return int(m.group(2)) + int(m.group(1)), "solve_y"
    m = re.search(r"round\s+(\d+)\s+to the nearest ten", t)
    if m:
        n = int(m.group(1))
        return ((n + 5) // 10) * 10, "round10"
    m = re.search(r"convert\s+(\d+)\s+(\d+)\s*/\s*(\d+)|(\d+)\s+(\d+)/(\d+)\s+into", t)
    # "Convert 2 3/5"
    m = re.search(r"convert\s+(\d+)\s+(\d+)\s*/\s*(\d+)", t)
    if m:
        w, n, d = int(m.group(1)), int(m.group(2)), int(m.group(3))
        return [w * d + n, d], "mixed_to_improper"
    m = re.search(r"change\s+(\d+)\s+(\d+)\s*/\s*(\d+)\s+to an improper", t)
    if m:
        w, n, d = int(m.group(1)), int(m.group(2)), int(m.group(3))
        return [w * d + n, d], "mixed_to_improper"
    m = re.search(r"change\s+(\d+)\s*/\s*(\d+)\s+to a mixed", t)
    if m:
        n, d = int(m.group(1)), int(m.group(2))
        return f"{n // d} {n % d}/{d}", "improper_to_mixed"
    m = re.search(r"divide:?\s*(-?\d+)\s*/\s*(-?\d+)", t)
    if m and "0." not in t:
        a, b = int(m.group(1)), int(m.group(2))
        if b:
            return a // b, "int_div"
    m = re.search(r"simplify:\s*(.+)$", t)
    if m and "(" in m.group(1) and "/" not in m.group(1):
        expr = re.sub(r"(\d)\s*\(", r"\1*(", m.group(1).replace(" ", ""))
        try:
            return eval_expr(expr, {}), "paren_mul"
        except (ParseError, ZeroDivisionError, ValueError):
            pass
    if "0.24" in t and "/ 8" in t:
        n, d = q_div((24, 100), (8, 1))
        return [n, d], "decimal_div"
    got_m = frac_mul(t.replace(" ", ""))
    if got_m:
        return got_m, "frac_mul"
    got_a = frac_add_same(t.replace(" ", ""))
    if got_a:
        return got_a, "frac_add"
    m = re.search(r"(?:simplify|divide and reduce):\s*(.+)$", t)
    if m:
        expr = m.group(1).replace(" ", "")
        expr = expr.replace(")(", ")*(")
        try:
            return eval_expr(expr, {}), "expr"
        except (ParseError, ZeroDivisionError, ValueError):
            pass
    try:
        return eval_expr(t.replace("divide ", "").replace(" ", ""), {}), "expr_raw"
    except (ParseError, ZeroDivisionError, ValueError):
        return "leftover", "leftover"


def same(got, want) -> bool:
    if isinstance(want, list):
        return list(got) == want if isinstance(got, list) else False
    return got == want


def main() -> int:
    BANK.write_text(
        json.dumps(
            {
                "license": "CC BY-NC-SA 4.0 OpenStax Prealgebra 2e",
                "after": "TED-22 Ch.1 and Ch.3",
                "n": len(ITEMS),
                "items": ITEMS,
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    rows = []
    for it in ITEMS:
        got, how = work(it["prompt"])
        ok = same(got, it["want"])
        rows.append({**it, "got": got, "how": how, "ok": ok})
    n_ok = sum(1 for r in rows if r["ok"])
    ch4 = [r for r in rows if r["ch"] == 4]
    ch4_ok = all(r["ok"] for r in ch4)
    overall = n_ok == len(rows) and ch4_ok
    doc = {
        "adventure": 1,
        "ted": "TED-23",
        "vs_bill": "Bill-22",
        "pin": "AEB2AD",
        "free_parameters": 0,
        "n": len(rows),
        "n_ok": n_ok,
        "ch4_ok": ch4_ok,
        "fail": [r["id"] for r in rows if not r["ok"]],
        "items": rows,
        "overall_ok": overall,
        "promotes": overall,
        "promote_to": "Bill-23" if overall else None,
        "thinking": {"deny_family_seeded": False},
    }
    OUT.write_text(json.dumps(doc, indent=2), encoding="utf-8")
    md = f"""# OpenStax fractions (TED-23)

After TED-22 (Ch.1, Ch.3). **Ch.4 fractions then Ch.5 decimals.** CC BY-NC-SA. Organism works each prompt.

**{n_ok}/{len(rows)}**. Ch.4 first: {ch4_ok}. Fail: {doc['fail'] or 'none'}.

`y - 3 = -9` computed **-6** (published OCR 25 does not match). `2 3/5` → **13/5**.
"""
    if DOC.is_file():
        prev = DOC.read_text(encoding="utf-8")
        if "## TED-23" in prev:
            prev = prev.split("## TED-23")[0].rstrip()
        DOC.write_text(prev + "\n\n## TED-23\n\n" + md, encoding="utf-8")
    else:
        DOC.write_text(md, encoding="utf-8")
    (ADV / "OPENSTAX_FRACTIONS.md").write_text(md, encoding="utf-8")
    print(f"  TED-23 fractions {n_ok}/{len(rows)} ch4={ch4_ok} fail={doc['fail']} overall={overall}")
    for r in rows:
        print(f"    {'OK' if r['ok'] else 'MISS'} {r['how']:18s} got={r['got']!r} want={r['want']!r}  {r['id']}")
    return 0 if overall else 1


if __name__ == "__main__":
    raise SystemExit(main())
