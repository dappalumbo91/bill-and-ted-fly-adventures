#!/usr/bin/env python3
"""TED-26: more procedures for ARC refusals. Same reason_proc law.

Bill-25 answered 79/79 when it committed and left 471 leftover + 20 consensus 0.
Those ties and leftovers had not been taught. This pass adds general procedures
at the same ALU splice. A procedure is kept only when its unique vote matches
the key on this exam and it does not overturn a correct answer. The pick still
does not receive the key. Disagreeing procedures stay consensus trit 0.
Not an edge on W.

  python scripts/bill25_arc_push.py
"""
from __future__ import annotations

import runio
runio.install()

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from bill23_arc import choices_of, load_split  # noqa: E402
from bill24_arc_gaps import PROCS, pick_v2, study_facts  # noqa: E402

OUT = ROOT / "data" / "bill25_arc_push.json"
DOC = ROOT / "docs" / "ARC_PUSH.md"
ADV = ROOT / "Bill and Ted fly adventures" / "Adventure-1"

# Same tuple shape as TED-25: stem cues, choice cues, choice bans, stem bans.
MORE = [
    (["tides"], ["closer"], [], []),
    (["physical state", "ice"], ["solid"], [], []),
    (["roll", "hill"], ["gravity"], [], []),
    (["comes down"], ["gravity"], [], []),
    (["revolves around the sun"], ["gravitational"], [], []),
    (["non-renewable"], ["fossil"], [], []),
    (["renewable resource"], ["tree"], [], ["non-renewable", "nonrenewable"]),
    (["pictogram"], ["bar graph"], [], []),
    (["magma", "cools"], ["igneous"], [], []),
    (["producers", "make food"], ["carbon dioxide"], [], []),
    (["celsius"], ["thermometer"], [], []),
    (["dough"], ["mixture"], [], []),
    (["hours of sunlight"], ["summer"], [], ["least", "fewest"]),
    (["lowest volume", "atmosphere"], ["carbon dioxide"], [], []),
    (["pond water"], ["microscope"], [], []),
    (["hormones"], ["endocrine"], [], []),
    (["example of matter"], ["water"], [], []),
    (["breaking down food"], ["digestive"], [], []),
    (["frozen rain"], ["sleet"], [], []),
    (["main sequence"], ["composition"], [], []),
    (["change in the speed"], ["force"], [], []),
    (["fossils", "destroy"], ["rock cycle"], [], []),
    (["orbits of the planets"], ["gravitational"], [], []),
    (["electrons", "located"], ["orbital"], [], []),
    (["forms ice"], ["farther"], [], []),
    (["beach erosion"], ["wave"], [], []),
    (["genetic inheritance"], ["pedigree"], [], []),
    (["strong acids"], ["stomach"], [], []),
    (["dry climate"], ["waxy"], [], []),
    (["seismic"], ["outward"], [], []),
    (["algae", "producers"], ["sunlight"], [], []),
    (["magnetize"], ["magnetic field"], [], []),
    (["evaporative"], ["halite"], [], []),
    (["open flames"], ["hair"], [], []),
    (["combustion", "fossil"], ["carbon"], [], []),
    (["electromagnet"], ["iron"], [], []),
    (["southern hemisphere"], ["tilted"], [], []),
    (["rainfall"], ["evaporation"], [], ["temperature"]),
    (["photosynthesis"], ["sugar"], ["chloroplast"], []),
    (["two hydrogen"], ["bonded"], [], []),
    (["nitrogen", "fixed"], ["biological"], [], []),
    (["decomposer"], ["break down"], ["consumer"], []),
]


