#!/usr/bin/env python3
"""More TED-33 situation relations.

Each one is a situation, checked on a new wording, then allowed to finish the
original Challenge item. A near miss uses different wording so the relation stays quiet.
"""
from __future__ import annotations

import re

from bill28_use import _choose, _has

EXTRA_LAWS: list[tuple[str, object]] = []
EXTRA_SOURCES: dict[str, str] = {}
EXTRA_BANK: list[dict] = []


def _simple(need, avoid, bits, ban):
    def fn(sl, pairs):
        if all(part in sl for part in need) and not any(part in sl for part in avoid):
            return _choose(pairs, bits, ban)
        return None

    return fn


def add(name, need, bits, source, stem, choices, want, ban=(), avoid=()):
    EXTRA_LAWS.append((name, _simple(tuple(need), tuple(avoid), tuple(bits), tuple(ban))))
    if source:
        EXTRA_SOURCES[name] = source
    EXTRA_BANK.append(
        {
            "id": f"apply-{name}",
            "kind": "apply",
            "law": name,
            "stem": stem,
            "choices": choices,
            "want": want,
        }
    )


def near(name, stem, choices, want, nid=None):
    EXTRA_BANK.append(
        {
            "id": nid or f"near-{name}",
            "kind": "near",
            "law": name,
            "stem": stem,
            "choices": choices,
            "want": want,
        }
    )


def law_independent_changed(sl, pairs):
    if not _has(sl, ("independent variable", "independent (manipulated)", "manipulated variable")):
        return None
    varied = []
    for match in re.finditer(r"different (?:amounts?|sizes?|types?|kinds?) of ([a-z]+)", sl):
        word = match.group(1)
        if word.endswith("s") and len(word) > 3:
            word = word[:-1]
        varied.append(word)
    if "supplement" in sl and _has(sl, ("fed ", "were fed", "given")):
        varied.append("supplement")
    if not varied:
        return None
    return _choose(pairs, tuple(varied), ("test", "growth", "caught", "aging", "bait"))


def law_dependent_measured(sl, pairs):
    # "independent" contains the letters of "dependent", so the check is a whole word.
    if re.search(r"\bdependent variable\b", sl) is None and "responding variable" not in sl:
        return None
    return _choose(pairs, ("time", "height", "growth", "number", "distance"), ("amount of", "brand"))


def law_shown_chemical_change(sl, pairs):
    if "chemical change" not in sl:
        return None
    if _has(sl, ("paper", " log", "a log", "wood")):
        return None
    return _choose(pairs, ("burn", "flaky", "rust"), ("dissolv", "boil", "melt", "cut ", "sharpen", "break"))


def law_shown_physical_change(sl, pairs):
    if "physical change" not in sl or "chemical change" in sl:
        return None
    if _has(sl, ("paper", " log", "a log", "wood")):
        return None
    return _choose(pairs, ("melt", "dissolv", "boil"), ("burn", "flaky", "rust"))


def _formula_counts(formula: str) -> dict[str, int]:
    counts: dict[str, int] = {}
    i = 0
    n = len(formula)

    def read_num() -> int:
        nonlocal i
        start = i
        while i < n and formula[i].isdigit():
            i += 1
        return int(formula[start:i]) if start < i else 1

    def read_group() -> dict[str, int]:
        nonlocal i
        local: dict[str, int] = {}
        while i < n and formula[i] != ")":
            if formula[i] == "(":
                i += 1
                inner = read_group()
                if i < n and formula[i] == ")":
                    i += 1
                mult = read_num()
                for key, val in inner.items():
                    local[key] = local.get(key, 0) + val * mult
            elif formula[i].isupper():
                element = formula[i]
                i += 1
                if i < n and formula[i].islower():
                    element += formula[i]
                    i += 1
                mult = read_num()
                local[element] = local.get(element, 0) + mult
            else:
                i += 1
        return local

    counts = read_group()
    return counts


def _side_counts(side: str) -> dict[str, int] | None:
    total: dict[str, int] = {}
    for raw in side.split("+"):
        token = raw.strip()
        if not token:
            continue
        match = re.match(r"^(\d+)([A-Za-z(].*)$", token)
        coef = int(match.group(1)) if match else 1
        formula = match.group(2) if match else token
        if not re.search(r"[A-Za-z]", formula):
            return None
        for key, val in _formula_counts(formula).items():
            total[key] = total.get(key, 0) + val * coef
    return total


def law_balanced_equation(sl, pairs):
    if "balanced" not in sl or "equation" not in sl:
        return None
    labs = []
    for lab, text in pairs:
        raw = text.replace("→", "->")
        raw = re.sub(r"_\{(\d+)\}", r"\1", raw)
        raw = raw.replace(" ", "")
        if "->" not in raw:
            continue
        left, right = raw.split("->", 1)
        left_counts = _side_counts(left)
        right_counts = _side_counts(right)
        if left_counts and right_counts and left_counts == right_counts:
            labs.append(lab)
    labs = sorted(set(labs))
    return labs[0] if len(labs) == 1 else None


def law_wave_speed(sl, pairs):
    hz = re.search(r"(\d+)\s*-?\s*hz", sl)
    wave = re.search(r"wavelength of\s+(\d+)", sl)
    if not hz or not wave or "speed" not in sl:
        return None
    speed = int(hz.group(1)) * int(wave.group(1))
    return _choose(pairs, (f"{speed} ",), ())


def law_moon_year_count(sl, pairs):
    if "moon" not in sl or "orbit" not in sl or "year" not in sl or "how many" not in sl:
        return None
    target = 365 / 27.3
    scored = []
    for lab, text in pairs:
        nums = [int(n) for n in re.findall(r"\d+", text)]
        if len(nums) == 1:
            scored.append((abs(nums[0] - target), lab))
    if not scored:
        return None
    scored.sort()
    if len(scored) == 1 or scored[0][0] < scored[1][0]:
        return scored[0][1]
    return None


def law_lowest_tides(sl, pairs):
    if "tide" not in sl or not _has(sl, ("lowest", "neap")):
        return None
    labs = []
    for lab, text in pairs:
        low = text.lower()
        if "full" in low or "new moon" in low:
            continue
        if "first quarter" in low and "last quarter" in low:
            labs.append(lab)
    labs = sorted(set(labs))
    return labs[0] if len(labs) == 1 else None


def law_greywater_plants(sl, pairs):
    if "greywater" not in sl and "graywater" not in sl:
        return None
    labs = []
    for lab, text in pairs:
        low = text.lower()
        if "drinking" in low or "washing dishes" in low:
            continue
        if "irrigat" in low or "watering trees" in low or "flowerbed" in low:
            labs.append(lab)
    labs = sorted(set(labs))
    return labs[0] if len(labs) == 1 else None


def law_asteroid_comet(sl, pairs):
    if "asteroid" not in sl or "comet" not in sl:
        return None
    labs = []
    for lab, text in pairs:
        low = text.lower()
        if "asteroids are gaseous" in low or "comets are solid" in low:
            continue
        rocky = ("solid" in low or "rock" in low) and "asteroid" in low
        gassy = "gas" in low and "comet" in low
        if rocky and gassy:
            labs.append(lab)
    labs = sorted(set(labs))
    return labs[0] if len(labs) == 1 else None


def law_vapor_invisible(sl, pairs):
    if "water vapor" not in sl:
        return None
    return _choose(pairs, ("invisible gas",), ("liquid",))


def law_hot_drink_spoon(sl, pairs):
    if "spoon" not in sl or not _has(sl, ("hot chocolate", "tea", "hot drink", "coffee")):
        return None
    directed = []
    for lab, text in pairs:
        low = text.lower()
        if "conduction" not in low or "from the spoon" in low:
            continue
        if _has(low, ("from the hot chocolate", "from the tea", "from the drink", "to the spoon")):
            directed.append(lab)
    directed = sorted(set(directed))
    if len(directed) == 1:
        return directed[0]
    return _choose(pairs, ("conduction",), ("convection", "radiation", "evaporation"))


def law_direction_velocity(sl, pairs):
    if not _has(sl, ("direction", "north", "south", "east", "west", "northeasterly")):
        return None
    if not _has(sl, ("km/h", "m/s", "rate of")):
        return None
    return _choose(pairs, ("velocity",), ("acceleration", "deceleration"))


def law_nuclear_not_jobs(sl, pairs):
    if "nuclear" not in sl or "controvers" not in sl or " not " not in f" {sl} ":
        return None
    return _choose(pairs, ("unemployment",), ("waste", "health", "thermal"))


def law_falling_velocity(sl, pairs):
    if "acorn falls" not in sl and "as an acorn falls" not in sl:
        return None
    return _choose(pairs, ("velocity", "speed"), ("mass", "density", "force"))


CUSTOM = [
    ("independent_changed", law_independent_changed, "Mercury_7103215",
     "Students give each plant a different amount of fertilizer and measure the height. What is the independent variable?",
     [("A", "the height grown"), ("B", "the amount of fertilizer"), ("C", "the hours of daylight, which stayed the same"), ("D", "the type of pot, which stayed the same")],
     "B"),
    ("dependent_measured", law_dependent_measured, None,
     "Each cup gets a different amount of salt. Students measure how long the ice takes to melt. What is the dependent variable?",
     [("A", "the amount of salt"), ("B", "the melt time"), ("C", "the brand of salt"), ("D", "the day of the week")],
     "B"),
    ("shown_chemical_change", law_shown_chemical_change, "Mercury_7133858",
     "Which event is a chemical change?",
     [("A", "salt dissolving in water"), ("B", "wood burning in a fire"), ("C", "water boiling"), ("D", "ice melting")],
     "B"),
    ("shown_physical_change", law_shown_physical_change, None,
     "Which event is a physical change?",
     [("A", "a nail turning rusty and flaky"), ("B", "a log burning"), ("C", "an ice cube melting"), ("D", "paper turning to ash")],
     "C"),
    ("balanced_equation", law_balanced_equation, "Mercury_400885",
     "Which equation is a balanced chemical equation?",
     [("A", "H2 + O2 -> H2O"), ("B", "2H2 + O2 -> 2H2O"), ("C", "Na + Cl2 -> NaCl"), ("D", "C + O2 -> 2CO")],
     "B"),
    ("wave_speed", law_wave_speed, "Mercury_412683",
     "What is the speed of a 3-Hz wave that has a wavelength of 4 m?",
     [("A", "7 m/s"), ("B", "12 m/s"), ("C", "1 m/s"), ("D", "0.75 m/s")],
     "B"),
    ("moon_year_count", law_moon_year_count, "Mercury_SC_415491",
     "Earth goes around the Sun once each year. About how many times does the Moon orbit Earth in that same year?",
     [("A", "1"), ("B", "7"), ("C", "13"), ("D", "28")],
     "C"),
    ("lowest_tides", law_lowest_tides, "Mercury_7171938",
     "During which lunar phases are ocean tides lowest?",
     [("A", "full and first quarter"), ("B", "full moon and new moon"), ("C", "last quarter and new moon"), ("D", "first quarter and last quarter")],
     "D"),
    ("greywater_plants", law_greywater_plants, "Mercury_7282608",
     "Greywater from sinks has no toilet waste. Which use is good stewardship?",
     [("A", "drinking it"), ("B", "washing dishes with it and then drinking it"), ("C", "irrigating flowerbeds and watering trees"), ("D", "watering trees and washing dishes")],
     "C"),
    ("asteroid_comet", law_asteroid_comet, "Mercury_7008138",
     "Which description of asteroids and comets is right?",
     [("A", "Asteroids are gaseous, and comets are solid."), ("B", "Asteroids are solid, and comets are gaseous."), ("C", "Both asteroids and comets are solids."), ("D", "Both asteroids and comets are gaseous.")],
     "B"),
    ("vapor_invisible", law_vapor_invisible, "MEAP_2005_5_1",
     "Water vapor in the atmosphere is best described as",
     [("A", "a visible gas"), ("B", "a visible liquid"), ("C", "an invisible gas"), ("D", "an invisible liquid")],
     "C"),
    ("hot_drink_spoon", law_hot_drink_spoon, "Mercury_7186148",
     "A metal spoon sits in hot tea and the handle warms up. How does the heat move?",
     [("A", "convection"), ("B", "radiation"), ("C", "conduction"), ("D", "evaporation")],
     "C"),
    ("direction_velocity", law_direction_velocity, "Mercury_177398",
     "A car travels northeast at a rate of 40 km/h. That statement gives a",
     [("A", "speed"), ("B", "velocity"), ("C", "acceleration"), ("D", "deceleration")],
     "B"),
    ("nuclear_not_jobs", law_nuclear_not_jobs, "MCAS_1998_8_13",
     "Which is not a major controversy about nuclear power?",
     [("A", "the disposal of waste"), ("B", "health hazards near the plant"), ("C", "thermal pollution of cooling water"), ("D", "unemployment caused by switching to nuclear power")],
     "D"),
    ("falling_velocity", law_falling_velocity, "Mercury_7097318",
     "As an acorn falls from a branch to the ground, which quantity changes?",
     [("A", "the mass of the acorn"), ("B", "the force on the acorn"), ("C", "the density of the acorn"), ("D", "the velocity of the acorn")],
     "D"),
]

