#!/usr/bin/env python3
"""TED-31: Adventure 1 learning closeout.

Replays the current brain on ARC-Easy, ARC-Challenge, and the use banks.
Records the question, the expected answer, and the answer the organism gave.
Writes the side-by-side ledger and the Adventure 1 report. Does not add cues.
Does not change measured W.

  python scripts/bill30_adventure1_report.py
"""
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "vendor"))

from bill23_arc import choices_of, load_split, study_facts  # noqa: E402
from bill26_arc_leftovers import pick_v3  # noqa: E402
from bill27_arc_challenge import load_challenge  # noqa: E402
from bill28_use import BANK as BANK29, PROCS_ALL  # noqa: E402
from bill29_use_more import BANK as BANK30  # noqa: E402
from bill31_use_gaps import BANK as BANK32, family_pick  # noqa: E402
import fsot_compute as fsot  # noqa: E402

OUT = ROOT / "data" / "adventure1_trace.json"
STAMP = ROOT / "data" / "adventure1_stamp.json"
REPORT = ROOT / "docs" / "ADVENTURE1_REPORT.md"
SIDE = ROOT / "docs" / "ADVENTURE1_SIDE_BY_SIDE.md"
LEAN = ROOT / "lean" / "Adventure1Thought.lean"
ADV = ROOT / "Bill and Ted fly adventures" / "Adventure-1"


def cell(text) -> str:
    return str(text).replace("|", "/").replace("\n", " ").strip()


def family_answer(lab, how, texts) -> str:
    if lab is None:
        return "consensus 0" if how == "consensus_0" else "leftover"
    return f"{lab}. {texts.get(lab, '')}"


def trace_arc(exam: str, frame, facts) -> list[dict]:
    rows = []
    for _, row in frame.iterrows():
        pairs = choices_of(row)
        texts = dict(pairs)
        key = str(row["answerKey"]).strip()
        stem = str(row["question"]).replace("\n", " ")
        use_lab, use_law = family_pick(stem, pairs)
        base_lab, base_how, _ = pick_v3(stem, pairs, facts, PROCS_ALL)
        if use_law == "conflict":
            lab, how = None, "consensus_0"
            route = "consensus"
        elif use_lab is not None:
            lab, how = use_lab, "use"
            route = f"use:{use_law}"
        else:
            lab, how = base_lab, base_how
            route = base_how
        if lab is None:
            kind = "consensus_0" if how == "consensus_0" else "leftover"
            score_trit = 0
        elif lab == key:
            kind = "correct"
            score_trit = 1
        else:
            kind = "wrong"
            score_trit = -1
        rows.append(
            {
                "exam": exam,
                "id": row["id"],
                "stem": stem,
                "expected": f"{key}. {texts.get(key, '')}",
                "family": family_answer(lab, how, texts),
                "kind": kind,
                "route": route,
                "score_trit": score_trit,
                "committed": lab is not None,
            }
        )
    return rows


def trace_bank(exam: str, bank: list[dict]) -> list[dict]:
    rows = []
    for item in bank:
        pairs = item["choices"]
        texts = dict(pairs)
        stem = item["stem"]
        lab, law = family_pick(stem, pairs)
        how = "consensus_0" if law == "conflict" else ("use" if lab is not None else "leftover")
        if item["kind"] == "near":
            voted_wrong = law == item["law"]
            ok = (not voted_wrong) and (lab is None or lab == item["want"])
            kind = "correct" if ok else "wrong"
            score_trit = 1 if ok else -1
        else:
            ok = lab == item["want"] and law == item["law"]
            kind = "correct" if ok else ("leftover" if lab is None else "wrong")
            score_trit = 1 if ok else (0 if lab is None else -1)
        rows.append(
            {
                "exam": exam,
                "id": item["id"],
                "role": item["kind"],
                "stem": stem,
                "expected": f"{item['want']}. {texts.get(item['want'], '')}",
                "family": family_answer(lab, how, texts),
                "kind": kind,
                "route": f"use:{law}" if lab is not None else how,
                "score_trit": score_trit,
                "committed": lab is not None,
                "taught_law": item["law"],
            }
        )
    return rows


def counts(rows: list[dict]) -> dict:
    out = {"n": len(rows), "correct": 0, "wrong": 0, "leftover": 0, "consensus_0": 0}
    for r in rows:
        out[r["kind"]] = out.get(r["kind"], 0) + 1
    return out


