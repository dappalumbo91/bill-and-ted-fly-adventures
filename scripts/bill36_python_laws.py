#!/usr/bin/env python3
"""TED-36: Python laws in the sandbox.

Teach the laws, then score sentences the laws have not stored.
One plus one and one plus one plus one are the same fold.
A sentence that does not compose stays a leftover.
Courtship names DENY. Measured W stays unchanged.

  python scripts/bill36_python_laws.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from arith_steps import registry  # noqa: E402
from bill13_coding_tokens import run_code  # noqa: E402
from bill14_host_eval import PySandbox  # noqa: E402
from python_laws import LOOP_HORIZON, compose, run_prompt  # noqa: E402

OUT = ROOT / "data" / "bill36_python_laws.json"
DOC = ROOT / "docs" / "PYTHON_LAWS.md"
ADV = ROOT / "Bill and Ted fly adventures" / "Adventure-1" / "PYTHON_LAWS.md"

TAUGHT = [
    {"id": "sum-2", "prompt": "one plus one", "want": 2, "expect": "code"},
    {"id": "sum-3", "prompt": "one plus one plus one", "want": 3, "expect": "code"},
    {"id": "add-3", "prompt": "add 4 and 9 and 2", "want": 15, "expect": "code"},
    {"id": "bind", "prompt": "let x be 3 plus 4 then add 5", "want": 12, "expect": "code"},
    {"id": "larger", "prompt": "the larger of 6 and 2", "want": 6, "expect": "code"},
    {"id": "count", "prompt": "count from 0 to 4", "want": 4, "expect": "code"},
    {"id": "fn-twice", "prompt": "define step as add one. apply step twice to 5", "want": 7, "expect": "code"},
]
FRESH = [
    {"id": "fresh-sum-4", "prompt": "what is one plus one plus one plus one", "want": 4, "expect": "code"},
    {"id": "fresh-words", "prompt": "two plus two plus two", "want": 6, "expect": "code"},
    {"id": "fresh-add-5", "prompt": "add 1 and 1 and 1 and 1 and 1", "want": 5, "expect": "code"},
    {"id": "fresh-mix", "prompt": "one plus one minus one", "want": 1, "expect": "code"},
    {"id": "fresh-minus", "prompt": "five minus two minus one", "want": 2, "expect": "code"},
    {"id": "fresh-tie", "prompt": "the larger of nine and nine", "want": 9, "expect": "code"},
    {"id": "fresh-larger-sum", "prompt": "the larger of one plus one and 2", "want": 2, "expect": "code"},
    {"id": "fresh-count-11", "prompt": "count from zero to eleven", "want": 11, "expect": "code"},
    {"id": "fresh-count-from", "prompt": "count from 3 to 7", "want": 7, "expect": "code"},
    {"id": "fresh-bind", "prompt": "let y be 10 minus 3 then add 1", "want": 8, "expect": "code"},
    {"id": "fresh-grow", "prompt": "define grow as add 3. apply grow twice to 1", "want": 7, "expect": "code"},
    {"id": "fresh-thrice", "prompt": "define step as add one. apply step three times to 2", "want": 5, "expect": "code"},
    {"id": "fresh-apply-sum", "prompt": "define step as add one. apply step to one plus one", "want": 3, "expect": "code"},
    {"id": "fresh-back", "prompt": "define back as minus one. apply back twice to 5", "want": 3, "expect": "code"},
    {"id": "fresh-apply-11", "prompt": "define step as add one. apply step 11 times to 0", "want": 11, "expect": "code"},
]
REFUSE = [
    {"id": "ill-plus", "prompt": "plus plus one", "want": None, "expect": "leftover"},
    {"id": "ill-mid", "prompt": "one plus plus one", "want": None, "expect": "leftover"},
    {"id": "ill-add", "prompt": "add and 4", "want": None, "expect": "leftover"},
    {"id": "ill-tail", "prompt": "one plus", "want": None, "expect": "leftover"},
    {"id": "import", "prompt": "import os", "want": None, "expect": "leftover"},
    {"id": "open", "prompt": "open('x')", "want": None, "expect": "leftover"},
    {"id": "court", "prompt": "court = 1", "want": None, "expect": "deny"},
    {"id": "define-court", "prompt": "define court as add one", "want": None, "expect": "deny"},
    {"id": "sort", "prompt": "sort 4 and 1 and 3", "want": None, "expect": "leftover"},
    {"id": "count-12", "prompt": "count from 0 to 12", "want": None, "expect": "leftover"},
    {"id": "apply-12", "prompt": "define step as add one. apply step 12 times to 0", "want": None, "expect": "leftover"},
    {"id": "unbound", "prompt": "apply step twice to 1", "want": None, "expect": "leftover"},
]

PAIRS = [
    ("let x = 3 + 4; x", "x = 3 + 4\nx", 7),
    ("let y = 6 * 7; y", "y = 6 * 7\ny", 42),
    ("let a = 10 - 3; a", "a = 10 - 3\na", 7),
    ("if cons(1, 1) { 10 } else { 0 }", "10 if 1 == 1 else 0", 10),
    ("if cons(1, -1) { 10 } else { 0 }", "10 if 1 == -1 else 0", 0),
    ("let i = 0; let s = 0; while i < 3 { let s = s + i; let i = i + 1 }; s", "i = 0\ns = 0\nwhile i < 3:\n    s = s + i\n    i = i + 1\ns", 3),
    ("abs(3 - 10)", "abs(3 - 10)", 7),
]


def judge(item: dict) -> dict:
    row = run_prompt(item["prompt"])
    kind = row["kind"]
    got = row["got"]
    expect = item["expect"]
    want = item["want"]
    if expect == "code":
        if kind == "code" and got == want:
            status = "correct"
        elif kind == "code":
            status = "wrong"
        else:
            status = "leftover"
    elif expect == "deny":
        if kind == "deny":
            status = "correct"
        elif kind == "code":
            status = "wrong"
        else:
            status = "leftover"
    elif kind == "code":
        status = "wrong"
    else:
        status = "correct"
    return {
        "id": item["id"],
        "prompt": item["prompt"],
        "want": want,
        "expect": expect,
        "got": got,
        "status": status,
        "kind": kind,
        "source": row.get("source"),
        "how": "+".join(row.get("laws") or []) or row.get("why") or kind,
        "on_W": False,
    }


def counts(rows: list[dict]) -> dict:
    return {
        "n": len(rows),
        "correct": sum(1 for r in rows if r["status"] == "correct"),
        "wrong": sum(1 for r in rows if r["status"] == "wrong"),
        "leftover": sum(1 for r in rows if r["status"] == "leftover"),
    }


def same_law() -> dict:
    two = compose("one plus one")
    three = compose("one plus one plus one")
    four = compose("one plus one plus one plus one")
    add_two = compose("add 1 and 1")
    add_three = compose("add one and one and one")
    fn = compose("define step as add one. apply step twice to 5")
    fn3 = compose("define step as add one. apply step three times to 2")
    src2 = two.get("source") or ""
    src3 = three.get("source") or ""
    src4 = four.get("source") or ""
    fn_src = fn.get("source") or ""
    fn3_src = fn3.get("source") or ""
    ok = bool(
        two.get("laws") == ["fold"]
        and three.get("laws") == ["fold"]
        and four.get("laws") == ["fold"]
        and src3 == f"({src2} + 1)"
        and src4 == f"({src3} + 1)"
        and add_two.get("source") == src2
        and add_three.get("source") == src3
        and "return n + 1" in fn_src
        and "step(step(5))" in fn_src
        and "step(step(step(2)))" in fn3_src
    )
    return {
        "ok": ok,
        "one_plus_one": src2,
        "one_plus_one_plus_one": src3,
        "four": src4,
        "function": fn_src,
        "function_three": fn3_src,
    }


def sandbox_pairs() -> dict:
    base = registry()
    rows = []
    for fsot_src, py_src, want in PAIRS:
        fs = run_code(fsot_src, base)
        py = PySandbox({}).run(py_src)
        rows.append({
            "want": want,
            "fsot": fs.get("got"),
            "py": py.get("got"),
            "ok": fs.get("got") == py.get("got") == want,
        })
    fn = PySandbox({}).run("def step(n):\n    return n + 1\nstep(step(1))\n")
    deny = PySandbox({}).run("court = 1\ncourt")
    imp = PySandbox({}).run("import os\nos.system('x')")
    opn = PySandbox({}).run("open('x')")
    fn_ok = fn.get("got") == 3 and fn.get("kind") == "code"
    guard_ok = deny.get("kind") == "deny" and bool(imp.get("leftover")) and bool(opn.get("leftover"))
    return {
        "ok": all(r["ok"] for r in rows) and fn_ok and guard_ok,
        "n": len(rows),
        "matched": sum(1 for r in rows if r["ok"]),
        "function_twice": fn.get("got"),
        "rows": rows,
    }


def no_fake_horizon() -> bool:
    count = run_prompt("count from 0 to 12")
    apply = run_prompt("define step as add one. apply step 12 times to 0")
    return bool(
        count["kind"] != "code"
        and count["got"] != 11
        and apply["kind"] != "code"
        and apply["got"] != 12
    )


def table(rows: list[dict]) -> str:
    lines = []
    for r in rows:
        src = (r.get("source") or "").replace("\n", " / ")
        lines.append(
            f"| `{r['id']}` | {r['status']} | {r['want']} | {r['got']} | {r['how']} | `{src}` |"
        )
    return "\n".join(lines)


def main() -> int:
    taught = [judge(it) for it in TAUGHT]
    fresh = [judge(it) for it in FRESH]
    refuse = [judge(it) for it in REFUSE]
    law = same_law()
    pairs = sandbox_pairs()
    horizon_ok = no_fake_horizon()
    g, f, r = counts(taught), counts(fresh), counts(refuse)
    overall = bool(
        g["correct"] == g["n"] and g["wrong"] == 0 and g["leftover"] == 0
        and f["correct"] == f["n"] and f["wrong"] == 0 and f["leftover"] == 0
        and r["correct"] == r["n"] and r["wrong"] == 0
        and law["ok"]
        and pairs["ok"]
        and horizon_ok
    )
    doc = {
        "adventure": 1,
        "ted": "TED-36",
        "vs_bill": "Bill-35",
        "pin": "AEB2AD",
        "free_parameters": 0,
        "measured_W_changed": False,
        "loop_horizon": LOOP_HORIZON,
        "on_W": False,
        "taught": g,
        "fresh": f,
        "refuse": r,
        "same_law": law["ok"],
        "same_law_sources": {
            "one_plus_one": law["one_plus_one"],
            "one_plus_one_plus_one": law["one_plus_one_plus_one"],
            "function": law["function"],
        },
        "sandbox_pairs_ok": pairs["ok"],
        "sandbox_pairs_matched": pairs["matched"],
        "sandbox_pairs_n": pairs["n"],
        "horizon_refusal_ok": horizon_ok,
        "overall_ok": overall,
        "promotes": overall,
        "promote_to": "Bill-36" if overall else None,
        "items": {"taught": taught, "fresh": fresh, "refuse": refuse},
    }
    OUT.write_text(json.dumps(doc, indent=2), encoding="utf-8")
    head = "| id | status | want | sandbox gave | law | program |\n|---|---|---|---|---|---|\n"
    fn_src = law["function"]
    text = f"""# Python laws