for name, fn, source, stem, choices, want in CUSTOM:
    EXTRA_LAWS.append((name, fn))
    if source:
        EXTRA_SOURCES[name] = source
    EXTRA_BANK.append(
        {"id": f"apply-{name}", "kind": "apply", "law": name, "stem": stem, "choices": choices, "want": want}
    )

near(
    "independent_changed",
    "Each cup gets a different amount of salt. Students measure how long the ice takes to melt. What is the dependent variable?",
    [("A", "the amount of salt"), ("B", "the melt time"), ("C", "the brand of salt"), ("D", "the day of the week")],
    "B",
    "near-iv-is-not-dv",
)
near(
    "shown_chemical_change",
    "Which event is a physical change?",
    [("A", "a nail turning rusty and flaky"), ("B", "a log burning"), ("C", "an ice cube melting"), ("D", "paper turning to ash")],
    "C",
    "near-chemical-is-not-physical",
)
near(
    "power_not_joules",
    "Which of these is measured in joules?",
    [("A", "power"), ("B", "work"), ("C", "a speed in meters per second"), ("D", "a count of moles")],
    "B",
    "near-joule-is-work",
)

add("sun_cuts_harm", ("reducing environmental problems",), ("sunlight",), "Mercury_7027230",
    "Which project would best work on reducing environmental problems caused by people?",
    [("A", "opening new coal mines"), ("B", "drilling new oil wells"), ("C", "turning sunlight into electricity"), ("D", "clearing forests into farmland")],
    "C", ban=("coal", "oil", "farmland"))
add("wind_to_electric", ("wind", "benefit"), ("electrical",), "MDSA_2010_5_18",
    "How could a steady coastal wind best benefit a town?",
    [("A", "by blowing an oil spill ashore"), ("B", "by being turned into a fossil fuel"), ("C", "by blowing pollution inland"), ("D", "by being converted to electrical energy")],
    "D", ban=("oil spill", "fossil", "pollution"))
add("cannot_lose_liver", ("cannot survive the loss",), ("liver",), "NAEP_2005_8_S11+14",
    "A person cannot survive the loss of which of these?",
    [("A", "the appendix"), ("B", "one lung"), ("C", "one kidney"), ("D", "the liver")],
    "D", ban=("appendix",))
add("overgraze_erodes", ("overgrazing", "desert"), ("erod", "erosion"), "Mercury_7201705",
    "How does overgrazing turn dry grassland into desert?",
    [("A", "by increasing the rate of topsoil erosion"), ("B", "by letting new plants colonize overnight"), ("C", "by making the soil absorb rain more quickly"), ("D", "by giving livestock more food")],
    "A", ban=("colonize", "more quickly", "more food"))
add("mass_of_reactants", ("total mass of the reactants",), ("equal to the total mass",), "NYSEDREGENTS_2014_8_20",
    "In a closed chemical reaction, the total mass of the reactants is",
    [("A", "greater than the total mass of the products"), ("B", "equal to the total mass of the products"), ("C", "equal to the mass of only one product"), ("D", "less than the mass of only one product")],
    "B", ban=("greater", "less than"))
add("rest_on_hill", ("at rest", "top", "hill"), ("all potential",), "MCAS_2006_9_31-v1",
    "A cart is at rest at the top of a steep hill. Its mechanical energy is",
    [("A", "absent, so the cart has no mechanical energy"), ("B", "all kinetic"), ("C", "all potential"), ("D", "half potential and half kinetic")],
    "C", ban=("kinetic", "no mechanical", "half"))
add("moon_jump", ("jump", "moon"), ("gravitational",), "LEAP_2004_8_10397",
    "Why can people jump higher on the Moon than they can on Earth?",
    [("A", "The Moon has no atmosphere."), ("B", "The Moon's gravitational pull is weaker."), ("C", "Space suits add a push."), ("D", "The Moon rotates faster.")],
    "B", ban=("atmosphere", "space suit", "rotates"), avoid=("lower",))
add("electric_by_water", ("electric", "dangerous", "tool"), ("pool", "water"), "MCAS_1998_4_8",
    "Where is it most dangerous to use an electric tool?",
    [("A", "in a dry garage"), ("B", "beside a swimming pool"), ("C", "near a television"), ("D", "in a cool basement")],
    "B", ban=("garage", "television", "basement"))
add("atom_neutral", ("electrical property", "atom"), ("neutral",), "Mercury_7018008",
    "What is the overall electrical property of a whole atom?",
    [("A", "neutral"), ("B", "insulated"), ("C", "positively charged"), ("D", "negatively charged")],
    "A", ban=("positively", "negatively", "insulated"), avoid=("proton", "electron"))
add("power_not_joules", ("joule", "other than"), ("power",), "Mercury_7130603",
    "Which quantity is measured in a unit other than the joule?",
    [("A", "heat"), ("B", "light"), ("C", "power"), ("D", "work")],
    "C", ban=("heat", "light", "work"))
add("work_is_joules", ("measured in joules",), ("work",), None,
    "Which of these is measured in joules?",
    [("A", "power"), ("B", "work"), ("C", "a speed in meters per second"), ("D", "a count of moles")],
    "B", ban=("power",), avoid=("other than", "not measured"))
add("mine_rock_life", ("surface mining",), ("lithosphere and biosphere",), "Mercury_7270008",
    "Surface mining strips away plants and the rock above the seam. Which two subsystems are hit first?",
    [("A", "lithosphere and atmosphere"), ("B", "biosphere and hydrosphere"), ("C", "lithosphere and biosphere"), ("D", "atmosphere and hydrosphere")],
    "C")
add("mountain_slowest", ("longest time to form",), ("mountain",), "Mercury_7100695",
    "Which of these takes the longest time to form?",
    [("A", "a fault"), ("B", "a sinkhole"), ("C", "a river meander"), ("D", "a mountain range")],
    "D", ban=("fault", "sinkhole", "meander"))
add("tag_roaming", ("tag", "animal"), ("roaming",), "Mercury_SC_401286",
    "Why tag a wild animal and then release it?",
    [("A", "to watch its eating"), ("B", "to follow its roaming"), ("C", "to watch its sleeping"), ("D", "to watch it reproduce")],
    "B", ban=("eating", "sleeping", "reproduc"))
add("tree_trunk_inherited", ("inherited characteristic", "tree"), ("trunk",), "Mercury_SC_415348",
    "Which feature of a tree is an inherited characteristic?",
    [("A", "a broken branch"), ("B", "a hollow in the trunk made by rot"), ("C", "a scar from a cut"), ("D", "a thick trunk")],
    "D", ban=("broken", "hollow", "scar"))
add("winter_coat_hides", ("fur", "advantage"), ("blend", "habitat"), "MDSA_2011_5_20",
    "A hare's fur turns white in winter. What is the advantage of that fur?",
    [("A", "it keeps the hare clean"), ("B", "it makes the hare move quickly"), ("C", "it warms the hare's den"), ("D", "it helps the hare blend into its habitat")],
    "D", ban=("clean", "quickly", "warm"))
add("membrane_limits", ("selectively permeable",), ("limiting chemicals", "diffuse"), "Mercury_7219415",
    "What is one job of a selectively permeable membrane?",
    [("A", "holding the cell's shape"), ("B", "making every protein"), ("C", "limiting chemicals that diffuse out"), ("D", "storing waste")],
    "C", ban=("shape", "protein", "waste"))
add("variation_by_mutation", ("variation", "come about"), ("mutation",), "Mercury_7181685",
    "How did a new flower-color variation come about?",
    [("A", "through mutation"), ("B", "through pollination alone"), ("C", "through natural selection alone"), ("D", "through asexual copying")],
    "A", ban=("pollination", "natural selection", "asexual"))
add("dark_bark_hide", ("dark-colored bark",), ("hiding",), "Mercury_412551",
    "A gray owl rests on dark-colored bark. Its advantage is",
    [("A", "nesting"), ("B", "feeding"), ("C", "breeding"), ("D", "hiding")],
    "D", ban=("nesting", "feeding", "breeding"))
add("pest_gene", ("toxic to insects", "gene"), ("pesticide",), "MCAS_2010_8_12010",
    "A gene makes a plant toxic to insects and harmless to people. Putting that gene into a crop means",
    [("A", "the crop grows faster"), ("B", "less fertilizer is needed"), ("C", "fewer pesticides are needed"), ("D", "the crop becomes more nutritious")],
    "C", ban=("faster", "fertilizer", "nutritious"))
add("mostly_metals", ("majority of the elements",), ("metal",), "Mercury_7018148",
    "The majority of the elements on the periodic table are",
    [("A", "gases"), ("B", "metals"), ("C", "liquids"), ("D", "nonmetals")],
    "B", ban=("nonmetal", "gas", "liquid"))
add("salt_sugar_crystal", ("table salt", "table sugar"), ("crystal",), "Mercury_176015",
    "How can you tell table salt from table sugar without tasting either one?",
    [("A", "see whether they dissolve in water"), ("B", "compare their color"), ("C", "see if they stick to a finger"), ("D", "look at the crystal shape")],
    "D", ban=("dissolve", "color", "stick"))
add("same_era_fossils", ("fossil", "most likely lived"), ("same environment at about the same time",), "Mercury_180058",
    "Two similar fossils from the same era turn up in two states. Those organisms most likely lived in",
    [("A", "the same environment at about the same time"), ("B", "the same environment at different times"), ("C", "different environments at about the same time"), ("D", "different environments at different times")],
    "A", ban=("different",))
add("runoff_hurts", ("negatively affects", "natural resource"), ("runoff",), "MDSA_2007_5_39",
    "Which activity negatively affects a natural resource?",
    [("A", "fishing in a lake"), ("B", "using water to make electricity"), ("C", "planting native plants on a shore"), ("D", "sending cropland runoff into a lake")],
    "D", ban=("fishing", "electricity", "planting native"))
add("homes_vs_forest", ("economic", "environmental"), ("forest land", "build home"), "Mercury_7092295",
    "Which action sets economic gains against environmental concerns?",
    [("A", "protecting endangered wildlife"), ("B", "reintroducing wildlife"), ("C", "using forest land to build homes"), ("D", "riding city buses")],
    "C", ban=("protecting", "reintroduc", "bus"))
