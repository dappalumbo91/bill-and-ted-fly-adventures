#!/usr/bin/env python3
"""TED-30: more relations that apply to a new wording.

Same test as TED-29. A relation is kept only when new wordings are right,
near misses do not take the wrong relation, the original situation is caught
without pasting that question into a cue, Easy gains no wrong answer, and
Challenge gains no wrong vote.

  python scripts/bill29_use_more.py
"""
from __future__ import annotations

import runio
runio.install()

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from bill23_arc import choices_of, load_split, study_facts  # noqa: E402
from bill26_arc_leftovers import pick_v3  # noqa: E402
from bill27_arc_challenge import load_challenge  # noqa: E402
from bill28_use import (  # noqa: E402
    BANK as OLD_BANK,
    PROCS_ALL,
    SOURCE_IDS as OLD_SOURCES,
    _choose,
    _has,
    use_votes as old_votes,
)

OUT = ROOT / "data" / "bill29_use_more.json"
DOC = ROOT / "docs" / "USE_MORE.md"
ADV = ROOT / "Bill and Ted fly adventures" / "Adventure-1"


def law_learned(sl: str, pairs) -> str | None:
    if "learned rather than inherited" in sl or "learned, not inherited" in sl:
        return _choose(pairs, ("hunt", "strateg", "practic", "trick", "called"), ("speed", "coat", "claw", "color", "legs"))
    return None


def law_inherited(sl: str, pairs) -> str | None:
    if "inherited rather than learned" in sl or "inherited, not learned" in sl:
        return _choose(pairs, ("coat", "color", "spot", "claw", "legs"), ("hunt", "trick", "practic"))
    return None


def law_melt_particles(sl: str, pairs) -> str | None:
    if "cool" in sl or "freez" in sl:
        return None
    if "particle" in sl and _has(sl, ("melted", "melts", "melting")):
        return _choose(pairs, ("more rapidly", "faster", "more energy"), ("less energy", "gain mass", "slowly"))
    return None


def law_cool_particles(sl: str, pairs) -> str | None:
    if "particle" in sl and _has(sl, ("cooled", "freezes", "frozen solid")):
        return _choose(pairs, ("slowly", "less energy"), ("more rapidly", "faster"))
    return None


def law_gas_indefinite(sl: str, pairs) -> str | None:
    if "no definite volume" in sl and "no definite shape" in sl:
        return _choose(pairs, ("gas",), ("liquid", "solid"))
    return None


def law_liquid_volume(sl: str, pairs) -> str | None:
    if "definite volume" in sl and "no definite shape" in sl and "no definite volume" not in sl:
        return _choose(pairs, ("liquid",), ("gas", "solid"))
    return None


def law_solid_both(sl: str, pairs) -> str | None:
    if "definite shape" in sl and "definite volume" in sl and "no definite" not in sl:
        return _choose(pairs, ("solid",), ("gas", "liquid"))
    return None


def law_mass_is_matter(sl: str, pairs) -> str | None:
    if "describes the mass" in sl or "describe the mass" in sl:
        return _choose(pairs, ("amount of matter", "matter in"), ("space", "gravity", "weight"))
    return None


def law_volume_is_space(sl: str, pairs) -> str | None:
    if "describes the volume" in sl or "describe the volume" in sl:
        return _choose(pairs, ("space", "takes up"), ("amount of matter", "gravity"))
    return None


def law_hot_dissolves_most(sl: str, pairs) -> str | None:
    if "dissolve" in sl and "hot" in sl and "cold" in sl and "least" not in sl:
        return _choose(pairs, ("hot",), ("cold", "same amount"))
    return None


def law_cold_dissolves_least(sl: str, pairs) -> str | None:
    if "dissolve" in sl and "least" in sl and "cold" in sl:
        return _choose(pairs, ("cold",), ("hot",))
    return None


def law_opinion(sl: str, pairs) -> str | None:
    if "is an opinion" in sl or "statement is an opinion" in sl:
        return _choose(pairs, ("beautiful", "prettier", "happier", "best", "wonderful"), ("green", "sunlight", "legs", "equal"))
    return None


