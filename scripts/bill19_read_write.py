#!/usr/bin/env python3
"""TED-20 Adventure 1: teach reading and writing, then a school exam.

Not LLM pretraining. Teach decode (read) and encode (write) as steps.
Then a combined unseen quiz: read + write + math + retention.
Self-study: leftover → closed dictionary lookup (API hub later, not Wikipedia over W).
Capability ledger vs LLM-scale end goal.

Datasets on G:\\AI_Datasets (flickr, python snippets, text.zip) stay for later
reshape; this TED uses the splice the organism can actually take.

  python scripts/bill19_read_write.py
"""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
import sys

sys.path.insert(0, str(ROOT / "scripts"))

from bill12_language_splice import interpret  # noqa: E402
from bill13_coding_tokens import run_code  # noqa: E402
from bill17_adaptive import grammar_math  # noqa: E402
from bill18_bio_teach import reward_trit  # noqa: E402
from trit_alu import from_bt, mul_bt, to_bt  # noqa: E402

OUT = ROOT / "data" / "bill19_read_write.json"
CAP = ROOT / "docs" / "CAPABILITY.md"
STUDY = ROOT / "docs" / "SELF_STUDY.md"
ADV = ROOT / "Bill and Ted fly adventures" / "Adventure-1"
DATASETS = Path(r"G:\AI_Datasets")


def read_meaning(text: str) -> dict:
    """Decode writing → job/value. Own work, not a stored answer."""
    t = text.lower()
    # Sense before ALU: "times as many" is divide, not lexicon 'times' = multiply.
    if "as many" in t or "as much" in t or re.search(r"\d+\s*%", t) or re.search(r"n\s*\+", t):
        got, how = grammar_math(text)
        if got != "leftover":
            return {"kind": "read_math", "got": got, "how": how, "leftover": False, "on_W": False}
    rec = interpret(text, {}, {})
    if rec.get("kind") in {"command", "deny"}:
        return rec
    if rec.get("kind") == "alu" and "as many" not in t:
        return rec
    got, how = grammar_math(text)
    if got != "leftover":
        return {"kind": "read_math", "got": got, "how": how, "leftover": False, "on_W": False}
    if rec.get("kind") == "leftover":
        return rec
    return {"kind": "leftover", "got": "leftover", "leftover": True}


def write_percent(n: int, pct: int) -> dict:
    """Encode meaning → writing + compute. Taught procedure."""
    sentence = f"{pct}% of {n}"
    code = f"let x = {n} * {pct} / 100; x"
    val = from_bt(mul_bt(to_bt(n), to_bt(pct))) // 100
    return {"write": sentence, "code": code, "got": val}


def write_command(job: str) -> str:
    table = {"walk": "walk", "hear_steer": "turn", "descend_escape": "fly"}
    return table.get(job, "leftover")


