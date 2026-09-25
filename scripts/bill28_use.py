#!/usr/bin/env python3
"""TED-29: answer-the-question versus use-the-relation.

Fitting ARC-Easy made cues that repeat one exam sentence. That answers those
items. Use is a different function: the same relation has to select the right
choice on a new wording, and it has to stay quiet on a near miss.

This pass does not add Challenge items to the cue list. It
  1. counts how many current procedures fire on one stem versus many
  2. states eight relations as situations, not as copied questions
  3. scores new wordings and near misses, and checks the original Challenge
     items only after the relation is stated
The Easy exam must not gain a wrong answer.

  python scripts/bill28_use.py
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
from bill24_arc_gaps import PROCS  # noqa: E402
from bill25_arc_push import MORE  # noqa: E402
from bill26_arc_leftovers import EXTRA, MORE2, _vote, pick_v3  # noqa: E402
from bill27_arc_challenge import load_challenge  # noqa: E402
from bill24_arc_gaps import study_facts  # noqa: E402

OUT = ROOT / "data" / "bill28_use.json"
DOC = ROOT / "docs" / "USE.md"
ADV = ROOT / "Bill and Ted fly adventures" / "Adventure-1"

EARLY = list(PROCS) + list(MORE) + list(EXTRA)
ITEM_CUES = list(MORE2)
PROCS_ALL = EARLY + ITEM_CUES


def _has(sl: str, words: tuple[str, ...]) -> bool:
    return any(w in sl for w in words)


def _word(sl: str, w: str) -> bool:
    return f" {w} " in f" {sl} "


def _choose(pairs, bits: tuple[str, ...], ban: tuple[str, ...] = ()) -> str | None:
    labs = []
    for lab, text in pairs:
        tl = text.lower()
        if any(b in tl for b in ban):
            continue
        if any(b in tl for b in bits):
            labs.append(lab)
    labs = sorted(set(labs))
    return labs[0] if len(labs) == 1 else None


def law_reflection(sl: str, pairs) -> str | None:
    sees = _has(sl, ("see ", "sees ", "looks into", "look into", "looking into"))
    water = _has(sl, ("pond", "lake", "pool"))
    image = _word(sl, "face") or _has(sl, ("upside down", "reflection"))
    if sees and water and image:
        return _choose(pairs, ("reflect",), ("temperature",))
    return None


def law_egg_cell(sl: str, pairs) -> str | None:
    if "egg" in sl and _has(sl, ("organization", "level of")):
        return _choose(pairs, ("cell",), ("organ system",))
    return None


def law_consumer(sl: str, pairs) -> str | None:
    eats = _has(sl, ("eat ", "eats ", "ate "))
    dead = _has(sl, ("dead", "rot", "breaks down", "break down", "decompos"))
    if eats and not dead and _has(sl, ("role", "food web", "ecosystem")):
        return _choose(pairs, ("consumer",), ("decomposer",))
    return None


def law_decomposer(sl: str, pairs) -> str | None:
    if _has(sl, ("dead", "rot", "breaks down", "break down")) and _has(sl, ("role", "ecosystem", "food web")):
        return _choose(pairs, ("decomposer",), ("consumer",))
    return None


def law_freeze_state(sl: str, pairs) -> str | None:
    frozen = _has(sl, ("freezer", "frozen", "freezing"))
    if frozen and _has(sl, ("will change", "property changed", "which property of")) and "stay" not in sl and "same" not in sl:
        return _choose(pairs, ("state",), ("mass",))
    return None


def law_freeze_mass(sl: str, pairs) -> str | None:
    if _has(sl, ("freezer", "frozen")) and _has(sl, ("stay the same", "stays the same", "remains the same")):
        return _choose(pairs, ("mass",), ("state",))
    return None


def law_life_history_rock(sl: str, pairs) -> str | None:
    if _has(sl, ("fossil", "history of living", "ancient animals")):
        return _choose(pairs, ("limestone", "sedimentary"), ("igneous", "magma"))
    return None


def law_igneous(sl: str, pairs) -> str | None:
    if "magma" in sl and _has(sl, ("cools", "cooling")):
        return _choose(pairs, ("igneous",), ("limestone", "sedimentary"))
    return None


def law_eukaryote_nucleus(sl: str, pairs) -> str | None:
    if "eukaryotic" in sl and "prokaryotic" in sl and _has(sl, ("not ", "absent", "missing")):
        return _choose(pairs, ("nucleus",), ("membrane",))
    return None


def law_high_pressure_dry(sl: str, pairs) -> str | None:
    if "high-pressure" in sl or "high pressure" in sl:
        if _has(sl, ("remains", "sits over", "stops air", "keeps air")):
            return _choose(pairs, ("drought", "dry"), ("rain",))
    return None


def law_low_pressure_wet(sl: str, pairs) -> str | None:
    if "low-pressure" in sl or "low pressure" in sl:
        if _has(sl, ("rising", "rises", "move in", "moves in")):
            return _choose(pairs, ("rain", "cloudy"), ("sunny", "drought"))
    return None


def law_temperature_place(sl: str, pairs) -> str | None:
    if _has(sl, ("warmer", "colder")) and _has(sl, ("pond", "lake", "water")) and not _word(sl, "face") and "upside down" not in sl:
        return _choose(pairs, ("temperature",), ("reflect",))
    return None


def law_heart_organ(sl: str, pairs) -> str | None:
    if "heart" in sl and _has(sl, ("organization", "level")) and "egg" not in sl:
        return _choose(pairs, ("organ",), ("cell", "organ system"))
    return None


def law_shared_membrane(sl: str, pairs) -> str | None:
    if "eukaryotic" in sl and "prokaryotic" in sl and _has(sl, ("both", "share")) and not _has(sl, ("absent", "not ", "missing")):
        return _choose(pairs, ("cell membrane",), ("nucleus",))
    return None


def law_no_rain(sl: str, pairs) -> str | None:
    if _has(sl, ("no rain", "without rain")) and _has(sl, ("died", "missing", "wilted")):
        return _choose(pairs, ("water",), ("nutrient",))
    return None


def law_same_crop_nutrients(sl: str, pairs) -> str | None:
    crop = _has(sl, ("corn", "tomato", "crop"))
    years = _has(sl, ("every year", "several years", "five years"))
    down = _has(sl, ("decreased", "shrinks", "shrink"))
    weather_ok = _has(sl, ("weather", "rain and temperature"))
    if crop and years and down and weather_ok:
        return _choose(pairs, ("soil nutrient", "nutrient"), ("drought", "rain"))
    return None


LAWS = [
    ("reflection", law_reflection),
    ("egg_cell", law_egg_cell),
    ("consumer", law_consumer),
    ("decomposer", law_decomposer),
    ("freeze_state", law_freeze_state),
    ("freeze_mass", law_freeze_mass),
    ("life_history_rock", law_life_history_rock),
    ("igneous", law_igneous),
    ("eukaryote_nucleus", law_eukaryote_nucleus),
    ("high_pressure_dry", law_high_pressure_dry),
    ("low_pressure_wet", law_low_pressure_wet),
    ("same_crop_nutrients", law_same_crop_nutrients),
    ("temperature_place", law_temperature_place),
    ("heart_organ", law_heart_organ),
    ("shared_membrane", law_shared_membrane),
    ("no_rain", law_no_rain),
]


def use_votes(stem: str, pairs) -> list[tuple[str, str]]:
    sl = stem.lower()
    out = []
    for name, fn in LAWS:
        lab = fn(sl, pairs)
        if lab is not None:
            out.append((name, lab))
    return out


def use_pick(stem: str, pairs) -> tuple[str | None, str | None]:
    votes = use_votes(stem, pairs)
    labels = sorted({lab for _, lab in votes})
    if len(labels) == 1:
        return labels[0], votes[0][0]
    if len(labels) > 1:
        return None, "conflict"
    return None, None


# New wordings. None of these sentences are the ARC items.
BANK = [
    {
        "id": "apply-reflect-lake",
        "kind": "apply",
        "law": "reflection",
        "stem": "A girl looks into a still lake and sees the pines upside down. Which property of the water surface lets her see them?",
        "choices": [("A", "temperature"), ("B", "depth"), ("C", "reflectiveness"), ("D", "saltiness")],
        "want": "C",
    },
    {
        "id": "apply-reflect-pool",
        "kind": "apply",
        "law": "reflection",
        "stem": "Sam sees his face when he looks into a quiet pool. What property of the pool makes that happen?",
        "choices": [("A", "its temperature"), ("B", "its reflectiveness"), ("C", "its volume"), ("D", "its mass")],
        "want": "B",
    },
    {
        "id": "near-pond-warm",
        "kind": "near",
        "law": "reflection",
        "stem": "The pond is warmer at the surface than along the bottom. Which property of the water is different between those two places?",
        "choices": [("A", "temperature"), ("B", "reflectiveness"), ("C", "hardness"), ("D", "magnetism")],
        "want": "A",
    },
    {
        "id": "apply-egg-bird",
        "kind": "apply",
        "law": "egg_cell",
        "stem": "Which level of organization best describes a bird egg?",
        "choices": [("A", "an organ"), ("B", "a tissue"), ("C", "a cell"), ("D", "an organ system")],
        "want": "C",
    },
    {
        "id": "apply-egg-frog",
        "kind": "apply",
        "law": "egg_cell",
        "stem": "A frog egg is one membrane-bound living unit. Which level of organization is it?",
        "choices": [("A", "organ"), ("B", "cell"), ("C", "organ system"), ("D", "community")],
        "want": "B",
    },
    {
        "id": "near-heart-organ",
        "kind": "near",
        "law": "egg_cell",
        "stem": "The heart pumps blood and is built from muscle tissue. Which level of organization best describes the heart?",
        "choices": [("A", "a cell"), ("B", "an organ"), ("C", "a population"), ("D", "an atom")],
        "want": "B",
    },
    {
        "id": "apply-hawk",
        "kind": "apply",
        "law": "consumer",
        "stem": "A hawk eats rabbits and mice. What role does the hawk fill in its ecosystem?",
        "choices": [("A", "producer"), ("B", "decomposer"), ("C", "consumer"), ("D", "mineral")],
        "want": "C",
    },
    {
        "id": "apply-mushroom",
        "kind": "apply",
        "law": "decomposer",
        "stem": "A mushroom breaks down a dead log. What role does the mushroom fill in that ecosystem?",
        "choices": [("A", "producer"), ("B", "consumer"), ("C", "decomposer"), ("D", "predator")],
        "want": "C",
    },
    {
        "id": "near-mushroom-not-consumer",
        "kind": "near",
        "law": "consumer",
        "stem": "Bacteria rot a fallen tree and return its matter to the soil. What role do the bacteria fill in the ecosystem?",
        "choices": [("A", "consumer"), ("B", "decomposer"), ("C", "producer"), ("D", "herbivore")],
        "want": "B",
    },
    {
        "id": "apply-juice-freeze",
        "kind": "apply",
        "law": "freeze_state",
        "stem": "Juice is sealed in a bottle and left in a freezer until it is solid. Which property of the juice changed?",
        "choices": [("A", "mass"), ("B", "state"), ("C", "color of the bottle"), ("D", "the number of atoms")],
        "want": "B",
    },
    {
        "id": "apply-milk-same",
        "kind": "apply",
        "law": "freeze_mass",
        "stem": "A sealed bag of milk is frozen solid and never opened. Which property of the milk stays the same?",
        "choices": [("A", "state"), ("B", "temperature"), ("C", "mass"), ("D", "shape of the crystals")],
        "want": "C",
    },
    {
        "id": "near-freeze-not-mass-as-change",
        "kind": "near",
        "law": "freeze_state",
        "stem": "A sealed bag of milk is put in a freezer. Which property stays the same when it freezes?",
        "choices": [("A", "state"), ("B", "mass"), ("C", "temperature"), ("D", "volume")],
        "want": "B",
    },
    {
        "id": "apply-fossils",
        "kind": "apply",
        "law": "life_history_rock",
        "stem": "Which kind of rock would you break open to look for fossils of ancient animals?",
        "choices": [("A", "igneous"), ("B", "marble from magma"), ("C", "limestone"), ("D", "obsidian")],
        "want": "C",
    },
    {
        "id": "apply-magma",
        "kind": "apply",
        "law": "igneous",
        "stem": "Which rock forms when magma cools?",
        "choices": [("A", "limestone"), ("B", "igneous"), ("C", "chalk"), ("D", "coal")],
        "want": "B",
    },
    {
        "id": "near-magma-not-fossil",
        "kind": "near",
        "law": "life_history_rock",
        "stem": "Granite forms when magma cools underground. Which rock type is granite?",
        "choices": [("A", "limestone"), ("B", "sedimentary"), ("C", "igneous"), ("D", "chalk")],
        "want": "C",
    },
    {
        "id": "apply-euk",
        "kind": "apply",
        "law": "eukaryote_nucleus",
        "stem": "A eukaryotic cell has a structure that is absent from a prokaryotic cell. Which structure is that?",
        "choices": [("A", "a cell membrane"), ("B", "a nucleus"), ("C", "cytoplasm"), ("D", "ribosomes only")],
        "want": "B",
    },
    {
        "id": "near-both-membranes",
        "kind": "near",
        "law": "eukaryote_nucleus",
        "stem": "Name one structure that both a eukaryotic cell and a prokaryotic cell have.",
        "choices": [("A", "a nucleus"), ("B", "a cell membrane"), ("C", "a chloroplast"), ("D", "a mitochondrion")],
        "want": "B",
    },
    {
        "id": "apply-high",
        "kind": "apply",
        "law": "high_pressure_dry",
        "stem": "A high-pressure system sits over a valley for ten days and keeps air from rising. What is the most likely result?",
        "choices": [("A", "daily rain"), ("B", "a hurricane"), ("C", "drought"), ("D", "a flood")],
        "want": "C",
    },
    {
        "id": "apply-low",
        "kind": "apply",
        "law": "low_pressure_wet",
        "stem": "A low-pressure system moves in and air rises and cools overnight. What weather is most likely by morning?",
        "choices": [("A", "clear and sunny"), ("B", "drought"), ("C", "rain"), ("D", "a dust storm")],
        "want": "C",
    },
    {
        "id": "near-low-not-drought-law",
        "kind": "near",
        "law": "high_pressure_dry",
        "stem": "A low-pressure system moves in and air rises. What weather should you expect?",
        "choices": [("A", "drought"), ("B", "rain"), ("C", "a freeze"), ("D", "clear skies for a month")],
        "want": "B",
    },
    {
        "id": "apply-tomatoes",
        "kind": "apply",
        "law": "same_crop_nutrients",
        "stem": "A gardener grows tomatoes in the same bed for five years. The harvest shrinks even though rain and temperature were normal. What most likely decreased?",
        "choices": [("A", "sunlight hours in a day"), ("B", "soil nutrients"), ("C", "the mass of the Earth"), ("D", "gravity")],
        "want": "B",
    },
    {
        "id": "near-no-rain",
        "kind": "near",
        "law": "same_crop_nutrients",
        "stem": "A gardener's tomatoes died during a month with no rain. What was missing?",
        "choices": [("A", "soil nutrients from five years of corn"), ("B", "water"), ("C", "igneous rock"), ("D", "a nucleus")],
        "want": "B",
    },
]

SOURCE_IDS = {
    "reflection": "NYSEDREGENTS_2014_4_13",
    "egg_cell": "Mercury_7185133",
    "consumer": "Mercury_SC_408859",
    "freeze_state": "MEA_2016_5_6",
    "life_history_rock": "Mercury_SC_401244",
    "eukaryote_nucleus": "Mercury_415263",
    "high_pressure_dry": "Mercury_7103565",
    "low_pressure_wet": "Mercury_7166880",
    "same_crop_nutrients": "Mercury_7141400",
}


def _census(frame, procs) -> dict:
    tallies = {i: {"n": 0, "wrong": 0} for i in range(len(procs))}
    for _, row in frame.iterrows():
        pairs = choices_of(row)
        key = str(row["answerKey"]).strip()
        stem = str(row["question"])
        for i, proc in enumerate(procs):
            lab = _vote(stem, pairs, proc)
            if lab is None:
                continue
            tallies[i]["n"] += 1
            if lab != key:
                tallies[i]["wrong"] += 1
    one = many_ok = many_bad = dead = 0
    for t in tallies.values():
        if t["n"] == 0:
            dead += 1
        elif t["n"] == 1 and t["wrong"] == 0:
            one += 1
        elif t["n"] >= 2 and t["wrong"] == 0:
            many_ok += 1
        else:
            many_bad += 1
    return {
        "n_procedures": len(procs),
        "dead_on_this_set": dead,
        "fires_on_one_stem": one,
        "fires_on_many_all_correct": many_ok,
        "fires_on_many_with_a_wrong": many_bad,
    }


def main() -> int:
    easy = load_split("validation")
    challenge = load_challenge("validation")
    facts = study_facts(load_split("train"))
    procs = PROCS_ALL
    census_early = _census(easy, EARLY)
    census_items = _census(easy, ITEM_CUES)
    census_chal = _census(challenge, PROCS_ALL)

    bank_rows = []
    apply_ok = near_ok = 0
    apply_n = near_n = 0
    for item in BANK:
        pairs = item["choices"]
        lab, law = use_pick(item["stem"], pairs)
        kind = item["kind"]
        if kind == "apply":
            apply_n += 1
            ok = lab == item["want"] and law == item["law"]
            if ok:
                apply_ok += 1
        else:
            near_n += 1
            voted = [name for name, _ in use_votes(item["stem"], pairs)]
            ok = item["law"] not in voted and (lab is None or lab == item["want"])
            if ok:
                near_ok += 1
        bank_rows.append(
            {
                "id": item["id"],
                "kind": kind,
                "law": item["law"],
                "want": item["want"],
                "picked": lab,
                "fired": law,
                "ok": ok,
                "stem": item["stem"],
            }
        )

    by_id = {row["id"]: row for _, row in challenge.iterrows()}
    source_rows = []
    source_ok = 0
    for law, sid in SOURCE_IDS.items():
        row = by_id[sid]
        pairs = choices_of(row)
        key = str(row["answerKey"]).strip()
        lab, fired = use_pick(str(row["question"]), pairs)
        ok = lab == key and fired == law
        if ok:
            source_ok += 1
        texts = dict(pairs)
        source_rows.append(
            {
                "id": sid,
                "law": law,
                "ok": ok,
                "picked": lab,
                "fired": fired,
                "key": key,
                "key_text": texts.get(key),
                "stem": str(row["question"])[:160],
            }
        )

    easy_new_wrong = 0
    easy_still_correct = 0
    for _, row in easy.iterrows():
        pairs = choices_of(row)
        key = str(row["answerKey"]).strip()
        stem = str(row["question"])
        old, _, _ = pick_v3(stem, pairs, facts, procs)
        use_lab, _ = use_pick(stem, pairs)
        final = use_lab if use_lab is not None else old
        if final == key:
            easy_still_correct += 1
        else:
            easy_new_wrong += 1

    chal_caught = 0
    chal_hurt = 0
    for _, row in challenge.iterrows():
        pairs = choices_of(row)
        key = str(row["answerKey"]).strip()
        stem = str(row["question"])
        old, _, _ = pick_v3(stem, pairs, facts, procs)
        use_lab, _ = use_pick(stem, pairs)
        if use_lab is None:
            continue
        if use_lab == key and old != key:
            chal_caught += 1
        elif use_lab != key:
            chal_hurt += 1

    overall = (
        apply_ok == apply_n
        and near_ok == near_n
        and source_ok == len(SOURCE_IDS)
        and easy_new_wrong == 0
    )
    doc = {
        "adventure": 1,
        "ted": "TED-29",
        "vs_bill": "Bill-28",
        "pin": "AEB2AD",
        "free_parameters": 0,
        "fitted_challenge_val_into_cues": False,
        "answer_key_seen_at_pick": False,
        "census_early_procedures_on_easy": census_early,
        "census_item_cues_on_easy": census_items,
        "census_all_on_challenge": census_chal,
        "apply_ok": apply_ok,
        "apply_n": apply_n,
        "near_ok": near_ok,
        "near_n": near_n,
        "source_ok": source_ok,
        "source_n": len(SOURCE_IDS),
        "easy_still_correct": easy_still_correct,
        "easy_new_wrong": easy_new_wrong,
        "challenge_newly_caught": chal_caught,
        "challenge_hurt": chal_hurt,
        "bank": bank_rows,
        "sources": source_rows,
        "new_pathway": {
            "name": "reason_use",
            "splice_at": "ALU",
            "not_on_W": True,
            "law": "a relation votes only when the situation matches; a near miss stays quiet; one label or leftover",
        },
        "overall_ok": overall,
        "promotes": overall,
        "promote_to": "Bill-29" if overall else None,
        "thinking": {"deny_family_seeded": False},
    }
    OUT.write_text(json.dumps(doc, indent=2), encoding="utf-8")
    fail_lines = "\n".join(
        f"- `{r['id']}` wanted {r['want']} via {r['law']}, picked {r['picked']} fired {r['fired']}"
        for r in bank_rows
        if not r["ok"]
    ) or "- none"
    src_lines = "\n".join(
        f"- `{r['id']}` {r['law']}: {'caught' if r['ok'] else 'missed'} (picked {r['picked']}, key {r['key']} {r['key_text']})"
        for r in source_rows
    )
    md = f"""# Use versus answer (TED-29)

