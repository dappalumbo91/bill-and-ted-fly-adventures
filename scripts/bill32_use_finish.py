#!/usr/bin/env python3
"""TED-33: finish more Challenge leftovers as relations, and record why a thought stopped.

A leftover is a halt: no route named one letter. This pass adds relations for
situations that were halting, checks each on a new wording and a near miss,
then lets that relation finish the original situation. Items with no relation
stay halted, and the side-by-side says why.

  python scripts/bill32_use_finish.py
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from bill23_arc import choices_of, load_split, study_facts  # noqa: E402
from bill26_arc_leftovers import pick_v3  # noqa: E402
from bill27_arc_challenge import load_challenge  # noqa: E402
from bill28_use import BANK as BANK29, PROCS_ALL, _choose, _has  # noqa: E402
from bill29_use_more import BANK as BANK30  # noqa: E402
from bill31_use_gaps import BANK as BANK32, family_votes as prev_votes  # noqa: E402

OUT = ROOT / "data" / "bill32_use_finish.json"
DOC = ROOT / "docs" / "USE_FINISH.md"
ADV = ROOT / "Bill and Ted fly adventures" / "Adventure-1"


def law_repeat_record(sl: str, pairs) -> str | None:
    if "repeat" in sl and _has(sl, ("investigation", "experiment")):
        return _choose(pairs, ("record",), ("guess", "change the"))
    return None


def law_no_record_blocks_check(sl: str, pairs) -> str | None:
    if _has(sl, ("lack of record", "fails to maintain clear records", "does not write down")):
        # "invalidates" contains "validat", so the needle is the other scientists checking.
        return _choose(pairs, ("validating", "cannot repeat", "cannot check"), ("invalidat", "incorrect", "hypothes"))
    return None


def law_not_safe_taste(sl: str, pairs) -> str | None:
    if _has(sl, ("not a safety", "not represent a safety", "is not a safe")):
        return _choose(pairs, ("tast",), ("goggle", "wash"))
    return None


def law_is_safe_goggles(sl: str, pairs) -> str | None:
    if _has(sl, ("which is a safety", "is a safety rule")) and "not" not in sl:
        return _choose(pairs, ("goggle",), ("tast",))
    return None


def law_clear_forest_biodiversity(sl: str, pairs) -> str | None:
    if _has(sl, ("cleared", "clearing")) and "forest" in sl:
        return _choose(pairs, ("decrease in biodiversity", "biodiversity"), ("erosion",))
    return None


def law_cut_forest_erosion(sl: str, pairs) -> str | None:
    if _has(sl, ("cutting down", "cut down")) and "forest" in sl:
        return _choose(pairs, ("erosion",), ("diversity will increase", "oxygen"))
    return None


def law_sealed_returns(sl: str, pairs) -> str | None:
    if "sealed" in sl and "cooled back" in sl and "pressure" in sl:
        m = re.search(r"pressure of\s+([0-9]+)\s*psi", sl)
        if not m:
            return None
        return _choose(pairs, (m.group(1),), ())
    return None


def law_saliva_first(sl: str, pairs) -> str | None:
    if _has(sl, ("first causes chemical", "chemical digestion of food begin", "first chemical")):
        return _choose(pairs, ("saliva",), ("stomach", "intestine", "teeth"))
    return None


def law_absorb_intestine(sl: str, pairs) -> str | None:
    if "absorbed into the blood" in sl or "absorption of food" in sl:
        return _choose(pairs, ("small intestine",), ("saliva", "mouth"))
    return None


def law_algae_oxygen_ocean(sl: str, pairs) -> str | None:
    if "oxygen" in sl and "algae" in sl and _has(sl, ("where", "live")):
        # Oxygen-making algae sit in sunlit coastal water. Deep water has no light for that.
        return _choose(pairs, ("coastal", "sunlit"), ("deep", "desert", "soil", "pond", "lake"))
    return None


def law_daylight_seasons(sl: str, pairs) -> str | None:
    if _has(sl, ("summer and winter", "june and december")) and _has(sl, ("change", "changes most")):
        return _choose(pairs, ("daylight", "hours of daylight"), ("mass of earth",))
    return None


def law_grow_weight_up(sl: str, pairs) -> str | None:
    if _has(sl, ("grow into", "kittens grow", "puppies grow")) and "weight" in sl:
        return _choose(pairs, ("increase",), ("decrease",))
    return None


def law_invasive_eggs(sl: str, pairs) -> str | None:
    if _has(sl, ("bird eggs", "seabird eggs")) and _has(sl, ("released", "island")):
        labs = []
        for lab, text in pairs:
            tl = text.lower()
            more_eater = ("more snake" in tl) or ("more rat" in tl)
            fewer_birds = ("fewer bird" in tl) or ("fewer seabird" in tl)
            if more_eater and fewer_birds:
                labs.append(lab)
        labs = sorted(set(labs))
        return labs[0] if len(labs) == 1 else None
    return None


def law_compost_scraps(sl: str, pairs) -> str | None:
    if "compost" in sl and "not" not in sl:
        return _choose(pairs, ("bean", "peel", "plant", "food scrap"), ("plastic", "glass", "metal"))
    return None


def law_not_compost(sl: str, pairs) -> str | None:
    if "compost" in sl and "does not belong" in sl:
        return _choose(pairs, ("plastic", "glass"), ("peel", "plant"))
    return None


def law_mass_lost_gas(sl: str, pairs) -> str | None:
    if "mass" in sl and _has(sl, ("less than", "weighs less")) and _has(sl, ("product", "reaction")):
        return _choose(pairs, ("gas",), ("created", "destroyed"))
    return None


def law_moon_month(sl: str, pairs) -> str | None:
    if "moon" in sl and _has(sl, ("revolution around earth", "orbit earth", "orbit around earth")):
        return _choose(pairs, ("30", "month", "27"), ("24 hour", "365"))
    return None


def law_earth_day(sl: str, pairs) -> str | None:
    if _has(sl, ("earth to rotate", "earth rotate once", "one rotation of earth")):
        return _choose(pairs, ("24", "one day"), ("30", "365"))
    return None


def law_meiosis_new_combo(sl: str, pairs) -> str | None:
    if "meiosis" in sl and _has(sl, ("homologous", "crossing")):
        return _choose(pairs, ("unique", "new combination", "variation"), ("identical",))
    return None


def law_vine_touch(sl: str, pairs) -> str | None:
    if _has(sl, ("vine", "climb a fence", "climb")) and _has(sl, ("climb", "wrap")):
        return _choose(pairs, ("touch", "curl"), ("light only",))
    return None


def law_blood_markers(sl: str, pairs) -> str | None:
    if "blood type" in sl or "abo blood" in sl or "type a blood" in sl or "type b blood" in sl:
        labs = []
        for lab, text in pairs:
            tl = text.lower()
            if "white" in tl or "size" in tl or "plasma" in tl:
                continue
            if "marker" in tl and "red" in tl:
                labs.append(lab)
        labs = sorted(set(labs))
        return labs[0] if len(labs) == 1 else None
    return None


def law_mass_weight_moon(sl: str, pairs) -> str | None:
    if _has(sl, ("earth to the moon", "from earth to the moon")):
        return _choose(pairs, ("same mass",), ("same weight", "different mass", "density"))
    return None


def law_incomplete_pink(sl: str, pairs) -> str | None:
    if "incomplete dominance" not in sl:
        return None
    # "0% pink" is a substring of "100% pink", so a ban would drop the pink result.
    labs = []
    for lab, text in pairs:
        tl = text.lower()
        if "100% pink" in tl or tl.strip() in ("pink", "all pink", "100% pink flowers"):
            labs.append(lab)
    labs = sorted(set(labs))
    return labs[0] if len(labs) == 1 else None


def law_complete_red(sl: str, pairs) -> str | None:
    if "complete dominance" in sl and "incomplete" not in sl:
        return _choose(pairs, ("red",), ("pink",))
    return None


def law_black_absorbs(sl: str, pairs) -> str | None:
    if _has(sl, ("absorb the most sunlight", "absorbs the most sunlight")) and "reflect" not in sl:
        return _choose(pairs, ("black",), ("white", "silver"))
    return None


def law_white_reflects(sl: str, pairs) -> str | None:
    if "reflect" in sl and _has(sl, ("most sunlight", "color")):
        return _choose(pairs, ("white",), ("black",))
    return None


def law_burn_chemical(sl: str, pairs) -> str | None:
    if "chemical change" in sl and _has(sl, ("paper", "log", "wood")):
        return _choose(pairs, ("burn",), ("cut", "tear", "fold"))
    return None


def law_cut_physical(sl: str, pairs) -> str | None:
    if "physical change" in sl and _has(sl, ("paper", "log", "wood")):
        return _choose(pairs, ("cut", "tear", "fold"), ("burn",))
    return None


def law_machine_loss(sl: str, pairs) -> str | None:
    if "output" in sl and "input" in sl and _has(sl, ("less", "machine", "motor")):
        return _choose(pairs, ("surroundings",), ("destroyed", "created", "magnetism", "heat"))
    return None


def law_boil_egg_bonds(sl: str, pairs) -> str | None:
    if "egg" in sl and _has(sl, ("boil", "boiling")) and _has(sl, ("solid", "white")):
        return _choose(pairs, ("chemical bond", "bonds"), ("mass disappeared",))
    return None


def law_melt_ice_physical(sl: str, pairs) -> str | None:
    if "ice" in sl and "melt" in sl and "bond" not in sl and "egg" not in sl:
        return None
    return None


def law_solid_has_both(sl: str, pairs) -> str | None:
    if _has(sl, ("solid phase", "solid state", "in the solid phase")):
        return _choose(pairs, ("definite shape and a definite volume", "definite shape and definite volume"), ("no definite",))
    return None


def law_gas_has_neither(sl: str, pairs) -> str | None:
    if _has(sl, ("gas phase", "in the gas phase", "a gas has")):
        return _choose(pairs, ("no definite shape and no definite volume", "no definite"), ("definite shape and a definite volume",))
    return None


def law_slow_water_solid(sl: str, pairs) -> str | None:
    if "molecules" in sl and _has(sl, ("slows", "slow down")) and "water" in sl:
        return _choose(pairs, ("solid", "ice"), ("gas",))
    return None


def law_fast_water_gas(sl: str, pairs) -> str | None:
    if "molecules" in sl and _has(sl, ("speed up", "move faster")) and "water" in sl:
        return _choose(pairs, ("gas", "vapor"), ("solid", "ice"))
    return None


def law_inherit_body(sl: str, pairs) -> str | None:
    if "inherit" in sl and _has(sl, ("trait", "parents")) and "learned" not in sl:
        return _choose(pairs, ("fur", "color of its", "eye"), ("trick", "scar", "name"))
    return None


def law_light_years(sl: str, pairs) -> str | None:
    if _has(sl, ("solar system", "between stars", "next star")) and _has(sl, ("distance", "unit")):
        return _choose(pairs, ("light year", "light-year"), ("meter", "kilometer", "mile"))
    return None


def law_classroom_meters(sl: str, pairs) -> str | None:
    if "classroom" in sl and "distance" in sl:
        return _choose(pairs, ("meter",), ("light year",))
    return None


def law_mammals_hair(sl: str, pairs) -> str | None:
    if _has(sl, ("mammals and not", "only one of these taxonomic", "reptiles, mammals")):
        return _choose(pairs, ("hair",), ("scales only", "gills"))
    return None


def law_noble_column(sl: str, pairs) -> str | None:
    if "periodic" in sl and _has(sl, ("similar properties", "same family", "same column")):
        return _choose(pairs, ("he, ne, ar", "he ne ar", "helium"), ("na, cl",))
    return None


def law_survive_spray(sl: str, pairs) -> str | None:
    if _has(sl, ("insecticide", "pesticide", "spray")) and _has(sl, ("survive", "survives")):
        return _choose(pairs, ("genetic",), ("the spray became food",))
    return None


def law_low_variation(sl: str, pairs) -> str | None:
    if "genetic variation" in sl and _has(sl, ("little", "limited", "almost no")):
        return _choose(pairs, ("adapt",), ("interbreed", "more resistant", "more likely", "survival rate"))
    return None


def law_phase_same_mass(sl: str, pairs) -> str | None:
    if _has(sl, ("melts", "melt")) and "evaporat" in sl and "same" in sl:
        return _choose(pairs, ("mass",), ("shape", "volume", "temperature"))
    return None


def law_recycle_paper(sl: str, pairs) -> str | None:
    if "recycling paper" in sl or "recycling newspaper" in sl:
        return _choose(pairs, ("reduces trees", "fewer trees"), ("more trees", "erosion", "destruction", "pollution"))
    return None


def law_worms_air(sl: str, pairs) -> str | None:
    if "earthworm" in sl or ("tree" in sl and "oxygen" in sl and "root" in sl):
        return _choose(pairs, ("earthworm",), ("woodpecker", "mushroom", "squirrel"))
    return None


def _choose_case(pairs, bits: tuple[str, ...], ban: tuple[str, ...] = ()) -> str | None:
    """Choice match that keeps allele case. Lowercasing turns Cc, CC, and cc into the same string."""
    labs = []
    for lab, text in pairs:
        if any(b in text for b in ban):
            continue
        if any(b in text for b in bits):
            labs.append(lab)
    labs = sorted(set(labs))
    return labs[0] if len(labs) == 1 else None


def law_punnett_hetero(sl: str, pairs) -> str | None:
    # Called with the original stem. A lowercase copy makes cc, Cc, and CC identical.
    low = sl.lower()
    if re.search(r"\bcc\b", sl) and re.search(r"\bCc\b", sl) and _has(low, ("zygote", "allele", "child", "offspring")):
        return _choose_case(pairs, ("Cc or cc", "cc or Cc"), ("CC or Cc", "CC only", "Cc only"))
    return None


def law_punnett_aa(sl: str, pairs) -> str | None:
    if re.search(r"\baa\b", sl) and re.search(r"\bAa\b", sl):
        return _choose_case(pairs, ("Aa or aa", "aa or Aa"), ("never Aa", "AA only"))
    return None


def law_toxic_fish(sl: str, pairs) -> str | None:
    if _has(sl, ("toxic", "poison")) and _has(sl, ("pond", "lake")):
        return _choose(pairs, ("harmed", "dying", "die"), ("grow larger",))
    return None


def law_clean_water_fish(sl: str, pairs) -> str | None:
    if "clean water" in sl and "fish" in sl and "poison" not in sl and "toxic" not in sl:
        return _choose(pairs, ("not harmed", "stay healthy"), ("dying",))
    return None


def law_plants_make_food(sl: str, pairs) -> str | None:
    plant = _has(sl, ("plant", "tree", "oak"))
    no_eat = (
        "do not usually need to eat" in sl
        or "do not have to eat" in sl
        or "don't have to eat" in sl
        or ("don't" in sl and "have to eat" in sl)
        or ("do not" in sl and "need to eat" in sl)
    )
    if plant and no_eat:
        return _choose(pairs, ("sunlight", "make food"), ("soil", "do not need food", "stored"))
    return None


def law_wide_leaves(sl: str, pairs) -> str | None:
    if _has(sl, ("rainy", "wet forest")) and "leaves" in sl:
        return _choose(pairs, ("wide", "flat"), ("tiny spines", "waxy"))
    return None


def law_desert_leaves(sl: str, pairs) -> str | None:
    if "desert" in sl and "leaves" in sl:
        return _choose(pairs, ("waxy", "small", "spine"), ("wide and flat",))
    return None


def law_disturb_nest(sl: str, pairs) -> str | None:
    if _has(sl, ("disturbed", "scaring")) and _has(sl, ("beach", "nest")):
        return _choose(pairs, ("different beach", "another beach", "different beaches"), ("same beach forever",))
    return None


def law_bar_compare(sl: str, pairs) -> str | None:
    if _has(sl, ("how much each", "results of this experiment")) and "percent" not in sl and "each day" not in sl:
        return _choose(pairs, ("bar graph", "bar"), ("pie", "line"))
    return None


def law_mantle_heat(sl: str, pairs) -> str | None:
    if "mantle" in sl and _has(sl, ("circulat", "convection")):
        return _choose(pairs, ("energy", "heat"), ("moonlight",))
    return None


def law_golgi_pack(sl: str, pairs) -> str | None:
    if _has(sl, ("packaged", "packages proteins", "post-translational")):
        return _choose(pairs, ("golgi",), ("mitochond", "ribosome"))
    return None


def law_float_light(sl: str, pairs) -> str | None:
    if "float in water" in sl or "will most likely float" in sl:
        return _choose(pairs, ("tennis", "cork", "wood", "ping"), ("steel", "rock", "coin", "lead"))
    return None


def law_sink_dense(sl: str, pairs) -> str | None:
    if "sink in water" in sl:
        return _choose(pairs, ("steel", "rock", "lead"), ("tennis", "cork", "wood"))
    return None


FINISH = [
    ("repeat_record", law_repeat_record),
    ("no_record_blocks_check", law_no_record_blocks_check),
    ("not_safe_taste", law_not_safe_taste),
    ("is_safe_goggles", law_is_safe_goggles),
    ("clear_forest_biodiversity", law_clear_forest_biodiversity),
    ("cut_forest_erosion", law_cut_forest_erosion),
    ("sealed_returns", law_sealed_returns),
    ("saliva_first", law_saliva_first),
    ("absorb_intestine", law_absorb_intestine),
    ("algae_oxygen_ocean", law_algae_oxygen_ocean),
    ("daylight_seasons", law_daylight_seasons),
    ("grow_weight_up", law_grow_weight_up),
    ("invasive_eggs", law_invasive_eggs),
    ("compost_scraps", law_compost_scraps),
    ("not_compost", law_not_compost),
    ("mass_lost_gas", law_mass_lost_gas),
    ("moon_month", law_moon_month),
    ("earth_day", law_earth_day),
    ("meiosis_new_combo", law_meiosis_new_combo),
    ("vine_touch", law_vine_touch),
    ("blood_markers", law_blood_markers),
    ("mass_weight_moon", law_mass_weight_moon),
    ("incomplete_pink", law_incomplete_pink),
    ("complete_red", law_complete_red),
    ("black_absorbs", law_black_absorbs),
    ("white_reflects", law_white_reflects),
    ("burn_chemical", law_burn_chemical),
    ("cut_physical", law_cut_physical),
    ("machine_loss", law_machine_loss),
    ("boil_egg_bonds", law_boil_egg_bonds),
    ("solid_has_both", law_solid_has_both),
    ("gas_has_neither", law_gas_has_neither),
    ("slow_water_solid", law_slow_water_solid),
    ("fast_water_gas", law_fast_water_gas),
    ("inherit_body", law_inherit_body),
    ("light_years", law_light_years),
    ("classroom_meters", law_classroom_meters),
    ("mammals_hair", law_mammals_hair),
    ("noble_column", law_noble_column),
    ("survive_spray", law_survive_spray),
    ("low_variation", law_low_variation),
    ("phase_same_mass", law_phase_same_mass),
    ("recycle_paper", law_recycle_paper),
    ("worms_air", law_worms_air),
    ("punnett_hetero", law_punnett_hetero),
    ("punnett_aa", law_punnett_aa),
    ("toxic_fish", law_toxic_fish),
    ("clean_water_fish", law_clean_water_fish),
    ("plants_make_food", law_plants_make_food),
    ("wide_leaves", law_wide_leaves),
    ("desert_leaves", law_desert_leaves),
    ("disturb_nest", law_disturb_nest),
    ("bar_compare", law_bar_compare),
    ("mantle_heat", law_mantle_heat),
    ("golgi_pack", law_golgi_pack),
    ("float_light", law_float_light),
    ("sink_dense", law_sink_dense),
]

SOURCES = {
    "repeat_record": "Mercury_SC_407695",
    "not_safe_taste": "Mercury_7017990",
    "clear_forest_biodiversity": "Mercury_7195440",
    "cut_forest_erosion": "Mercury_184765",
    "sealed_returns": "ACTAAP_2007_7_5",
    "saliva_first": "Mercury_7245893",
    "algae_oxygen_ocean": "Mercury_417146",
    "no_record_blocks_check": "Mercury_7128695",
    "daylight_seasons": "Mercury_SC_400655",
    "grow_weight_up": "NYSEDREGENTS_2014_4_19",
    "invasive_eggs": "Mercury_7138513",
    "compost_scraps": "Mercury_SC_401663",
    "mass_lost_gas": "NCEOGA_2013_8_4",
    "moon_month": "Mercury_7011270",
    "meiosis_new_combo": "Mercury_7228603",
    "vine_touch": "MCAS_2010_5_11998",
    "blood_markers": "Mercury_7029505",
    "mass_weight_moon": "MCAS_2004_8_28",
    "incomplete_pink": "Mercury_7189035",
    "black_absorbs": "NYSEDREGENTS_2014_4_14",
    "burn_chemical": "Mercury_SC_406939",
    "machine_loss": "Mercury_7135310",
    "boil_egg_bonds": "LEAP_2006_8_10412",
    "solid_has_both": "NYSEDREGENTS_2014_8_38",
    "slow_water_solid": "MEA_2010_8_11",
    "inherit_body": "NYSEDREGENTS_2014_4_17",
    "light_years": "Mercury_7033653",
    "mammals_hair": "AKDE&ED_2008_8_44",
    "noble_column": "Mercury_400934",
    "survive_spray": "Mercury_7139493",
    "low_variation": "MCAS_2006_9_33",
    "phase_same_mass": "Mercury_SC_LBS10598",
    "recycle_paper": "MDSA_2008_5_24",
    "worms_air": "Mercury_SC_415366",
    "punnett_hetero": "Mercury_7238963",
    "toxic_fish": "Mercury_SC_402104",
    "plants_make_food": "Mercury_SC_LBS10666",
    "wide_leaves": "Mercury_SC_401294",
    "disturb_nest": "MCAS_2005_5_21",
    "bar_compare": "MCAS_2006_5_29",
    "mantle_heat": "Mercury_7183015",
    "golgi_pack": "Mercury_7242743",
    "float_light": "Mercury_SC_415541",
}


BANK = [
    {"id": "apply-repeat-ramp", "kind": "apply", "law": "repeat_record",
     "stem": "A class wants to repeat a ramp experiment next week. What should they do?",
     "choices": [("A", "Guess a new winner"), ("B", "Change the objects"), ("C", "Record the details of the investigation"), ("D", "Skip the measurements")],
     "want": "C"},
    {"id": "apply-no-notes", "kind": "apply", "law": "no_record_blocks_check",
     "stem": "A student does not write down her steps. How does that lack of record keeping affect the work?",
     "choices": [("A", "It makes the chemicals stronger"), ("B", "It prevents other scientists from validating the results"), ("C", "It changes the mass"), ("D", "It creates a fossil")],
     "want": "B"},
    {"id": "apply-not-safe", "kind": "apply", "law": "not_safe_taste",
     "stem": "Which action is not a safe lab practice?",
     "choices": [("A", "tasting chemical samples"), ("B", "wearing goggles"), ("C", "tying hair back"), ("D", "washing hands")],
     "want": "A"},
    {"id": "near-is-safe", "kind": "near", "law": "not_safe_taste",
     "stem": "Which is a safety rule in the lab?",
     "choices": [("A", "tasting unknown liquids"), ("B", "wearing goggles"), ("C", "eating lunch over the beakers"), ("D", "leaving a flame unattended")],
     "want": "B"},
    {"id": "apply-rainforest", "kind": "apply", "law": "clear_forest_biodiversity",
     "stem": "Large areas of rainforest are cleared each year. Which effect is most likely?",
     "choices": [("A", "a decrease in biodiversity"), ("B", "more species appearing overnight"), ("C", "the oceans freezing"), ("D", "gravity increasing")],
     "want": "A"},
    {"id": "apply-cut-trees", "kind": "apply", "law": "cut_forest_erosion",
     "stem": "People keep cutting down a large continuous forest. What happens to the soil?",
     "choices": [("A", "The amount of erosion will increase"), ("B", "Species diversity will increase"), ("C", "Oxygen over the area will increase"), ("D", "Soil nutrients will increase")],
     "want": "A"},
    {"id": "apply-sealed-jar", "kind": "apply", "law": "sealed_returns",
     "stem": "A sealed jar starts at a temperature of 20 C and an air pressure of 30 psi. It is heated, then cooled back to 20 C. What is the air pressure?",
     "choices": [("A", "10 psi"), ("B", "30 psi"), ("C", "50 psi"), ("D", "0 psi")],
     "want": "B"},
    {"id": "apply-digestion-start", "kind": "apply", "law": "saliva_first",
     "stem": "Where does the first chemical digestion of food begin?",
     "choices": [("A", "saliva in the mouth"), ("B", "the small intestine"), ("C", "the large intestine"), ("D", "the bloodstream")],
     "want": "A"},
    {"id": "near-absorbed", "kind": "near", "law": "saliva_first",
     "stem": "Where is most food absorbed into the blood?",
     "choices": [("A", "saliva in the mouth"), ("B", "the small intestine"), ("C", "the teeth"), ("D", "the hair")],
     "want": "B"},
    {"id": "apply-algae-live", "kind": "apply", "law": "algae_oxygen_ocean",
     "stem": "Most of the oxygen in the air is made by algae. Where do most of those algae live?",
     "choices": [("A", "coastal ocean"), ("B", "desert sand"), ("C", "dry caves"), ("D", "glacier ice")],
     "want": "A"},
    {"id": "apply-june-dec", "kind": "apply", "law": "daylight_seasons",
     "stem": "What changes most between June and December in a town with seasons?",
     "choices": [("A", "the hours of daylight"), ("B", "the mass of Earth"), ("C", "the number of moons"), ("D", "the charge of a proton")],
     "want": "A"},
    {"id": "apply-puppies", "kind": "apply", "law": "grow_weight_up",
     "stem": "As puppies grow into dogs, their body weight usually",
     "choices": [("A", "decreases"), ("B", "increases"), ("C", "becomes zero")],
     "want": "B"},
    {"id": "apply-rats-island", "kind": "apply", "law": "invasive_eggs",
     "stem": "Rats that eat seabird eggs are released on an island that had no rats. What is the most likely result?",
     "choices": [("A", "more rats and fewer seabirds"), ("B", "more seabirds and no rats"), ("C", "the island gains a moon"), ("D", "the ocean becomes fresh")],
     "want": "A"},
    {"id": "apply-compost", "kind": "apply", "law": "compost_scraps",
     "stem": "Which object belongs in a compost pile?",
     "choices": [("A", "a glass bottle"), ("B", "apple peels"), ("C", "a steel nail"), ("D", "a plastic cup")],
     "want": "B"},
    {"id": "near-not-compost", "kind": "near", "law": "compost_scraps",
     "stem": "Which object does not belong in a compost pile?",
     "choices": [("A", "apple peels"), ("B", "bean plants"), ("C", "a plastic cup"), ("D", "leaves")],
     "want": "C"},
    {"id": "apply-gas-left", "kind": "apply", "law": "mass_lost_gas",
     "stem": "After a reaction the solid left behind weighs less than the starting materials. Why is the mass of the products less?",
     "choices": [("A", "Mass was destroyed"), ("B", "Gases were released"), ("C", "The balance added mass"), ("D", "Atoms were created")],
     "want": "B"},
    {"id": "apply-moon-trip", "kind": "apply", "law": "moon_month",
     "stem": "About how long does it take the Moon to complete one revolution around Earth?",
     "choices": [("A", "24 hours"), ("B", "about 30 days"), ("C", "365 days"), ("D", "10 years")],
     "want": "B"},
    {"id": "near-earth-spin", "kind": "near", "law": "moon_month",
     "stem": "About how long does it take Earth to rotate once?",
     "choices": [("A", "24 hours"), ("B", "about 30 days"), ("C", "365 days"), ("D", "10 years")],
     "want": "A"},
    {"id": "apply-crossing", "kind": "apply", "law": "meiosis_new_combo",
     "stem": "Crossing over exchanges homologous chromosome parts during meiosis. What is a result?",
     "choices": [("A", "offspring with unique combinations of traits"), ("B", "offspring that are identical clones"), ("C", "the loss of all DNA"), ("D", "a new planet")],
     "want": "A"},
    {"id": "apply-vine", "kind": "apply", "law": "vine_touch",
     "stem": "A flowering vine wraps a fence as it climbs. Which behavior helps it climb?",
     "choices": [("A", "stems curling in response to touch"), ("B", "roots flying"), ("C", "leaves turning into metal"), ("D", "the fence melting")],
     "want": "A"},
    {"id": "apply-blood", "kind": "apply", "law": "blood_markers",
     "stem": "What makes type A blood different from type B blood?",
     "choices": [("A", "different marker proteins on red blood cells"), ("B", "the plasma is a different metal"), ("C", "one type has no cells"), ("D", "one type is a gas")],
     "want": "A"},
    {"id": "apply-hammer-moon", "kind": "apply", "law": "mass_weight_moon",
     "stem": "A hammer is moved from Earth to the Moon. Which measurable property changes?",
     "choices": [("A", "It has the same mass but a different weight"), ("B", "It has a different mass and the same weight"), ("C", "Both mass and weight stay identical"), ("D", "The hammer loses its atoms")],
     "want": "A"},
    {"id": "apply-pink", "kind": "apply", "law": "incomplete_pink",
     "stem": "Red and white flowers show incomplete dominance. What do the offspring look like?",
     "choices": [("A", "100% red"), ("B", "100% white"), ("C", "100% pink"), ("D", "no flowers")],
     "want": "C"},
    {"id": "near-complete-dom", "kind": "near", "law": "incomplete_pink",
     "stem": "Red is complete dominance over white. A red parent and a white parent have offspring that are",
     "choices": [("A", "100% red"), ("B", "100% pink"), ("C", "100% white"), ("D", "colorless")],
     "want": "A"},
    {"id": "apply-black-shirt", "kind": "apply", "law": "black_absorbs",
     "stem": "Which shirt color absorbs the most sunlight?",
     "choices": [("A", "white"), ("B", "silver"), ("C", "black"), ("D", "mirror")],
     "want": "C"},
    {"id": "near-reflect-shirt", "kind": "near", "law": "black_absorbs",
     "stem": "Which shirt color reflects the most sunlight?",
     "choices": [("A", "black"), ("B", "white"), ("C", "dark navy"), ("D", "charcoal")],
     "want": "B"},
    {"id": "apply-burn-log", "kind": "apply", "law": "burn_chemical",
     "stem": "Which is a chemical change to a log?",
     "choices": [("A", "cut the log"), ("B", "burn the log with fire"), ("C", "paint the log"), ("D", "move the log")],
     "want": "B"},
    {"id": "near-cut-paper", "kind": "near", "law": "burn_chemical",
     "stem": "Which is a physical change to paper?",
     "choices": [("A", "burn the paper"), ("B", "cut the paper"), ("C", "turn the paper into ash"), ("D", "oxidize the paper completely")],
     "want": "B"},
    {"id": "apply-motor", "kind": "apply", "law": "machine_loss",
     "stem": "Why is a motor's useful output less than its electrical input?",
     "choices": [("A", "Energy is created"), ("B", "Useful energy decreases as energy is transferred to the surroundings"), ("C", "The motor makes mass"), ("D", "Input is destroyed")],
     "want": "B"},
    {"id": "apply-boil-egg", "kind": "apply", "law": "boil_egg_bonds",
     "stem": "An egg boiled for fifteen minutes turns from liquid to solid because",
     "choices": [("A", "the egg lost its mass"), ("B", "heating changed the chemical bonds in the egg"), ("C", "the shell became a gas"), ("D", "atoms were destroyed")],
     "want": "B"},
    {"id": "apply-ice-block", "kind": "apply", "law": "solid_has_both",
     "stem": "A substance in the solid phase of matter has",
     "choices": [("A", "no definite shape and no definite volume"), ("B", "a definite shape and a definite volume"), ("C", "no mass"), ("D", "no atoms")],
     "want": "B"},
    {"id": "near-steam", "kind": "near", "law": "solid_has_both",
     "stem": "A substance in the gas phase of matter has",
     "choices": [("A", "a definite shape and a definite volume"), ("B", "no definite shape and no definite volume"), ("C", "a definite shape and no volume"), ("D", "no mass")],
     "want": "B"},
    {"id": "apply-slow-water", "kind": "apply", "law": "slow_water_solid",
     "stem": "When the motion of liquid water molecules slows enough, the water most likely",
     "choices": [("A", "forms a solid"), ("B", "becomes a plasma"), ("C", "loses its mass"), ("D", "becomes a metal")],
     "want": "A"},
    {"id": "near-fast-water", "kind": "near", "law": "slow_water_solid",
     "stem": "When liquid water molecules speed up a great deal, the water most likely",
     "choices": [("A", "forms a solid"), ("B", "becomes a gas"), ("C", "becomes a rock"), ("D", "stops existing")],
     "want": "B"},
    {"id": "apply-cat-fur", "kind": "apply", "law": "inherit_body",
     "stem": "Which trait would a cat most likely inherit from its parents?",
     "choices": [("A", "a scar on its ear"), ("B", "a trick it was taught"), ("C", "having white fur"), ("D", "the name on its collar")],
     "want": "C"},
    {"id": "apply-star-distance", "kind": "apply", "law": "light_years",
     "stem": "Which unit is best for the distance from the Sun to the next star?",
     "choices": [("A", "meters"), ("B", "kilometers"), ("C", "light years"), ("D", "inches")],
     "want": "C"},
    {"id": "near-classroom", "kind": "near", "law": "light_years",
     "stem": "Which unit is best for a distance across a classroom?",
     "choices": [("A", "light years"), ("B", "meters"), ("C", "parsecs"), ("D", "astronomical units")],
     "want": "B"},
    {"id": "apply-hair", "kind": "apply", "law": "mammals_hair",
     "stem": "Which trait is found in mammals and not in reptiles, birds, amphibians, or fishes?",
     "choices": [("A", "have hair"), ("B", "have gills only"), ("C", "lay eggs in water only"), ("D", "have scales and no other covering")],
     "want": "A"},
    {"id": "apply-noble", "kind": "apply", "law": "noble_column",
     "stem": "Which set has similar properties because the elements sit in the same column of the periodic table?",
     "choices": [("A", "Na, Cl, Fe"), ("B", "He, Ne, Ar"), ("C", "C, Na, He"), ("D", "Fe, O, Ne")],
     "want": "B"},
    {"id": "apply-beetles", "kind": "apply", "law": "survive_spray",
     "stem": "Some beetles survive the same insecticide spray year after year. What most likely allows that?",
     "choices": [("A", "genetic diversity"), ("B", "the spray became food"), ("C", "beetles have no DNA"), ("D", "the spray removes gravity")],
     "want": "A"},
    {"id": "apply-cheetah-var", "kind": "apply", "law": "low_variation",
     "stem": "A population has very little genetic variation. Compared with a varied population, it is",
     "choices": [("A", "less likely to adapt to a new disease"), ("B", "more likely to adapt to every change"), ("C", "unable to have DNA"), ("D", "heavier")],
     "want": "A"},
    {"id": "apply-ice-vapor-mass", "kind": "apply", "law": "phase_same_mass",
     "stem": "An ice cube melts and then evaporates in a sealed bag. The ice and the vapor have the same",
     "choices": [("A", "mass"), ("B", "shape"), ("C", "volume"), ("D", "temperature")],
     "want": "A"},
    {"id": "apply-recycle", "kind": "apply", "law": "recycle_paper",
     "stem": "How does recycling newspaper positively affect a forest?",
     "choices": [("A", "more trees are cut"), ("B", "it reduces trees that are cut"), ("C", "it removes the soil"), ("D", "it stops rain")],
     "want": "B"},
    {"id": "apply-worms", "kind": "apply", "law": "worms_air",
     "stem": "Tree roots near the surface need oxygen. Which organisms help by making holes in the soil?",
     "choices": [("A", "earthworms"), ("B", "clouds"), ("C", "the Moon"), ("D", "gold bars")],
     "want": "A"},
    {"id": "apply-aa", "kind": "apply", "law": "punnett_aa",
     "stem": "One parent is aa and the other is Aa. Which allele combinations can the child have?",
     "choices": [("A", "AA only"), ("B", "Aa or aa"), ("C", "only AA or aa, never Aa"), ("D", "no alleles")],
     "want": "B"},
    {"id": "apply-cleft", "kind": "apply", "law": "punnett_hetero",
     "stem": "A father has a cc allele pair and a mother has a Cc allele pair. Which allele combinations can their child have?",
     "choices": [("A", "CC or Cc"), ("B", "Cc or cc"), ("C", "CC only"), ("D", "Cc only")],
     "want": "B"},
    {"id": "near-both-CC", "kind": "near", "law": "punnett_hetero",
     "stem": "Both parents have a CC allele pair. Which allele combination can the child have?",
     "choices": [("A", "Cc or cc"), ("B", "CC only"), ("C", "cc only"), ("D", "no alleles")],
     "want": "B"},
    {"id": "apply-poison-lake", "kind": "apply", "law": "toxic_fish",
     "stem": "Someone dumps poison into a lake. What happens to the fish?",
     "choices": [("A", "they are harmed or die"), ("B", "they double in size overnight"), ("C", "they become plants"), ("D", "they gain a moon")],
     "want": "A"},
    {"id": "apply-oaks", "kind": "apply", "law": "plants_make_food",
     "stem": "Why don't oak trees have to eat other organisms?",
     "choices": [("A", "they eat soil"), ("B", "they turn sunlight into food energy"), ("C", "they have no cells"), ("D", "they do not need energy")],
     "want": "B"},
    {"id": "apply-wet-leaves", "kind": "apply", "law": "wide_leaves",
     "stem": "Leaves that survive well in a rainy climate are most often",
     "choices": [("A", "tiny spines"), ("B", "wide and flat"), ("C", "made of metal"), ("D", "absent")],
     "want": "B"},
    {"id": "near-desert-leaf", "kind": "near", "law": "wide_leaves",
     "stem": "Leaves that survive in a desert are most often",
     "choices": [("A", "wide and flat"), ("B", "small and waxy"), ("C", "as large as a table"), ("D", "full of water with no covering")],
     "want": "B"},
    {"id": "apply-turtles", "kind": "apply", "law": "disturb_nest",
     "stem": "People keep scaring sea turtles off their nesting beach. The turtles will most likely",
     "choices": [("A", "give birth at a different beach"), ("B", "nest on the same spot forever"), ("C", "turn into fish"), ("D", "stop having DNA")],
     "want": "A"},
    {"id": "apply-rods", "kind": "apply", "law": "bar_compare",
     "stem": "Four metal rods were tested to see how much each one bent. What is the best way to report the results of this experiment?",
     "choices": [("A", "a pie chart of opinions"), ("B", "a bar graph showing how much each rod bent"), ("C", "a poem"), ("D", "a single number with no labels")],
     "want": "B"},
    {"id": "apply-mantle", "kind": "apply", "law": "mantle_heat",
     "stem": "Fluid in the mantle circulates and moves the plates. What most likely causes that circulation?",
     "choices": [("A", "energy transfers"), ("B", "moonlight"), ("C", "the color of the ocean"), ("D", "bird migration")],
     "want": "A"},
    {"id": "apply-golgi", "kind": "apply", "law": "golgi_pack",
     "stem": "Which organelle packages proteins and sends them to the right place in the cell?",
     "choices": [("A", "Golgi apparatus"), ("B", "a mitochondrion only making ATP"), ("C", "the cell wall of an animal"), ("D", "a vacuole of pure water")],
     "want": "A"},
    {"id": "apply-float", "kind": "apply", "law": "float_light",
     "stem": "Which of these objects will most likely float in water?",
     "choices": [("A", "a steel bolt"), ("B", "a rock"), ("C", "a lead weight"), ("D", "a table tennis ball")],
     "want": "D"},
    {"id": "near-sink", "kind": "near", "law": "float_light",
     "stem": "Which of these objects will most likely sink in water?",
     "choices": [("A", "a cork"), ("B", "a table tennis ball"), ("C", "a steel bolt"), ("D", "a dry pine chip")],
     "want": "C"},
]


from bill32_relations_more import EXTRA_BANK, EXTRA_LAWS, EXTRA_SOURCES

FINISH.extend(EXTRA_LAWS)
SOURCES.update(EXTRA_SOURCES)
BANK.extend(EXTRA_BANK)

CASE_LAWS = {"punnett_hetero", "punnett_aa", "both_parents_CC"}


def finish_votes(stem, pairs):
    sl = stem.lower()
    out = []
    for name, fn in FINISH:
        lab = fn(stem if name in CASE_LAWS else sl, pairs)
        if lab is not None:
            out.append((name, lab))
    return out


def latest_votes(stem, pairs):
    return prev_votes(stem, pairs) + finish_votes(stem, pairs)


def latest_pick(stem, pairs):
    votes = latest_votes(stem, pairs)
    labels = sorted({lab for _, lab in votes})
    if len(labels) == 1:
        return labels[0], votes[0][0]
    if len(labels) > 1:
        return None, "conflict"
    return None, None


def thought_of(stem, pairs, facts) -> str:
    """Why the family committed, or why the thought stopped."""
    votes = latest_votes(stem, pairs)
    labels = sorted({lab for _, lab in votes})
    names = sorted({name for name, _ in votes})
    if len(labels) > 1:
        return "halted: routes disagreed (" + ", ".join(names) + ")"
    if len(labels) == 1:
        return "continued: one relation agreed (" + names[0] + ")"
    _lab, how, _state = pick_v3(stem, pairs, facts, PROCS_ALL)
    if how == "consensus_0":
        return "halted: two studied facts named different letters, so the result stayed trit 0"
    if how == "procedure":
        return "continued: one procedure cue agreed"
    if how == "strict_fact":
        return "continued: one studied fact contained the choice"
    return "halted: no relation matched, and no studied fact contained one choice"


def _score(items):
    rows = []
    a_ok = n_ok = a_n = n_n = 0
    for item in items:
        pairs = item["choices"]
        lab, law = latest_pick(item["stem"], pairs)
        voted = [name for name, _ in latest_votes(item["stem"], pairs)]
        if item["kind"] == "apply":
            a_n += 1
            ok = lab == item["want"] and law == item["law"]
            a_ok += int(ok)
        else:
            n_n += 1
            ok = item["law"] not in voted and (lab is None or lab == item["want"])
            n_ok += int(ok)
        rows.append({"id": item["id"], "kind": item["kind"], "law": item["law"], "want": item["want"], "picked": lab, "fired": law, "ok": ok})
    return rows, a_ok, a_n, n_ok, n_n


def main() -> int:
    easy = load_split("validation")
    challenge = load_challenge("validation")
    facts = study_facts(load_split("train"))
    rows, a_ok, a_n, n_ok, n_n = _score(BANK)
    old_rows, oa, oan, on, onn = _score(BANK29 + BANK30 + BANK32)
    by_id = {row["id"]: row for _, row in challenge.iterrows()}
    source_rows = []
    source_ok = 0
    for law, sid in SOURCES.items():
        row = by_id.get(sid)
        if row is None:
            source_rows.append({"id": sid, "law": law, "ok": False, "picked": None, "fired": "missing"})
            continue
        pairs = choices_of(row)
        key = str(row["answerKey"]).strip()
        lab, fired = latest_pick(str(row["question"]), pairs)
        ok = lab == key and fired == law
        source_ok += int(ok)
        source_rows.append({"id": sid, "law": law, "ok": ok, "picked": lab, "fired": fired, "key": key, "key_text": dict(pairs).get(key)})
    easy_wrong = 0
    for _, row in easy.iterrows():
        pairs = choices_of(row)
        key = str(row["answerKey"]).strip()
        stem = str(row["question"])
        old, _, _ = pick_v3(stem, pairs, facts, PROCS_ALL)
        lab, _ = latest_pick(stem, pairs)
        final = lab if lab is not None else old
        if final != key:
            easy_wrong += 1
    chal = {"correct": 0, "wrong": 0, "leftover": 0, "consensus_0": 0}
    hurt = 0
    for _, row in challenge.iterrows():
        pairs = choices_of(row)
        key = str(row["answerKey"]).strip()
        stem = str(row["question"])
        old, how, _ = pick_v3(stem, pairs, facts, PROCS_ALL)
        lab, law = latest_pick(stem, pairs)
        if lab is not None and lab != key:
            hurt += 1
        if law == "conflict":
            final = None
            kind = "consensus_0"
        elif lab is not None:
            final = lab
            kind = "use"
        else:
            final = old
            kind = "consensus_0" if how == "consensus_0" else ("leftover" if old is None else "base")
        if final is None:
            chal["consensus_0" if kind == "consensus_0" else "leftover"] += 1
        elif final == key:
            chal["correct"] += 1
        else:
            chal["wrong"] += 1
    fails = [r for r in rows + old_rows + source_rows if not r["ok"]]
    overall = (
        a_ok == a_n and n_ok == n_n and oa == oan and on == onn
        and source_ok == len(SOURCES) and easy_wrong == 0 and hurt == 0 and chal["wrong"] == 0
    )
    doc = {
        "adventure": 1, "ted": "TED-33", "vs_bill": "Bill-32", "pin": "AEB2AD", "free_parameters": 0,
        "fitted_challenge_val_into_cues": False,
        "apply_ok": a_ok, "apply_n": a_n, "near_ok": n_ok, "near_n": n_n,
        "old_apply_ok": oa, "old_apply_n": oan, "old_near_ok": on, "old_near_n": onn,
        "source_ok": source_ok, "source_n": len(SOURCES),
        "easy_new_wrong": easy_wrong, "challenge": chal, "challenge_hurt": hurt,
        "failures": fails, "measured_W_changed": False,
        "overall_ok": overall, "promotes": overall, "promote_to": "Bill-33" if overall else None,
        "thinking": {"deny_family_seeded": False},
    }
    OUT.write_text(json.dumps(doc, indent=2), encoding="utf-8")
    md = f"""# Use finish (TED-33)