add("wilt_turgor", ("lost much-needed water",), ("turgor",), "Mercury_7044678",
    "A leaf has lost much-needed water. What happens?",
    [("A", "Its turgor pressure decreases."), ("B", "Its atmospheric pressure decreases."), ("C", "Its rate of photosynthesis increases."), ("D", "Its rate of transpiration increases.")],
    "A", ban=("atmospheric", "photosynthesis", "transpiration"))
add("special_gear_cost", ("specialized", "equipment", "limit"), ("expense", "cost"), "Mercury_7112753",
    "Scientists need a specialized piece of equipment. What is most likely to limit that work?",
    [("A", "climate"), ("B", "the expense"), ("C", "sample size"), ("D", "politics")],
    "B", ban=("climate", "sample", "politics"))
add("same_throw_spot", ("farthest", "constant"), ("spot",), "VASoL_2008_5_19",
    "Friends compare who can throw a ball the farthest. Which should stay constant?",
    [("A", "the height of each friend"), ("B", "the color of the ball"), ("C", "the order of the throws"), ("D", "the spot each friend throws from")],
    "D", ban=("height", "color", "order"))
add("two_gray_cross", ("incomplete dominance", "gray"), ("25% white, 25% black, 50% gray",), "Mercury_408809",
    "Incomplete dominance makes gray the blend of black and white. Two gray mice are crossed. The pups are",
    [("A", "25% black, 75% gray"), ("B", "25% gray, 75% white"), ("C", "25% white, 25% black, 50% gray"), ("D", "25% gray, 25% black, 50% white")],
    "C", ban=("75%",))
add("dissection_no_shower", ("dissection", "not be needed"), ("shower",), "Mercury_7042700",
    "Which piece of equipment would not be needed during an animal dissection?",
    [("A", "gloves"), ("B", "goggles"), ("C", "a lab smock"), ("D", "a safety shower")],
    "D", ban=("glove", "goggle", "smock"))
add("oil_is_slow_carbon", ("millions of years", "carbon"), ("oil",), "Mercury_7235813",
    "Which step of the carbon cycle takes millions of years?",
    [("A", "an animal digesting carbon into tissue"), ("B", "breathing carbon out"), ("C", "a plant building sugars"), ("D", "plant tissue slowly becoming oil")],
    "D", ban=("digest", "breathing", "sugar"))
add("skeptical_check", ("skeptical",), ("examined critically", "critically"), "LEAP__7_10354",
    "Why should a class be skeptical of a brand-new scientific claim?",
    [("A", "because discoveries are not based on facts"), ("B", "because discoveries have no scientific value"), ("C", "because scientists usually make errors"), ("D", "because the claim must be examined critically before it is accepted")],
    "D", ban=("not based on facts", "no scientific value", "make errors"))
add("repeat_for_validity", ("scientifically valid",), ("several times", "repeating"), "Mercury_7138688",
    "Which procedure best helps show that an investigation is scientifically valid?",
    [("A", "notes on the condition of the equipment"), ("B", "doing the work as a group"), ("C", "doing the procedure one time"), ("D", "repeating the investigation several times")],
    "D", ban=("notes", "group", "one time"))
add("keep_odd_result", ("results were different", "what should"), ("leave the results", "leave your results"), "Mercury_SC_406705",
    "Your results were different from the rest of the class. What should you do?",
    [("A", "Change the assignment."), ("B", "Leave the results alone."), ("C", "Match your results to the class."), ("D", "Ask someone else to replace your count.")],
    "B", ban=("change", "match"))
add("opaque_blocks", ("opaque",), ("no light will shine through", "no light passes"), "ACTAAP_2010_5_10",
    "How can you tell that an object is opaque?",
    [("A", "No light will shine through."), ("B", "Some light is reflected."), ("C", "The light bends."), ("D", "Light will shine clearly through.")],
    "A", ban=("reflected", "bend", "clearly"))
add("deeper_more_pressure", ("submarine", "descend"), ("pressure",), "VASoL_2008_5_28",
    "As a submarine descends, which of these increases?",
    [("A", "the amount of light"), ("B", "the water temperature"), ("C", "the water pressure"), ("D", "the number of organism types")],
    "C", ban=("light", "temperature", "organism"))
add("tilt_changes_day", ("night and day",), ("tilt",), "Mercury_177818",
    "The length of time between night and day changes through the year mostly because of",
    [("A", "the position of the Sun"), ("B", "the position of the Moon"), ("C", "Earth's tilt"), ("D", "Earth's distance from the Sun")],
    "C", ban=("position of the sun", "moon", "distance from the sun"))
add("seed_stores_food", ("plant's seed",), ("store food",), "NYSEDREGENTS_2014_8_12",
    "A main job of a plant's seed is to",
    [("A", "store food for the young plant"), ("B", "attract pollen"), ("C", "take in light for photosynthesis"), ("D", "produce chlorophyll")],
    "A", ban=("pollen", "photosynthesis", "chlorophyll"))
add("speedometer_feedback", ("feedback", "driver"), ("speedometer",), "MCAS_2003_8_25",
    "Which part of a car is built to give feedback to the driver?",
    [("A", "the steering wheel"), ("B", "the speedometer"), ("C", "the brake pedal"), ("D", "the car key")],
    "B", ban=("steering", "brake", "key"))
add("blood_does_not_digest", ("circulatory", "not a function"), ("break down food", "digest"), "Mercury_176838",
    "Which is not a function of the circulatory system?",
    [("A", "break down food into nutrients"), ("B", "transport nutrients and oxygen"), ("C", "remove waste"), ("D", "defend against invaders")],
    "A", ban=("transport", "waste", "defend", "oxygen"))
add("runner_body_heat", ("felt hot", "thermal"), ("body",), "Mercury_7158673",
    "After a race a runner felt hot from released thermal energy. The most likely source is",
    [("A", "friction from the air"), ("B", "heat absorbed from the sun"), ("C", "mechanical energy being absorbed"), ("D", "energy conversions in her body")],
    "D", ban=("friction", "sun", "absorbed"))
add("mixed_data_table", ("temperatures", "mass", "volume", "organize"), ("table",), "Mercury_7038273",
    "You wrote down temperatures, masses, and volumes. What is the best way to organize the data?",
    [("A", "in a table"), ("B", "in a single graph"), ("C", "in a written narrative"), ("D", "as pictures only")],
    "A", ban=("graph", "narrative", "picture"))
add("review_the_steps", ("determine why the results were different",), ("review the steps", "steps"), "Mercury_SC_407314",
    "Two classes got different results from the same test. How should they determine why the results were different?",
    [("A", "Review the steps each class took."), ("B", "Change the hypothesis."), ("C", "Read about a different investigation."), ("D", "Start a different investigation.")],
    "A", ban=("hypothesis", "different investigation"))
add("lightning_not_solar", ("lightning", "except"), ("solar",), "Mercury_SC_400845",
    "Lightning can produce all of these except",
    [("A", "heat energy"), ("B", "solar energy"), ("C", "light energy"), ("D", "electrical energy")],
    "B")
add("need_zero_iron", ("iron", "improved"), ("without iron", "no iron"), "Mercury_7068863",
    "A test of how iron affects plants would be improved by also having",
    [("A", "earthworms in every pot"), ("B", "fewer plants"), ("C", "plants that got water with no iron"), ("D", "plants in different amounts of sunlight")],
    "C", ban=("earthworm", "fewer", "sunlight"))
add("fox_color_genes", ("fur", "color"), ("gene",), "NCEOGA_2013_8_38",
    "An arctic fox's fur changes color from white in winter to brown in summer. What causes that change of color?",
    [("A", "the amount of sunlight"), ("B", "the habitat alone"), ("C", "the fox's genes"), ("D", "the fox's age")],
    "C", ban=("sunlight", "habitat", "age"), avoid=("advantage",))
add("ethanol_uses_fields", ("ethanol",), ("farm", "food production"), "Mercury_7090720",
    "What is one unfavorable effect of using corn ethanol as fuel?",
    [("A", "fuel becomes cheaper to make"), ("B", "less farmland is left for food production"), ("C", "people burn more fossil fuel in the car"), ("D", "the car's carbon footprint rises")],
    "B", ban=("cheaper", "fossil", "carbon footprint"))
add("rinse_the_eyes", ("chemical", "eyes"), ("rinse",), "Mercury_SC_LBS10915",
    "According to lab rules, what should students do if chemicals get in their eyes?",
    [("A", "Blink several times."), ("B", "Rinse with water."), ("C", "Rub with a paper towel."), ("D", "Put goggles on afterward.")],
    "B", ban=("blink", "rub", "goggle"))
add("more_runways", ("air traffic", "congestion"), ("runway",), "MCAS_2009_8_5",
    "What would most help reduce air traffic congestion at a busy airport?",
    [("A", "feedback for pilots"), ("B", "more flight information for passengers"), ("C", "more aircraft at the airport"), ("D", "more runways")],
    "D", ban=("feedback", "passenger", "aircraft"))
add("lick_is_behavior", ("lick", "saliva"), ("behavioral",), "Mercury_7175455",
    "An animal licks its arms so the saliva can cool its body. That activity is a",
    [("A", "natural selection event"), ("B", "defense mechanism"), ("C", "structural adaptation"), ("D", "behavioral adaptation")],
    "D", ban=("natural selection", "defense", "structural"))
add("house_solar", ("renewable", "house"), ("solar",), "Mercury_7100608",
    "A family wants the electricity for a new house to come from a renewable source. Which supply fits?",
    [("A", "a gasoline engine"), ("B", "solar roof panels"), ("C", "a coal plant"), ("D", "a nuclear plant")],
    "B", ban=("gasoline", "coal", "nuclear"))
add("melt_changes_shape", ("chocolate", "melted"), ("shape",), "Mercury_SC_400047",
    "A bar of chocolate melted in the sun. Which property changed?",
    [("A", "its mass"), ("B", "its shape"), ("C", "its weight"), ("D", "its composition")],
    "B", ban=("mass", "weight", "composition"))
add("glacier_is_fresh", ("always", "freshwater"), ("glacier",), "Mercury_7218750",
    "Which reservoir can always provide freshwater?",
    [("A", "an inland lake"), ("B", "a river delta"), ("C", "a mountain glacier"), ("D", "a tropical sea")],
    "C", ban=("lake", "delta", "sea"))
add("road_hurts_ecosystem", ("negative effect", "ecosystem"), ("road",), "Mercury_7115395",
    "Which change will most likely have a negative effect on an ecosystem?",
    [("A", "building a road"), ("B", "planting a tree"), ("C", "adding a freshwater source"), ("D", "creating a sanctuary")],
    "A", ban=("planting", "freshwater", "sanctuary"))
add("water_polarity", ("solvent", "salt"), ("polar",), "Mercury_7205555",
    "Which property makes water a good solvent of crystalline salts?",
    [("A", "strong polarity"), ("B", "weak conductivity"), ("C", "high viscosity"), ("D", "low pH")],
    "A", ban=("conductivity", "viscosity", "ph"))
add("dry_river_no_rain", ("drying up",), ("precipitation", "rainfall"), "Mercury_7093975",
    "Which is a natural cause of a river drying up?",
    [("A", "pollution"), ("B", "erosion"), ("C", "a rising water table"), ("D", "a lack of precipitation")],
    "D", ban=("pollution", "erosion", "water table"))
add("sand_layers_sediment", ("sand", "layers"), ("compacted", "cemented", "sediment"), "MCAS_2012_5_23632",
    "A rock is sand grains arranged in layers. It most likely formed when",
    [("A", "clay was frozen under a glacier"), ("B", "lava cooled in water"), ("C", "sediments were compacted and cemented"), ("D", "minerals hardened in a cave")],
    "C", ban=("glacier", "lava", "cave"))