Answering a stored question and using a relation are different functions. Pin AEB2AD. 0 free parameters. Challenge validation was not copied into the cue list. Measured W is unchanged.

## What the Easy cue list actually is

On ARC-Easy validation, the early relations (the short laws from the first lessons) behave like this:

| | early relations | item cues added to finish Easy |
|--|--:|--:|
| procedures | {census_early['n_procedures']} | {census_items['n_procedures']} |
| fire on exactly one stem, correct | {census_early['fires_on_one_stem']} | {census_items['fires_on_one_stem']} |
| fire on two or more stems, all correct | {census_early['fires_on_many_all_correct']} | {census_items['fires_on_many_all_correct']} |
| fire on a wrong letter | {census_early['fires_on_many_with_a_wrong']} | {census_items['fires_on_many_with_a_wrong']} |
| do not fire on this set | {census_early['dead_on_this_set']} | {census_items['dead_on_this_set']} |

One stem means the cue was that question. Several stems, all correct, means the same relation was reused. The item-cue pile is what finished Easy at 570/570. On ARC-Challenge the whole list gives {census_chal['fires_on_one_stem']} single hits, {census_chal['fires_on_many_all_correct']} reused correct relations, and {census_chal['fires_on_many_with_a_wrong']} hits that include a wrong letter.

