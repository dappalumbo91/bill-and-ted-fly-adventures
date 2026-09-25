#!/usr/bin/env python3
"""Why Chapter 6 refused, and the rational procedure that works those operations.

The Be Prepared items stay the published sentences. New wordings use the same
operations. Near misses ask for the other quantity. No per-exercise cue.

  python scripts/bill34_ch6_refine.py
"""
from __future__ import annotations

import runio
runio.install()

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from bill18_bio_teach import reward_trit  # noqa: E402
from bill21_openstax import BANK_ITEMS, openstax_work  # noqa: E402
from bill33_before_a2 import BLIND  # noqa: E402

OUT = ROOT / "data" / "bill34_ch6.json"
DOC = ROOT / "docs" / "CH6_REFINE.md"
ADV = ROOT / "Bill and Ted fly adventures" / "Adventure-1" / "CH6_REFINE.md"

# What the Bill-33 worker could see. Recorded from the blind score, not refit.
WHY = {
    "os6-6.1": "No sentence shape for 'ratio of A to B'. The numbers never reached an operation.",
    "os6-6.2": "No sentence shape for writing a fraction as a decimal.",
    "os6-6.3": "No sentence shape for writing a decimal as a fraction.",
    "os6-6.4": "'3/4 of x is 24' is a one-step equation. The percent grammar only sees 'N% of M'.",
    "os6-6.5": "The simplify path ran, then the integer ALU stopped at the decimal point.",
    "os6-6.6": "The only solve shape was 'letter - whole = whole'. '3.5 = 0.7n' is a coefficient.",
    "os6-6.7": "The prompt says multiplication, not simplify, so the expression was never evaluated. It is also a decimal.",
    "os6-6.8": "The prompt says division, not simplify. 12.96 / 0.04 never reached the ALU, and the ALU would have stopped at the point.",
    "os6-6.9": "'0.6y = 45' is a coefficient equation. That shape was not in the grammar.",
    "os6-6.10": "'n / 1.45 = 4.6' divides the unknown. That shape was not in the grammar.",
    "os6-6.12": "'x / 4 = 20' is whole numbers the ALU can multiply, but the sentence shape was missing.",
    "os6-6.13": "A rate is distance divided by time. The sentence named miles and hours and was not recognized.",
}

FRESH = [
    {"id": "fresh-ratio", "prompt": "Translate the ratio of 8 to 12.", "want": "2/3", "kind": "expr"},
    {"id": "fresh-decimal", "prompt": "Write 1/4 as a decimal.", "want": 0.25, "kind": "number"},
    {"id": "fresh-fraction", "prompt": "Write 0.75 as a fraction.", "want": "3/4", "kind": "expr"},
    {"id": "fresh-of", "prompt": "2/5 of y is 10. What is y?", "want": 25, "kind": "number"},
    {"id": "fresh-product", "prompt": "Simplify: (2.5)(4)", "want": 10, "kind": "number"},
    {"id": "fresh-coeff", "prompt": "Solve: 1.2 = 0.3n", "want": 4, "kind": "number"},
    {"id": "fresh-times", "prompt": "Solve 0.25(80) through multiplication.", "want": 20, "kind": "number"},
    {"id": "fresh-div", "prompt": "Solve 6.3 / 0.3 through division.", "want": 21, "kind": "number"},
    {"id": "fresh-yc", "prompt": "Solve: 0.5y = 9", "want": 18, "kind": "number"},
    {"id": "fresh-over", "prompt": "Solve: z / 0.5 = 7", "want": 3.5, "kind": "number"},
    {"id": "fresh-whole", "prompt": "Solve: w / 8 = 3", "want": 24, "kind": "number"},
    {"id": "fresh-rate", "prompt": "Write as a rate: a car travels 30 miles in 2 hours.", "want": 15, "kind": "number"},
]