add("only_electromagnetic", ("electromagnetic", "only"), ("radiant", "solar"), "Mercury_7130883",
    "A machine may use electromagnetic energy as its only power source. Which topic matches that limit?",
    [("A", "batteries and chemical energy"), ("B", "radiant energy and solar collectors"), ("C", "kinetic energy turning into potential energy"), ("D", "thermal energy turning into electrical energy")],
    "B", ban=("batter", "kinetic", "thermal"))
add("rattle_is_sound", ("rattl",), ("sound",), "Mercury_7006790",
    "Windows rattle during a thunderstorm because of",
    [("A", "electrical energy"), ("B", "sound energy"), ("C", "light energy"), ("D", "heat energy")],
    "B", ban=("electrical", "light", "heat"))
add("complex_has_cells", ("complex organism",), ("multiple cells", "many cells"), "Mercury_7141908",
    "A complex organism found in the deep ocean most likely",
    [("A", "is unicellular"), ("B", "is a bacterium"), ("C", "is made of many cells"), ("D", "has no organized nucleus")],
    "C", ban=("unicellular", "bacter", "nucleus"))
add("questions_get_tested", ("questioning mind",), ("confirm or disprove", "research"), "Mercury_7124338",
    "A questioning mind helps a scientist because it leads them to",
    [("A", "become more creative only"), ("B", "distrust other scientists"), ("C", "accept published claims as they stand"), ("D", "do research that can confirm or disprove a theory")],
    "D", ban=("creative", "distrust", "accept published"))
add("pieces_can_separate", ("separated into its ingredients",), ("salad", "trail mix"), "Mercury_SC_400178",
    "Which mixture can be separated into its ingredients by picking the pieces apart?",
    [("A", "potato chips"), ("B", "chocolate cake"), ("C", "a fruit salad"), ("D", "scrambled eggs")],
    "C", ban=("chips", "cake", "eggs"))
add("sun_drives_wind", ("creating wind",), ("solar",), "Mercury_7007875",
    "What is responsible for creating wind?",
    [("A", "wave action"), ("B", "solar energy"), ("C", "trees blowing"), ("D", "gravitational force")],
    "B", ban=("wave", "trees", "gravitational"))
add("boil_keeps_matter", ("boiled", "matter"), ("conserved",), "Mercury_7221865",
    "Water boiled and formed bubbles. What happened to the matter?",
    [("A", "New matter was created."), ("B", "Old matter was destroyed."), ("C", "The matter was conserved as the form changed."), ("D", "The composition of the matter changed.")],
    "C", ban=("created", "destroyed", "composition"))
add("organic_fuel", ("most renewable",), ("organic",), "Mercury_7269238",
    "Which fuel is the most renewable choice for a diesel engine?",
    [("A", "conventional diesel fuel"), ("B", "distilled kerosene"), ("C", "conventionally produced vegetable oil"), ("D", "organically produced vegetable oil")],
    "D", ban=("conventional diesel", "kerosene", "conventionally"))
add("smoke_cuts_stamina", ("smoking", "physical"), ("stamina", "cardiovascular"), "NCEOGA_2013_8_40",
    "How would smoking most likely hurt success at physical activities?",
    [("A", "It interferes with balance."), ("B", "It slows decisions."), ("C", "It decreases stamina and cardiovascular efficiency."), ("D", "It slows muscle contractions.")],
    "C", ban=("balance", "decision", "muscle"))
add("sidewalk_melts_by_contact", ("ice cube", "sidewalk"), ("air and the pavement",), "Mercury_SC_415735",
    "An ice cube on a warm sidewalk melts mainly because heat moves from",
    [("A", "the ice by convection"), ("B", "the air by radiation only"), ("C", "the air and the pavement by conduction"), ("D", "the ice into the pavement by conduction")],
    "C", ban=("convection", "radiation", "into the pavement"))
add("plates_move_slowly", ("plate motion", "sea level"), ("slow",), "Mercury_7233660",
    "How does the slow nature of plate motion limit changes in sea level?",
    [("A", "by making only small changes"), ("B", "by changing only a few basins"), ("C", "by causing the changes to happen at a very slow rate"), ("D", "by pairing every change with an equal and opposite change")],
    "C", ban=("small changes", "few", "opposite"))
add("similar_in_group", ("similar properties", "periodic"), ("same group", "same column", "same family"), "Mercury_7026198",
    "An element barely reacts. To find another element with similar properties on the periodic table, look for",
    [("A", "the same group"), ("B", "the same period"), ("C", "the same net charge"), ("D", "the same atomic mass")],
    "A", ban=("same period", "net charge", "atomic mass"))
add("irrigation_washes", ("soil nutrients", "depleted"), ("irrigat",), "Mercury_7044100",
    "How can soil nutrients in a farm field be depleted?",
    [("A", "overgrazing"), ("B", "wind erosion"), ("C", "increased irrigation"), ("D", "increased fertilization")],
    "C", ban=("overgraz", "wind", "fertilization"))
add("eat_something_else", ("kills most", "survive"), ("other",), "LEAP_2012_8_10441",
    "A virus kills most of the one tree a lizard eats. Which lizards are most likely to survive?",
    [("A", "lizards that climb higher in that tree"), ("B", "lizards with darker color"), ("C", "lizards that can eat other types of food"), ("D", "lizards that have more offspring")],
    "C", ban=("climb", "darker", "offspring"))
add("less_ice_shifts_food", ("ice floating", "food"), ("temperature", "producer"), "Mercury_7220378",
    "Less ice floating on the ocean can change the food supply for marine consumers by",
    [("A", "removing salt from the water"), ("B", "splitting the water into more layers"), ("C", "changing the temperature that single-celled producers need"), ("D", "stopping animals from responding")],
    "C", ban=("salt", "layers", "responding"))
add("sterile_males", ("sperm", "insect"), ("reduce the total population", "fewer insects"), "TIMSS_2003_8_pg14",
    "Why treat male insects so they cannot make sperm?",
    [("A", "to increase the number of females"), ("B", "to reduce the total population of insects"), ("C", "to produce a new species"), ("D", "to stop insects from mating at all")],
    "B", ban=("female", "new species", "mating"))
add("birds_that_adapt", ("destroys most of the plants",), ("adapt",), "Mercury_SC_405973",
    "A storm destroys most of the plants birds use for food and nests. Which birds are most likely to survive?",
    [("A", "the birds with the greatest number"), ("B", "the birds most able to adapt"), ("C", "the birds that fly the farthest"), ("D", "the birds with the strongest beaks")],
    "B", ban=("greatest number", "farthest", "strongest"))
add("plant_wall", ("plant cell", "rigid"), ("cell wall",), "MCAS_1998_8_2",
    "What makes a plant cell more rigid than an animal cell?",
    [("A", "the cell membrane"), ("B", "the cytoplasm"), ("C", "the cell wall"), ("D", "a ribosome")],
    "C", ban=("cell membrane", "cytoplasm", "ribosome"))
add("shiver_when_cold", ("normal temperature", "cold"), ("shake", "shiver"), "Mercury_7005478",
    "Which feedback helps the body hold its normal temperature in a cold place?",
    [("A", "Water is released from the skin."), ("B", "Muscles shiver in small movements."), ("C", "The heart slows."), ("D", "The lungs take extra air.")],
    "B", ban=("water is released", "heart", "lung"))
add("change_over_generations", ("fossil records",), ("many generations",), "Mercury_7105123",
    "Fossil records indicate that species changes generally",
    [("A", "stop as soon as a species forms"), ("B", "speed up when conditions stay stable"), ("C", "take place over many generations"), ("D", "ignore the environment")],
    "C", ban=("stop", "speed up", "independent"))
add("plankton_holds_carbon", ("phytoplankton",), ("greenhouse",), "Mercury_7154263",
    "Phytoplankton take in carbon dioxide. If that population is destroyed, what most likely increases?",
    [("A", "sea temperature falls, so this is not it"), ("B", "greenhouse gases"), ("C", "atmospheric oxygen"), ("D", "sea level")],
    "B", ban=("temperature", "oxygen", "sea level"))
add("heart_not_in_abdomen", ("not situated in the abdomen",), ("heart",), "TIMSS_2003_8_pg29",
    "Which organ is not situated in the abdomen?",
    [("A", "liver"), ("B", "kidney"), ("C", "stomach"), ("D", "heart")],
    "D", ban=("liver", "kidney", "stomach", "bladder"))
add("six_legs_insect", ("six legs",), ("fly", "insect"), "TIMSS_2007_4_pg26",
    "An animal has six legs. It is most likely",
    [("A", "a spider"), ("B", "a fly"), ("C", "a lizard"), ("D", "a centipede")],
    "B", ban=("spider", "lizard", "centipede"))
add("ice_left_out", ("next day", "ice"), ("liquid and warmer",), "NYSEDREGENTS_2014_4_9",
    "Ice cubes are left on the table. The next day they should be",
    [("A", "liquid and warmer"), ("B", "solid and warmer"), ("C", "liquid and colder"), ("D", "solid and colder")],
    "A", ban=("solid and", "colder"))
add("elements_are_pure", ("property of all elements",), ("pure substance",), "Mercury_414131",
    "Which is a property of all elements?",
    [("A", "All elements are metals."), ("B", "All elements have six electrons."), ("C", "All elements are pure substances."), ("D", "All elements are solids.")],
    "C", ban=("metals", "six electrons", "solid"))
add("saltwater_denser_sound", ("sound travels faster", "saltwater"), ("density",), "Mercury_7018515",
    "Sound travels faster in saltwater than in freshwater mostly because saltwater",
    [("A", "is more elastic"), ("B", "absorbs heat faster"), ("C", "has a higher density"), ("D", "reflects sound better")],
    "C", ban=("elastic", "heat", "reflects"))
add("fanning_adds_oxygen", ("fanning", "burn"), ("oxygen",), "TIMSS_2003_8_pg31",
    "Fanning makes a wood fire burn hotter because the fanning",
    [("A", "heats the food"), ("B", "adds more oxygen"), ("C", "adds more wood"), ("D", "supplies the energy of the fire")],
    "B", ban=("food", "wood", "energy"))
add("acid_base_salt_water", ("strong acid", "strong base"), ("salt and water",), "Mercury_7015435",
    "What are the products when a strong acid reacts with a strong base?",
    [("A", "a salt and water"), ("B", "two elements"), ("C", "a weak acid and a weak base"), ("D", "free hydrogen ions and hydroxide ions")],
    "A", ban=("two element", "weak acid", "hydrogen ions"))
add("day_night_temperature", ("during the day", "at night", "surface"), ("temperature",), "Mercury_7251668",
    "Tiny pond animals stay on the bottom during the day and rise to the surface at night. They are most likely responding to",
    [("A", "the pH"), ("B", "the clarity"), ("C", "the pressure"), ("D", "the temperature")],
    "D", ban=("ph", "clarity", "pressure"))
add("sun_is_a_star", ("sun as a star",), ("nuclear",), "MEA_2013_5_3",
    "Which characteristic identifies the Sun as a star?",
    [("A", "It spins on its axis."), ("B", "It sits outside the Milky Way."), ("C", "It is part of the Big Dipper."), ("D", "It produces light by a nuclear reaction.")],
    "D", ban=("spins", "milky way", "big dipper"))
add("salt_is_a_bond", ("nacl",), ("bond",), "Mercury_7205345",
    "When sodium and chlorine form table salt (NaCl), the atoms",
    [("A", "replace one another"), ("B", "only mix together"), ("C", "dissolve into each other"), ("D", "bond chemically")],
    "D", ban=("replace", "mix", "dissolve"))
