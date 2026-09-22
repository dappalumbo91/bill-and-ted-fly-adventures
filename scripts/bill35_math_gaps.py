#!/usr/bin/env python3
"""Fill the math gaps that were still wrong or still refusing.

Integer division was turning 1/3 * 1/4 into 0. Percent-of was flooring
35% of 90 to 31. 'What percent of 80 is 20' swapped the numbers and
returned 400. One-step equations, powers, tips, and discounts had no shape.

  python scripts/bill35_math_gaps.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from bill18_bio_teach import reward_trit  # noqa: E402
from bill21_openstax import BANK_ITEMS, openstax_work  # noqa: E402
from bill33_before_a2 import BLIND  # noqa: E402
from bill34_ch6_refine import FRESH, NEAR  # noqa: E402

OUT = ROOT / "data" / "bill35_math_gaps.json"
DOC = ROOT / "docs" / "MATH_GAPS.md"
ADV = ROOT / "Bill and Ted fly adventures" / "Adventure-1" / "MATH_GAPS.md"

# Published OpenStax wording, plus the error cases the worker was returning.
GAPS = [
    {
        "id": "os6-6.11",
        "prompt": "Simplify: 1/3 * 1/4",
        "want": "1/12",
        "kind": "expr",
        "cite": "Be Prepared 6.11; the product is 1/12. The integer ALU had returned 0.",
    },
    {
        "id": "ex-6.14",
        "prompt": "What number is 35% of 90?",
        "want": 31.5,
        "kind": "number",
        "cite": "Example 6.14. The percent grammar had returned 31.",
    },
    {
        "id": "ex-6.16",
        "prompt": "36 is 75% of what number?",
        "want": 48,
        "kind": "number",
        "cite": "Example 6.16",
    },
    {
        "id": "gap-what-percent",
        "prompt": "What percent of 80 is 20?",
        "want": 25,
        "kind": "number",
        "cite": "Same shape as Try It percent questions. The old order of the numbers returned 400.",
    },
    {
        "id": "gap-linear",
        "prompt": "Solve: 2y - 3 = 9",
        "want": 6,
        "kind": "number",
        "cite": "Be Prepared 4.7",
    },
    {
        "id": "gap-power",
        "prompt": "Simplify: 4^5",
        "want": 1024,
        "kind": "number",
        "cite": "Be Prepared 2.2, 4 to the fifth",
    },
    {
        "id": "gap-tip",
        "prompt": "A bill is 80 dollars. The tip is 20%. How much is the tip?",
        "want": 16,
        "kind": "number",
        "cite": "Chapter 6 tip example, 20% of 80",
    },
    {
        "id": "gap-sale",
        "prompt": "The price is 40 dollars. A 25% discount is taken. What is the sale price?",
        "want": 30,
        "kind": "number",
        "cite": "Chapter 6 discount",
    },
]

FRESH2 = [
    {"id": "fresh-frac", "prompt": "Simplify: 2/5 * 3/4", "want": "3/10", "kind": "expr"},
    {"id": "fresh-pct", "prompt": "What number is 15% of 60?", "want": 9, "kind": "number"},
    {"id": "fresh-base", "prompt": "12 is 40% of what number?", "want": 30, "kind": "number"},
    {"id": "fresh-wp", "prompt": "What percent of 50 is 10?", "want": 20, "kind": "number"},
    {"id": "fresh-lin", "prompt": "Solve: 3x + 4 = 19", "want": 5, "kind": "number"},
    {"id": "fresh-pow", "prompt": "Simplify: 2^6", "want": 64, "kind": "number"},
    {"id": "fresh-tip", "prompt": "A bill is 50 dollars. The tip is 10%. How much is the tip?", "want": 5, "kind": "number"},
    {"id": "fresh-sale", "prompt": "The price is 80 dollars. A 20% discount is taken. What is the sale price?", "want": 64, "kind": "number"},
]

NEAR2 = [
    {"id": "near-frac-sum", "prompt": "Simplify: 1/3 + 1/4", "want": "7/12", "kind": "expr"},
    {"id": "near-pct-part", "prompt": "What number is 25% of 80?", "want": 20, "kind": "number"},
    {"id": "near-lin-plus", "prompt": "Solve: 2y + 3 = 9", "want": 3, "kind": "number"},
    {"id": "near-pow", "prompt": "Simplify: 5^4", "want": 625, "kind": "number"},
    {"id": "near-discount-amount", "prompt": "The price is 40 dollars. A 25% discount is taken. What is the discount amount?", "want": 10, "kind": "number"},
    {"id": "near-gallons", "prompt": "Bin capacity 50 gallons. What percent is 5 gallons?", "want": 10, "kind": "number"},
]


def _same(got, want, kind: str) -> str:
    if got == "leftover":
        return "leftover"
    if kind == "expr":
        return "correct" if str(got).replace(" ", "") == str(want).replace(" ", "") else "wrong"
    try:
        if abs(float(got) - float(want)) < 1e-6:
            return "correct"
    except (TypeError, ValueError):
        return "wrong"
    return "wrong"


def score(item) -> dict:
    got, how = openstax_work(item["prompt"])
    status = "leftover" if got == "leftover" or how == "leftover" else _same(got, item["want"], item["kind"])
    return {
        "id": item["id"],
        "prompt": item["prompt"],
        "want": item["want"],
        "got": got if isinstance(got, (int, float, str)) else str(got),
        "how": how,
        "status": status,
        "cite": item.get("cite", ""),
    }


def counts(rows):
    return {
        "n": len(rows),
        "correct": sum(1 for r in rows if r["status"] == "correct"),
        "wrong": sum(1 for r in rows if r["status"] == "wrong"),
        "leftover": sum(1 for r in rows if r["status"] == "leftover"),
    }


def main() -> int:
    gaps = [score(it) for it in GAPS]
    fresh = [score(it) for it in FRESH2]
    near = [score(it) for it in NEAR2]
    blind = [score(it) for it in BLIND]
    old_fresh = [score(it) for it in FRESH]
    old_near = [score(it) for it in NEAR]
    old = []
    for it in BANK_ITEMS:
        got, how = openstax_work(it["prompt"])
        ok = got != "leftover" and how != "leftover" and reward_trit(got, it["want"]) == 1
        old.append({"id": it["id"], "ok": ok, "got": got if isinstance(got, (int, float, str)) else str(got), "how": how, "want": it["want"]})
    g, f, n = counts(gaps), counts(fresh), counts(near)
    b, of, on = counts(blind), counts(old_fresh), counts(old_near)
    old_ok = sum(1 for r in old if r["ok"])
    overall = (
        g["correct"] == g["n"] and g["wrong"] == 0
        and f["correct"] == f["n"] and f["wrong"] == 0
        and n["correct"] == n["n"] and n["wrong"] == 0
        and b["correct"] == b["n"] and b["wrong"] == 0
        and of["correct"] == of["n"] and on["correct"] == on["n"]
        and old_ok == len(old)
    )
    doc = {
        "adventure": 1,
        "ted": "TED-35",
        "vs_bill": "Bill-34",
        "pin": "AEB2AD",
        "free_parameters": 0,
        "measured_W_changed": False,
        "gaps": g,
        "fresh": f,
        "near": n,
        "blind_ch6": b,
        "prior_fresh": of,
        "prior_near": on,
        "old_openstax_ok": old_ok,
        "old_openstax_n": len(old),
        "overall_ok": overall,
        "promotes": overall,
        "promote_to": "Bill-35" if overall else None,
        "items": {"gaps": gaps, "fresh": fresh, "near": near, "old_fail": [r for r in old if not r["ok"]]},
    }
    OUT.write_text(json.dumps(doc, indent=2), encoding="utf-8")

    def table(rows):
        return "\n".join(
            f"| `{r['id']}` | {r['status']} | {r['want']} | {r['got']} | {r['how']} |"
            for r in rows
        )

    head = "| id | status | want | family gave | route |\n|---|---|---|---|---|\n"
    text = f"""# Math gaps and the errors they exposed

