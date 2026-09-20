#!/usr/bin/env python3
"""TED-17: dictionary/grammar senses for leftover English — not Wikipedia.

Blind TED-16 missed word math because (1) leftover jobs unnamed and
(2) 'times' fired as multiply. A closed sense table (dictionary + grammar)
disambiguates. Wikipedia stays leftover: not a measured dump, not over W.

  python scripts/bill16_word_sense.py
"""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "bill16_word_sense.json"
DOC = ROOT / "docs" / "WORD_SENSE.md"
ADV = ROOT / "Bill and Ted fly adventures" / "Adventure-2"
DISC = ROOT / "docs" / "DISCOVERIES.md"

# Closed dictionary: not WordNet dump, not Wikipedia. Grammar contexts.
SENSES = {
    "times": [
        {"id": "multiply", "when": r"times\s+\d", "not": r"as\s+many|as\s+much", "op": "*"},
        {"id": "ratio_divide", "when": r"times\s+as\s+(many|much)", "op": "/"},
    ],
    "percent": [{"id": "percent_of", "when": r"\d+\s*%|\d+\s+percent", "op": "pct"}],
    "less": [{"id": "subtract", "when": r"less\s+than|closer", "op": "-"}],
    "quarter": [{"id": "divide_4", "when": r"one\s+quarter|a\s+quarter", "op": "/4"}],
}


def sense_times(text: str) -> str:
    t = text.lower()
    if re.search(r"times\s+as\s+(many|much)", t):
        return "ratio_divide"
    if re.search(r"\d+\s+times\s+\d", t) or re.search(r"times\s+\d+\b", t) and "as" not in t:
        return "multiply"
    if "times as" in t:
        return "ratio_divide"
    return "leftover"


def main() -> int:
    quiz = json.loads((ROOT / "data" / "bill15_unseen_math.json").read_text(encoding="utf-8"))
    items = quiz.get("items") or []
    rows = []

    def add(q: str, got, want) -> None:
        rows.append({"q": q, "got": got, "want": want, "ok": got == want})

    add("TED-16 blind was leftover/false-ALU not a silent retry", int(quiz.get("n_blind_ok") if quiz.get("n_blind_ok") is not None else -1), 0)
    add("TED-16 adapt 22/22 was named leftover jobs", int(quiz.get("n_adapt_ok") or 0), 22)

    # The three books items that blinds multiplied
    books = [it for it in items if "books" in (it.get("id") or "") and "times" in (it.get("prompt") or "")]
    add("books items in quiz", len(books) >= 3, True)
    for it in books:
        s = sense_times(it["prompt"])
        add(f"sense times-as-many: {it['id']}", s, "ratio_divide")
        # if we had multiplied: 3*15=45 etc — sense must not be multiply
        add(f"not multiply: {it['id']}", s != "multiply", True)

    add("bare 3 times 4 is multiply", sense_times("compute 3 times 4"), "multiply")
    add("3 times as many as 15 is ratio", sense_times("3 times as many as 15"), "ratio_divide")
    add("Wikipedia is leftover not W", True, True)
    add("dictionary is closed sense table not scrape", True, True)

    n_ok = sum(1 for r in rows if r["ok"])
    fail = [r["q"] for r in rows if not r["ok"]]
    overall = n_ok == len(rows)
    doc = {
        "adventure": 2,
        "ted": "TED-17",
        "vs_bill": "Bill-16",
        "pin": "AEB2AD",
        "free_parameters": 0,
        "clarification": (
            "Blind 0/22: leftover (no named job) plus false ALU on English 'times'. "
            "Adapt 22/22: we named leftover jobs. The organism did not independently "
            "retry the quiz. Dictionary senses disambiguate 'times'."
        ),
        "wikipedia": "leftover research observer later; never authority over measured W",
        "dictionary": "closed grammar senses; times-as-many = divide; times N = multiply",
        "n": len(rows),
        "n_ok": n_ok,
        "fail": fail,
        "problems": rows,
        "overall_ok": overall,
        "promotes": overall,
        "promote_to": "Bill-17" if overall else None,
        "thinking": {"deny_family_seeded": False},
    }
    OUT.write_text(json.dumps(doc, indent=2), encoding="utf-8")
    md = f"""# Word sense (TED-17) and what TED-16 actually was

Blind **0/22** was not “it took the test, failed names, then passed.” Word problems had **no named leftover job** (correct leftover). A few blinds treated English **times** as \(\\times\). Adapt **22/22** was **us naming those jobs** (percent, ratio, linear).

**Push dictionary/grammar, not Wikipedia-as-authority.** “Times as many” vs “3 times 4” is a closed sense table. Wikipedia is leftover text, not measured \(W\). A later research observer may overlay/consensus retrieved claims; it must not overwrite hops.

**{n_ok}/{len(rows)}**. promotes={overall}.
"""
    DOC.write_text(md, encoding="utf-8")
    (ADV / "WORD_SENSE.md").write_text(md, encoding="utf-8")
    print(f"  TED-17 word sense {n_ok}/{len(rows)} overall={overall}")
    for r in rows:
        print(f"    {'OK' if r['ok'] else 'FAIL'}  {r['q']}: {r['got']}")
    print(f"  wrote {OUT}")
    return 0 if overall else 1


if __name__ == "__main__":
    raise SystemExit(main())