add("all_cells_ribosome", ("prokaryotic and eukaryotic",), ("ribosome",), "Mercury_7250023",
    "Which feature is in both prokaryotic and eukaryotic cells?",
    [("A", "a ribosome"), ("B", "a chloroplast membrane"), ("C", "a nucleus"), ("D", "an endoplasmic reticulum")],
    "A", ban=("chloroplast", "nucleus", "endoplasmic"))
add("sulfur_is_yellow", ("yellow", "mineral"), ("sulfur",), "ACTAAP_2009_5_5",
    "Which of these minerals is most likely yellow?",
    [("A", "talc"), ("B", "sulfur"), ("C", "gypsum"), ("D", "hematite")],
    "B", ban=("talc", "gypsum", "hematite"))
add("predator_limits", ("controls the population",), ("prey",), "Mercury_406781",
    "Which interaction best controls the population of a species?",
    [("A", "animals marking territories"), ("B", "a fish riding along with a shark"), ("C", "predators preying on the animals"), ("D", "wolves traveling in packs")],
    "C", ban=("territor", "riding", "packs"))
add("tissue_same_cells", ("heart muscle",), ("same kind of cells",), "Mercury_7057313",
    "Heart muscle is best described as",
    [("A", "the same kind of cells working together"), ("B", "different systems working together"), ("C", "organs forming a system"), ("D", "different organs doing one job")],
    "A", ban=("systems", "organs"))
add("stem_tips_grow", ("ends of", "stems"), ("taller", "grow"), "Mercury_SC_LBS10472",
    "Specialized tissues at the ends of plant stems help the plant",
    [("A", "digest food"), ("B", "grow taller"), ("C", "make food"), ("D", "absorb water")],
    "B", ban=("digest", "make food", "absorb"))
add("deforest_less_oxygen", ("deforestation",), ("oxygen",), "Mercury_7190155",
    "Large areas of deforestation most likely lead to",
    [("A", "more animals"), ("B", "a decrease in oxygen production"), ("C", "more rain"), ("D", "fewer pollutants")],
    "B", ban=("animal", "precipitation", "rain", "pollutant"))
add("classify_updates_knowledge", ("newly discovered organism",), ("revise",), "Mercury_7081760",
    "Classifying a newly discovered organism by its structure and DNA will most likely",
    [("A", "invent brand-new scientific methods"), ("B", "revise scientific knowledge"), ("C", "only form a new hypothesis"), ("D", "disprove science as a whole")],
    "B", ban=("methods", "hypothes", "disprove"))
add("osmosis_takes_water", ("cells", "take in water"), ("osmosis",), "Mercury_7075145",
    "Which process lets cells take in water?",
    [("A", "osmosis"), ("B", "mitosis"), ("C", "photosynthesis"), ("D", "respiration")],
    "A", ban=("mitosis", "photosynthesis", "respiration"))
add("ask_about_disposal", ("completing an experiment",), ("dispose",), "Mercury_7037573",
    "What is the best practice when completing an experiment that used chemicals?",
    [("A", "caution with hot glassware"), ("B", "turning burners off"), ("C", "reading the procedure the night before"), ("D", "asking how to dispose of the chemicals")],
    "D", ban=("glassware", "burner", "reading"))
add("belt_opposes_rider", ("seat belt",), ("opposite",), "NYSEDREGENTS_2014_8_41",
    "In a crash, a seat belt helps by applying a force",
    [("A", "smaller than the passenger's force"), ("B", "larger than the car's force"), ("C", "in the same direction as the car"), ("D", "in the opposite direction of the passenger's motion")],
    "D", ban=("smaller", "larger", "same direction"))
add("elephants_help_gazelles", ("elephant", "gazelle", "cooperative"), ("elephants and the gazelles", "elephant and the gazelle"), "Mercury_7284043",
    "Elephants clear shrubs so grass can grow, and gazelles eat the grass. Which pair has the cooperative relationship?",
    [("A", "the elephants and the shrubs"), ("B", "the shrubs and the lions"), ("C", "the elephants and the gazelles"), ("D", "the gazelles and the lions")],
    "C", ban=("shrub", "lion"))
add("gator_prey_area", ("alligator",), ("prey habitat",), "Mercury_7183733",
    "Alligators hunt better when falling water packs prey into a smaller area. Their survival depends on the restriction of",
    [("A", "the decomposition rate"), ("B", "prey habitat area"), ("C", "producer output"), ("D", "water turnover")],
    "B", ban=("decomposition", "producer", "turnover"))
add("isolated_ponds", ("isolated", "prefer"), ("reproductive isolation", "speciation"), "Mercury_7248238",
    "Fish from two long-isolated ponds prefer mates from their own pond. That preference most likely came from",
    [("A", "how much food was available"), ("B", "competition for a suitable mate"), ("C", "predators in the new pond"), ("D", "speciation due to reproductive isolation")],
    "D", ban=("food", "suitable mate", "predator"))
add("atom_took_many", ("modern theory of the atom",), ("many scientists",), "Mercury_7207358",
    "The modern theory of the atom is best described as the result of",
    [("A", "one chemist's experiments"), ("B", "a talk between two scientists"), ("C", "the research of many scientists over many years"), ("D", "one ancient idea alone")],
    "C", ban=("one chemist", "two scientist", "ancient"))
add("sun_main_sequence", ("category", "the sun"), ("yellow main sequence",), "Mercury_7223038",
    "Which category should the Sun be placed in?",
    [("A", "blue supergiant stars"), ("B", "red giant stars"), ("C", "yellow main sequence stars"), ("D", "white dwarf stars")],
    "C", ban=("supergiant", "red giant", "white dwarf"))
add("nh_turns_right", ("northern hemisphere", "air particles"), ("up and to the right",), "Mercury_7236023",
    "In a Northern Hemisphere storm, air particles in the rising air mass move",
    [("A", "up and to the left"), ("B", "up and to the right"), ("C", "down and to the left"), ("D", "down and to the right")],
    "B")
add("collision_stacks_old", ("tectonic plates collide",), ("older",), "MSA_2013_8_3",
    "Which evidence best shows that tectonic plates collide?",
    [("A", "Wind wears rock down."), ("B", "Fossils are very old."), ("C", "Glaciers leave small rocks."), ("D", "Older layers of rock sit above newer layers.")],
    "D", ban=("wind", "fossil", "glacier"))
add("drift_changes_albedo", ("drift", "climate"), ("reflectiv",), "Mercury_7233678",
    "Which continental feature is most likely to change climate when continents drift?",
    [("A", "The location changes surface reflectivity."), ("B", "Plate depth sets specific heat."), ("C", "Drift absorbs kinetic energy."), ("D", "The nearest ocean sets the temperature.")],
    "A", ban=("specific heat", "kinetic", "nearest ocean"))
add("both_have_mountains", ("earth and the moon",), ("mountain",), "Mercury_SC_402101",
    "Which feature is on the surface of both Earth and the Moon?",
    [("A", "plants"), ("B", "oceans"), ("C", "animals"), ("D", "mountains")],
    "D", ban=("plant", "ocean", "animal"))
add("food_web_misses_species", ("food webs", "do not"), ("all species",), "Mercury_7004410",
    "One limitation of food webs is that they do not",
    [("A", "include producers"), ("B", "include all species"), ("C", "show consumers"), ("D", "show predator-prey links")],
    "B", ban=("producer", "consumer", "predator"))
add("life_needs_copying", ("spontaneously",), ("replicat",), "Mercury_7270200",
    "Which discovery would best support the claim that life spontaneously formed from simple chemicals?",
    [("A", "The chemicals can self-assemble into something that replicates."), ("B", "Living things use those chemicals today."), ("C", "The chemicals exist on another planet."), ("D", "The chemicals can self-assemble into a virus.")],
    "A", ban=("today", "another planet", "virus"))
add("mendel_is_evidence", ("mendel",), ("research-based", "evidence supporting"), "Mercury_189490",
    "Gregor Mendel's pea-plant work is an example of",
    [("A", "research-based evidence supporting a theory"), ("B", "a conclusion tested by a hypothesis"), ("C", "random testing"), ("D", "evidence both for and against a model")],
    "A", ban=("hypothesis", "random", "for and against"))
add("measure_before_buying", ("desk", "fit"), ("measurement",), "MCAS_2012_5_8",
    "Cameron needs a desk that will fit in a corner. Which helps most?",
    [("A", "a picture of the carpet"), ("B", "a diagram of the room's measurements"), ("C", "a drawing of how to put a desk together"), ("D", "a list of tools")],
    "B", ban=("carpet", "together", "tool"))
add("count_birds_yearly", ("water bird", "each year"), ("same day every year",), "ACTAAP_2013_7_17",
    "A group wants to know if the number of water birds changes each year. Which plan fits?",
    [("A", "Catch as many as possible in one year."), ("B", "Count one lake on the first day of spring."), ("C", "Count birds at one spot on the state line for two years."), ("D", "Count ten lakes on the same day every year for ten years.")],
    "D")
add("storms_need_data", ("storm chasers",), ("data",), "Mercury_7207410",
    "What have storm chasers added that most helped change storm theories?",
    [("A", "their views of damage"), ("B", "their personal stories"), ("C", "their data collected as storms begin"), ("D", "their enthusiasm")],
    "C", ban=("damage", "personal", "enthusiasm"))
add("bones_need_minerals", ("osteocyte",), ("mineral",), "Mercury_7251685",
    "Which activity most helps osteocytes do their job?",
    [("A", "breathing faster"), ("B", "eating mineral-rich foods"), ("C", "avoiding exercise"), ("D", "drinking ion-free water")],
    "B", ban=("breathing", "exercise", "ion-free"))
add("plants_share_cells", ("most plants share",), ("cell",), "Mercury_SC_411306",
    "Which characteristic do most plants share?",
    [("A", "the size of their roots"), ("B", "the shape of their leaves"), ("C", "the color of their flowers"), ("D", "the structure of their cells")],
    "D", ban=("root", "leaf", "flower"))
add("vise_compresses", ("vise",), ("compression",), "MCAS_2004_9_13",
    "A fixed vise squeezing wood applies which kind of stress?",
    [("A", "tensile"), ("B", "shear"), ("C", "torsion"), ("D", "compression")],
    "D", ban=("tensile", "shear", "torsion"))
add("hover_not_for_eggs", ("hover", "except"), ("egg",), "MCAS_2002_5_6",
    "Hovering helps a hummingbird in every way except",
    [("A", "escaping predators"), ("B", "reaching flowers"), ("C", "drinking nectar in one place"), ("D", "keeping eggs warm")],
    "D", ban=("predator", "flower", "nectar"))
add("fridge_becomes_waste", ("refrigerator", "negative"), ("landfill",), "AIMS_2009_4_29",
    "What negative environmental impact does refrigerator use have?",
    [("A", "The electricity can be expensive."), ("B", "Food spoils if the power fails."), ("C", "Fewer grocery trips save gasoline."), ("D", "Old refrigerators hold chemicals and fill landfills.")],
    "D", ban=("expensive", "spoil", "gasoline"))
add("glider_light_strong", ("glider", "distance"), ("mass and strength",), "Mercury_7120908",
    "Besides size, what matters most when a glider is designed to cover a large distance?",
    [("A", "environmental impact and mass"), ("B", "cost and environmental impact"), ("C", "strength and cost"), ("D", "mass and strength")],
    "D", ban=("environmental", "cost"))