def main() -> int:
    ds = {
        "root": str(DATASETS),
        "present": DATASETS.is_dir(),
        "names": sorted(p.name for p in DATASETS.iterdir()) if DATASETS.is_dir() else [],
    }

    # LESSON (steps): read one percent, write one percent, read one command.
    lesson_read = read_meaning("25% of 40")
    lesson_write = write_percent(40, 25)
    lesson_cmd = read_meaning("walk")

    # SCHOOL EXAM — new numbers/jobs, mix read/write/math/retain.
    exam = []

    def add_exam(kind: str, prompt: str, got, want) -> None:
        trit = reward_trit(got, want) if not isinstance(want, str) else (1 if got == want else -1)
        exam.append(
            {
                "kind": kind,
                "prompt": prompt,
                "got": got,
                "want": want,
                "reward_trit": trit,
                "ok": got == want,
            }
        )

    r1 = read_meaning("15% of 40")
    add_exam("read_math", "15% of 40", r1.get("got"), 6)
    r2 = read_meaning("5 times as many as 20")
    add_exam("read_math", "5 times as many as 20", r2.get("got"), 4)
    r3 = read_meaning("n+6=19")
    add_exam("read_math", "n+6=19", r3.get("got"), 13)
    w1 = write_percent(40, 15)
    add_exam("write_math", "write 15% of 40", w1["got"], 6)
    add_exam("write_form", "write sentence 15% of 40", w1["write"], "15% of 40")
    c1 = read_meaning("turn left")
    add_exam("read_cmd", "turn left", c1.get("splice_at") or c1.get("kind"), "DNg29")
    add_exam("write_cmd", "write walk", write_command("walk"), "walk")
    add_exam("write_cmd", "write fly", write_command("descend_escape"), "fly")
    code = run_code("let a = 15 * 40 / 100; a", {})
    add_exam("write_code", "let a = 15 * 40 / 100; a", code.get("got"), 6)
    deny = read_meaning("court")
    add_exam("deny", "court", deny.get("kind"), "deny")

    # Interference then retention of a taught job
    _ = run_code("let z = 9 * 9; z", {})
    retain = read_meaning("15% of 40")
    add_exam("retain_read", "15% of 40 after 9*9", retain.get("got"), 6)

    n_ok = sum(1 for e in exam if e["ok"])
    n = len(exam)
    by = {}
    for e in exam:
        by.setdefault(e["kind"], {"n": 0, "n_ok": 0})
        by[e["kind"]]["n"] += 1
        if e["ok"]:
            by[e["kind"]]["n_ok"] += 1

    cap = {
        "end_goal": "LLM-scale read/write/math/code/self-study — FSOT organism, not a trained net on W",
        "now": [
            {"skill": "read command lexicon", "status": "on", "note": "walk/turn/fly splice at bottlenecks"},
            {"skill": "read word-math grammar", "status": "on", "note": "percent, times-as-many, n+a=b"},
            {"skill": "write percent sentence+code", "status": "on", "note": "TED-20 encode"},
            {"skill": "write command word", "status": "on", "note": "closed table"},
            {"skill": "trit ALU / let-if-while", "status": "on", "note": "TED-14"},
            {"skill": "DA leftover reward + LTM bind", "status": "on", "note": "TED-19"},
            {"skill": "open vocab / essays / HumanEval", "status": "leftover", "note": "not LLM"},
            {"skill": "web/Wikipedia authority", "status": "leftover", "note": "never over W"},
            {"skill": "self-study API hub", "status": "mapped", "note": "leftover → dictionary lookup; hub later"},
            {"skill": "G:\\AI_Datasets reshape", "status": "wait", "note": str(ds["names"][:8])},
        ],
        "school_exam": {"n_ok": n_ok, "n": n, "by_kind": by},
    }

    overall = n_ok == n and lesson_write["got"] == 10 and lesson_cmd.get("kind") == "command"
    doc = {
        "adventure": 1,
        "ted": "TED-20",
        "vs_bill": "Bill-19",
        "pin": "AEB2AD",
        "free_parameters": 0,
        "datasets": ds,
        "lesson": {
            "read_25pct_40": lesson_read.get("got"),
            "write_25pct_40": lesson_write,
            "read_walk": lesson_cmd.get("kind"),
        },
        "exam": exam,
        "n_ok": n_ok,
        "n": n,
        "capability": cap,
        "overall_ok": overall,
        "promotes": overall,
        "promote_to": "Bill-20" if overall else None,
        "thinking": {"deny_family_seeded": False},
    }
    OUT.write_text(json.dumps(doc, indent=2), encoding="utf-8")

    cap_md = f"""# Capability ledger (Adventure 1 → LLM-scale end)

Pin **AEB2AD**. End goal: this fly organism as capable as LLMs at read/write/math/code/self-study. **Not** a trained net on FlyWire \(W\). Courtship/aggression \(T_1\) off.

| Skill | Now | End |
|-------|-----|-----|
| Read commands | closed lexicon → bottlenecks | open vocab |
| Read word-math | grammar senses | GSM8K-scale |
| Write | percent sentence+code; command words | open generation |
| Code | let/if/while trit ALU | HumanEval-scale |
| Reward | DA leftover +1 LTM bind | same law |
| Self-study | leftover → dictionary | API hub |
| G:\\AI_Datasets | present {ds['present']} {ds['names'][:6]} | reshape to Q&A this splice can take |

TED-20 school exam **{n_ok}/{n}** (read+write+math+retain).
"""
    CAP.write_text(cap_md, encoding="utf-8")
    study_md = """# Self-study map (not a human at a browser)

When leftover: query the **closed dictionary/grammar** (TED-17/18). Hit → LTM bind (TED-19 DA leftover). Miss → leftover, do not guess.

Later **API hub**: same leftover lookup, optional retrieved text as overlay observer. Consensus 0 if it disagrees with measured \(W\). Never Wikipedia-as-authority. Never courtship/aggression seed.

G:\\AI_Datasets (flickr captions, python snippets) reshape later into Q&A this organism can actually take — not dumped as LLM pretrain.
"""
    STUDY.write_text(study_md, encoding="utf-8")
    (ADV / "CAPABILITY.md").write_text(cap_md, encoding="utf-8")
    print(f"  TED-20 read/write exam {n_ok}/{n} overall={overall} datasets={ds['present']}")
    for e in exam:
        print(f"    {'OK' if e['ok'] else 'MISS'} {e['kind']:12s} got={e['got']!r} want={e['want']!r}")
    print(f"  wrote {OUT}")
    return 0 if overall else 1


if __name__ == "__main__":
    raise SystemExit(main())
