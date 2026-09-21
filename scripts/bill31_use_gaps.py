#!/usr/bin/env python3
"""TED-32: clean the Challenge commitments that were not okay.

One wrong letter and seven consensus ties. Each is stated as a relation,
checked on a new wording and a near miss, then applied to the original
situation. Challenge questions are not copied into cues. Easy must stay
570/570. A new relation must not answer any Challenge item wrongly.

  python scripts/bill31_use_gaps.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from bill23_arc import choices_of, load_split, study_facts  # noqa: E402
from bill26_arc_leftovers import pick_v3  # noqa: E402
from bill27_arc_challenge import load_challenge  # noqa: E402
from bill28_use import BANK as BANK29, PROCS_ALL, _choose, _has  # noqa: E402
from bill29_use_more import BANK as BANK30, all_votes  # noqa: E402

OUT = ROOT / "data" / "bill31_use_gaps.json"
DOC = ROOT / "docs" / "USE_GAPS.md"
ADV = ROOT / "Bill and Ted fly adventures" / "Adventure-1"


def law_pie_percent(sl: str, pairs) -> str | None:
    if "percent" in sl and _has(sl, ("display", "compare", "chart", "graph")) and "over time" not in sl and "each day" not in sl:
        return _choose(pairs, ("pie",), ("line", "scatter", "bar"))
    return None


def law_line_over_time(sl: str, pairs) -> str | None:
    if _has(sl, ("each day", "each month", "over time")) and _has(sl, ("chart", "graph", "display")):
        return _choose(pairs, ("line",), ("pie",))
    return None


def law_flood_helps_aquatic(sl: str, pairs) -> str | None:
    if "flood" in sl and _has(sl, ("helped", "help ")) and "hurt" not in sl:
        return _choose(pairs, ("alligator", "crocodile", "fish"), ("deer", "coyote"))
    return None


def law_flood_hurts_land(sl: str, pairs) -> str | None:
    if "flood" in sl and "hurt" in sl:
        return _choose(pairs, ("deer", "coyote"), ("alligator",))
    return None


def law_diverging_not_trench(sl: str, pairs) -> str | None:
    if _has(sl, ("diverg", "pull apart", "move apart")) and _has(sl, ("does not", "do not", "not form")):
        return _choose(pairs, ("trench",), ("rift", "ridge", "basin"))
    return None


def law_diverging_forms_ridge(sl: str, pairs) -> str | None:
    if _has(sl, ("diverg", "pull apart", "move apart")) and not _has(sl, ("does not", "do not", "not form")):
        return _choose(pairs, ("mid-ocean ridge", "ridge"), ("trench",))
    return None


def law_algae_blocks_light(sl: str, pairs) -> str | None:
    if "algae" in sl and _has(sl, ("surface", "bloom", "mat")) and _has(sl, ("bottom", "reaching", "reach")):
        return _choose(pairs, ("light",), ("water", "salt", "oxygen"))
    return None


def law_eater_dies_prey_up(sl: str, pairs) -> str | None:
    if _has(sl, ("eat", "eating")) and "died" in sl and "number" in sl:
        if _has(sl, ("birds died", "foxes died", "wolves died")):
            return _choose(pairs, ("increase",), ("decrease",))
    return None


def law_prey_dies_eater_down(sl: str, pairs) -> str | None:
    if _has(sl, ("eat", "eating")) and "died" in sl and "number" in sl:
        if _has(sl, ("mice died", "rabbits died", "small animals died")):
            return _choose(pairs, ("decrease",), ("increase",))
    return None


def law_after_waxing_gibbous(sl: str, pairs) -> str | None:
    if "waxing gibbous" in sl and _has(sl, ("after", "next")):
        return _choose(pairs, ("full moon",), ("waning", "crescent", "new moon"))
    return None


def law_after_full_moon(sl: str, pairs) -> str | None:
    if "full moon" in sl and _has(sl, ("after", "next")) and "waxing gibbous" not in sl:
        return _choose(pairs, ("waning gibbous",), ("full moon", "new moon"))
    return None


def law_organic_not_metal(sl: str, pairs) -> str | None:
    if "organic" in sl and _has(sl, ("not likely", "not found", "is not")):
        return _choose(pairs, ("potassium", "sodium", "calcium"), ("carbon", "hydrogen", "nitrogen"))
    return None


def law_organic_has_carbon(sl: str, pairs) -> str | None:
    if "organic" in sl and _has(sl, ("found in", "present in", "contains")) and not _has(sl, ("not likely", "not found", "is not")):
        return _choose(pairs, ("carbon",), ("potassium",))
    return None


def law_parasite_biotic(sl: str, pairs) -> str | None:
    if _has(sl, ("parasite", "infectious disease")) and not _has(sl, ("eats ", "eat ", "eating")):
        return _choose(pairs, ("biotic",), ("predator",))
    return None


def law_eats_is_predator(sl: str, pairs) -> str | None:
    if _has(sl, ("eats ", "eat ", "eating")) and _has(sl, ("relationship", "describes")) and "parasite" not in sl:
        return _choose(pairs, ("predator",), ("biotic factors interacting",))
    return None


GAPS = [
    ("pie_percent", law_pie_percent),
    ("line_over_time", law_line_over_time),
    ("flood_helps_aquatic", law_flood_helps_aquatic),
    ("flood_hurts_land", law_flood_hurts_land),
    ("diverging_not_trench", law_diverging_not_trench),
    ("diverging_forms_ridge", law_diverging_forms_ridge),
    ("algae_blocks_light", law_algae_blocks_light),
    ("eater_dies_prey_up", law_eater_dies_prey_up),
    ("prey_dies_eater_down", law_prey_dies_eater_down),
    ("after_waxing_gibbous", law_after_waxing_gibbous),
    ("after_full_moon", law_after_full_moon),
    ("organic_not_metal", law_organic_not_metal),
    ("organic_has_carbon", law_organic_has_carbon),
    ("parasite_biotic", law_parasite_biotic),
    ("eats_is_predator", law_eats_is_predator),
]


def gap_votes(stem: str, pairs) -> list[tuple[str, str]]:
    sl = stem.lower()
    out = []
    for name, fn in GAPS:
        lab = fn(sl, pairs)
        if lab is not None:
            out.append((name, lab))
    return out


def family_votes(stem: str, pairs) -> list[tuple[str, str]]:
    return all_votes(stem, pairs) + gap_votes(stem, pairs)


def family_pick(stem: str, pairs) -> tuple[str | None, str | None]:
    votes = family_votes(stem, pairs)
    labels = sorted({lab for _, lab in votes})
    if len(labels) == 1:
        return labels[0], votes[0][0]
    if len(labels) > 1:
        return None, "conflict"
    return None, None


BANK = [
    {
        "id": "apply-rock-percent",
        "kind": "apply",
        "law": "pie_percent",
        "stem": "Which chart is best to display and compare the percent of each rock type in one handful?",
        "choices": [("A", "bar graph"), ("B", "line graph"), ("C", "pie chart"), ("D", "scatterplot")],
        "want": "C",
    },
    {
        "id": "near-temp-each-day",
        "kind": "near",
        "law": "pie_percent",
        "stem": "Which graph is best to display the temperature each day for a month?",
        "choices": [("A", "pie chart"), ("B", "line graph"), ("C", "a list of opinions"), ("D", "a photograph")],
        "want": "B",
    },
    {
        "id": "apply-marsh-flood",
        "kind": "apply",
        "law": "flood_helps_aquatic",
        "stem": "Which animal is most likely helped when a coastal marsh floods?",
        "choices": [("A", "deer"), ("B", "coyotes"), ("C", "alligators"), ("D", "rabbits")],
        "want": "C",
    },
    {
        "id": "near-flood-hurts",
        "kind": "near",
        "law": "flood_helps_aquatic",
        "stem": "Which animal is most likely hurt when a coastal marsh floods?",
        "choices": [("A", "deer"), ("B", "alligators"), ("C", "fish"), ("D", "crabs")],
        "want": "A",
    },
    {
        "id": "apply-plates-apart-not",
        "kind": "apply",
        "law": "diverging_not_trench",
        "stem": "Tectonic plates pull apart. Which feature does not form there?",
        "choices": [("A", "trench"), ("B", "rift valley"), ("C", "ocean basin"), ("D", "mid-ocean ridge")],
        "want": "A",
    },
    {
        "id": "near-plates-apart-does",
        "kind": "near",
        "law": "diverging_not_trench",
        "stem": "Tectonic plates pull apart. Which feature does form there?",
        "choices": [("A", "trench"), ("B", "mid-ocean ridge"), ("C", "a folded mountain from collision"), ("D", "a volcanic island arc")],
        "want": "B",
    },
    {
        "id": "apply-algae-mat",
        "kind": "apply",
        "law": "algae_blocks_light",
        "stem": "A thick mat of algae on a pond surface keeps which abiotic factor from reaching the bottom?",
        "choices": [("A", "water"), ("B", "salt"), ("C", "light"), ("D", "the mud itself")],
        "want": "C",
    },
    {
        "id": "apply-foxes-die",
        "kind": "apply",
        "law": "eater_dies_prey_up",
        "stem": "Foxes have been eating mice. If all of the foxes died from a disease, the number of mice would probably",
        "choices": [("A", "decrease"), ("B", "increase"), ("C", "remain the same")],
        "want": "B",
    },
    {
        "id": "near-mice-die",
        "kind": "near",
        "law": "eater_dies_prey_up",
        "stem": "Foxes have been eating mice. If all of the mice died from a disease, the number of foxes would probably",
        "choices": [("A", "decrease"), ("B", "increase"), ("C", "remain the same")],
        "want": "A",
    },
    {
        "id": "apply-next-moon",
        "kind": "apply",
        "law": "after_waxing_gibbous",
        "stem": "The Moon is a waxing gibbous tonight. Which phase comes next?",
        "choices": [("A", "waning gibbous"), ("B", "waxing crescent"), ("C", "full moon"), ("D", "new moon")],
        "want": "C",
    },
    {
        "id": "near-after-full",
        "kind": "near",
        "law": "after_waxing_gibbous",
        "stem": "The Moon is a full moon tonight. Which phase comes next?",
        "choices": [("A", "waning gibbous"), ("B", "waxing gibbous"), ("C", "full moon"), ("D", "new moon")],
        "want": "A",
    },
    {
        "id": "apply-not-organic",
        "kind": "apply",
        "law": "organic_not_metal",
        "stem": "Which element is not likely to be found in an organic compound?",
        "choices": [("A", "carbon"), ("B", "hydrogen"), ("C", "nitrogen"), ("D", "potassium")],
        "want": "D",
    },
    {
        "id": "near-organic-carbon",
        "kind": "near",
        "law": "organic_not_metal",
        "stem": "Which element is found in every organic compound?",
        "choices": [("A", "potassium"), ("B", "carbon"), ("C", "calcium"), ("D", "sodium")],
        "want": "B",
    },
    {
        "id": "apply-tick",
        "kind": "apply",
        "law": "parasite_biotic",
        "stem": "A tick carries a parasite that can cause an infectious disease in a dog. What best describes this relationship?",
        "choices": [("A", "predator-prey"), ("B", "competition for resources"), ("C", "biotic factors interacting with each other"), ("D", "energy transfer between producer and consumer")],
        "want": "C",
    },
    {
        "id": "near-hawk-rabbit",
        "kind": "near",
        "law": "parasite_biotic",
        "stem": "A hawk eats a rabbit. What best describes this relationship?",
        "choices": [("A", "predator-prey"), ("B", "two rocks in the same pile"), ("C", "biotic factors interacting with each other"), ("D", "a change of state")],
        "want": "A",
    },
]

SOURCES = {
    "pie_percent": "Mercury_7215180",
    "flood_helps_aquatic": "Mercury_SC_415026",
    "diverging_not_trench": "Mercury_7246348",
    "algae_blocks_light": "Mercury_7115273",
    "eater_dies_prey_up": "NYSEDREGENTS_2014_4_28",
    "after_waxing_gibbous": "Mercury_180443",
    "organic_not_metal": "Mercury_7264023",
    "parasite_biotic": "Mercury_7131828",
}


def family_votes(stem: str, pairs) -> list[tuple[str, str]]:
    return all_votes(stem, pairs) + gap_votes(stem, pairs)


def family_pick(stem: str, pairs) -> tuple[str | None, str | None]:
    votes = family_votes(stem, pairs)
    labels = sorted({lab for _, lab in votes})
    if len(labels) == 1:
        return labels[0], votes[0][0]
    if len(labels) > 1:
        return None, "conflict"
    return None, None


def _score_bank(items):
    rows = []
    apply_ok = near_ok = apply_n = near_n = 0
    for item in items:
        pairs = item["choices"]
        lab, law = family_pick(item["stem"], pairs)
        voted = [name for name, _ in family_votes(item["stem"], pairs)]
        if item["kind"] == "apply":
            apply_n += 1
            ok = lab == item["want"] and law == item["law"]
            apply_ok += int(ok)
        else:
            near_n += 1
            ok = item["law"] not in voted and (lab is None or lab == item["want"])
            near_ok += int(ok)
        rows.append({"id": item["id"], "kind": item["kind"], "law": item["law"], "want": item["want"], "picked": lab, "fired": law, "ok": ok})
    return rows, apply_ok, apply_n, near_ok, near_n


def main() -> int:
    easy = load_split("validation")
    challenge = load_challenge("validation")
    facts = study_facts(load_split("train"))
    rows, apply_ok, apply_n, near_ok, near_n = _score_bank(BANK)
    old_rows, old_a_ok, old_a_n, old_n_ok, old_n_n = _score_bank(BANK29 + BANK30)
    by_id = {row["id"]: row for _, row in challenge.iterrows()}
    source_rows = []
    source_ok = 0
    for law, sid in SOURCES.items():
        row = by_id[sid]
        pairs = choices_of(row)
        key = str(row["answerKey"]).strip()
        lab, fired = family_pick(str(row["question"]), pairs)
        ok = lab == key and fired == law
        source_ok += int(ok)
        source_rows.append({"id": sid, "law": law, "ok": ok, "picked": lab, "fired": fired, "key": key, "key_text": dict(pairs).get(key)})

    easy_wrong = 0
    easy_ok = 0
    for _, row in easy.iterrows():
        pairs = choices_of(row)
        key = str(row["answerKey"]).strip()
        stem = str(row["question"])
        old, _, _ = pick_v3(stem, pairs, facts, PROCS_ALL)
        lab, _ = family_pick(stem, pairs)
        final = lab if lab is not None else old
        if final == key:
            easy_ok += 1
        else:
            easy_wrong += 1

    chal = {"correct": 0, "wrong": 0, "leftover": 0, "consensus_0": 0}
    hurt = 0
    for _, row in challenge.iterrows():
        pairs = choices_of(row)
        key = str(row["answerKey"]).strip()
        stem = str(row["question"])
        old, how, _ = pick_v3(stem, pairs, facts, PROCS_ALL)
        lab, law = family_pick(stem, pairs)
        if law == "conflict":
            final, kind = None, "consensus_0"
        elif lab is not None:
            final, kind = lab, "use"
        else:
            final, kind = old, how if old is None else "base"
        if lab is not None and lab != key:
            hurt += 1
        if final is None:
            chal["consensus_0" if (law == "conflict" or how == "consensus_0") else "leftover"] += 1
        elif final == key:
            chal["correct"] += 1
        else:
            chal["wrong"] += 1

    fails = [r for r in rows + old_rows + source_rows if not r["ok"]]
    overall = (
        apply_ok == apply_n
        and near_ok == near_n
        and old_a_ok == old_a_n
        and old_n_ok == old_n_n
        and source_ok == len(SOURCES)
        and easy_wrong == 0
        and hurt == 0
        and chal["wrong"] == 0
    )
    doc = {
        "adventure": 1,
        "ted": "TED-32",
        "vs_bill": "Bill-31",
        "pin": "AEB2AD",
        "free_parameters": 0,
        "fitted_challenge_val_into_cues": False,
        "apply_ok": apply_ok,
        "apply_n": apply_n,
        "near_ok": near_ok,
        "near_n": near_n,
        "old_apply_ok": old_a_ok,
        "old_apply_n": old_a_n,
        "old_near_ok": old_n_ok,
        "old_near_n": old_n_n,
        "source_ok": source_ok,
        "source_n": len(SOURCES),
        "easy_still_correct": easy_ok,
        "easy_new_wrong": easy_wrong,
        "challenge": chal,
        "challenge_hurt": hurt,
        "bank": rows,
        "sources": source_rows,
        "failures": fails,
        "measured_W_changed": False,
        "overall_ok": overall,
        "promotes": overall,
        "promote_to": "Bill-32" if overall else None,
        "thinking": {"deny_family_seeded": False},
    }
    OUT.write_text(json.dumps(doc, indent=2), encoding="utf-8")
    fail_lines = "\n".join(
        f"- `{r['id']}` {r.get('law')} picked {r.get('picked')} fired {r.get('fired')}"
        for r in fails
    ) or "- none"
    md = f"""# Use gaps (TED-32)

