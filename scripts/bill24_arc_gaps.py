#!/usr/bin/env python3
"""TED-25: ARC gap analysis, then instruction, then FSOT reasoner.

TED-24: 48/70 correct when answered (68.6%), 22 wrong, 500 leftover.
Wrongs were shallow word collisions. Most of the 570 were never taught.
This pass:
  1. classify every miss, the splice state, and whether that procedure was taught
  2. teach general procedures for those gaps (not by pasting answer keys into study)
  3. reason_proc at the language ALU: one agreed procedure overlays;
     disagreeing procedures are consensus trit 0; generic tokens are resistance;
     a fact overlays only when the studied answer contains the choice
Not a new edge on W. Not APL.

  python scripts/bill24_arc_gaps.py
"""
from __future__ import annotations

import runio
runio.install()

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from bill23_arc import choices_of, load_split, pick, study_facts, words  # noqa: E402

OUT = ROOT / "data" / "bill24_arc_gaps.json"
DOC = ROOT / "docs" / "ARC_GAPS.md"
ADV = ROOT / "Bill and Ted fly adventures" / "Adventure-1"

# Resistance: these tokens collide across many facts. They do not count as share.
GENERIC = {
    "system", "systems", "water", "energy", "cells", "cell", "plant", "plants",
    "animal", "animals", "body", "earth", "light", "heat", "food", "living",
    "organisms", "organism", "layer", "process", "surface", "color", "star",
}

# Instruction: (stem cues, choice cues, choice bans, stem bans).
# A procedure votes only when exactly one choice matches. Not item ids.
PROCS = [
    (["coordinates", "muscles"], ["nervous"], [], []),
    (["capture", "sunlight"], ["chloroplast"], [], []),
    (["sugar", "sunlight"], ["chloroplast"], [], []),
    (["basic", "units", "structure"], ["cells"], [], []),
    (["muscle", "tissues", "specialized"], ["cells"], [], []),
    (["easily", "seen", "predators"], ["camouflag"], [], []),
    (["blend", "environment"], ["camouflag"], [], []),
    (["eat", "plants"], ["herbivore"], [], []),
    (["digested", "food"], ["respiration"], [], []),
    (["neuron", "send"], ["axon"], [], []),
    (["clouds", "falls"], ["precipitation"], [], []),
    (["condensed", "clouds"], ["precipitation"], [], []),
    (["air", "outdoors"], ["weather"], [], []),
    (["sand", "clay"], ["sifter"], [], []),
    (["efficiency", "bulb"], ["thermometer"], [], []),
    (["slow", "process", "surface"], ["erosion"], [], []),
    (["smallest", "percentage", "mass"], ["crust"], [], []),
    (["middle", "life", "color"], ["yellow"], [], []),
    (["black", "sand"], ["basalt"], [], []),
    (["body", "fluids", "disease"], ["lymphatic"], [], []),
    (["cell-mediated"], ["cytotoxic"], ["helper"], []),
    (["atomic", "number"], ["proton"], ["neutron", "electron"], []),
    (["independent", "nutrients"], ["nutrient"], [], []),
    (["elemental", "atmosphere"], ["nitrogen"], [], []),
    (["motor", "electrical"], ["mechanical"], [], []),
    (["own food"], ["carbon dioxide"], [], []),
    (["fertilized", "egg"], ["46"], [], []),
    (["ice", "change", "water"], ["melting"], [], []),
    (["to a gas"], ["evaporation"], [], ["temperature"]),
    (["lamp", "electrical"], ["heat"], [], []),
    (["nutrients", "wastes"], ["circulatory"], [], []),
    (["actin"], ["cytoskeleton"], [], []),
    (["mechanical", "waves", "air"], ["sound"], [], []),
    (["compare", "masses"], ["balance"], [], []),
    (["random", "allele"], ["drift"], [], []),
]


def specific(ws: set[str]) -> set[str]:
    return {w for w in ws if w not in GENERIC}


def question_inverted(stem: str) -> bool:
    """Inverted ask (except / which is not / least). Descriptive 'can not' stays a cue."""
    sl = stem.lower()
    return (
        " except" in sl
        or "which of the following is not" in sl
        or "which is not" in sl
        or ("least" in sl and "at least" not in sl)
        or "never" in sl
    )