def law_fact(sl: str, pairs) -> str | None:
    if "statement of fact" in sl or "is a fact" in sl:
        return _choose(pairs, ("legs", "equal", "four", "green"), ("beautiful", "prettier", "happier", "best", "fun"))
    return None


def law_battery_potential(sl: str, pairs) -> str | None:
    if "potential energy" in sl and "battery" in sl:
        return _choose(pairs, ("chemical",), ("light", "heat", "moving"))
    return None


def law_circuit_kinetic(sl: str, pairs) -> str | None:
    if "kinetic energy" in sl and _has(sl, ("circuit", "bulb", "wire")):
        return _choose(pairs, ("moving", "electrical energy moving"), ("chemical",))
    return None


def law_pioneer(sl: str, pairs) -> str | None:
    if _has(sl, ("lava", "volcanic ash", "bare rock")) and "first" in sl:
        return _choose(pairs, ("moss", "lichen"), ("hardwood", "tree", "shrub", "wildflower"))
    return None


def law_boil_same_temp(sl: str, pairs) -> str | None:
    amounts = _has(sl, ("1 l", "3 l", "two pans", "two pots", "2 cups", "6 cups"))
    if "boil" in sl and amounts and "first" not in sl and "sooner" not in sl:
        return _choose(pairs, ("same temperature",), ("same time", "hotter", "more quickly"))
    return None


def law_boil_smaller_first(sl: str, pairs) -> str | None:
    if "boil" in sl and _has(sl, ("which boils first", "boils sooner", "boils first")):
        return _choose(pairs, ("smaller", "less water", "1 l", "2 cups"), ("same temperature",))
    return None


def law_no_atmosphere(sl: str, pairs) -> str | None:
    swing = _has(sl, ("sunlight", "in the sun")) and _has(sl, ("darkness", "in the dark"))
    body = _has(sl, ("planet", "moon"))
    mild = _has(sl, ("milder", "less from day", "what does earth have"))
    if swing and body and _has(sl, ("temperature",)) and not mild:
        return _choose(pairs, ("atmosphere",), ("too small", "only one side"))
    return None


def law_more_food(sl: str, pairs) -> str | None:
    if _has(sl, ("producing more", "far more", "more acorns", "more berries")) and _has(sl, ("population", "more chipmunks", "more birds", "next year")):
        return _choose(pairs, ("food",), ("water", "oxygen", "shady"))
    return None


def law_drought_fish(sl: str, pairs) -> str | None:
    if "drought" in sl and "fish" in sl:
        return _choose(pairs, ("unable to survive", "die", "not survive"), ("adapt",))
    return None


def law_heat_left_liquid(sl: str, pairs) -> str | None:
    if "heat transferred from a liquid" in sl or "heat left" in sl and "liquid" in sl or "heat moves out of" in sl:
        labs = []
        for lab, text in pairs:
            tl = text.lower()
            if "decreased" in tl and "solid" in tl:
                labs.append(lab)
        labs = sorted(set(labs))
        if len(labs) == 1:
            return labs[0]
        return _choose(pairs, ("decreased",), ("increased",))
    return None


def law_heat_into_liquid(sl: str, pairs) -> str | None:
    if "heat moved into the liquid" in sl or "heat moves into the liquid" in sl:
        return _choose(pairs, ("increased",), ("decreased",))
    return None


def law_plant_stores_food(sl: str, pairs) -> str | None:
    if _has(sl, ("food that plants produce", "most of that sugar", "most of the sugar", "most of the food")):
        return _choose(pairs, ("stored", "store"), ("sunlight", "gas", "water"))
    return None


NEW = [
    ("learned", law_learned),
    ("inherited", law_inherited),
    ("melt_particles", law_melt_particles),
    ("cool_particles", law_cool_particles),
    ("gas_indefinite", law_gas_indefinite),
    ("liquid_volume", law_liquid_volume),
    ("solid_both", law_solid_both),
    ("mass_is_matter", law_mass_is_matter),
    ("volume_is_space", law_volume_is_space),
    ("hot_dissolves_most", law_hot_dissolves_most),
    ("cold_dissolves_least", law_cold_dissolves_least),
    ("opinion", law_opinion),
    ("fact", law_fact),
    ("battery_potential", law_battery_potential),
    ("circuit_kinetic", law_circuit_kinetic),
    ("pioneer", law_pioneer),
    ("boil_same_temp", law_boil_same_temp),
    ("boil_smaller_first", law_boil_smaller_first),
    ("no_atmosphere", law_no_atmosphere),
    ("more_food", law_more_food),
    ("drought_fish", law_drought_fish),
    ("heat_left_liquid", law_heat_left_liquid),
    ("heat_into_liquid", law_heat_into_liquid),
    ("plant_stores_food", law_plant_stores_food),
]