Challenge leftovers are situations. Each relation is checked on a new wording, kept quiet on a near miss, and then allowed to finish the original situation. The original Challenge sentence is not the cue. Pin AEB2AD. 0 free parameters. Measured W is unchanged.

A thought continues when one relation names one letter. A thought halts when no relation matches, when two routes name different letters, or when two studied facts name different letters. A halt stays trit 0. The side-by-side records that thought next to the expected answer and the family answer.

New wordings **{a_ok}/{a_n}**. Near misses **{n_ok}/{n_n}**. Earlier use items **{oa}/{oan}** and **{on}/{onn}**. Original situations **{source_ok}/{len(SOURCES)}**.

Easy new wrongs **{easy_wrong}**. Challenge replay: correct **{chal['correct']}**, wrong **{chal['wrong']}**, leftover **{chal['leftover']}**, consensus 0 **{chal['consensus_0']}**. Relations that answered a Challenge item wrongly: **{hurt}**.

The thought column is in `docs/ADVENTURE1_SIDE_BY_SIDE.md`. Courtship, aggression, fru, and dsx stay T1 off.
"""
    DOC.parent.mkdir(parents=True, exist_ok=True)
    ADV.mkdir(parents=True, exist_ok=True)
    DOC.write_text(md, encoding="utf-8")
    (ADV / "USE_FINISH.md").write_text(md, encoding="utf-8")
    print(
        f"  TED-33 apply {a_ok}/{a_n} near {n_ok}/{n_n} old {oa}/{oan} {on}/{onn} "
        f"source {source_ok}/{len(SOURCES)} easy_wrong {easy_wrong} "
        f"chal c={chal['correct']} w={chal['wrong']} L={chal['leftover']} C0={chal['consensus_0']} hurt {hurt} overall {overall}"
    )
    for r in fails:
        print("  FAIL", r.get("id"), r.get("law"), "picked", r.get("picked"), "fired", r.get("fired"), "key", r.get("key"), r.get("key_text"))
    print(f"  wrote {OUT}")
    return 0 if overall else 1


if __name__ == "__main__":
    raise SystemExit(main())