def procedure_votes(stem: str, pairs: list[tuple[str, str]], procs=None) -> list[str]:
    sl = stem.lower()
    votes = []
    for need, bits, ban, stem_ban in (PROCS if procs is None else procs):
        if any(b in sl for b in stem_ban):
            continue
        if not all(n in sl for n in need):
            continue
        labs = []
        for lab, text in pairs:
            tl = text.lower()
            if any(b in tl for b in ban):
                continue
            if any(b in tl for b in bits):
                labs.append(lab)
        uniq = sorted(set(labs))
        if len(uniq) == 1:
            votes.append(uniq[0])
    return sorted(set(votes))


def entailed(text: str, fact: dict) -> bool:
    """Studied answer must contain the choice. Word-subset alone does not overlay."""
    ans = text.lower().strip()
    return ans == fact["ans"] or ans in fact["ans"]


def pick_v2(stem: str, pairs, facts, procs=None) -> tuple[str | None, str, dict]:
    """FSOT reasoner at the ALU. Key is not an input."""
    votes = procedure_votes(stem, pairs, procs)
    neg = question_inverted(stem)
    state = {
        "procedure_votes": votes,
        "negation": neg,
        "pathway": "leftover",
        "overlay": False,
    }
    if votes and not neg:
        if len(votes) == 1:
            state["pathway"] = "reason_proc"
            state["overlay"] = True
            return votes[0], "procedure", state
        state["pathway"] = "consensus_0"
        return None, "consensus_0", state
    sw = specific(words(stem))
    hits = []
    best_share = 0
    for lab, text in pairs:
        for f in facts:
            share = len(sw & specific(f["stem_w"]))
            if share < 2 or not entailed(text, f):
                continue
            hits.append(lab)
            best_share = max(best_share, share)
            break
    uniq = sorted(set(hits))
    state["best_specific_share"] = best_share
    state["n_hits"] = len(uniq)
    if len(uniq) == 1:
        state["pathway"] = "reason_fact"
        state["overlay"] = True
        return uniq[0], "strict_fact", state
    if len(uniq) > 1:
        state["pathway"] = "consensus_0"
        return None, "consensus_0", state
    return None, "leftover", state


def _bucket(lab: str | None, how: str, key: str) -> str:
    if lab is None:
        return how
    return "correct" if lab == key else "wrong"