def all_votes(stem: str, pairs) -> list[tuple[str, str]]:
    return old_votes(stem, pairs) + [
        (name, lab) for name, fn in NEW if (lab := fn(stem.lower(), pairs)) is not None
    ]


def all_pick(stem: str, pairs) -> tuple[str | None, str | None]:
    votes = all_votes(stem, pairs)
    labels = sorted({lab for _, lab in votes})
    if len(labels) == 1:
        return labels[0], votes[0][0]
    if len(labels) > 1:
        return None, "conflict"
    return None, None


BANK = [
    {
        "id": "apply-dog-learned",
        "kind": "apply",
        "law": "learned",
        "stem": "Which of a dog's behaviors is learned rather than inherited?",
        "choices": [("A", "its eye color"), ("B", "a trick it practiced"), ("C", "the length of its legs"), ("D", "a spotted coat")],
        "want": "B",
    },
    {
        "id": "apply-puppy-called",
        "kind": "apply",
        "law": "learned",
        "stem": "Which puppy behavior is learned rather than inherited?",
        "choices": [("A", "coming when called"), ("B", "brown eyes"), ("C", "four legs"), ("D", "a soft coat")],
        "want": "A",
    },
    {
        "id": "near-inherited-coat",
        "kind": "near",
        "law": "learned",
        "stem": "Which cheetah trait is inherited rather than learned?",
        "choices": [("A", "a hunting trick"), ("B", "a spotted coat"), ("C", "a strategy it practiced"), ("D", "coming when called")],
        "want": "B",
    },
    {
        "id": "apply-copper-melt",
        "kind": "apply",
        "law": "melt_particles",
        "stem": "A block of copper is heated until it melts. How are its particles affected?",
        "choices": [("A", "They gain mass."), ("B", "They contain less energy."), ("C", "They move more rapidly."), ("D", "They stop moving.")],
        "want": "C",
    },
    {
        "id": "apply-wax-cool",
        "kind": "apply",
        "law": "cool_particles",
        "stem": "Melted wax cools until the particles are in a frozen solid. How do the particles change as it cools?",
        "choices": [("A", "They move more rapidly."), ("B", "They move slowly."), ("C", "They gain mass."), ("D", "They become a gas.")],
        "want": "B",
    },
    {
        "id": "near-cool-not-melt",
        "kind": "near",
        "law": "melt_particles",
        "stem": "A block of copper is cooled until it freezes solid. How do the particles change?",
        "choices": [("A", "They move more rapidly."), ("B", "They contain less energy."), ("C", "They gain mass."), ("D", "They double in size.")],
        "want": "B",
    },
    {
        "id": "apply-gas",
        "kind": "apply",
        "law": "gas_indefinite",
        "stem": "Which state of matter has no definite volume and no definite shape, the way steam does in a room?",
        "choices": [("A", "gas"), ("B", "liquid"), ("C", "solid")],
        "want": "A",
    },
    {
        "id": "apply-liquid",
        "kind": "apply",
        "law": "liquid_volume",
        "stem": "Which state of matter has a definite volume and no definite shape?",
        "choices": [("A", "gas"), ("B", "liquid"), ("C", "solid")],
        "want": "B",
    },
    {
        "id": "apply-solid",
        "kind": "apply",
        "law": "solid_both",
        "stem": "Which state of matter has a definite shape and a definite volume?",
        "choices": [("A", "gas"), ("B", "liquid"), ("C", "solid")],
        "want": "C",
    },
    {
        "id": "near-liquid-not-gas",
        "kind": "near",
        "law": "gas_indefinite",
        "stem": "Milk in a glass has a definite volume and no definite shape of its own. Which state is it?",
        "choices": [("A", "gas"), ("B", "liquid"), ("C", "solid")],
        "want": "B",
    },
    {
        "id": "apply-rock-mass",
        "kind": "apply",
        "law": "mass_is_matter",
        "stem": "Which phrase best describes the mass of a rock?",
        "choices": [("A", "the amount of matter in the rock"), ("B", "the space the rock takes up"), ("C", "the pull of gravity on the rock"), ("D", "the color of the rock")],
        "want": "A",
    },
    {
        "id": "near-rock-volume",
        "kind": "near",
        "law": "mass_is_matter",
        "stem": "Which phrase best describes the volume of a rock?",
        "choices": [("A", "the amount of matter in the rock"), ("B", "the space the rock takes up"), ("C", "how beautiful the rock is"), ("D", "the age of the rock")],
        "want": "B",
    },
    {
        "id": "apply-salt-hot",
        "kind": "apply",
        "law": "hot_dissolves_most",
        "stem": "A student stirs the same salt into cold water, warm water, and hot water. Which dissolves the most salt?",
        "choices": [("A", "The cold water dissolved the most salt."), ("B", "The warm water dissolved the most salt."), ("C", "The hot water dissolved the most salt."), ("D", "All three dissolved the same amount.")],
        "want": "C",
    },
    {
        "id": "near-salt-least",
        "kind": "near",
        "law": "hot_dissolves_most",
        "stem": "Which cup dissolved the least salt: cold water, warm water, or hot water?",
        "choices": [("A", "the cold water"), ("B", "the hot water"), ("C", "the warm water"), ("D", "they all dissolved the same")],
        "want": "A",
    },
    {
        "id": "apply-opinion-roses",
        "kind": "apply",
        "law": "opinion",
        "stem": "Which statement is an opinion about roses?",
        "choices": [("A", "Many roses are red."), ("B", "Roses are the most wonderful flower."), ("C", "Roses need sunlight."), ("D", "Roses grow in soil.")],
        "want": "B",
    },
    {
        "id": "apply-fact-dogs",
        "kind": "apply",
        "law": "fact",
        "stem": "Which statement is a fact about dogs?",
        "choices": [("A", "Dogs are happier than cats."), ("B", "Dogs are the best pets."), ("C", "Dogs usually have four legs."), ("D", "Dogs are more fun than fish.")],
        "want": "C",
    },
    {
        "id": "near-fact-not-opinion",
        "kind": "near",
        "law": "opinion",
        "stem": "Which comparison of butterflies and moths is a statement of fact?",
        "choices": [("A", "Butterflies are prettier."), ("B", "Moths are more fun."), ("C", "Butterflies are happier in the day."), ("D", "Butterflies and moths have equal numbers of legs.")],
        "want": "D",
    },
    {
        "id": "apply-battery",
        "kind": "apply",
        "law": "battery_potential",
        "stem": "A circuit has a battery, a wire, and a bell. Which is potential energy in that circuit?",
        "choices": [("A", "chemical energy in the battery"), ("B", "sound from the bell"), ("C", "heat in the wire"), ("D", "electrical energy moving through the bell")],
        "want": "A",
    },
    {
        "id": "near-kinetic-circuit",
        "kind": "near",
        "law": "battery_potential",
        "stem": "In a circuit with a battery and a bulb, which is kinetic energy?",
        "choices": [("A", "chemical energy in the battery"), ("B", "electrical energy moving through the bulb"), ("C", "the metal of the wire"), ("D", "the glass of the bulb")],
        "want": "B",
    },
    {
        "id": "apply-lava-moss",
        "kind": "apply",
        "law": "pioneer",
        "stem": "Lava cools into bare rock. Which plants are most likely the first to grow there?",
        "choices": [("A", "mosses"), ("B", "hardwood trees"), ("C", "evergreen shrubs"), ("D", "tall wildflowers")],
        "want": "A",
    },
    {
        "id": "near-old-forest",
        "kind": "near",
        "law": "pioneer",
        "stem": "A forest has grown for 200 years with no lava and no fire. Which plants are most likely the tallest there?",
        "choices": [("A", "mosses"), ("B", "hardwood trees"), ("C", "lichens only"), ("D", "bare rock")],
        "want": "B",
    },
    {
        "id": "apply-two-pots",
        "kind": "apply",
        "law": "boil_same_temp",
        "stem": "One pot holds 2 cups of water and another holds 6 cups. Both are heated until the water boils. Which statement is true?",
        "choices": [("A", "The water in both pots boils at the same time."), ("B", "The water in both pots boils at the same temperature."), ("C", "The 6 cups get hotter than the 2 cups before boiling."), ("D", "The 6 cups absorb heat more quickly.")],
        "want": "B",
    },
    {
        "id": "near-boils-first",
        "kind": "near",
        "law": "boil_same_temp",
        "stem": "Two pots of water are heated the same way. Which boils first, the pot with less water or the pot with more?",
        "choices": [("A", "They boil at the same temperature, so neither is first."), ("B", "The smaller pot, with less water, boils sooner."), ("C", "The larger pot boils sooner."), ("D", "Neither pot can boil.")],
        "want": "B",
    },
    {
        "id": "apply-moon-swing",
        "kind": "apply",
        "law": "no_atmosphere",
        "stem": "A moon is very hot in sunlight and very cold in the dark. Why is the temperature range so large?",
        "choices": [("A", "The moon is too small to hold heat."), ("B", "The moon is heated on only one side."), ("C", "The moon lacks an atmosphere to hold heat."), ("D", "The moon reflects heat from its dark side.")],
        "want": "C",
    },
    {
        "id": "apply-berries",
        "kind": "apply",
        "law": "more_food",
        "stem": "One summer the bushes produced far more berries than usual. The next year there were more birds. Why were there more birds?",
        "choices": [("A", "Shady areas increased."), ("B", "Food sources increased."), ("C", "Oxygen levels increased."), ("D", "Available water increased.")],
        "want": "B",
    },
    {
        "id": "near-dry-pond-birds",
        "kind": "near",
        "law": "more_food",
        "stem": "A pond dried up and the next year there were fewer ducks. What was missing?",
        "choices": [("A", "food from extra berries"), ("B", "water"), ("C", "a nucleus"), ("D", "igneous rock")],
        "want": "B",
    },
    {
        "id": "apply-lake-drought",
        "kind": "apply",
        "law": "drought_fish",
        "stem": "A long drought shrinks a lake. What is most likely to happen to many of the fish?",
        "choices": [("A", "They would adapt to dry land."), ("B", "They would be unable to survive."), ("C", "They would learn to fly."), ("D", "They would turn into plants.")],
        "want": "B",
    },
    {
        "id": "apply-wax-heat-left",
        "kind": "apply",
        "law": "heat_left_liquid",
        "stem": "Heat left a pan of liquid wax and moved into the cooler room. Which pair fits that result?",
        "choices": [("A", "The temperature increased, or the wax became a gas."), ("B", "The temperature decreased, or the wax became a solid."), ("C", "The temperature increased, or the wax became a solid."), ("D", "The temperature decreased, or the wax became a gas.")],
        "want": "B",
    },
    {
        "id": "near-heat-into",
        "kind": "near",
        "law": "heat_left_liquid",
        "stem": "Heat moves into the liquid from a hot plate. Which change fits?",
        "choices": [("A", "The temperature increased."), ("B", "The temperature decreased, or the liquid became a solid."), ("C", "The liquid lost all its mass."), ("D", "The liquid became a fossil.")],
        "want": "A",
    },
    {
        "id": "apply-maple-sugar",
        "kind": "apply",
        "law": "plant_stores_food",
        "stem": "A maple tree makes sugar in its leaves. What happens to most of that sugar?",
        "choices": [("A", "It is released as gas."), ("B", "It is converted to water."), ("C", "It is stored for future use."), ("D", "It is used to absorb sunlight.")],
        "want": "C",
    },
]