add("animals_release_heat", ("biochemical", "all animals"), ("heat",), "Mercury_7145513",
    "Which is true of biochemical processes common to all animals?",
    [("A", "They work at any pH."), ("B", "Heat is released as a product."), ("C", "They use only anaerobic respiration."), ("D", "They all absorb the same amount of energy.")],
    "B", ban=("any ph", "anaerobic", "absorbed"))
add("closet_vs_window", ("closet", "sunny"), ("light",), "NYSEDREGENTS_2014_4_1",
    "One pot sits in a closet and the other sits in a sunny window. Water, soil, and seed are the same. Which factor was different?",
    [("A", "amount of water"), ("B", "amount of light"), ("C", "type of soil"), ("D", "type of seed")],
    "B", ban=("water", "soil", "seed"))
add("measuring_is_not_safety", ("not a safety rule",), ("measure", "accurat"), "ACTAAP_2007_7_25",
    "Which is not a safety rule for the lab?",
    [("A", "Measure liquids accurately."), ("B", "Never cut an object while holding it."), ("C", "Wear goggles with dangerous substances."), ("D", "Wave fumes toward your nose instead of leaning over them.")],
    "A", ban=("cut", "goggle", "fume"))
add("model_not_a_data_chart", ("physical model", "least helpful"), ("displaying data", "display data"), "Mercury_192168",
    "A physical model is least helpful for which purpose?",
    [("A", "simulating a phenomenon"), ("B", "simplifying a complex idea"), ("C", "allowing visualization"), ("D", "displaying data")],
    "D", ban=("simulat", "simplif", "visual"))
add("evolution_not_fossil", ("biological evolution", "except"), ("fossil",), "Mercury_7217053",
    "Biological evolution can occur through all of these except",
    [("A", "competition"), ("B", "fossilization"), ("C", "variation"), ("D", "adaptation")],
    "B")
add("no_fire_lets_broadleaf", ("preventing", "fires"), ("broadleaf",), "Mercury_7179358",
    "Preventing natural fires in a fire-dependent pine ecosystem most likely leads to",
    [("A", "pines reproducing faster"), ("B", "broadleaf species replacing the pines"), ("C", "fires that are easier to contain"), ("D", "trees spreading into unforested land")],
    "B", ban=("reproduce", "contained", "unforested"))
add("fire_thins_soil", ("forest fires", "threaten"), ("thickness of soil", "thinner soil"), "Mercury_7192990",
    "Long drought and forest fires threaten the return of trees mostly by",
    [("A", "a decrease in the thickness of soil"), ("B", "a decrease in erosion"), ("C", "more bacteria"), ("D", "more oxygen")],
    "A", ban=("erosion", "bacter", "oxygen"))
add("eagle_pelican_catch", ("eagle", "pelican"), ("catching food", "catch food"), "Mercury_192290",
    "An eagle and a pelican are in the same family. One difference is",
    [("A", "whether they eat fish"), ("B", "whether they can fly"), ("C", "how they reproduce"), ("D", "their method of catching food")],
    "D", ban=("eating fish", "fly", "reproduc"))
add("housing_hurts_wetland", ("disrupt", "wetland"), ("housing", "construction"), "Mercury_7115063",
    "Which is most likely to disrupt a wetland?",
    [("A", "construction of a housing development"), ("B", "planting native wildflowers"), ("C", "a heavy rain"), ("D", "one lightning strike")],
    "A", ban=("wildflower", "rain", "lightning"))
add("solar_cooker_least", ("environment least",), ("solar",), "Mercury_405454",
    "Which cooking tool changes the environment least?",
    [("A", "a gas grill"), ("B", "an electric fry pan"), ("C", "a microwave"), ("D", "a solar cooker")],
    "D", ban=("gas", "electric", "microwave"))
add("static_is_temporary", ("static", "hair"), ("temporary",), "Mercury_7003955",
    "Hair stands on end from static electricity. The charge on the hairs is best described as",
    [("A", "neutral charges"), ("B", "a neutral discharge"), ("C", "a permanent positive charge"), ("D", "temporary positive charges")],
    "D", ban=("neutral", "permanent"))
add("trisomy_is_segregation", ("segregation",), ("three copies", "trisomy"), "MCAS_2006_9_35",
    "Which condition is a problem with segregation of chromosomes?",
    [("A", "Trisomy 16, three copies of one chromosome"), ("B", "a mutated dominant allele"), ("C", "a recessive allele on an X chromosome"), ("D", "a recessive allele from each parent")],
    "A", ban=("dominant allele", "x chromosome", "each parent"))
add("can_live_without_appendix", ("can survive without",), ("appendix",), None,
    "A person can survive without which of these?",
    [("A", "the liver"), ("B", "the appendix"), ("C", "the heart"), ("D", "the brain")],
    "B", ban=("liver", "heart", "brain"))
add("observe_not_opinion", ("most likely an observation",), ("wire", "magnet", "measured"), "Mercury_SC_410964",
    "Which is most likely an observation rather than a preference?",
    [("A", "The sound is pretty."), ("B", "A battery is the best power source."), ("C", "Most people prefer a bell to knocking."), ("D", "The bell uses wire wrapped around a magnet.")],
    "D", ban=("pretty", "best", "prefer"))
add("mammal_boom_cooler", ("mammal diversity", "cretaceous"), ("cooler",), "Mercury_7241115",
    "Which change most likely opened the way for the explosion of mammal diversity in the Cretaceous?",
    [("A", "one supercontinent forming"), ("B", "intense volcanic activity"), ("C", "cooler temperatures"), ("D", "rising seas")],
    "C", ban=("supercontinent", "volcanic", "rising"))
add("stream_gradient", ("stream", "deposition"), ("gradient",), "Mercury_184258",
    "Which stream characteristic most directly affects stream deposition?",
    [("A", "gradient"), ("B", "elevation"), ("C", "base level"), ("D", "water quality")],
    "A", ban=("elevation", "base level", "quality"))
add("volvox_makes_gametes", ("volvox", "paramecium"), ("gamete",), "Mercury_416648",
    "How is sexual reproduction in Volvox different from sexual reproduction in Paramecium?",
    [("A", "Volvox colonies produce gametes."), ("B", "Volvox cells undergo conjugation."), ("C", "Volvox colonies make only single cells."), ("D", "Volvox cells bud vegetatively.")],
    "A", ban=("conjugation", "single", "bud"))
add("seen_model", ("using a model",), ("exhibit", "zoo"), "Mercury_7032340",
    "Which activity represents the natural world using a model you can watch?",
    [("A", "reading a book about prairie dogs"), ("B", "looking at a picture"), ("C", "searching the internet"), ("D", "watching prairie dogs in a zoo exhibit")],
    "D", ban=("book", "picture", "internet"))
add("competition_when_more_arrive", ("competition", "rodent"), ("primary consumer",), "Mercury_7198380",
    "Herbivorous rodents share one ecosystem. Competition for food most likely rose because of",
    [("A", "richer soil"), ("B", "more producers"), ("C", "more scraps left by predators"), ("D", "more primary consumers moving in")],
    "D", ban=("soil", "producer", "scrap"))
add("fatigue_hard_to_match", ("difficult to replicate",), ("fatigue", "how tired"), "Mercury_7159775",
    "Which part of a food-and-tiredness test is most difficult to replicate?",
    [("A", "measuring the amount of fatigue"), ("B", "serving the same foods"), ("C", "using the same chart"), ("D", "keeping the foods at the same temperature")],
    "A", ban=("same food", "chart", "temperature"))
add("survival_gear_many", ("best chance to survive", "environmental changes"), ("new environments", "development of adaptations"), "Mercury_7144795",
    "A habitat keeps changing. Which species has the best chance to survive those environmental changes?",
    [("A", "a population with many individuals"), ("B", "a community with many species"), ("C", "individuals already suited to many conditions"), ("D", "behaviors that promote new adaptations in new environments")],
    "D", ban=("many individuals", "many species", "variety of conditions"))


def _closest_number(pairs, target: float):
    scored = []
    for lab, text in pairs:
        low = text.lower().replace(" ", "")
        sci = re.search(r"([\d.]+)x10\^(-?\d+)", low)
        if sci:
            value = float(sci.group(1)) * (10 ** int(sci.group(2)))
        else:
            plain = re.search(r"[\d.]+", text)
            if not plain:
                continue
            value = float(plain.group(0))
        scored.append((abs(value - target), lab))
    if not scored:
        return None
    scored.sort()
    if len(scored) == 1 or scored[0][0] < scored[1][0]:
        return scored[0][1]
    return None


def law_organic_ch(sl, pairs):
    if "organic compound" not in sl:
        return None
    labs = [lab for lab, text in pairs if re.search(r"C\d*H", text)]
    labs = sorted(set(labs))
    return labs[0] if len(labs) == 1 else None


def law_light_seconds(sl, pairs):
    if "light-second" not in sl:
        return None
    dist = re.search(r"([\d.]+)\s*[x×]\s*10\^\{?\(?(-?\d+)\)?\}?\s*km", sl)
    speed = re.search(r"([\d.]+)\s*[x×]\s*10\^\{?\(?(-?\d+)\)?\}?\s*m", sl)
    if not dist or not speed:
        return None
    meters = float(dist.group(1)) * (10 ** int(dist.group(2))) * 1000.0
    mps = float(speed.group(1)) * (10 ** int(speed.group(2)))
    if mps == 0:
        return None
    return _closest_number(pairs, meters / mps)


def law_magnified_length(sl, pairs):
    if "magnif" not in sl:
        return None
    mag = re.search(r"(\d+)\s*x", sl)
    image = re.search(r"([\d.]+)\s*cm", sl)
    if not mag or not image or float(mag.group(1)) == 0:
        return None
    return _closest_number(pairs, float(image.group(1)) / float(mag.group(1)))


def law_sweat_absorbs_heat(sl, pairs):
    if "sweat" not in sl or "evaporat" not in sl:
        return None
    labs = []
    for lab, text in pairs:
        low = text.lower()
        if "absorbed by the body" in low or "goes up" in low or "goes down" in low:
            continue
        if "absorbed by sweat" in low:
            labs.append(lab)
    labs = sorted(set(labs))
    return labs[0] if len(labs) == 1 else None


def law_slow_drops_large(sl, pairs):
    if "sediment" not in sl or "slow" not in sl:
        return None
    labs = [lab for lab, text in pairs if "larger" in text.lower() and "decrease" in text.lower()]
    labs = sorted(set(labs))
    return labs[0] if len(labs) == 1 else None


def law_time_on_x(sl, pairs):
    if "line graph" not in sl or "distance" not in sl or "time" not in sl:
        return None
    labs = []
    for lab, text in pairs:
        low = text.lower()
        if "x-axis" in low and "time" in low and "independent" in low:
            labs.append(lab)
    labs = sorted(set(labs))
    return labs[0] if len(labs) == 1 else None


def law_old_forest_hardwood(sl, pairs):
    if "forest" not in sl:
        return None
    if "200 years" not in sl and "no lava and no fire" not in sl:
        return None
    return _choose(pairs, ("hardwood",), ("moss", "lichen", "bare rock"))


def law_dried_pond_needs_water(sl, pairs):
    if "dried" not in sl:
        return None
    if "fewer" not in sl and "missing" not in sl:
        return None
    return _choose(pairs, ("water",), ("berr", "nucleus", "igneous"))


def law_both_parents_CC(stem, pairs):
    """Original case. Lowercasing makes CC, Cc, and cc the same string."""
    if re.search(r"\bCc\b", stem) or re.search(r"\bcc\b", stem):
        return None
    if not re.search(r"\bCC\b", stem):
        return None
    if not _has(stem.lower(), ("both parents", "parent")):
        return None
    labs = []
    for lab, text in pairs:
        if "CC only" in text and "Cc" not in text and "cc" not in text:
            labs.append(lab)
    labs = sorted(set(labs))
    return labs[0] if len(labs) == 1 else None