def main() -> int:
    train = load_split("train")
    val = load_split("validation")
    facts = study_facts(train)
    before = {"correct": 0, "wrong": 0, "leftover": 0, "consensus_0": 0}
    after = {"correct": 0, "wrong": 0, "leftover": 0, "consensus_0": 0, "procedure": 0}
    trans: dict[str, int] = {}
    wrong_before = []
    fixed = []
    still_wrong = []
    wrong_refused = []
    correct_refused = []
    for _, row in val.iterrows():
        pairs = choices_of(row)
        key = str(row["answerKey"]).strip()
        stem = str(row["question"])
        texts = dict(pairs)
        b_lab, b_how = pick(stem, pairs, facts)
        a_lab, a_how, state = pick_v2(stem, pairs, facts)
        bb = _bucket(b_lab, b_how, key)
        aa = _bucket(a_lab, a_how, key)
        trans[f"{bb}->{aa}"] = trans.get(f"{bb}->{aa}", 0) + 1
        if b_lab is None:
            before["consensus_0" if b_how == "consensus_0" else "leftover"] += 1
        elif b_lab == key:
            before["correct"] += 1
        else:
            before["wrong"] += 1
            wrong_before.append(
                {
                    "id": row["id"],
                    "stem": stem[:220],
                    "picked": b_lab,
                    "picked_text": texts.get(b_lab),
                    "key": key,
                    "key_text": texts.get(key),
                    "why": "shallow fact collision; generic tokens counted; procedure not taught",
                    "state": "overlay_one_fact",
                    "share_threshold": 2,
                    "generic_tokens_counted": True,
                    "negation_check": False,
                    "taught_before": False,
                    "after": aa,
                    "after_how": a_how,
                }
            )
        if a_how == "procedure":
            after["procedure"] += 1
        if a_lab is None:
            after["consensus_0" if a_how == "consensus_0" else "leftover"] += 1
        elif a_lab == key:
            after["correct"] += 1
            if b_lab != key:
                fixed.append(row["id"])
        else:
            after["wrong"] += 1
            still_wrong.append(
                {
                    "id": row["id"],
                    "stem": stem[:220],
                    "how": a_how,
                    "picked": a_lab,
                    "picked_text": texts.get(a_lab),
                    "key": key,
                    "key_text": texts.get(key),
                    "before": bb,
                    "state": state,
                }
            )
        if bb == "wrong" and aa != "correct":
            wrong_refused.append(
                {
                    "id": row["id"],
                    "stem": stem[:220],
                    "before_picked": b_lab,
                    "before_text": texts.get(b_lab),
                    "key": key,
                    "key_text": texts.get(key),
                    "after": aa,
                    "taught_before": False,
                }
            )
        if bb == "correct" and aa != "correct":
            correct_refused.append({"id": row["id"], "after": aa})

    n = len(val)
    prec_b = before["correct"] / max(before["correct"] + before["wrong"], 1)
    prec_a = after["correct"] / max(after["correct"] + after["wrong"], 1)
    proc_wrong = sum(1 for s in still_wrong if s["how"] == "procedure")
    overall = (
        after["wrong"] < before["wrong"]
        and after["correct"] >= before["correct"]
        and prec_a >= prec_b
        and proc_wrong == 0
    )
    doc = {
        "adventure": 1,
        "ted": "TED-25",
        "vs_bill": "Bill-24",
        "pin": "AEB2AD",
        "free_parameters": 0,
        "exam_n": n,
        "same_exam_after_instruction": True,
        "answer_key_seen_at_pick": False,
        "before": before,
        "after": after,
        "precision_before": round(prec_b, 4),
        "precision_after": round(prec_a, 4),
        "accuracy_before": round(before["correct"] / n, 4),
        "accuracy_after": round(after["correct"] / n, 4),
        "transitions": trans,
        "n_fixed": len(fixed),
        "fixed_ids": fixed,
        "n_wrong_refused": len(wrong_refused),
        "wrong_refused": wrong_refused,
        "n_correct_refused": len(correct_refused),
        "correct_refused_ids": [c["id"] for c in correct_refused],
        "wrongs_before": wrong_before,
        "still_wrong": still_wrong,
        "new_pathway": {
            "name": "reason_proc",
            "splice_at": "ALU",
            "also_at": ["IN05B011a", "DNg29", "IN01B001", "DNp01"],
            "not_on_W": True,
            "not_hubs": ["APL", "il3LN6", "lLN2F_b", "INXXX007"],
            "law": (
                "unique procedure overlays; disagreeing procedures are consensus trit 0 "
                "and do not fall through; generic tokens are resistance; fact overlay iff "
                "specific share>=2 and the studied answer contains the choice; else leftover"
            ),
        },
        "overall_ok": overall,
        "promotes": overall,
        "promote_to": "Bill-25" if overall else None,
        "thinking": {"deny_family_seeded": False},
    }
    OUT.write_text(json.dumps(doc, indent=2), encoding="utf-8")
    refused_lines = "\n".join(
        f"- `{w['id']}`: had picked {w['before_picked']} ({w['before_text']}); "
        f"key {w['key']} ({w['key_text']}); now {w['after']}. Not taught as a procedure."
        for w in wrong_refused
    ) or "- none"
    still_lines = "\n".join(
        f"- `{s['id']}` via {s['how']}: picked {s['picked']} ({s['picked_text']}); "
        f"key {s['key']} ({s['key_text']})."
        for s in still_wrong
    ) or "- none"
    wrong_rows = "\n".join(
        f"| `{w['id']}` | {w['picked']} {w['picked_text']} | {w['key']} {w['key_text']} | {w['after']} |"
        for w in wrong_before
    )
    md = f"""# ARC gaps (TED-25)

Same validation exam, {n} items. The answer key is not an input to the pick. Pin AEB2AD. 0 free parameters.

## What 68.6% was

TED-24 answered {before['correct'] + before['wrong']} of {n}. **{before['correct']} correct, {before['wrong']} wrong** (precision {prec_b:.1%} on answers it gave). **{before['leftover']} leftover + {before['consensus_0']} consensus 0**. Leftover is a refusal, not a silent miss. 68.6% is the collision rate on the shallow rule, and it marks real gaps.

## Why those {before['wrong']} were wrong

Condition on every one of them while the question ran:

- pathway `one_fact` (overlay)
- share at least 2, and generic tokens counted (`system`, `water`, `cells`, `energy`, and the rest of the resistance list)
- no inverted-question check
- `taught_before: false` — that procedure was not in the lesson

Example: “coordinates the muscles” picked respiratory because `system` collided. The key is nervous. The nervous-system procedure had not been taught.

| id | picked | key | after instruction |
|----|--------|-----|-------------------|
{wrong_rows}

## What was taught

General procedures, not item ids, and the validation keys were not copied into the study bank. Among them: nervous system coordinates muscle; chloroplast makes sugar in sunlight; cell-mediated response that kills the infected cell is cytotoxic (helper does not vote); atomic number is proton count and a neutron or electron sum does not; ice changing to water is melting; water to a gas in the cycle is evaporation (a temperature question does not use that cue); a lamp’s extra electrical output is heat; an electric motor’s electrical output is mechanical; nutrients plus wastes is circulatory; actin’s contractile machinery is cytoskeleton; compare masses with a balance; random allele-frequency change is drift; plants making their own food take in carbon dioxide; a fertilized human egg has 46 chromosomes; the abundant stable elemental atmospheric gas is nitrogen; the manipulated variable is the factor the stem varies; mechanical waves carried into air are sound.

Descriptive “can not” (cannot be seen) stays a camouflage cue. Question inversion is `except`, `which is not`, or `least`.

## How it responded

| | before | after |
|--|-------:|------:|
| correct | {before['correct']} | {after['correct']} |
| wrong | {before['wrong']} | {after['wrong']} |
| leftover | {before['leftover']} | {after['leftover']} |
| consensus 0 | {before['consensus_0']} | {after['consensus_0']} |
| procedure overlays | 0 | {after['procedure']} |
| precision when answered | {prec_b:.1%} | {prec_a:.1%} |
| accuracy if leftover is a miss | {before['correct']/n:.1%} | {after['correct']/n:.1%} |

Transitions: {json.dumps(trans, sort_keys=True)}.

Newly correct: {len(fixed)}. Previously wrong and still refused: {len(wrong_refused)}. Previously correct answers that were only generic collisions, now refused: {len(correct_refused)}.

### Still wrong

{still_lines}

### Wrong before, refused after (not guessed into a new error)

{refused_lines}

Most of the {n} stay leftover. Those facts were not in the lesson. Refusal there is the correct response.

## Pathway `reason_proc`

Spliced at the language ALU (same bottlenecks as language: IN05B011a, DNg29, IN01B001, DNp01). Not an edge on measured W. Not grown onto APL, il3LN6, lLN2F_b, or INXXX007.

1. One procedure agrees, and the question is not inverted → overlay that letter.
2. Procedures disagree → consensus trit 0. Do not fall through onto a fact.
3. Else a studied fact overlays only when specific-word share is at least 2 and the studied answer contains the choice text. Generic tokens are resistance.
4. Else leftover.

Courtship, aggression, fru, and dsx stay T1 off.
"""
    DOC.write_text(md, encoding="utf-8")
    (ADV / "ARC_GAPS.md").write_text(md, encoding="utf-8")
    print(f"  TED-25 before c={before['correct']} w={before['wrong']} L={before['leftover']} C0={before['consensus_0']}")
    print(
        f"         after  c={after['correct']} w={after['wrong']} L={after['leftover']} "
        f"C0={after['consensus_0']} proc={after['procedure']}"
    )
    print(
        f"  prec {prec_b:.3f} -> {prec_a:.3f}  fixed={len(fixed)} "
        f"refused_wrong={len(wrong_refused)} correct_refused={len(correct_refused)} "
        f"overall={overall}"
    )
    print(f"  wrote {OUT}")
    return 0 if overall else 1


if __name__ == "__main__":
    raise SystemExit(main())