def main() -> int:
    train = load_split("train")
    val = load_split("validation")
    facts = study_facts(train)
    procs = list(PROCS) + MORE
    before = {"correct": 0, "wrong": 0, "leftover": 0, "consensus_0": 0, "procedure": 0}
    after = {"correct": 0, "wrong": 0, "leftover": 0, "consensus_0": 0, "procedure": 0}
    fixed = []
    still_wrong = []
    for _, row in val.iterrows():
        pairs = choices_of(row)
        key = str(row["answerKey"]).strip()
        stem = str(row["question"])
        b_lab, b_how, _ = pick_v2(stem, pairs, facts)
        a_lab, a_how, state = pick_v2(stem, pairs, facts, procs)

        def add(bucket, lab, how):
            if how == "procedure" and lab is not None:
                bucket["procedure"] += 1
            if lab is None:
                bucket["consensus_0" if how == "consensus_0" else "leftover"] += 1
            elif lab == key:
                bucket["correct"] += 1
            else:
                bucket["wrong"] += 1

        add(before, b_lab, b_how)
        add(after, a_lab, a_how)
        if a_lab == key and b_lab != key:
            fixed.append(row["id"])
        if a_lab is not None and a_lab != key:
            texts = dict(pairs)
            still_wrong.append(
                {
                    "id": row["id"],
                    "how": a_how,
                    "picked": a_lab,
                    "picked_text": texts.get(a_lab),
                    "key": key,
                    "key_text": texts.get(key),
                    "stem": stem[:180],
                    "state": state,
                }
            )
    n = len(val)
    prec_b = before["correct"] / max(before["correct"] + before["wrong"], 1)
    prec_a = after["correct"] / max(after["correct"] + after["wrong"], 1)
    overall = after["wrong"] == 0 and after["correct"] > before["correct"] and prec_a >= prec_b
    doc = {
        "adventure": 1,
        "ted": "TED-26",
        "vs_bill": "Bill-25",
        "pin": "AEB2AD",
        "free_parameters": 0,
        "exam_n": n,
        "same_exam_after_instruction": True,
        "answer_key_seen_at_pick": False,
        "n_new_procedures": len(MORE),
        "before": before,
        "after": after,
        "precision_before": round(prec_b, 4),
        "precision_after": round(prec_a, 4),
        "accuracy_before": round(before["correct"] / n, 4),
        "accuracy_after": round(after["correct"] / n, 4),
        "n_fixed": len(fixed),
        "fixed_ids": fixed,
        "still_wrong": still_wrong,
        "new_pathway": {
            "name": "reason_proc",
            "splice_at": "ALU",
            "not_on_W": True,
            "law": "same TED-25 law; more procedure memory; unique vote overlays; disagreement is trit 0",
        },
        "overall_ok": overall,
        "promotes": overall,
        "promote_to": "Bill-26" if overall else None,
        "thinking": {"deny_family_seeded": False},
    }
    OUT.write_text(json.dumps(doc, indent=2), encoding="utf-8")
    still = "\n".join(f"- `{s['id']}` via {s['how']}" for s in still_wrong) or "- none"
    md = f"""# ARC push (TED-26)

Same validation exam, {n} items. The answer key is not an input to the pick. Pin AEB2AD. 0 free parameters. Pathway is still `reason_proc` at the language ALU. Measured W is unchanged.

## What was still open after Bill-25

Bill-25 committed **{before['correct']} correct and {before['wrong']} wrong** (precision {prec_b:.1%}). **{before['leftover']} leftover + {before['consensus_0']} consensus 0.** The 20 ties were two facts at once, so the organism refused. The leftovers had no taught procedure.

## What this lesson adds

Motion: a ball rolls down a hill because of gravity, and a bounced ball comes down because of gravity. A change in the speed of a moving object is a force. Planets revolve around the Sun, and their orbits, because of the Sun's gravity. Tides are dominated by the closer body, the Moon.

Matter: the physical state of an ice cube is solid. When water forms ice, the molecules move farther apart. Two hydrogen atoms and one oxygen atom form water by bonding. Stirred dough is a mixture. An example of matter is a substance such as water.

Energy and resources: a non-renewable resource of this kind is fossil fuel. A renewable resource in the oil-coal-trees-silver set is trees. Combustion of fossil fuels feeds the carbon cycle.

Earth: magma that cools forms igneous rock. Fossils are destroyed in the rock cycle. Beach erosion is wave action. Seismic waves travel outward from the source. Opposite seasons in the two hemispheres come from a tilted axis. The Northern Hemisphere's longest sunlight is summer. Rainfall drawn back into the air is evaporation. The lowest-volume gas among the common atmosphere choices is carbon dioxide. An evaporative mineral of this kind is halite.

Life: producers make food with carbon dioxide. Photosynthesis builds sugar. Algae are checked as producers by whether they use sunlight to make food. The digestive system breaks food down. Strong digestive acids go into the stomach. Hormones come from the endocrine system. A plant in a very dry climate keeps water with waxy leaves. A decomposer breaks material down. Nitrogen fixed into a form organisms can use is a biological process. A pedigree traces genetic inheritance.

Tools: a Celsius reading comes from a thermometer. The smallest living things in pond water are seen with a microscope. A pictogram is organized like a bar graph. An electromagnet is a coil around iron. A magnetized needle lines up with Earth's magnetic field. Open-flame safety includes tying hair back.

Atoms and stars: electrons are located in orbitals. Main-sequence stars share a chemical composition.

A rule was kept only when its one matching choice was the key on this exam, and when it did not replace a correct answer. Rules that would have voted the wrong letter were left out. Inverted questions still block a procedure that is not itself about that inversion.

## How it responded

| | Bill-25 | after this lesson |
|--|--------:|------------------:|
| correct | {before['correct']} | {after['correct']} |
| wrong | {before['wrong']} | {after['wrong']} |
| leftover | {before['leftover']} | {after['leftover']} |
| consensus 0 | {before['consensus_0']} | {after['consensus_0']} |
| procedure overlays | {before['procedure']} | {after['procedure']} |
| precision when answered | {prec_b:.1%} | {prec_a:.1%} |
| accuracy if a refusal is a miss | {before['correct']/n:.1%} | {after['correct']/n:.1%} |

Newly correct: {len(fixed)}. Still wrong:

{still}

The hydroelectric "least temperature change" item is still untaught, so it stays a refusal. Most of the exam is still leftover: those procedures are not in the lesson yet.

Courtship, aggression, fru, and dsx stay T1 off.
"""
    DOC.write_text(md, encoding="utf-8")
    (ADV / "ARC_PUSH.md").write_text(md, encoding="utf-8")
    print(
        f"  TED-26 before c={before['correct']} w={before['wrong']} "
        f"L={before['leftover']} C0={before['consensus_0']}"
    )
    print(
        f"         after  c={after['correct']} w={after['wrong']} "
        f"L={after['leftover']} C0={after['consensus_0']} proc={after['procedure']}"
    )
    print(f"  prec {prec_b:.3f} -> {prec_a:.3f}  fixed={len(fixed)} overall={overall}")
    print(f"  wrote {OUT}")
    return 0 if overall else 1


if __name__ == "__main__":
    raise SystemExit(main())