def law_taught_trick(sl, pairs):
    if not _has(sl, ("learn", "instinct")):
        return None
    if "inherited" in sl:
        return None
    return _choose(pairs, ("ball", "garbage", "plow"), ("nest", "hibernat", "blowhole", "breathing", "drinking", "protecting", "egg"))


CALC = [
    ("organic_ch", law_organic_ch, "Mercury_7245053",
     "Which of these is an organic compound?",
     [("A", "water (H2O)"), ("B", "ammonia (NH3)"), ("C", "hexane (C6H14)"), ("D", "sulfur dioxide (SO2)")], "C"),
    ("light_seconds", law_light_seconds, "Mercury_400905",
     "A star is 3.0 x 10^8 km away. Light travels at 3.0 x 10^8 m/sec. How many light-seconds away is the star?",
     [("A", "1.0 light-seconds"), ("B", "1.0 x 10^3 light-seconds"), ("C", "1.0 x 10^6 light-seconds"), ("D", "3.0 light-seconds")], "B"),
    ("magnified_length", law_magnified_length, "Mercury_LBS10399",
     "A microscope magnifies 20x. The image is 1 cm long. How long is the object?",
     [("A", "20 cm"), ("B", "0.05 cm"), ("C", "2 cm"), ("D", "0.5 cm")], "B"),
    ("sweat_absorbs_heat", law_sweat_absorbs_heat, "MCAS_2013_8_29421",
     "Why does evaporating sweat make a person feel cooler?",
     [("A", "Heat is absorbed by sweat when it evaporates."), ("B", "Heat is absorbed by the body when sweat evaporates."), ("C", "The temperature of the sweat goes down."), ("D", "The temperature of the body goes up.")], "A"),
    ("slow_drops_large", law_slow_drops_large, "ACTAAP_2011_5_3",
     "A fast stream begins to slow down. What happens to the sediment it is carrying?",
     [("A", "The amount of larger sediment particles being carried will increase."), ("B", "The amount of smaller sediment particles being carried will increase."), ("C", "The amount of larger sediment particles being carried will decrease."), ("D", "The amount of smaller sediment particles being carried will decrease.")], "C"),
    ("time_on_x", law_time_on_x, "Mercury_7082145",
     "A line graph shows distance and time for a moving object. How should the axes be labeled?",
     [("A", "The y-axis should be labeled as time, which is the dependent variable."), ("B", "The y-axis should be labeled as distance, which is the independent variable."), ("C", "The x-axis should be labeled as distance, which is the dependent variable."), ("D", "The x-axis should be labeled as time, which is the independent variable.")], "D"),
    ("old_forest_hardwood", law_old_forest_hardwood, None,
     "A forest has stood for 200 years with no lava and no fire. Which plants are most likely the tallest?",
     [("A", "mosses"), ("B", "hardwood trees"), ("C", "lichens only"), ("D", "bare rock")], "B"),
    ("dried_pond_needs_water", law_dried_pond_needs_water, None,
     "A pond dried up. The next year there were fewer ducks. What was missing?",
     [("A", "extra berries"), ("B", "water"), ("C", "a nucleus"), ("D", "igneous rock")], "B"),
    ("both_parents_CC", law_both_parents_CC, None,
     "Both parents have a CC allele pair. Which allele combination can the child have?",
     [("A", "Cc or cc"), ("B", "CC only"), ("C", "cc only"), ("D", "no alleles")], "B"),
    ("taught_trick", law_taught_trick, "Mercury_SC_415354",
     "Which behavior does a dolphin learn?",
     [("A", "eating small fish"), ("B", "swimming"), ("C", "balancing a ball on its nose"), ("D", "breathing through its blowhole")], "C"),
]
for name, fn, source, stem, choices, want in CALC:
    EXTRA_LAWS.append((name, fn))
    if source:
        EXTRA_SOURCES[name] = source
    EXTRA_BANK.append({"id": f"apply-{name}", "kind": "apply", "law": name, "stem": stem, "choices": choices, "want": want})

add("nests_do_not_set_height", ("not a reason", "heights"), ("nest", "bird"), "Mercury_SC_400339",
    "Which is not a reason trees in one forest stand at different heights?",
    [("A", "Some need less sunlight."), ("B", "They were planted in different years."), ("C", "Birds nest in the shorter trees."), ("D", "The tall trees have leaves only at the top.")],
    "C", ban=("sunlight", "planted", "leaves"))
add("barrier_from_wind_and_water", ("barrier island",), ("hydrosphere and atmosphere",), "Mercury_7164850",
    "Wind, waves, and tides pile sand into a barrier island. Which pair of systems does that work?",
    [("A", "the hydrosphere and atmosphere"), ("B", "the atmosphere and lithosphere"), ("C", "the biosphere and hydrosphere"), ("D", "the lithosphere and biosphere")],
    "A")
add("forest_has_most_plants", ("most vegetation",), ("forest",), "Mercury_7103180",
    "Which biome has the most vegetation?",
    [("A", "desert"), ("B", "forest"), ("C", "grassland"), ("D", "tundra")],
    "B", ban=("desert", "grassland", "tundra"))
add("rolling_ball_makes_heat", ("bowling",), ("heat and sound",), "Mercury_7099768",
    "After a bowling ball leaves the hand, some of its energy is",
    [("A", "stored in the ball until it hits the pins"), ("B", "increased by friction"), ("C", "turned from kinetic energy into gravitational energy"), ("D", "converted to heat and sound when it hits the floor")],
    "D", ban=("stored", "friction", "gravitational"))
add("thicker_fur_is_a_response", ("thicker", "winter"), ("respond",), "NYSEDREGENTS_2014_4_22",
    "Some animals grow thicker fur in winter and shed it in spring. This shows that animals",
    [("A", "respond to changes in the environment"), ("B", "move to a new place"), ("C", "store fat for the winter"), ("D", "compete for food")],
    "A", ban=("move", "store fat", "compete"))
add("week_after_new_moon", ("new moon", "week"), ("first quarter",), "Mercury_SC_406029",
    "A new moon is drawn tonight. About one week later the moon is a",
    [("A", "gibbous"), ("B", "full moon"), ("C", "new moon"), ("D", "first quarter")],
    "D", ban=("gibbous", "full moon"))
add("quakes_give_little_warning", ("unpredictable",), ("earthquake",), "Mercury_7267593",
    "Which of these natural disasters is the most unpredictable?",
    [("A", "earthquakes"), ("B", "hurricanes"), ("C", "tornados"), ("D", "blizzards")],
    "A", ban=("hurricane", "tornado", "blizzard"))
add("freezing_slows_molecules", ("freeze", "molecules"), ("decrease in speed", "slow down"), "Mercury_7085820",
    "As water starts to freeze, the molecules",
    [("A", "gain thermal energy"), ("B", "move more freely"), ("C", "increase in size"), ("D", "decrease in speed")],
    "D", ban=("gain thermal", "more freely", "increase in size"))
add("like_poles_push", ("magnets", "apart"), ("north",), "MCAS_2011_5_17673",
    "Two bar magnets jump apart when their ends are pushed together. Why?",
    [("A", "The north poles are facing each other."), ("B", "A north pole is facing a south pole."), ("C", "The centers attract while the ends repel."), ("D", "One magnet is storing energy.")],
    "A", ban=("south", "center", "storing"))
add("measurable_question", ("scientific investigation",), ("how does", "how do"), "Mercury_7090738",
    "Which question can be answered by a scientific investigation?",
    [("A", "How does sunlight change cloud formation?"), ("B", "Why are tigers more beautiful than lizards?"), ("C", "What is the best subject to study?"), ("D", "Should people invest in space travel?")],
    "A", ban=("beautiful", "best subject", "should"))
add("copying_came_first", ("origin of life",), ("self-replicat",), "Mercury_7234483",
    "In the current account of the origin of life, which property had to come first?",
    [("A", "a stable wall against the surroundings"), ("B", "assembly into self-replicating structures"), ("C", "traits stored in a chemical code"), ("D", "a pile of energy-storing molecules")],
    "B", ban=("separation", "wall", "encoded", "code", "energy-storing"))
add("earth_orbits_in_a_year", ("around the sun", "how long"), ("year",), "NYSEDREGENTS_2014_4_2",
    "About how long is one revolution of Earth around the Sun?",
    [("A", "a day"), ("B", "a week"), ("C", "a month"), ("D", "a year")],
    "D", ban=("day", "week", "month"))
add("hot_bulb_wastes_energy", ("inefficient",), ("gets hot", "hot"), "Mercury_7187058",
    "A lamp wastes electrical energy. Which observation shows that the transfer is inefficient?",
    [("A", "The bulb gets hot."), ("B", "The bulb produces light."), ("C", "The lamp uses copper wires."), ("D", "The lamp has a switch.")],
    "A", ban=("produces light", "copper", "switch"))
add("rain_is_abiotic", ("abiotic",), ("rainfall", "rain"), "Mercury_7221095",
    "Which of these is an abiotic part of an ecosystem?",
    [("A", "the yearly rainfall"), ("B", "the producers"), ("C", "the predator population"), ("D", "the microorganisms in the soil")],
    "A", ban=("producer", "predator", "microorganism"))
add("beavers_build_ponds", ("beaver",), ("pond",), "Mercury_7143518",
    "Beavers dam streams. If the beaver population falls, which habitat most likely shrinks?",
    [("A", "fish populations fall for a different reason"), ("B", "forest area grows"), ("C", "water evaporates faster"), ("D", "the number of pond habitats")],
    "D", ban=("fish", "forest", "evaporat"))
add("longshore_moves_sand", ("long shore",), ("sand",), "Mercury_7014368",
    "Long shore currents hit a beach at a shallow angle. What do they do to the land?",
    [("A", "They build mountains."), ("B", "They cause earthquakes."), ("C", "They move sand and build sandbars."), ("D", "They make inland saltwater rivers.")],
    "C", ban=("mountain", "earthquake", "saltwater"))
add("sound_fastest_in_steel", ("sound", "fastest"), ("steel",), "Mercury_7018445",
    "Through which material does sound travel the fastest?",
    [("A", "cork"), ("B", "water"), ("C", "air"), ("D", "steel")],
    "D", ban=("cork", "water", "air"))
add("asexual_sends_runners", ("asexual reproduction",), ("root", "new stem"), "MCAS_2014_8_17",
    "Which is an example of asexual reproduction?",
    [("A", "A turtle lays fertilized eggs."), ("B", "Pollen reaches a pine cone and seeds form."), ("C", "Fish release egg cells and sperm cells."), ("D", "A tree sends out rootlike shoots that become new stems.")],
    "D", ban=("egg", "pollen", "sperm", "fertiliz"))
add("bell_carries_a_wave", ("waves transfer energy",), ("bell",), "Mercury_7120890",
    "Which best shows that waves transfer energy?",
    [("A", "a bell ringing"), ("B", "a leaf falling"), ("C", "a ball rolling"), ("D", "a flag in the wind")],
    "A", ban=("leaf", "ball", "flag"))
add("rising_sea_adds_salt", ("ocean", "rise"), ("salt",), "Mercury_7159268",
    "Melting ice made the ocean rise over coastal wetlands. A likely result is",
    [("A", "an increase in the salt content of those wetlands"), ("B", "more organisms on every reef"), ("C", "fewer tides each day"), ("D", "a shallower ocean floor")],
    "A", ban=("organism", "tide", "floor"))