NEAR = [
    {"id": "near-keep-fraction", "prompt": "Write 3/5 as a fraction.", "want": "3/5", "kind": "expr"},
    {"id": "near-keep-decimal", "prompt": "Write 0.62 as a decimal.", "want": 0.62, "kind": "number"},
    {"id": "near-miles", "prompt": "Sale rode his bike 24 miles in 2 hours. How many miles did he ride?", "want": 24, "kind": "number"},
    {"id": "near-hours", "prompt": "Sale rode his bike 24 miles in 2 hours. How many hours did the ride take?", "want": 2, "kind": "number"},
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
    if got == "leftover" or how == "leftover":
        status = "leftover"
    else:
        status = _same(got, item["want"], item["kind"])
    return {
        "id": item["id"],
        "prompt": item["prompt"],
        "want": item["want"],
        "got": got if isinstance(got, (int, float, str)) else str(got),
        "how": how,
        "status": status,
    }


def main() -> int:
    blind = []
    for item in BLIND:
        row = score({**item, "kind": item["kind"]})
        row["why_it_refused"] = WHY[item["id"]]
        blind.append(row)
    fresh = [score(it) for it in FRESH]
    near = [score(it) for it in NEAR]
    old = []
    for it in BANK_ITEMS:
        got, how = openstax_work(it["prompt"])
        ok = got != "leftover" and how != "leftover" and reward_trit(got, it["want"]) == 1
        old.append({"id": it["id"], "want": it["want"], "got": got if isinstance(got, (int, float, str)) else str(got), "how": how, "ok": ok})
    counts = lambda rows: {
        "n": len(rows),
        "correct": sum(1 for r in rows if r["status"] == "correct"),
        "wrong": sum(1 for r in rows if r["status"] == "wrong"),
        "leftover": sum(1 for r in rows if r["status"] == "leftover"),
    }
    b, f, n = counts(blind), counts(fresh), counts(near)
    old_ok = sum(1 for r in old if r["ok"])
    overall = b["correct"] == b["n"] and b["wrong"] == 0 and f["correct"] == f["n"] and n["correct"] == n["n"] and old_ok == len(old)
    doc = {
        "adventure": 1,
        "ted": "TED-34",
        "vs_bill": "Bill-33",
        "pin": "AEB2AD",
        "free_parameters": 0,
        "new_relations_on_challenge": 0,
        "measured_W_changed": False,
        "integer_alu_unchanged": True,
        "blind": b,
        "fresh": f,
        "near": n,
        "old_openstax_ok": old_ok,
        "old_openstax_n": len(old),
        "overall_ok": overall,
        "promotes": False,
        "items": {"blind": blind, "fresh": fresh, "near": near, "old": old},
    }
    OUT.write_text(json.dumps(doc, indent=2), encoding="utf-8")

    def table(rows, why=False):
        lines = []
        for r in rows:
            extra = f" | {r['why_it_refused']}" if why else ""
            lines.append(
                f"| `{r['id']}` | {r['status']} | {r['want']} | {r['got']} | {r['how']}{extra} |"
            )
        return "\n".join(lines)

    why_head = "| id | now | want | family gave | route | why it had refused |\n|---|---|---|---|---|---|\n"
    plain_head = "| id | status | want | family gave | route |\n|---|---|---|---|---|\n"
    text = f"""# Chapter 6 refusals, refined

Pin AEB2AD. 0 free parameters. Measured edges unchanged. The integer trit ALU is unchanged. Decimals are not balanced-ternary digits, so a separate rational procedure now handles them.

The Chapter 6 Be Prepared set had been **0** correct, **0** wrong, **12** leftover. Each refusal was a missing operation, or the integer ALU stopping at a decimal point.

{why_head}{table(blind, why=True)}

After the rational procedure: correct **{b['correct']}** / **{b['n']}**, wrong **{b['wrong']}**, leftover **{b['leftover']}**.

## New wordings

Same operations, different numbers and sentences. Correct **{f['correct']}** / **{f['n']}**, wrong **{f['wrong']}**, leftover **{f['leftover']}**.

{plain_head}{table(fresh)}

## Near misses

The other reading of a nearby sentence. Correct **{n['correct']}** / **{n['n']}**, wrong **{n['wrong']}**, leftover **{n['leftover']}**.

{plain_head}{table(near)}

## Already taught

OpenStax chapters already in the bank stay exact: **{old_ok}** / **{len(old)}**.
"""
    DOC.write_text(text, encoding="utf-8")
    ADV.write_text(text, encoding="utf-8")
    print(
        f"  blind {b['correct']}/{b['n']} w={b['wrong']} L={b['leftover']} "
        f"fresh {f['correct']}/{f['n']} near {n['correct']}/{n['n']} old {old_ok}/{len(old)} overall {overall}"
    )
    for row in blind + fresh + near + [{"id": r["id"], "status": "ok" if r["ok"] else "FAIL", "want": r["want"], "got": r["got"], "how": r["how"]} for r in old]:
        if row.get("status") not in ("correct", "ok"):
            print(" ", row["id"], row.get("status"), "want", row["want"], "got", row["got"], row["how"])
    print(f"  wrote {DOC}")
    return 0 if overall else 1


if __name__ == "__main__":
    raise SystemExit(main())