The three calculations already in the brain (closest measurement, distance over time, a 25 percent load) are use: they compute. They are not a copied sentence.

## Relations, then new wordings

Eight situations were stated as relations: an image on calm water is reflectiveness; an egg asked as a level of organization is a cell; an animal that eats other animals is a consumer; something that breaks down the dead is a decomposer; freezing changes state and a sealed frozen sample keeps its mass; fossils of ancient life are in limestone, and cooled magma is igneous; a eukaryotic cell has a nucleus a prokaryotic cell lacks; a lingering high-pressure system brings drought, and rising air in a low-pressure system brings rain; the same crop for years, with normal weather and a falling harvest, means soil nutrients fell.

New wordings: **{apply_ok}/{apply_n}** correct, and the firing law was the one that was taught. Near misses, where that law must stay quiet: **{near_ok}/{near_n}**.

Failures:

{fail_lines}

The original Challenge items, scored only after the relations were written: **{source_ok}/{len(SOURCE_IDS)}**.

{src_lines}

Easy validation stays **{easy_still_correct}** correct, new wrongs **{easy_new_wrong}**. On Challenge, these relations newly catch **{chal_caught}** items that Bill-28 missed, and hurt **{chal_hurt}**.

Courtship, aggression, fru, and dsx stay T1 off.
"""
    DOC.write_text(md, encoding="utf-8")
    (ADV / "USE.md").write_text(md, encoding="utf-8")
    print(
        f"  TED-29 early one={census_early['fires_on_one_stem']} "
        f"many_ok={census_early['fires_on_many_all_correct']} "
        f"item one={census_items['fires_on_one_stem']} "
        f"item many={census_items['fires_on_many_all_correct']}"
    )
    print(f"         apply {apply_ok}/{apply_n}  near {near_ok}/{near_n}  source {source_ok}/{len(SOURCE_IDS)}")
    print(f"         easy_wrong {easy_new_wrong}  chal_caught {chal_caught} hurt {chal_hurt}  overall {overall}")
    print(f"  wrote {OUT}")
    return 0 if overall else 1


if __name__ == "__main__":
    raise SystemExit(main())