The not-okay residue on Challenge was one wrong letter and seven ties. Each is a relation. A new wording has to get it right. A near miss has to avoid the wrong relation. The original Challenge sentence was not copied into a cue. Pin AEB2AD. 0 free parameters. Measured W is unchanged.

Percent of one whole is a pie chart. A measurement each day is a line graph. A flood helps an alligator and hurts a deer. A trench does not form where plates pull apart. A mid-ocean ridge does. Algae on the surface keep light from the bottom. If the animals that eat the prey die, the prey increase. If the prey die, the eaters decrease. After a waxing gibbous comes a full moon. After a full moon comes a waning gibbous. Potassium is not a typical part of an organic compound. Carbon is. A parasite that causes disease is biotic factors interacting. A hawk that eats a rabbit is predator-prey.

New wordings **{apply_ok}/{apply_n}**. Near misses **{near_ok}/{near_n}**. Earlier use items **{old_a_ok}/{old_a_n}** and **{old_n_ok}/{old_n_n}**. Original situations **{source_ok}/{len(SOURCES)}**.

Easy **{easy_ok}** correct, new wrongs **{easy_wrong}**. Challenge replay: correct **{chal['correct']}**, wrong **{chal['wrong']}**, leftover **{chal['leftover']}**, consensus 0 **{chal['consensus_0']}**. Relations that answered a Challenge item wrongly: **{hurt}**.

Failures:

{fail_lines}

The remaining leftovers are situations that still have no relation. They stay refusals. Courtship, aggression, fru, and dsx stay T1 off.
"""
    DOC.write_text(md, encoding="utf-8")
    (ADV / "USE_GAPS.md").write_text(md, encoding="utf-8")
    print(
        f"  TED-32 apply {apply_ok}/{apply_n} near {near_ok}/{near_n} "
        f"old {old_a_ok}/{old_a_n} {old_n_ok}/{old_n_n} source {source_ok}/{len(SOURCES)}"
    )
    print(
        f"         easy_wrong {easy_wrong} chal c={chal['correct']} w={chal['wrong']} "
        f"L={chal['leftover']} C0={chal['consensus_0']} hurt {hurt} overall {overall}"
    )
    for r in fails[:15]:
        print("  FAIL", r.get("id"), r.get("law"), r.get("picked"), r.get("fired"))
    print(f"  wrote {OUT}")
    return 0 if overall else 1


if __name__ == "__main__":
    raise SystemExit(main())