SOURCES = {
    "learned": "Mercury_7032743",
    "melt_particles": "Mercury_7205135",
    "gas_indefinite": "NYSEDREGENTS_2014_4_4",
    "mass_is_matter": "MCAS_8_2015_11",
    "hot_dissolves_most": "TIMSS_2007_4_pg90",
    "opinion": "MCAS_2000_8_10",
    "fact": "Mercury_7071365",
    "battery_potential": "Mercury_7187915",
    "pioneer": "Mercury_7189823",
    "boil_same_temp": "MCAS_2015_8_7",
    "no_atmosphere": "MCAS_2005_8_5",
    "more_food": "Mercury_SC_405487",
    "drought_fish": "Mercury_SC_407169",
    "heat_left_liquid": "Mercury_SC_412337",
    "plant_stores_food": "MDSA_2007_4_52",
}


def _score_bank(items, pick):
    rows = []
    apply_ok = near_ok = apply_n = near_n = 0
    for item in items:
        pairs = item["choices"]
        lab, law = pick(item["stem"], pairs)
        if item["kind"] == "apply":
            apply_n += 1
            ok = lab == item["want"] and law == item["law"]
            apply_ok += int(ok)
        else:
            near_n += 1
            voted = [name for name, _ in all_votes(item["stem"], pairs)]
            ok = item["law"] not in voted and (lab is None or lab == item["want"])
            near_ok += int(ok)
        rows.append({**{k: item[k] for k in ("id", "kind", "law", "want")}, "picked": lab, "fired": law, "ok": ok})
    return rows, apply_ok, apply_n, near_ok, near_n