Pin AEB2AD. 0 free parameters. Measured edges unchanged. Loop horizon {LOOP_HORIZON}, which is round(φ^5). The program runs in the restricted Python sandbox on the language splice.

The laws are a value, a fold, a name binding, a larger-of choice, a count, and a function. A function is the fold with a hole. Applying it twice is that same function used again. The sandbox is what produces the number. The sentence does not carry the answer.

One plus one is `{law['one_plus_one']}`. One plus one plus one is `{law['one_plus_one_plus_one']}`. The second program is the first program with one more sum. Add-and uses that same fold: add 1 and 1 writes the same source as one plus one.

```
{fn_src}
```

That run returns 7. Three applications of the same function, `step(step(step(2)))`, return 5.

A sentence that does not compose stays a leftover. `plus plus one` has no value where a value has to be. `import` and `open` stay outside the sandbox. A courtship name is DENY. Sort has no law here. A count with more than {LOOP_HORIZON} steps is a refusal. The result stays unset.

## Taught

Correct **{g['correct']}** / **{g['n']}**, wrong **{g['wrong']}**, leftover **{g['leftover']}**.

{head}{table(taught)}

## New sentences

Correct **{f['correct']}** / **{f['n']}**, wrong **{f['wrong']}**, leftover **{f['leftover']}**.

{head}{table(fresh)}

## Refusals

Correct **{r['correct']}** / **{r['n']}**, wrong **{r['wrong']}**, leftover **{r['leftover']}**.

{head}{table(refuse)}

## Sandbox already in the simulation

The earlier worksheet still matches: **{pairs['matched']}** / **{pairs['n']}**. A defined function `step(step(1))` returns **{pairs['function_twice']}**. Courtship stays DENY. Import and open stay refused.

Same law held: **{law['ok']}**. Horizon refusal held: **{horizon_ok}**.
"""
    DOC.write_text(text, encoding="utf-8")
    ADV.write_text(text, encoding="utf-8")
    print(
        f"TED-36 taught {g['correct']}/{g['n']} fresh {f['correct']}/{f['n']} "
        f"refuse {r['correct']}/{r['n']} same_law={law['ok']} pairs={pairs['ok']} "
        f"horizon={horizon_ok} overall={overall}"
    )
    if not overall:
        for row in taught + fresh + refuse:
            if row["status"] != "correct":
                print(" ", row["id"], row["status"], row["kind"], row["got"], row["how"], row.get("source"))
    print(f"  wrote {OUT}")
    return 0 if overall else 1


if __name__ == "__main__":
    raise SystemExit(main())