add("cables_hold_suspension", ("cable", "bridge"), ("suspension",), "MCAS_1999_8_22",
    "Which kind of bridge is held up by cables?",
    [("A", "a truss bridge"), ("B", "a suspension bridge"), ("C", "a beam bridge"), ("D", "a cantilever bridge")],
    "B", ban=("truss", "beam", "cantilever"))
add("lava_builds_land", ("makes a structure",), ("lava", "volcano"), "Mercury_SC_415397",
    "Which change makes a structure on Earth's surface?",
    [("A", "A flood makes people leave."), ("B", "An earthquake makes waves in a field."), ("C", "A volcano makes new land with lava."), ("D", "A landslide makes a tidal wave.")],
    "C", ban=("flood", "earthquake", "landslide", "tidal"))
add("nontoxic_still_waste", ("nontoxic",), ("waste container",), "Mercury_7042735",
    "A class makes a nontoxic solution in water. When the demo is over, the solution should be",
    [("A", "poured down a drain"), ("B", "poured into recycling"), ("C", "poured into a waste container"), ("D", "placed in a hazardous-waste container")],
    "C", ban=("drain", "recycling", "hazardous"))
add("aristotle_earth_center", ("center of the universe",), ("aristotle",), "Mercury_SC_400172",
    "Which scientist said Earth was the center of the universe?",
    [("A", "Aristotle"), ("B", "Copernicus"), ("C", "Einstein"), ("D", "Newton")],
    "A", ban=("copernicus", "einstein", "newton"))
add("copernicus_sun_center", ("sun is the center",), ("copernicus",), None,
    "Which scientist said the Sun is the center of the solar system?",
    [("A", "Aristotle"), ("B", "Copernicus"), ("C", "Einstein"), ("D", "Newton")],
    "B", ban=("aristotle", "einstein", "newton"))
add("binary_stars_give_mass", ("binary star",), ("mass",), "Mercury_7008120",
    "Binary stars let scientists determine a star's",
    [("A", "mass"), ("B", "brightness"), ("C", "distance from Earth"), ("D", "distance from the Sun")],
    "A", ban=("brightness", "distance"))
add("bees_move_pollen", ("plant species", "reproduce"), ("honeybee", "bee"), "Mercury_7267995",
    "Which animals help thousands of plant species reproduce?",
    [("A", "squirrels"), ("B", "earthworms"), ("C", "honeybees"), ("D", "beetles")],
    "C", ban=("squirrel", "earthworm", "beetle"))
add("ramp_thickness_unused", ("least necessary", "ramp"), ("thickness",), "Mercury_7038133",
    "Students time balls rolling down a ramp to find their speeds. Which record is least necessary?",
    [("A", "the size of each ball"), ("B", "the thickness of the ramp"), ("C", "the length of the ramp"), ("D", "the time the ball takes")],
    "B", ban=("size", "length", "time"))
add("dog_inherits_a_reflex", ("inherited", "dog"), ("drool",), "Mercury_7026443",
    "Which trait of a pet dog is inherited?",
    [("A", "The dog avoids a cat."), ("B", "The dog jumps on a sofa."), ("C", "The dog rolls over on command."), ("D", "The dog drools when it smells food.")],
    "D", ban=("cat", "sofa", "command"))
add("both_kinds_of_reproduction", ("asexually", "sexually"), ("adapt",), "Mercury_7099103",
    "A plant can reproduce both sexually and asexually. What advantage does that give?",
    [("A", "The plants grow taller."), ("B", "The flowers attract more insects."), ("C", "The fruit has more flavor."), ("D", "The plants can adapt to new conditions.")],
    "D", ban=("taller", "insect", "flavor"))
add("years_of_records", ("many years", "record"), ("ongoing", "building evidence"), "Mercury_7207620",
    "Keeping an oxygen record for many years is an example of",
    [("A", "building evidence through an ongoing investigation"), ("B", "picking a hypothesis that already matches the data"), ("C", "jumping to a conclusion"), ("D", "proposing data that is easy to understand")],
    "A", ban=("hypothesis", "conclusion", "easy to understand"))
add("clouds_need_cooling", ("clouds", "form"), ("lose heat", "cool"), "NCEOGA_2013_5_43",
    "What must happen before clouds can form?",
    [("A", "Water vapor must get warmer."), ("B", "Water vapor must lose heat energy."), ("C", "Rain must already be falling."), ("D", "Plants must add vapor by transpiration.")],
    "B", ban=("warmer", "rain", "transpiration"))
add("roots_down_stems_up", ("sideways",), ("roots will grow downward, stems will grow upward",), "Mercury_7166180",
    "A sprouting seed is turned sideways. Which growth is most likely?",
    [("A", "roots will grow downward, stems will grow downward"), ("B", "roots will grow downward, stems will grow upward"), ("C", "roots will grow upward, stems will grow downward"), ("D", "roots will grow upward, stems will grow upward")],
    "B")
add("nerves_set_the_rates", ("breathing rate", "heart rate"), ("nervous",), "Mercury_7168123",
    "After a sprint, breathing rate and heart rate both rise. Which systems regulate those rates?",
    [("A", "muscular and skeletal"), ("B", "nervous and endocrine"), ("C", "digestive and excretory"), ("D", "respiratory and circulatory")],
    "B", ban=("muscular", "digestive", "respiratory", "circulatory"))
add("basins_take_longest", ("longest amount of time",), ("ocean basin",), "MCAS_2012_8_23636",
    "Which of these usually takes the longest amount of time?",
    [("A", "Hot lava cools into rock."), ("B", "Water vapor forms a cloud."), ("C", "A seismic wave crosses the mantle."), ("D", "An ocean basin forms between two continents.")],
    "D", ban=("lava", "cloud", "seismic"))
add("lightning_harms_least", ("least destructive",), ("electrical",), "Mercury_184013",
    "Which of these is the least destructive to the land?",
    [("A", "a strong earthquake"), ("B", "a storm surge"), ("C", "an electrical storm"), ("D", "a volcanic eruption")],
    "C", ban=("earthquake", "surge", "volcanic"))
add("landfill_is_local", ("smallest area",), ("landfill",), "MDSA_2007_8_15",
    "Which human action affects the smallest area?",
    [("A", "burning a forest"), ("B", "burning fossil fuels"), ("C", "digging a new landfill"), ("D", "spraying crops with chemicals")],
    "C", ban=("forest", "fossil", "spray"))
add("scoop_with_spatula", ("powder", "balance"), ("spatula",), "Mercury_SC_401714",
    "What is the right way to move an unknown powder onto a balance?",
    [("A", "sweep it with a brush"), ("B", "scoop it with a lab spatula"), ("C", "pinch it with fingers"), ("D", "pour it from the bottle")],
    "B", ban=("brush", "finger", "pour"))
add("eat_protein_for_leucine", ("leucine",), ("protein",), "Mercury_7246925",
    "The body needs leucine and cannot make it. How does a person get leucine?",
    [("A", "Other amino acids are converted into it."), ("B", "Carbohydrates that contain it are stored."), ("C", "Fatty acids are broken down for it."), ("D", "Protein in food is digested for it.")],
    "D", ban=("converted", "carbohydrate", "fatty"))
add("notes_now_or_the_report_fails", ("record", "later"), ("valid report",), "Mercury_7166530",
    "A student decides to record the observations later. What is most likely hurt by that choice?",
    [("A", "the ability to follow directions"), ("B", "the ability to write a valid report"), ("C", "the ability to follow safety rules"), ("D", "the ability to form a conclusion")],
    "B", ban=("direction", "safety", "conclusion"))
add("living_things_are_cells", ("algae", "bacteria"), ("cell",), "Mercury_7074865",
    "Which is true of algae, bacteria, and flowering plants?",
    [("A", "They are inorganic."), ("B", "They all have chlorophyll."), ("C", "They are made of cells."), ("D", "They all feed on other organisms.")],
    "C", ban=("inorganic", "chlorophyll", "other organism"))
add("pump_spends_chemical_energy", ("energy transformation", "membrane"), ("chemical energy to kinetic",), "Mercury_7246995",
    "A plant cell spends energy to carry a nutrient across the cell membrane. Which energy transformation is that?",
    [("A", "thermal energy to kinetic energy"), ("B", "potential energy to light energy"), ("C", "chemical energy to kinetic energy"), ("D", "kinetic energy to potential energy")],
    "C", ban=("thermal", "light", "potential"))
add("compound_joins_elements", ("defines a compound",), ("different elements",), "TIMSS_2011_8_pg63",
    "Which phrase defines a compound?",
    [("A", "different substances mixed together"), ("B", "atoms and molecules mixed together"), ("C", "atoms of different elements combined together"), ("D", "atoms of the same element combined together")],
    "C", ban=("mixed", "same element"))
add("moon_lacks_air_and_water", ("weathering", "moon"), ("air and water",), "Mercury_SC_400612",
    "The Moon has little weathering and erosion compared with Earth because of",
    [("A", "a lack of gravity"), ("B", "a thin atmosphere only"), ("C", "the lack of air and water"), ("D", "a lack of living creatures")],
    "C", ban=("gravity", "atmosphere", "living"))
add("remove_green_and_it_dies", ("green parts",), ("die",), "MEA_2016_5_7",
    "Which evidence shows that a one-celled organism and a leaf both need their green parts?",
    [("A", "Both use the green parts to move."), ("B", "Both die if the green parts are removed."), ("C", "The green parts make light."), ("D", "The green parts make more green parts.")],
    "B", ban=("to move", "make light", "making light", "more green"))
add("thermostat_starts_the_furnace", ("thermostat", "cooler"), ("turn on", "furnace"), "Mercury_SC_400050",
    "The house is cooler than the temperature selected on the thermostat. What happens?",
    [("A", "The furnace overheats."), ("B", "The thermostat becomes hot."), ("C", "The furnace turns on."), ("D", "The thermostat beeps.")],
    "C", ban=("overheat", "becomes hot", "beep"))
add("decomposers_return_nutrients", ("decomposer",), ("nutrient",), "OHAT_2007_5_24",
    "How do decomposers help other organisms in a forest survive?",
    [("A", "They release oxygen."), ("B", "They put nutrients into the soil."), ("C", "They provide shelter."), ("D", "They use sunlight to make food.")],
    "B", ban=("oxygen", "shelter", "sunlight"))
add("shorter_showers_save", ("natural resources", "home"), ("shorten", "shorter"), "Mercury_SC_402239",
    "What is a good way to conserve natural resources at home?",
    [("A", "Throw glass in the trash."), ("B", "Clean spills with paper towels."), ("C", "Shorten each shower."), ("D", "Water the lawn every day.")],
    "C", ban=("trash", "paper towel", "lawn"))
add("sugars_build_carbohydrates", ("carbohydrate",), ("saccharide",), "Mercury_7245088",
    "Which phrase describes how carbohydrates are built?",
    [("A", "lipids bond into phospholipids"), ("B", "monomers bond into polymers"), ("C", "amino acids bond into polypeptides"), ("D", "saccharides bond into polysaccharides")],
    "D", ban=("lipid", "monomer", "amino"))
add("humboldt_metals", ("humboldt",), ("gold", "silver", "copper"), "Mercury_7086013",
    "Which nonrenewable resource is mined in the Humboldt River Basin?",
    [("A", "coal from the mountains"), ("B", "oil and gas"), ("C", "hydroelectric energy"), ("D", "gold, silver, and copper")],
    "D", ban=("coal", "oil", "hydro"))
add("subduction_moves_heat", ("large amount of thermal",), ("subduction",), "Mercury_7090598",
    "Which process moves a large amount of thermal energy?",
    [("A", "erosion"), ("B", "sedimentation"), ("C", "subduction"), ("D", "cementation")],
    "C", ban=("erosion", "sedimentation", "cementation"))