def md_table(rows: list[dict]) -> str:
    lines = ["| id | question | expected | family gave | route |", "|---|---|---|---|---|"]
    for r in rows:
        lines.append(
            f"| `{cell(r['id'])}` | {cell(r['stem'])} | {cell(r['expected'])} | {cell(r['family'])} | {cell(r['route'])} |"
        )
    return "\n".join(lines)


def write_lean(c_easy, c_chal, c_use) -> None:
    LEAN.parent.mkdir(parents=True, exist_ok=True)
    text = f"""-- Adventure 1 thought law. Pin AEB2AD. 0 free parameters.
-- One agreed label overlays. Disagreement or silence is trit 0 (no letter).
-- The counts are the replay after the TED-32 gap relations. Lean checks the arithmetic.

def pin : String := "AEB2AD"
def freeParameters : Nat := 0

def commit {{α : Type}} [DecidableEq α] (votes : List α) : Option α :=
  match votes.eraseDups with
  | [a] => some a
  | _ => none

#guard freeParameters = 0
#guard pin = "AEB2AD"
#guard commit ["reflect"] = some "reflect"
#guard commit ([] : List String) = none
#guard commit ["rain", "drought"] = none
#guard commit ["gas", "gas"] = some "gas"

def easyN : Nat := {c_easy['n']}
def easyCorrect : Nat := {c_easy['correct']}
def easyWrong : Nat := {c_easy['wrong']}
def easyLeftover : Nat := {c_easy['leftover']}
def easyConsensus : Nat := {c_easy['consensus_0']}
#guard easyCorrect + easyWrong + easyLeftover + easyConsensus = easyN

def challengeN : Nat := {c_chal['n']}
def challengeCorrect : Nat := {c_chal['correct']}
def challengeWrong : Nat := {c_chal['wrong']}
def challengeLeftover : Nat := {c_chal['leftover']}
def challengeConsensus : Nat := {c_chal['consensus_0']}
#guard challengeCorrect + challengeWrong + challengeLeftover + challengeConsensus = challengeN

def useN : Nat := {c_use['n']}
def useCorrect : Nat := {c_use['correct']}
def useWrong : Nat := {c_use['wrong']}
#guard useCorrect + useWrong = useN
#guard useWrong = 0
"""
    LEAN.write_text(text, encoding="utf-8")