Pin AEB2AD. 0 free parameters. Measured edges unchanged.

Three results were wrong, not refusals.

- `Simplify: 1/3 * 1/4` reached the integer ALU. Integer division makes 1/3 into 0, so the product was 0. The fraction is 1/12. That is Be Prepared 6.11.
- `What number is 35% of 90?` used whole-number percent and returned 31. Example 6.14 is 31.5.
- `What percent of 80 is 20?` took the numbers in the order written and returned 400. The part is 20 and the whole is 80, so the percent is 25.

The gaps that were still refusals are one-step equations (`2y - 3 = 9`), a whole-number power (`4^5`), a tip, and a sale price after a discount.

## These items

Correct **{g['correct']}** / **{g['n']}**, wrong **{g['wrong']}**, leftover **{g['leftover']}**.

{head}{table(gaps)}

## New wordings

Correct **{f['correct']}** / **{f['n']}**, wrong **{f['wrong']}**, leftover **{f['leftover']}**.

{head}{table(fresh)}

## Near misses

Correct **{n['correct']}** / **{n['n']}**, wrong **{n['wrong']}**, leftover **{n['leftover']}**.

{head}{table(near)}

## Still holding

Chapter 6 Be Prepared **{b['correct']}** / **{b['n']}**. Earlier new wordings **{of['correct']}** / **{of['n']}**. Earlier near misses **{on['correct']}** / **{on['n']}**. OpenStax bank **{old_ok}** / **{len(old)}**.
"""
    DOC.write_text(text, encoding="utf-8")
    ADV.write_text(text, encoding="utf-8")
    print(
        f"  gaps {g['correct']}/{g['n']} w={g['wrong']} L={g['leftover']} "
        f"fresh {f['correct']}/{f['n']} near {n['correct']}/{n['n']} "
        f"blind {b['correct']}/{b['n']} oldfresh {of['correct']}/{of['n']} "
        f"old {old_ok}/{len(old)} overall {overall}"
    )
    for row in gaps + fresh + near + blind + old_fresh + old_near:
        if row["status"] != "correct":
            print(" FAIL", row["id"], row["status"], "want", row["want"], "got", row["got"], row["how"])
    for row in old:
        if not row["ok"]:
            print(" OLD", row["id"], row["want"], row["got"], row["how"])
    print(f"  wrote {DOC}")
    return 0 if overall else 1


if __name__ == "__main__":
    raise SystemExit(main())