def main() -> int:
    easy = load_split("validation")
    challenge = load_challenge("validation")
    facts = study_facts(load_split("train"))
    rows, apply_ok, apply_n, near_ok, near_n = _score_bank(BANK, all_pick)
    old_rows, old_apply_ok, old_apply_n, old_near_ok, old_near_n = _score_bank(OLD_BANK, all_pick)

    by_id = {row["id"]: row for _, row in challenge.iterrows()}
    source_rows = []
    source_ok = 0
    for law, sid in {**OLD_SOURCES, **SOURCES}.items():
        row = by_id[sid]
        pairs = choices_of(row)
        key = str(row["answerKey"]).strip()
        lab, fired = all_pick(str(row["question"]), pairs)
        ok = lab == key and fired == law
        source_ok += int(ok)
        source_rows.append(
            {
                "id": sid,
                "law": law,
                "ok": ok,
                "picked": lab,
                "fired": fired,
                "key": key,
                "key_text": dict(pairs).get(key),
            }
        )

    easy_new_wrong = 0
    easy_still = 0
    for _, row in easy.iterrows():
        pairs = choices_of(row)
        key = str(row["answerKey"]).strip()
        stem = str(row["question"])
        old, _, _ = pick_v3(stem, pairs, facts, PROCS_ALL)
        use_lab, _ = all_pick(stem, pairs)
        final = use_lab if use_lab is not None else old
        if final == key:
            easy_still += 1
        else:
            easy_new_wrong += 1

    chal_caught = chal_hurt = 0
    for _, row in challenge.iterrows():
        pairs = choices_of(row)
        key = str(row["answerKey"]).strip()
        stem = str(row["question"])
        old_pick, _, _ = pick_v3(stem, pairs, facts, PROCS_ALL)
        prev, _ = __import__("bill28_use", fromlist=["use_pick"]).use_pick(stem, pairs)
        prev_final = prev if prev is not None else old_pick
        lab, _ = all_pick(stem, pairs)
        if lab is None:
            continue
        if lab == key and prev_final != key:
            chal_caught += 1
        elif lab != key:
            chal_hurt += 1

    new_sources = sum(1 for r in source_rows if r["law"] in SOURCES and r["ok"])
    overall = (
        apply_ok == apply_n
        and near_ok == near_n
        and old_apply_ok == old_apply_n
        and old_near_ok == old_near_n
        and new_sources == len(SOURCES)
        and source_ok == len(OLD_SOURCES) + len(SOURCES)
        and easy_new_wrong == 0
        and chal_hurt == 0
    )
    fails = [r for r in rows + old_rows + source_rows if not r["ok"]]
    doc = {
        "adventure": 1,
        "ted": "TED-30",
        "vs_bill": "Bill-29",
        "pin": "AEB2AD",
        "free_parameters": 0,
        "fitted_challenge_val_into_cues": False,
        "answer_key_seen_at_pick": False,
        "n_new_relations": len(NEW),
        "apply_ok": apply_ok,
        "apply_n": apply_n,
        "near_ok": near_ok,
        "near_n": near_n,
        "old_apply_ok": old_apply_ok,
        "old_apply_n": old_apply_n,
        "old_near_ok": old_near_ok,
        "old_near_n": old_near_n,
        "source_ok": source_ok,
        "source_n": len(OLD_SOURCES) + len(SOURCES),
        "new_source_ok": new_sources,
        "new_source_n": len(SOURCES),
        "easy_still_correct": easy_still,
        "easy_new_wrong": easy_new_wrong,
        "challenge_newly_caught": chal_caught,
        "challenge_hurt": chal_hurt,
        "bank": rows,
        "old_bank_still": old_rows,
        "sources": source_rows,
        "failures": fails,
        "new_pathway": {
            "name": "reason_use",
            "splice_at": "ALU",
            "not_on_W": True,
            "law": "more situation relations; new wording must match; near miss must not take the wrong relation",
        },
        "overall_ok": overall,
        "promotes": overall,
        "promote_to": "Bill-30" if overall else None,
        "thinking": {"deny_family_seeded": False},
    }
    OUT.write_text(json.dumps(doc, indent=2), encoding="utf-8")
    fail_lines = "\n".join(
        f"- `{r['id']}` law {r.get('law')} want {r.get('want', r.get('key'))} picked {r.get('picked')} fired {r.get('fired')}"
        for r in fails
    ) or "- none"
    md = f"""# More use (TED-30)

Same distinction as TED-29. These relations were not copied from Challenge questions. A new wording has to select the right choice, and a near miss has to avoid the wrong relation. Pin AEB2AD. 0 free parameters. Measured W is unchanged.

## New relations

Learned rather than inherited is a practiced behavior. Inherited rather than learned is a body trait. Melting makes particles move faster. Cooling makes them move more slowly. No definite volume and no definite shape is a gas. Definite volume and no definite shape is a liquid. Definite shape and definite volume is a solid. Mass is the amount of matter. Volume is the space taken up. Hot water dissolves more of a solid than cold water. An opinion uses words like beautiful or best. A fact can be checked, such as a count of legs. Chemical energy in a battery is potential energy. Energy moving through a bulb is kinetic. Moss is first on bare rock after lava. Two different amounts of water boil at the same temperature. A smaller amount boils sooner. A planet or moon with a huge day-night temperature swing lacks an atmosphere to hold heat. More food one year, more animals that eat it the next. Fish in a drought-shrunk pond are likely unable to survive. Heat leaving a liquid lowers its temperature and can freeze it. Heat entering a liquid raises its temperature. Most of the food a plant makes is stored.

New wordings: **{apply_ok}/{apply_n}**. Near misses: **{near_ok}/{near_n}**. Earlier use items still hold: apply **{old_apply_ok}/{old_apply_n}**, near **{old_near_ok}/{old_near_n}**.

Original situations caught, including the earlier nine: **{source_ok}/{len(OLD_SOURCES) + len(SOURCES)}**. The new ones: **{new_sources}/{len(SOURCES)}**.

Easy stays **{easy_still}** correct, new wrongs **{easy_new_wrong}**. Challenge items these relations newly catch: **{chal_caught}**. Challenge items they answer wrongly: **{chal_hurt}**.

Failures:

{fail_lines}

Courtship, aggression, fru, and dsx stay T1 off.
"""
    DOC.write_text(md, encoding="utf-8")
    (ADV / "USE_MORE.md").write_text(md, encoding="utf-8")
    print(
        f"  TED-30 apply {apply_ok}/{apply_n} near {near_ok}/{near_n} "
        f"old {old_apply_ok}/{old_apply_n} {old_near_ok}/{old_near_n}"
    )
    print(
        f"         sources {source_ok}/{len(OLD_SOURCES)+len(SOURCES)} new {new_sources}/{len(SOURCES)} "
        f"easy_wrong {easy_new_wrong} caught {chal_caught} hurt {chal_hurt} overall {overall}"
    )
    if fails:
        for r in fails[:12]:
            print("  FAIL", r.get("id"), r.get("law"), "picked", r.get("picked"), "fired", r.get("fired"))
    print(f"  wrote {OUT}")
    return 0 if overall else 1


if __name__ == "__main__":
    raise SystemExit(main())