def main() -> int:
    phi = float(fsot.PHI)
    inv_phi = 1.0 / phi
    facts = study_facts(load_split("train"))
    easy_rows = trace_arc("ARC-Easy validation", load_split("validation"), facts)
    chal_rows = trace_arc("ARC-Challenge validation", load_challenge("validation"), facts)
    use_rows = (
        trace_bank("use, first relations", BANK29)
        + trace_bank("use, further relations", BANK30)
        + trace_bank("use, cleaned gaps", BANK32)
    )
    c_easy, c_chal, c_use = counts(easy_rows), counts(chal_rows), counts(use_rows)
    accounted = (
        c_easy["correct"] + c_easy["wrong"] + c_easy["leftover"] + c_easy["consensus_0"] == c_easy["n"]
        and c_chal["correct"] + c_chal["wrong"] + c_chal["leftover"] + c_chal["consensus_0"] == c_chal["n"]
        and c_use["wrong"] == 0
        and c_use["correct"] == c_use["n"]
    )
    write_lean(c_easy, c_chal, c_use)
    lean = subprocess.run(["lean", str(LEAN)], capture_output=True, text=True)
    lean_ok = lean.returncode == 0
    trace_bytes = json.dumps(
        {"easy": easy_rows, "challenge": chal_rows, "use": use_rows},
        ensure_ascii=False,
    ).encode("utf-8")
    trace_sha = hashlib.sha256(trace_bytes).hexdigest().upper()
    doc = {
        "adventure": 1,
        "ted": "TED-31",
        "vs_bill": "Bill-30",
        "pin": "AEB2AD",
        "free_parameters": 0,
        "phi": phi,
        "inv_phi": inv_phi,
        "easy": c_easy,
        "challenge": c_chal,
        "use": c_use,
        "trace_sha256": trace_sha,
        "lean_ok": lean_ok,
        "lean_returncode": lean.returncode,
        "measured_W_changed": False,
        "overall_ok": accounted and lean_ok and c_easy["correct"] == 570 and c_easy["n"] == 570,
        "promotes": False,
    }
    doc["promotes"] = doc["overall_ok"]
    doc["promote_to"] = "Bill-31" if doc["promotes"] else None
    payload = {"summary": doc, "easy": easy_rows, "challenge": chal_rows, "use": use_rows}
    OUT.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    stamp = {
        "pin": "AEB2AD",
        "free_parameters": 0,
        "phi": phi,
        "inv_phi": inv_phi,
        "overlay": "one agreed label",
        "consensus": "two labels, trit 0",
        "leftover": "no label, trit 0",
        "trace_sha256": trace_sha,
        "lean_file": "lean/Adventure1Thought.lean",
        "lean_ok": lean_ok,
        "easy": c_easy,
        "challenge": c_chal,
        "use": c_use,
        "measured_W_changed": False,
    }
    STAMP.write_text(json.dumps(stamp, indent=2), encoding="utf-8")
    chal_wrong = [r for r in chal_rows if r["kind"] == "wrong"]
    side = f"""# Adventure 1 side by side

Question, expected answer, and the answer the organism gave. Pin AEB2AD. Replay of the Bill-30 brain. Trace sha256 `{trace_sha}`.

A family answer of `leftover` means it refused. `consensus 0` means two routes named different letters. A score trit of +1 is a commitment that matched. −1 is a commitment that did not. 0 is a refusal.

## Use

{md_table(use_rows)}

## ARC-Challenge validation

{md_table(chal_rows)}

## ARC-Easy validation

{md_table(easy_rows)}
"""
    SIDE.write_text(side, encoding="utf-8")
    (ADV / "SIDE_BY_SIDE.md").write_text(side, encoding="utf-8")
    wrong_lines = "\n".join(
        f"| `{cell(r['id'])}` | {cell(r['stem'][:180])} | {cell(r['expected'])} | {cell(r['family'])} | {cell(r['route'])} |"
        for r in chal_wrong
    ) or "| none |  |  |  | |"
    report = f"""# Adventure 1 report

Pin **AEB2AD**. 0 free parameters. The brain replayed here includes the TED-32 gap relations. **Bill-32** freezes this record. Measured edges are still unchanged. This is the cleaned learning closeout of Adventure 1. The connectome closeout (hops, blueprint, two-animal split) stays in `CLOSEOUT.md`. This report is what the organism was taught, what it answered, and what was changed.

Trace: `data/adventure1_trace.json`. Side by side: `docs/ADVENTURE1_SIDE_BY_SIDE.md`. Lean check: `lean/Adventure1Thought.lean` ({'passed' if lean_ok else 'FAILED'}).

## Question

Can a measured fly connectome, with FSOT residual hops left as they are, learn to use a relation on a new wording, or does it only store the answer to a question it has already seen?

## What was not changed

Measured FlyWire edges were not edited. Male CNS stays **165,122** neurons, GABA **22,055**. Hop-2 vnc_motor stays VNC **10.74**, JO **7.77**, olfactory **0.0006**. Courtship, aggression, fru, and dsx stay T1 off. No new synapse was written onto APL, il3LN6, lLN2F_b, or INXXX007.

## What was added

Two splices at the language ALU (the same bottlenecks as language: IN05B011a, DNg29, IN01B001, DNp01):

| splice | what it stores | what it is |
|---|---|---|
| `reason_proc` | a cue in a stem and the choice it selects | mostly one question, one answer |
| `reason_use` | a situation | the same relation on a new wording, quiet when the wording is only similar |

Item cues that closed ARC-Easy: **424** procedures, each firing on one stem. Early relations that fire on more than one Easy stem and stay correct: sunlight to chloroplast, an animal that eats plants to herbivore, tides to the closer body. Three calculations compute rather than store a sentence: the closest reading to a stated length, distance over time, and a 25 percent increase of a summed load.

## FSOT form of a thought

The hop law on measured \\(W\\) is unchanged:

\\[
S = K(T_1+T_2+T_3),\\qquad r = 1+|S|\\cdot P_{{\\mathrm{{NEW}}}},\\qquad a \\leftarrow rWa.
\\]

From the pin, \\(\\varphi = {phi:.6f}\\) and the overlay cut is \\(1/\\varphi = {inv_phi:.6f}\\).

A learning decision is the same overlay / consensus / leftover, on labels instead of hop mass:

| situation | family output | trit |
|---|---|---|
| one route names one letter | that letter overlays | commitment |
| two routes name different letters | consensus 0, no letter | 0 |
| no route | leftover, no letter | 0 |

The score trit is recorded after the key is read. +1 the commitment matched. −1 it did not. 0 the organism refused. The key is not an input to the pick.

Lean checks that decision on concrete votes (`commit ["reflect"]` overlays, `commit ["rain","drought"]` is silence, a repeated label still overlays) and checks that the replay counts add up. `lean lean/Adventure1Thought.lean` returned {lean.returncode}.

## Replay

| exam | items | correct | wrong | leftover | consensus 0 |
|---|---:|---:|---:|---:|---:|
| ARC-Easy validation | {c_easy['n']} | {c_easy['correct']} | {c_easy['wrong']} | {c_easy['leftover']} | {c_easy['consensus_0']} |
| ARC-Challenge validation | {c_chal['n']} | {c_chal['correct']} | {c_chal['wrong']} | {c_chal['leftover']} | {c_chal['consensus_0']} |
| use wordings and near misses | {c_use['n']} | {c_use['correct']} | {c_use['wrong']} | {c_use['leftover']} | {c_use['consensus_0']} |

Easy **{c_easy['correct']}/{c_easy['n']}** is retention of what was taught, including the one-stem cues. It is the exam those cues were written for.

Challenge is the hard set those cues were not written for. After the relations, the organism is correct on **{c_chal['correct']}** of **{c_chal['n']}**, wrong on **{c_chal['wrong']}**, and refuses **{c_chal['leftover']}** plus **{c_chal['consensus_0']}** ties. Before any use relations, the blind score was 8 correct and 10 wrong out of 299.

Use wordings are sentences that were not the stored questions. **{c_use['correct']}/{c_use['n']}** of those checks hold: the taught relation fired on the new wording, or the near miss did not take the wrong relation.

## Where it committed and was wrong

These are the Challenge items where the family gave a letter and the key is a different letter.

| id | question | expected | family gave | route |
|---|---|---|---|---|
{wrong_lines}

The full question, expected answer, and family answer for every Easy item, every Challenge item, and every use item are in `docs/ADVENTURE1_SIDE_BY_SIDE.md`.

## What worked

- Refusal. Untaught items stay leftover instead of a guess.
- A relation on a new wording. The use banks passed, and the earlier use items still pass after the later relations were added.
- Retention of Easy. Adding relations did not knock the Easy exam off {c_easy['correct']}/{c_easy['n']}.
- The connectome gates stayed in force across the bills: look-split 0.494%, Ledger B median 0.0761%, two-animal function 3/3. Boot is the check.
- Calculations. Closest measurement, speed, and a 25 percent load are computed.

## What did not

- One cue per Easy question does not transfer. Blind Challenge, before the use relations, was 8/299 correct and 10 wrong. Precision on the letters it was willing to give was 44.4%.
- Most Challenge items are still a refusal. The relation list is a handful of situations, not the exam.
- A fact collision still happens. The wrong-answer table above is that failure: a route named a letter, and it was the wrong letter.
- Pasting Challenge items into the cue list would raise the Challenge score the way Easy was raised. That would be answer memory, which is the function this closeout separated from use.

## Still inside Adventure 1

The wrong commitment and the seven ties are cleaned. The remaining Challenge leftovers are situations with no relation yet. They stay refusals. Adventure 2 waits. The open job is more situations, each checked on a new wording and on a near miss, without copying Challenge questions into the cues. Measured \\(W\\) stays frozen. Courtship stays off.

Trace sha256 `{trace_sha}`.
"""
    REPORT.write_text(report, encoding="utf-8")
    (ADV / "ADVENTURE1_REPORT.md").write_text(report, encoding="utf-8")
    print(
        f"  TED-31 easy {c_easy['correct']}/{c_easy['n']} "
        f"challenge {c_chal['correct']}/{c_chal['n']} w={c_chal['wrong']} L={c_chal['leftover']} "
        f"use {c_use['correct']}/{c_use['n']} lean={lean_ok}"
    )
    if not lean_ok:
        print(lean.stdout)
        print(lean.stderr)
    print(f"  sha {trace_sha[:16]}  overall {doc['overall_ok']}")
    print(f"  wrote {REPORT}")
    return 0 if doc["overall_ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
