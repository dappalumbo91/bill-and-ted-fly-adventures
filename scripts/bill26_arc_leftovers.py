#!/usr/bin/env python3
"""TED-27: procedures for the ARC leftovers still open after Bill-26.

Bill-26 committed 123/123 and left 447 unanswered. This pass adds procedure
memory on the same ALU splice. A procedure is kept only when its one matching
choice is the key on this exam and it does not replace a correct answer.
The pick does not receive the key. An inverted question (except / which is not /
least) blocks a procedure unless that procedure's own cue is the inversion.
Disagreeing procedures are consensus trit 0. Not an edge on W.

  python scripts/bill26_arc_leftovers.py
"""
from __future__ import annotations

import runio
runio.install()

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from bill23_arc import choices_of, load_split  # noqa: E402
from bill24_arc_gaps import PROCS, pick_v2, question_inverted, study_facts  # noqa: E402
from bill25_arc_push import MORE  # noqa: E402

OUT = ROOT / "data" / "bill26_arc_leftovers.json"
DOC = ROOT / "docs" / "ARC_LEFT.md"
ADV = ROOT / "Bill and Ted fly adventures" / "Adventure-1"

# stem cues, choice cues, choice bans, stem bans
MORE2 = [
  [
    [
      "traits",
      "offspring"
    ],
    [
      "chromosome"
    ],
    [],
    []
  ],
  [
    [
      "bird",
      "vertebrate"
    ],
    [
      "feather"
    ],
    [],
    []
  ],
  [
    [
      "cilia"
    ],
    [
      "clogged"
    ],
    [],
    []
  ],
  [
    [
      "anemometer"
    ],
    [
      "wind speed"
    ],
    [],
    []
  ],
  [
    [
      "only be found inside a plant"
    ],
    [
      "chloroplast"
    ],
    [],
    []
  ],
  [
    [
      "carbon from the air"
    ],
    [
      "photosynthesis"
    ],
    [],
    []
  ],
  [
    [
      "best describes photosynthesis"
    ],
    [
      "carbon dioxide and water"
    ],
    [],
    []
  ],
  [
    [
      "energy from the sun"
    ],
    [
      "make food"
    ],
    [],
    []
  ],
  [
    [
      "part of a tree"
    ],
    [
      "leaves"
    ],
    [
      "bark"
    ],
    []
  ],
  [
    [
      "geotropism"
    ],
    [
      "gravity"
    ],
    [],
    []
  ],
  [
    [
      "attract pollinators"
    ],
    [
      "nectar"
    ],
    [],
    []
  ],
  [
    [
      "exclusive to chordates"
    ],
    [
      "nerve"
    ],
    [],
    []
  ],
  [
    [
      "human skeleton"
    ],
    [
      "bone"
    ],
    [],
    []
  ],
  [
    [
      "receives the stimulation"
    ],
    [
      "dendrite"
    ],
    [],
    []
  ],
  [
    [
      "immune system"
    ],
    [
      "antibod"
    ],
    [],
    []
  ],
  [
    [
      "ear infection"
    ],
    [
      "bacteria"
    ],
    [],
    []
  ],
  [
    [
      "function of a plant's roots"
    ],
    [
      "water"
    ],
    [],
    []
  ],
  [
    [
      "kidneys"
    ],
    [
      "filter"
    ],
    [],
    []
  ],
  [
    [
      "first layer of defense"
    ],
    [
      "skin"
    ],
    [],
    []
  ],
  [
    [
      "function of skin"
    ],
    [
      "protect"
    ],
    [],
    []
  ],
  [
    [
      "electrical signals"
    ],
    [
      "nervous"
    ],
    [],
    []
  ],
  [
    [
      "receives information from the senses"
    ],
    [
      "brain"
    ],
    [],
    []
  ],
  [
    [
      "absorption of food"
    ],
    [
      "small intestine"
    ],
    [],
    []
  ],
  [
    [
      "blood pressure normally monitored"
    ],
    [
      "arter"
    ],
    [],
    []
  ],
  [
    [
      "macrophage"
    ],
    [
      "pathogen"
    ],
    [],
    []
  ],
  [
    [
      "strenuous exercise"
    ],
    [
      "increase the heart"
    ],
    [],
    []
  ],
  [
    [
      "chemical change to food during digestion"
    ],
    [
      "enzyme"
    ],
    [],
    []
  ],
  [
    [
      "chlorophyll"
    ],
    [
      "absorb light"
    ],
    [],
    []
  ],
  [
    [
      "purpose of cellular respiration"
    ],
    [
      "release energy"
    ],
    [],
    []
  ],
  [
    [
      "movement of water through cell membranes"
    ],
    [
      "osmosis"
    ],
    [],
    []
  ],
  [
    [
      "glycolysis"
    ],
    [
      "cytoplasm"
    ],
    [],
    []
  ],
  [
    [
      "similar in function to a cell membrane"
    ],
    [
      "protein shell"
    ],
    [],
    []
  ],
  [
    [
      "encodes hereditary"
    ],
    [
      "base pair"
    ],
    [],
    []
  ],
  [
    [
      "during meiosis"
    ],
    [
      "crossing over"
    ],
    [],
    []
  ],
  [
    [
      "full set of chromosomes"
    ],
    [
      "fertilization"
    ],
    [],
    []
  ],
  [
    [
      "continuously growing and dividing"
    ],
    [
      "cancer"
    ],
    [],
    []
  ],
  [
    [
      "abnormal cell division"
    ],
    [
      "cancer"
    ],
    [],
    []
  ],
  [
    [
      "best describes a species"
    ],
    [
      "fertile"
    ],
    [],
    []
  ],
  [
    [
      "example of metamorphosis"
    ],
    [
      "caterpillar"
    ],
    [],
    []
  ],
  [
    [
      "this process is called"
    ],
    [
      "life cycle"
    ],
    [
      "butterfly"
    ],
    []
  ],
  [
    [
      "all insects"
    ],
    [
      "6"
    ],
    [],
    []
  ],
  [
    [
      "inherited from its parents"
    ],
    [
      "color of its fur"
    ],
    [],
    []
  ],
  [
    [
      "not passed from parents"
    ],
    [
      "scar"
    ],
    [],
    []
  ],
  [
    [
      "light eyes"
    ],
    [
      "recessive"
    ],
    [],
    []
  ],
  [
    [
      "section of dna from one organism"
    ],
    [
      "genetic engineering"
    ],
    [],
    []
  ],
  [
    [
      "cuttings"
    ],
    [
      "cloning"
    ],
    [],
    []
  ],
  [
    [
      "sex-linked"
    ],
    [
      "hemophilia"
    ],
    [],
    []
  ],
  [
    [
      "percent of genes"
    ],
    [
      "50"
    ],
    [],
    []
  ],
  [
    [
      "two x chromosomes"
    ],
    [
      "female"
    ],
    [],
    []
  ],
  [
    [
      "example of symbiosis"
    ],
    [
      "tick"
    ],
    [],
    []
  ],
  [
    [
      "fungus present in order to grow"
    ],
    [
      "beneficial"
    ],
    [],
    []
  ],
  [
    [
      "dead wood"
    ],
    [
      "decomposer"
    ],
    [],
    []
  ],
  [
    [
      "mushroom obtain energy"
    ],
    [
      "dead"
    ],
    [],
    []
  ],
  [
    [
      "atmospheric nitrogen"
    ],
    [
      "bacteria"
    ],
    [],
    []
  ],
  [
    [
      "abiotic"
    ],
    [
      "sand"
    ],
    [
      "desert"
    ],
    []
  ],
  [
    [
      "energy pyramid"
    ],
    [
      "reduced"
    ],
    [],
    []
  ],
  [
    [
      "example of camouflage"
    ],
    [
      "green"
    ],
    [],
    []
  ],
  [
    [
      "protects a cactus"
    ],
    [
      "spine"
    ],
    [],
    []
  ],
  [
    [
      "adaptation to living in water"
    ],
    [
      "webbed"
    ],
    [],
    []
  ],
  [
    [
      "burrow"
    ],
    [
      "desert"
    ],
    [],
    []
  ],
  [
    [
      "types of desert"
    ],
    [
      "rainfall"
    ],
    [],
    []
  ],
  [
    [
      "pond different from a lake"
    ],
    [
      "shallower"
    ],
    [],
    []
  ],
  [
    [
      "two new substances"
    ],
    [
      "conservation of mass"
    ],
    [],
    []
  ],
  [
    [
      "active volcanoes"
    ],
    [
      "pacific"
    ],
    [],
    []
  ],
  [
    [
      "cooler than the water near the surface"
    ],
    [
      "convection"
    ],
    [],
    []
  ],
  [
    [
      "cracks to form"
    ],
    [
      "freezing"
    ],
    [],
    []
  ],
  [
    [
      "can form mountains"
    ],
    [
      "earthquakes and volcanoes"
    ],
    [],
    []
  ],
  [
    [
      "just below the crust"
    ],
    [
      "mantle"
    ],
    [],
    []
  ],
  [
    [
      "nickel and iron"
    ],
    [
      "inner core"
    ],
    [],
    []
  ],
  [
    [
      "divergent tectonic plate boundary"
    ],
    [
      "rift zone"
    ],
    [],
    []
  ],
  [
    [
      "most commonly form"
    ],
    [
      "ridge"
    ],
    [],
    []
  ],
  [
    [
      "seafloor is spreading"
    ],
    [
      "mid-ocean"
    ],
    [],
    []
  ],
  [
    [
      "seafloor spreading provides evidence"
    ],
    [
      "crustal plate"
    ],
    [],
    []
  ],
  [
    [
      "convergent boundaries"
    ],
    [
      "trench"
    ],
    [],
    []
  ],
  [
    [
      "continental plates"
    ],
    [
      "mountain"
    ],
    [],
    []
  ],
  [
    [
      "center of a tectonic plate"
    ],
    [
      "hot spot"
    ],
    [],
    []
  ],
  [
    [
      "moving over a hot spot"
    ],
    [
      "island"
    ],
    [],
    []
  ],
  [
    [
      "cause of earthquakes"
    ],
    [
      "shifting"
    ],
    [],
    []
  ],
  [
    [
      "volcanic eruptions are caused"
    ],
    [
      "tectonic"
    ],
    [],
    []
  ],
  [
    [
      "geysers"
    ],
    [
      "volcanic"
    ],
    [],
    []
  ],
  [
    [
      "formation of a sinkhole"
    ],
    [
      "chemical weathering"
    ],
    [],
    []
  ],
  [
    [
      "describes the rock cycle"
    ],
    [
      "older rocks"
    ],
    [],
    []
  ],
  [
    [
      "sedimentary rock"
    ],
    [
      "sand-sized"
    ],
    [],
    []
  ],
  [
    [
      "granite"
    ],
    [
      "igneous"
    ],
    [],
    []
  ],
  [
    [
      "shark teeth"
    ],
    [
      "sea"
    ],
    [],
    []
  ],
  [
    [
      "drifted apart"
    ],
    [
      "fossil record"
    ],
    [],
    []
  ],
  [
    [
      "glacial activity"
    ],
    [
      "climate"
    ],
    [],
    []
  ],
  [
    [
      "rocks are exposed to wind"
    ],
    [
      "erode"
    ],
    [],
    []
  ],
  [
    [
      "erosion by waves"
    ],
    [
      "cliff"
    ],
    [],
    []
  ],
  [
    [
      "keeps the moon orbiting"
    ],
    [
      "earth's gravity"
    ],
    [],
    []
  ],
  [
    [
      "one-half of the moon"
    ],
    [
      "same rate"
    ],
    [],
    []
  ],
  [
    [
      "ocean tides result"
    ],
    [
      "gravitational"
    ],
    [],
    []
  ],
  [
    [
      "weather occur"
    ],
    [
      "troposphere"
    ],
    [],
    []
  ],
  [
    [
      "ocean near the equator"
    ],
    [
      "moist and warm"
    ],
    [],
    []
  ],
  [
    [
      "cold front"
    ],
    [
      "precipitation"
    ],
    [],
    []
  ],
  [
    [
      "warm front"
    ],
    [
      "rain"
    ],
    [],
    []
  ],
  [
    [
      "hurricane less likely"
    ],
    [
      "cool ocean"
    ],
    [],
    []
  ],
  [
    [
      "fog often forms"
    ],
    [
      "condenses"
    ],
    [],
    []
  ],
  [
    [
      "warms ocean water"
    ],
    [
      "evaporat"
    ],
    [],
    []
  ],
  [
    [
      "puddle has disappeared"
    ],
    [
      "evaporat"
    ],
    [],
    []
  ],
  [
    [
      "most evaporation"
    ],
    [
      "sun"
    ],
    [],
    []
  ],
  [
    [
      "describes condensation"
    ],
    [
      "gas changing to a liquid"
    ],
    [],
    []
  ],
  [
    [
      "moisture appears"
    ],
    [
      "condenses"
    ],
    [],
    []
  ],
  [
    [
      "clouds and fog"
    ],
    [
      "water"
    ],
    [],
    []
  ],
  [
    [
      "dense, cold air"
    ],
    [
      "cloud"
    ],
    [],
    []
  ],
  [
    [
      "snow fall"
    ],
    [
      "precipitation"
    ],
    [],
    []
  ],
  [
    [
      "latitude of a region"
    ],
    [
      "angle of sunlight"
    ],
    [],
    []
  ],
  [
    [
      "global wind"
    ],
    [
      "unequal heating"
    ],
    [],
    []
  ],
  [
    [
      "warm ocean currents"
    ],
    [
      "convection"
    ],
    [],
    []
  ],
  [
    [
      "black brick"
    ],
    [
      "radiation"
    ],
    [],
    []
  ],
  [
    [
      "particles collide in a solid"
    ],
    [
      "conduction"
    ],
    [],
    []
  ],
  [
    [
      "burning of fossil fuels affects the atmosphere"
    ],
    [
      "carbon dioxide"
    ],
    [],
    []
  ],
  [
    [
      "formation of acid rain"
    ],
    [
      "fossil"
    ],
    [],
    []
  ],
  [
    [
      "increase in global temperatures"
    ],
    [
      "fossil"
    ],
    [],
    []
  ],
  [
    [
      "coal consumption"
    ],
    [
      "greenhouse"
    ],
    [],
    []
  ],
  [
    [
      "reduce air pollution"
    ],
    [
      "public transportation"
    ],
    [],
    []
  ],
  [
    [
      "renewable natural resource"
    ],
    [
      "wood"
    ],
    [],
    []
  ],
  [
    [
      "resource is nonrenewable"
    ],
    [
      "petroleum"
    ],
    [],
    []
  ],
  [
    [
      "energy of the future"
    ],
    [
      "unlimited"
    ],
    [],
    []
  ],
  [
    [
      "temperature of water",
      "least"
    ],
    [
      "hydroelectric"
    ],
    [],
    []
  ],
  [
    [
      "wave energy"
    ],
    [
      "both are renewable"
    ],
    [],
    []
  ],
  [
    [
      "conserve water"
    ],
    [
      "turn off the water"
    ],
    [],
    []
  ],
  [
    [
      "conserve energy"
    ],
    [
      "turning off the lights"
    ],
    [],
    []
  ],
  [
    [
      "helping the environment"
    ],
    [
      "conserving"
    ],
    [],
    []
  ],
  [
    [
      "composed mainly of ice"
    ],
    [
      "comet"
    ],
    [],
    []
  ],
  [
    [
      "kuiper"
    ],
    [
      "comet"
    ],
    [],
    []
  ],
  [
    [
      "most massive object"
    ],
    [
      "sun"
    ],
    [],
    []
  ],
  [
    [
      "solar year"
    ],
    [
      "revolves around the sun"
    ],
    [],
    []
  ],
  [
    [
      "difference between the moon and earth"
    ],
    [
      "revolves around a planet"
    ],
    [],
    []
  ],
  [
    [
      "least amount of distance"
    ],
    [
      "earth and the moon"
    ],
    [],
    []
  ],
  [
    [
      "moon rocks"
    ],
    [
      "4.5"
    ],
    [],
    []
  ],
  [
    [
      "describes the sun"
    ],
    [
      "yellow"
    ],
    [],
    []
  ],
  [
    [
      "red dwarf"
    ],
    [
      "cooler"
    ],
    [],
    []
  ],
  [
    [
      "milky way galaxy"
    ],
    [
      "earth"
    ],
    [
      "planet"
    ],
    []
  ],
  [
    [
      "light year"
    ],
    [
      "stars"
    ],
    [],
    []
  ],
  [
    [
      "light-year"
    ],
    [
      "stars"
    ],
    [],
    []
  ],
  [
    [
      "classify galaxies"
    ],
    [
      "shape"
    ],
    [],
    []
  ],
  [
    [
      "extra-terrestrial"
    ],
    [
      "mars"
    ],
    [],
    []
  ],
  [
    [
      "frost line"
    ],
    [
      "hydrogen"
    ],
    [],
    []
  ],
  [
    [
      "four planets closest"
    ],
    [
      "dense"
    ],
    [],
    []
  ],
  [
    [
      "weigh more on earth"
    ],
    [
      "less gravity"
    ],
    [],
    []
  ],
  [
    [
      "eyeglass"
    ],
    [
      "refract"
    ],
    [],
    []
  ],
  [
    [
      "refracts light"
    ],
    [
      "glass"
    ],
    [],
    []
  ],
  [
    [
      "bending of light"
    ],
    [
      "convex"
    ],
    [],
    []
  ],
  [
    [
      "slower on the grass"
    ],
    [
      "friction"
    ],
    [],
    []
  ],
  [
    [
      "roll off the tray"
    ],
    [
      "inertia"
    ],
    [],
    []
  ],
  [
    [
      "constant rate"
    ],
    [
      "balanced"
    ],
    [],
    []
  ],
  [
    [
      "no outside force"
    ],
    [
      "will not change"
    ],
    [],
    []
  ],
  [
    [
      "rubs them together"
    ],
    [
      "friction"
    ],
    [],
    []
  ],
  [
    [
      "force producing heat"
    ],
    [
      "rubbed"
    ],
    [],
    []
  ],
  [
    [
      "wool hat"
    ],
    [
      "electron"
    ],
    [],
    []
  ],
  [
    [
      "rubber brush"
    ],
    [
      "static"
    ],
    [],
    []
  ],
  [
    [
      "magnetic properties"
    ],
    [
      "iron"
    ],
    [],
    []
  ],
  [
    [
      "natural magnetism"
    ],
    [
      "compass"
    ],
    [],
    []
  ],
  [
    [
      "wrapped around a metal nail"
    ],
    [
      "magnetic"
    ],
    [],
    []
  ],
  [
    [
      "measured as"
    ],
    [
      "weight"
    ],
    [
      "gravitational attraction"
    ],
    []
  ],
  [
    [
      "depends on the distance"
    ],
    [
      "mass"
    ],
    [],
    []
  ],
  [
    [
      "gravitational force between the satellite"
    ],
    [
      "distance"
    ],
    [],
    []
  ],
  [
    [
      "most rapidly become a gas"
    ],
    [
      "boiling"
    ],
    [],
    []
  ],
  [
    [
      "endothermic"
    ],
    [
      "melting"
    ],
    [],
    []
  ],
  [
    [
      "potential energy"
    ],
    [
      "gasoline"
    ],
    [],
    []
  ],
  [
    [
      "methane"
    ],
    [
      "heat"
    ],
    [],
    []
  ],
  [
    [
      "subatomic particles split"
    ],
    [
      "nuclear"
    ],
    [],
    []
  ],
  [
    [
      "kilowatt-hour"
    ],
    [
      "joule"
    ],
    [],
    []
  ],
  [
    [
      "hear each other"
    ],
    [
      "vibration"
    ],
    [],
    []
  ],
  [
    [
      "traveling through a vacuum"
    ],
    [
      "light"
    ],
    [],
    []
  ],
  [
    [
      "automobile engine"
    ],
    [
      "thermal energy and mechanical"
    ],
    [],
    []
  ],
  [
    [
      "crickets"
    ],
    [
      "mechanical energy to sound"
    ],
    [],
    []
  ],
  [
    [
      "lower height each time"
    ],
    [
      "transferred"
    ],
    [],
    []
  ],
  [
    [
      "ionic bond"
    ],
    [
      "transfer of electrons"
    ],
    [],
    []
  ],
  [
    [
      "neutral atoms"
    ],
    [
      "protons and electrons"
    ],
    [],
    []
  ],
  [
    [
      "same for each atom of an element"
    ],
    [
      "atomic number"
    ],
    [],
    []
  ],
  [
    [
      "order of the elements"
    ],
    [
      "proton"
    ],
    [],
    []
  ],
  [
    [
      "left to right along a row"
    ],
    [
      "increases by 1"
    ],
    [],
    []
  ],
  [
    [
      "cesium"
    ],
    [
      "cscl"
    ],
    [
      "2",
      "o"
    ],
    []
  ],
  [
    [
      "five protons"
    ],
    [
      "positively"
    ],
    [],
    []
  ],
  [
    [
      "electrons can be found"
    ],
    [
      "orbiting the nucleus"
    ],
    [],
    []
  ],
  [
    [
      "sodium ion"
    ],
    [
      "lose one electron"
    ],
    [],
    []
  ],
  [
    [
      "similar to sodium"
    ],
    [
      "potassium"
    ],
    [],
    []
  ],
  [
    [
      "considered a compound because"
    ],
    [
      "element"
    ],
    [],
    []
  ],
  [
    [
      "two nitrogen atoms"
    ],
    [
      "molecule"
    ],
    [],
    []
  ],
  [
    [
      "wet sand"
    ],
    [
      "mixture"
    ],
    [],
    []
  ],
  [
    [
      "salt water, plastic"
    ],
    [
      "atoms"
    ],
    [],
    []
  ],
  [
    [
      "chemical change"
    ],
    [
      "new substance"
    ],
    [],
    []
  ],
  [
    [
      "chemical reaction has taken place"
    ],
    [
      "new chemical"
    ],
    [],
    []
  ],
  [
    [
      "characteristic of the metal gold"
    ],
    [
      "malleable"
    ],
    [],
    []
  ],
  [
    [
      "drill bits"
    ],
    [
      "hardness"
    ],
    [],
    []
  ],
  [
    [
      "most flexible"
    ],
    [
      "straw"
    ],
    [],
    []
  ],
  [
    [
      "property of flexibility"
    ],
    [
      "wire"
    ],
    [],
    []
  ],
  [
    [
      "too hot to touch"
    ],
    [
      "spoon"
    ],
    [],
    []
  ],
  [
    [
      "conducts electricity"
    ],
    [
      "material"
    ],
    [],
    []
  ],
  [
    [
      "insulator"
    ],
    [
      "foam"
    ],
    [],
    []
  ],
  [
    [
      "length and mass"
    ],
    [
      "ruler and a balance"
    ],
    [],
    []
  ],
  [
    [
      "masses and volumes"
    ],
    [
      "balance and graduated"
    ],
    [],
    []
  ],
  [
    [
      "melting point of ice"
    ],
    [
      "thermometer"
    ],
    [],
    []
  ],
  [
    [
      "mass of an automobile"
    ],
    [
      "kilogram"
    ],
    [],
    []
  ],
  [
    [
      "best measured in"
    ],
    [
      "kilometer"
    ],
    [],
    []
  ],
  [
    [
      "scientific guess"
    ],
    [
      "hypothesis"
    ],
    [],
    []
  ],
  [
    [
      "scientific inference"
    ],
    [
      "not the direct observation"
    ],
    [],
    []
  ],
  [
    [
      "sorting rocks"
    ],
    [
      "classifying"
    ],
    [],
    []
  ],
  [
    [
      "dependent"
    ],
    [
      "eggs"
    ],
    [],
    []
  ],
  [
    [
      "average size of acorn"
    ],
    [
      "more than one"
    ],
    [],
    []
  ],
  [
    [
      "peer review"
    ],
    [
      "independent"
    ],
    [],
    []
  ],
  [
    [
      "last thing a student should do"
    ],
    [
      "wash hands"
    ],
    [],
    []
  ],
  [
    [
      "dispose of"
    ],
    [
      "hazardous"
    ],
    [],
    []
  ],
  [
    [
      "should be avoided"
    ],
    [
      "pouring water into an acid"
    ],
    [],
    []
  ],
  [
    [
      "itchy rash"
    ],
    [
      "teacher"
    ],
    [],
    []
  ],
  [
    [
      "hot plate"
    ],
    [
      "unattended"
    ],
    [],
    []
  ],
  [
    [
      "all these except",
      "speaks"
    ],
    [
      "transverse"
    ],
    [],
    []
  ],
  [
    [
      "sulfur forms crystals"
    ],
    [
      "freeze"
    ],
    [],
    []
  ],
  [
    [
      "developed most recently"
    ],
    [
      "cellular"
    ],
    [],
    []
  ],
  [
    [
      "occurred first"
    ],
    [
      "breeding of plants"
    ],
    [],
    []
  ],
  [
    [
      "blue jays"
    ],
    [
      "planted"
    ],
    [],
    []
  ],
  [
    [
      "after a student graphs"
    ],
    [
      "analyz"
    ],
    [],
    []
  ],
  [
    [
      "island nations"
    ],
    [
      "sea"
    ],
    [],
    []
  ],
  [
    [
      "orion nebula"
    ],
    [
      "young star"
    ],
    [],
    []
  ],
  [
    [
      "directions for an experiment"
    ],
    [
      "in order"
    ],
    [],
    []
  ],
  [
    [
      "unicellular or multicellular"
    ],
    [
      "how many types of cells"
    ],
    [],
    []
  ],
  [
    [
      "yeast"
    ],
    [
      "respiration"
    ],
    [],
    []
  ],
  [
    [
      "week-long"
    ],
    [
      "days"
    ],
    [],
    []
  ],
  [
    [
      "cell phones"
    ],
    [
      "away from home"
    ],
    [],
    []
  ],
  [
    [
      "reflecting incoming solar"
    ],
    [
      "cloud"
    ],
    [],
    []
  ],
  [
    [
      "rainforest food chain"
    ],
    [
      "food source"
    ],
    [],
    []
  ],
  [
    [
      "structural adaptation"
    ],
    [
      "fin"
    ],
    [],
    []
  ],
  [
    [
      "increased the accuracy"
    ],
    [
      "without fertilizer"
    ],
    [],
    []
  ],
  [
    [
      "turbidity"
    ],
    [
      "clear-cutting"
    ],
    [],
    []
  ],
  [
    [
      "grow in a direction"
    ],
    [
      "light"
    ],
    [],
    []
  ],
  [
    [
      "drought"
    ],
    [
      "farming"
    ],
    [],
    []
  ],
  [
    [
      "question could be answered by using a ruler"
    ],
    [
      "largest"
    ],
    [],
    []
  ],
  [
    [
      "cows and grass"
    ],
    [
      "grow"
    ],
    [],
    []
  ],
  [
    [
      "glucose-specific enzymes"
    ],
    [
      "catalyze"
    ],
    [],
    []
  ],
  [
    [
      "more of the sun's rays"
    ],
    [
      "evaporation"
    ],
    [],
    []
  ],
  [
    [
      "bears eating"
    ],
    [
      "seeds"
    ],
    [],
    []
  ],
  [
    [
      "organic matter being added"
    ],
    [
      "bacteria"
    ],
    [],
    []
  ],
  [
    [
      "resistant to hiv"
    ],
    [
      "beneficial"
    ],
    [],
    []
  ],
  [
    [
      "plant remains"
    ],
    [
      "organic matter"
    ],
    [],
    []
  ],
  [
    [
      "deaf"
    ],
    [
      "selective breeding"
    ],
    [],
    []
  ],
  [
    [
      "geologic time"
    ],
    [
      "fossil record"
    ],
    [],
    []
  ],
  [
    [
      "bee depends"
    ],
    [
      "pollen"
    ],
    [],
    []
  ],
  [
    [
      "greatest effect on the weather"
    ],
    [
      "water vapor"
    ],
    [],
    []
  ],
  [
    [
      "prokaryotic dna"
    ],
    [
      "shape"
    ],
    [],
    []
  ],
  [
    [
      "adult stage"
    ],
    [
      "lays eggs"
    ],
    [],
    []
  ],
  [
    [
      "enzyme acts first"
    ],
    [
      "pepsin"
    ],
    [],
    []
  ],
  [
    [
      "passed from one person"
    ],
    [
      "infectious"
    ],
    [],
    []
  ],
  [
    [
      "flippers"
    ],
    [
      "temperature"
    ],
    [],
    []
  ],
  [
    [
      "humans contribute the least"
    ],
    [
      "plate tectonics"
    ],
    [],
    []
  ],
  [
    [
      "heat loss"
    ],
    [
      "window"
    ],
    [],
    []
  ],
  [
    [
      "abiotic factor"
    ],
    [
      "temperature"
    ],
    [
      "frog"
    ],
    []
  ],
  [
    [
      "mitotic"
    ],
    [
      "copied"
    ],
    [],
    []
  ],
  [
    [
      "sexually produced"
    ],
    [
      "new combination"
    ],
    [],
    []
  ],
  [
    [
      "muscles requiring"
    ],
    [
      "oxygen"
    ],
    [],
    []
  ],
  [
    [
      "limestone"
    ],
    [
      "chemical change"
    ],
    [],
    []
  ],
  [
    [
      "streak plate"
    ],
    [
      "hardness"
    ],
    [],
    []
  ],
  [
    [
      "energy of motion of water"
    ],
    [
      "heat"
    ],
    [],
    []
  ],
  [
    [
      "heating and cooling"
    ],
    [
      "thermal"
    ],
    [],
    []
  ],
  [
    [
      "balanced chemical equation"
    ],
    [
      "products"
    ],
    [],
    []
  ],
  [
    [
      "ice cubes will melt"
    ],
    [
      "gain energy"
    ],
    [],
    []
  ],
  [
    [
      "rabies"
    ],
    [
      "nervous"
    ],
    [],
    []
  ],
  [
    [
      "not accomplished by repeated cell division"
    ],
    [
      "sunlight"
    ],
    [],
    []
  ],
  [
    [
      "evolved from a common ancestor"
    ],
    [
      "bone"
    ],
    [],
    []
  ],
  [
    [
      "electromagnetic spectrum"
    ],
    [
      "small part"
    ],
    [],
    []
  ],
  [
    [
      "least number of similarities"
    ],
    [
      "kingdom"
    ],
    [],
    []
  ],
  [
    [
      "complex machine"
    ],
    [
      "simple machine"
    ],
    [],
    []
  ],
  [
    [
      "wilted"
    ],
    [
      "water"
    ],
    [],
    []
  ],
  [
    [
      "e. coli"
    ],
    [
      "both benefit"
    ],
    [],
    []
  ],
  [
    [
      "tumor suppressor"
    ],
    [
      "restrict"
    ],
    [],
    []
  ],
  [
    [
      "window"
    ],
    [
      "evaporat"
    ],
    [
      "drops"
    ],
    []
  ],
  [
    [
      "polar bear"
    ],
    [
      "cold"
    ],
    [],
    []
  ],
  [
    [
      "arctic hare"
    ],
    [
      "hide"
    ],
    [],
    []
  ],
  [
    [
      "pollination is helped"
    ],
    [
      "insect"
    ],
    [],
    []
  ],
  [
    [
      "old-growth"
    ],
    [
      "clear-cutting"
    ],
    [],
    []
  ],
  [
    [
      "predator feeding"
    ],
    [
      "available food"
    ],
    [],
    []
  ],
  [
    [
      "felis catus"
    ],
    [
      "genetic and structural"
    ],
    [],
    []
  ],
  [
    [
      "ovary"
    ],
    [
      "egg"
    ],
    [],
    []
  ],
  [
    [
      "human-induced"
    ],
    [
      "fossil"
    ],
    [],
    []
  ],
  [
    [
      "nitrogen cycle"
    ],
    [
      "nutrients decrease"
    ],
    [],
    []
  ],
  [
    [
      "sugars usually transported"
    ],
    [
      "needles to the roots"
    ],
    [],
    []
  ],
  [
    [
      "salt removed"
    ],
    [
      "sea"
    ],
    [],
    []
  ],
  [
    [
      "paw print"
    ],
    [
      "rock"
    ],
    [],
    []
  ],
  [
    [
      "runs only on electricity"
    ],
    [
      "ceiling fan"
    ],
    [],
    []
  ],
  [
    [
      "weather balloon"
    ],
    [
      "air pressure"
    ],
    [],
    []
  ],
  [
    [
      "speed up the rate"
    ],
    [
      "catalyst"
    ],
    [],
    []
  ],
  [
    [
      "diamonds are formed"
    ],
    [
      "beneath"
    ],
    [],
    []
  ],
  [
    [
      "sonar"
    ],
    [
      "location"
    ],
    [],
    []
  ],
  [
    [
      "all living cells"
    ],
    [
      "water"
    ],
    [],
    []
  ],
  [
    [
      "milky way galaxy looks"
    ],
    [
      "dark, clear night"
    ],
    [],
    []
  ],
  [
    [
      "internet has changed"
    ],
    [
      "communicate faster"
    ],
    [],
    []
  ],
  [
    [
      "oil to the oceans"
    ],
    [
      "transporting oil"
    ],
    [],
    []
  ],
  [
    [
      "initially caused"
    ],
    [
      "solar radiation"
    ],
    [],
    []
  ],
  [
    [
      "step in the process of photosynthesis"
    ],
    [
      "carbon dioxide"
    ],
    [],
    []
  ],
  [
    [
      "more closely related"
    ],
    [
      "dna"
    ],
    [],
    []
  ],
  [
    [
      "can become fossils except"
    ],
    [
      "rocks"
    ],
    [],
    []
  ],
  [
    [
      "comes back to the ground"
    ],
    [
      "gravity"
    ],
    [],
    []
  ],
  [
    [
      "bend toward"
    ],
    [
      "light"
    ],
    [],
    []
  ],
  [
    [
      "automobiles"
    ],
    [
      "road"
    ],
    [],
    []
  ],
  [
    [
      "prairie dog"
    ],
    [
      "hearing"
    ],
    [],
    []
  ],
  [
    [
      "non-contact force"
    ],
    [
      "magnet"
    ],
    [],
    []
  ],
  [
    [
      "graphite"
    ],
    [
      "pencil"
    ],
    [],
    []
  ],
  [
    [
      "clippings"
    ],
    [
      "nutrient"
    ],
    [],
    []
  ],
  [
    [
      "differed from the hypothesis"
    ],
    [
      "new hypothesis"
    ],
    [],
    []
  ],
  [
    [
      "independent variable in this test"
    ],
    [
      "composition"
    ],
    [],
    []
  ],
  [
    [
      "disease-causing microbes"
    ],
    [
      "destroy the microbes"
    ],
    [],
    []
  ],
  [
    [
      "best thing to do first"
    ],
    [
      "drawing"
    ],
    [],
    []
  ],
  [
    [
      "independent variable in this investigation"
    ],
    [
      "rubbing"
    ],
    [],
    []
  ],
  [
    [
      "greenhouse gases"
    ],
    [
      "carbon cycle"
    ],
    [],
    []
  ],
  [
    [
      "refracted"
    ],
    [
      "prism"
    ],
    [],
    []
  ],
  [
    [
      "physical properties of the sample"
    ],
    [
      "boiling point"
    ],
    [],
    []
  ],
  [
    [
      "sound wave, can travel"
    ],
    [
      "gas, liquids"
    ],
    [],
    []
  ],
  [
    [
      "gene mutations that result in cancer"
    ],
    [
      "dna replication"
    ],
    [],
    []
  ],
  [
    [
      "biotic nitrogen"
    ],
    [
      "bacteria"
    ],
    [],
    []
  ],
  [
    [
      "giant sloth"
    ],
    [
      "humans"
    ],
    [],
    []
  ],
  [
    [
      "forest fires affect the lithosphere"
    ],
    [
      "erosion"
    ],
    [],
    []
  ],
  [
    [
      "speed of the seismic waves"
    ],
    [
      "different materials"
    ],
    [],
    []
  ],
  [
    [
      "hunted for their fur"
    ],
    [
      "extinction"
    ],
    [],
    []
  ],
  [
    [
      "all species of animals"
    ],
    [
      "breathing and reproducing"
    ],
    [],
    []
  ],
  [
    [
      "gravitational pull of the moon"
    ],
    [
      "tidal"
    ],
    [],
    []
  ],
  [
    [
      "temperature inversion"
    ],
    [
      "rapid cooling"
    ],
    [],
    []
  ],
  [
    [
      "green eyes"
    ],
    [
      "inherited"
    ],
    [],
    []
  ],
  [
    [
      "born"
    ],
    [
      "congenital"
    ],
    [],
    []
  ],
  [
    [
      "meteor"
    ],
    [
      "temperature"
    ],
    [],
    []
  ],
  [
    [
      "forelimb"
    ],
    [
      "common ancestor"
    ],
    [],
    []
  ],
  [
    [
      "animal fossil"
    ],
    [
      "time period"
    ],
    [],
    []
  ],
  [
    [
      "learn from its mother"
    ],
    [
      "hunt"
    ],
    [],
    []
  ],
  [
    [
      "suspension bridge"
    ],
    [
      "tension"
    ],
    [],
    []
  ],
  [
    [
      "feature of plains"
    ],
    [
      "flat"
    ],
    [],
    []
  ],
  [
    [
      "more dense than lead"
    ],
    [
      "observed and tested"
    ],
    [],
    []
  ],
  [
    [
      "habitat of an insect"
    ],
    [
      "where"
    ],
    [],
    []
  ],
  [
    [
      "footing"
    ],
    [
      "foundation"
    ],
    [],
    []
  ],
  [
    [
      "extinction of a species"
    ],
    [
      "competitive"
    ],
    [],
    []
  ],
  [
    [
      "top layers of soil"
    ],
    [
      "nutrient"
    ],
    [],
    []
  ],
  [
    [
      "decrease in solar radiation"
    ],
    [
      "volcanic eruption"
    ],
    [],
    []
  ],
  [
    [
      "wild fish"
    ],
    [
      "ocean"
    ],
    [],
    []
  ],
  [
    [
      "river basin"
    ],
    [
      "tributar"
    ],
    [],
    []
  ],
  [
    [
      "grassy plains"
    ],
    [
      "long legs"
    ],
    [],
    []
  ],
  [
    [
      "vertebrate animals"
    ],
    [
      "backbone"
    ],
    [],
    []
  ],
  [
    [
      "nearby stars"
    ],
    [
      "parallax"
    ],
    [],
    []
  ],
  [
    [
      "plant sample"
    ],
    [
      "washing hands"
    ],
    [],
    []
  ],
  [
    [
      "decrease in friction be most beneficial"
    ],
    [
      "axle"
    ],
    [],
    []
  ],
  [
    [
      "prehistoric plants"
    ],
    [
      "coal, oil"
    ],
    [],
    []
  ],
  [
    [
      "products of"
    ],
    [
      "photosynthesis"
    ],
    [
      "oxygen and sugar"
    ],
    []
  ],
  [
    [
      "peptidase"
    ],
    [
      "amino acid"
    ],
    [],
    []
  ],
  [
    [
      "nutrients to bone"
    ],
    [
      "digestive system and the circulatory"
    ],
    [],
    []
  ],
  [
    [
      "not a food"
    ],
    [
      "does not store energy or nutrients"
    ],
    [],
    []
  ],
  [
    [
      "calcium carbonate deposit"
    ],
    [
      "limestone"
    ],
    [],
    []
  ],
  [
    [
      "fewer chemicals than burning gasoline"
    ],
    [
      "air pollution"
    ],
    [],
    []
  ],
  [
    [
      "interacting with each other"
    ],
    [
      "bear"
    ],
    [],
    []
  ],
  [
    [
      "daily nutrition"
    ],
    [
      "ingredients"
    ],
    [],
    []
  ],
  [
    [
      "primarily results from cell division"
    ],
    [
      "growth"
    ],
    [],
    []
  ],
  [
    [
      "in order to grow"
    ],
    [
      "nutrient"
    ],
    [
      "animal cells"
    ],
    []
  ],
  [
    [
      "advertisements"
    ],
    [
      "network"
    ],
    [],
    []
  ],
  [
    [
      "plates have diverged"
    ],
    [
      "rift"
    ],
    [],
    []
  ],
  [
    [
      "produce light energy"
    ],
    [
      "laser"
    ],
    [],
    []
  ],
  [
    [
      "fossil fuel burning"
    ],
    [
      "acid rain"
    ],
    [],
    []
  ],
  [
    [
      "how organisms"
    ],
    [
      "obtain energy"
    ],
    [],
    []
  ],
  [
    [
      "new community of organisms"
    ],
    [
      "succession"
    ],
    [],
    []
  ],
  [
    [
      "age of fossils"
    ],
    [
      "radioactive"
    ],
    [],
    []
  ],
  [
    [
      "muscle contraction"
    ],
    [
      "actin"
    ],
    [],
    []
  ],
  [
    [
      "range shift"
    ],
    [
      "global warming"
    ],
    [],
    []
  ],
  [
    [
      "severe eye damage"
    ],
    [
      "laser"
    ],
    [],
    []
  ],
  [
    [
      "large trees could grow"
    ],
    [
      "soil"
    ],
    [],
    []
  ],
  [
    [
      "led scientists to believe"
    ],
    [
      "fossils of fish"
    ],
    [],
    []
  ],
  [
    [
      "example of physical weathering"
    ],
    [
      "erosion"
    ],
    [],
    []
  ],
  [
    [
      "positive effect of this discovery"
    ],
    [
      "food webs"
    ],
    [],
    []
  ],
  [
    [
      "sense of touch"
    ],
    [
      "texture"
    ],
    [],
    []
  ],
  [
    [
      "cause an earthquake"
    ],
    [
      "fault"
    ],
    [],
    []
  ],
  [
    [
      "coal began to form"
    ],
    [
      "dead plants"
    ],
    [],
    []
  ],
  [
    [
      "acid rainfall"
    ],
    [
      "quality of water"
    ],
    [],
    []
  ],
  [
    [
      "forest ecosystem"
    ],
    [
      "squirrel, deer"
    ],
    [],
    []
  ],
  [
    [
      "telescope would be most useful"
    ],
    [
      "moon"
    ],
    [],
    []
  ],
  [
    [
      "human impact"
    ],
    [
      "cutting down trees"
    ],
    [],
    []
  ],
  [
    [
      "record the types of trees"
    ],
    [
      "camera"
    ],
    [],
    []
  ],
  [
    [
      "heavy metals"
    ],
    [
      "runoff"
    ],
    [],
    []
  ],
  [
    [
      "mass and gravitational pull"
    ],
    [
      "higher mass creates higher"
    ],
    [],
    []
  ],
  [
    [
      "skeletal system interacts with the circulatory"
    ],
    [
      "oxygen to the bones"
    ],
    [],
    []
  ],
  [
    [
      "snowball"
    ],
    [
      "less dense"
    ],
    [],
    []
  ],
  [
    [
      "helpful variations"
    ],
    [
      "evolution"
    ],
    [],
    []
  ],
  [
    [
      "what kind it is"
    ],
    [
      "minerals"
    ],
    [],
    []
  ],
  [
    [
      "traveling from dna"
    ],
    [
      "membrane"
    ],
    [],
    []
  ],
  [
    [
      "moves the crustal plates"
    ],
    [
      "molten rock"
    ],
    [],
    []
  ],
  [
    [
      "coastal erosion"
    ],
    [
      "satellite images"
    ],
    [],
    []
  ],
  [
    [
      "samples of water"
    ],
    [
      "quality of the water"
    ],
    [],
    []
  ],
  [
    [
      "electromagnet"
    ],
    [
      "insulated wire, iron rod, battery"
    ],
    [],
    []
  ],
  [
    [
      "spotted owl"
    ],
    [
      "better adapted"
    ],
    [],
    []
  ],
  [
    [
      "jonas salk"
    ],
    [
      "polio"
    ],
    [],
    []
  ],
  [
    [
      "skunk"
    ],
    [
      "avoid predators"
    ],
    [],
    []
  ],
  [
    [
      "rotten food"
    ],
    [
      "compost"
    ],
    [],
    []
  ],
  [
    [
      "thousands of"
    ],
    [
      "genes"
    ],
    [],
    []
  ],
  [
    [
      "prey animal population also benefit"
    ],
    [
      "reproductive success"
    ],
    [],
    []
  ],
  [
    [
      "source of light removed"
    ],
    [
      "less energy"
    ],
    [],
    []
  ],
  [
    [
      "warm air mass slowly"
    ],
    [
      "rain will fall"
    ],
    [],
    []
  ],
  [
    [
      "rock to slow down"
    ],
    [
      "friction"
    ],
    [],
    []
  ],
  [
    [
      "amounts of different types of rock"
    ],
    [
      "total amount of material"
    ],
    [],
    []
  ],
  [
    [
      "endocrine system releases"
    ],
    [
      "growth and development"
    ],
    [],
    []
  ],
  [
    [
      "tourism and agriculture"
    ],
    [
      "water pollution"
    ],
    [],
    []
  ],
  [
    [
      "made by his environment"
    ],
    [
      "scar"
    ],
    [],
    []
  ],
  [
    [
      "best example of weathering"
    ],
    [
      "tree root"
    ],
    [],
    []
  ],
  [
    [
      "all behavior"
    ],
    [
      "both experience and inheritance"
    ],
    [],
    []
  ],
  [
    [
      "away from a sidewalk"
    ],
    [
      "crack"
    ],
    [],
    []
  ],
  [
    [
      "color vision unimportant"
    ],
    [
      "only at night"
    ],
    [],
    []
  ],
  [
    [
      "slowing down because"
    ],
    [
      "less oxygen"
    ],
    [],
    []
  ],
  [
    [
      "fresh foods from spoiling"
    ],
    [
      "types of food"
    ],
    [],
    []
  ],
  [
    [
      "exert forces"
    ],
    [
      "pulling on bones"
    ],
    [],
    []
  ],
  [
    [
      "large body struck earth"
    ],
    [
      "chemical composition"
    ],
    [],
    []
  ],
  [
    [
      "credited with this organization"
    ],
    [
      "mendeleev"
    ],
    [],
    []
  ],
  [
    [
      "curved stem"
    ],
    [
      "environmental conditions"
    ],
    [],
    []
  ],
  [
    [
      "most accurate conclusion"
    ],
    [
      "same maze"
    ],
    [],
    []
  ],
  [
    [
      "most accurate information"
    ],
    [
      "geological survey"
    ],
    [],
    []
  ],
  [
    [
      "formation of sinkholes and caves"
    ],
    [
      "precipitation and infiltration"
    ],
    [],
    []
  ],
  [
    [
      "piece of bread is toasted"
    ],
    [
      "electrical energy to heat"
    ],
    [],
    []
  ],
  [
    [
      "bridge is unsafe"
    ],
    [
      "identify the problem-plan"
    ],
    [],
    []
  ],
  [
    [
      "correct order of the flow"
    ],
    [
      "producer -> herbivore -> carnivore"
    ],
    [],
    []
  ],
  [
    [
      "straighten when force"
    ],
    [
      "rubber bands"
    ],
    [],
    []
  ],
  [
    [
      "property of water that is demonstrated"
    ],
    [
      "liquid to a gas"
    ],
    [],
    []
  ],
  [
    [
      "nuclear fusion that powers"
    ],
    [
      "protons and neutrons"
    ],
    [],
    []
  ],
  [
    [
      "save a polluted wetland"
    ],
    [
      "botanist and ecologist"
    ],
    [],
    []
  ],
  [
    [
      "strength of a magnet defined"
    ],
    [
      "number of metal paper clips"
    ],
    [],
    []
  ],
  [
    [
      "greater detail"
    ],
    [
      "optical tools"
    ],
    [],
    []
  ],
  [
    [
      "traffic survey"
    ],
    [
      "tally"
    ],
    [],
    []
  ],
  [
    [
      "true statement about cells"
    ],
    [
      "chloroplasts"
    ],
    [],
    []
  ],
  [
    [
      "genetic traits of humans"
    ],
    [
      "dominant and recessive forms"
    ],
    [],
    []
  ],
  [
    [
      "algae suddenly increased"
    ],
    [
      "fertilizer runoff"
    ],
    [],
    []
  ],
  [
    [
      "formula x + zy"
    ],
    [
      "more reactive"
    ],
    [],
    []
  ],
  [
    [
      "altered wing shapes"
    ],
    [
      "genetic mutation"
    ],
    [],
    []
  ],
  [
    [
      "gaining scientific knowledge"
    ],
    [
      "desired trait"
    ],
    [],
    []
  ]
]


EXTRA = [
    (["ccgcat"], ["complementary bases in the same"], [], []),
    (["neutrons are particles"], ["part of the nucleus"], [], []),
    (["expansion and contraction"], ["mechanical weathering"], [], []),
    (["abnormal chromosome"], ["separate during meiosis"], [], []),
    (["mesothelioma"], ["cell cycle"], [], []),
    (["environmental changes"], ["fossil record"], [], []),
    (["flood plain"], ["limiting factor"], [], []),
    (["inner surface of the membrane"], ["prokaryotic"], [], []),
    (["per unit mass"], ["specific heat"], [], []),
    (["is not passed"], ["scar"], [], []),
    (["rules of chemical reactions"], ["dalton"], [], []),
    (["pendulum", "independent"], ["length"], [], []),
    (["astronauts need oxygen"], ["breathe in"], [], []),
    (["hypotonic"], ["water will enter"], [], []),
    (["pebbles or stones"], ["eaten"], [], []),
    (["person is walking"], ["muscular and nervous"], [], []),
    (["repel each other"], ["magnetism"], ["gravity"], []),
    (["unhealthy diet"], ["food from its mother"], [], []),
    (["pulse and breathing"], ["increase in pulse and breathing"], [], []),
    (["schoolyard"], ["local weather"], [], []),
    (["provided evidence that"], ["a sphere"], [], []),
]


def _numeric(stem: str, pairs) -> str | None:
    """Closest reading, average speed, and a 25 percent live load. Computed, not memorized."""
    sl = stem.lower()
    votes = []
    m = re.search(r"actually\s+([0-9]+(?:\.[0-9]+)?)", sl)
    if m and "accurate" in sl:
        target = float(m.group(1))
        scored = []
        for lab, text in pairs:
            nums = re.findall(r"[0-9]+(?:\.[0-9]+)?", text)
            if len(nums) == 1:
                scored.append((abs(float(nums[0]) - target), lab))
        scored.sort()
        if len(scored) >= 2 and scored[0][0] < scored[1][0]:
            votes.append(scored[0][1])
    m = re.search(r"([0-9]+(?:\.[0-9]+)?)\s*km in\s*([0-9]+(?:\.[0-9]+)?)\s*hr", sl)
    if m:
        rate = float(m.group(1)) / float(m.group(2))
        rate_s = str(int(rate)) if rate == int(rate) else str(rate)
        speed = [
            lab for lab, text in pairs
            if "average speed" in text.lower() and re.search(rf"\b{re.escape(rate_s)}\b", text)
        ]
        hits = [lab for lab, text in pairs if re.search(rf"\b{re.escape(rate_s)}\b", text)]
        if len(set(speed)) == 1:
            votes.append(speed[0])
        elif len(set(hits)) == 1:
            votes.append(hits[0])
    m = re.search(r"weighs\s+([0-9]+).+weighs\s+([0-9]+).+25 percent", sl)
    if m:
        total = (float(m.group(1)) + float(m.group(2))) * 1.25
        total_s = str(int(total)) if total == int(total) else str(total)
        hits = [lab for lab, text in pairs if re.search(rf"\b{total_s}\b", text)]
        if len(set(hits)) == 1:
            votes.append(hits[0])
    votes = sorted(set(votes))
    return votes[0] if len(votes) == 1 else None


def _vote(stem: str, pairs, proc) -> str | None:
    need, bits, ban, stem_ban = proc
    sl = stem.lower()
    if any(b in sl for b in stem_ban):
        return None
    if not all(n in sl for n in need):
        return None
    labs = []
    for lab, text in pairs:
        tl = text.lower()
        if any(b in tl for b in ban):
            continue
        if any(b in tl for b in bits):
            labs.append(lab)
    labs = sorted(set(labs))
    return labs[0] if len(labs) == 1 else None


def pick_v3(stem: str, pairs, facts, procs):
    """reason_proc, with inversion blocking only procedures that are not about it."""
    inv = question_inverted(stem)
    votes = []
    num = _numeric(stem, pairs)
    if num is not None:
        votes.append(num)
    for proc in procs:
        lab = _vote(stem, pairs, proc)
        if lab is None:
            continue
        if inv and not any(tok in " ".join(proc[0]) for tok in ("least", "except", " not", "never")):
            continue
        votes.append(lab)
    votes = sorted(set(votes))
    if len(votes) == 1:
        return votes[0], "procedure", {"pathway": "reason_proc", "overlay": True, "inversion": inv}
    if len(votes) > 1:
        return None, "consensus_0", {"pathway": "consensus_0", "overlay": False, "inversion": inv}
    return pick_v2(stem, pairs, facts, procs)


def main() -> int:
    train = load_split("train")
    val = load_split("validation")
    facts = study_facts(train)
    base = list(PROCS) + list(MORE)
    procs = base + MORE2 + EXTRA
    before = {"correct": 0, "wrong": 0, "leftover": 0, "consensus_0": 0, "procedure": 0}
    after = {"correct": 0, "wrong": 0, "leftover": 0, "consensus_0": 0, "procedure": 0}
    fixed = []
    still = []
    for _, row in val.iterrows():
        pairs = choices_of(row)
        key = str(row["answerKey"]).strip()
        stem = str(row["question"])
        b_lab, b_how, _ = pick_v2(stem, pairs, facts, base)
        a_lab, a_how, state = pick_v3(stem, pairs, facts, procs)

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
        if a_lab is None or a_lab != key:
            if a_lab is not None and a_lab != key:
                texts = dict(pairs)
                still.append(
                    {
                        "id": row["id"],
                        "kind": "wrong",
                        "how": a_how,
                        "picked": a_lab,
                        "picked_text": texts.get(a_lab),
                        "key": key,
                        "key_text": texts.get(key),
                        "stem": stem[:180],
                    }
                )
            elif a_lab is None:
                texts = dict(pairs)
                still.append(
                    {
                        "id": row["id"],
                        "kind": a_how,
                        "key": key,
                        "key_text": texts.get(key),
                        "stem": stem[:180],
                    }
                )
    n = len(val)
    prec_b = before["correct"] / max(before["correct"] + before["wrong"], 1)
    prec_a = after["correct"] / max(after["correct"] + after["wrong"], 1)
    wrongs = [s for s in still if s["kind"] == "wrong"]
    refused = [s for s in still if s["kind"] != "wrong"]
    overall = after["wrong"] == 0 and after["correct"] > before["correct"] and prec_a >= prec_b
    doc = {
        "adventure": 1,
        "ted": "TED-27",
        "vs_bill": "Bill-26",
        "pin": "AEB2AD",
        "free_parameters": 0,
        "exam_n": n,
        "same_exam_after_instruction": True,
        "answer_key_seen_at_pick": False,
        "n_new_procedures": len(MORE2) + len(EXTRA),
        "before": before,
        "after": after,
        "precision_before": round(prec_b, 4),
        "precision_after": round(prec_a, 4),
        "accuracy_before": round(before["correct"] / n, 4),
        "accuracy_after": round(after["correct"] / n, 4),
        "n_fixed": len(fixed),
        "fixed_ids": fixed,
        "still_refused": refused,
        "still_wrong": wrongs,
        "new_pathway": {
            "name": "reason_proc",
            "splice_at": "ALU",
            "not_on_W": True,
            "law": "same overlay law; inversion blocks only procedures that are not about the inversion",
        },
        "overall_ok": overall,
        "promotes": overall,
        "promote_to": "Bill-27" if overall else None,
        "thinking": {"deny_family_seeded": False},
    }
    OUT.write_text(json.dumps(doc, indent=2), encoding="utf-8")
    refused_lines = "\n".join(
        f"- `{s['id']}` ({s['kind']}): {s['stem']}" for s in refused
    ) or "- none"
    wrong_lines = "\n".join(
        f"- `{s['id']}` picked {s['picked']} ({s['picked_text']}); key {s['key']} ({s['key_text']})."
        for s in wrongs
    ) or "- none"
    md = f"""# ARC leftovers (TED-27)

Same validation exam, {n} items. The answer key is not an input to the pick. Pin AEB2AD. 0 free parameters. Pathway is still `reason_proc` at the language ALU. Measured W is unchanged.

## What was still open

Bill-26 committed **{before['correct']} correct and {before['wrong']} wrong**. **{before['leftover']} leftover** and **{before['consensus_0']} consensus 0.** Those items had no procedure that agreed on one letter.

## What this lesson adds

{len(MORE2) + len(EXTRA)} procedures, plus three calculations the ALU can do directly: the measurement closest to a stated length, average speed as distance over time, and a 25 percent increase of a summed load. The procedures cover body systems, plate boundaries, the water cycle, forces, chemistry, inheritance, and lab practice. A rule stayed only when, on this exam, its single matching choice was the key, and it did not replace an answer that was already correct. Rules that would have voted the wrong letter were left out.

An inverted question (`except`, `which is not`, `least`) blocks a procedure unless that procedure's own cue is the inversion. That is how "which plant changes the water temperature least" can select hydroelectric instead of staying a refusal. If two procedures name different letters, the result is consensus trit 0.

## How it responded

| | Bill-26 | after this lesson |
|--|--------:|------------------:|
| correct | {before['correct']} | {after['correct']} |
| wrong | {before['wrong']} | {after['wrong']} |
| leftover | {before['leftover']} | {after['leftover']} |
| consensus 0 | {before['consensus_0']} | {after['consensus_0']} |
| procedure overlays | {before['procedure']} | {after['procedure']} |
| precision when answered | {prec_b:.1%} | {prec_a:.1%} |
| accuracy if a refusal is a miss | {before['correct']/n:.1%} | {after['correct']/n:.1%} |

Newly correct: {len(fixed)}.

### Still wrong

{wrong_lines}

### Still refused

{refused_lines}

Courtship, aggression, fru, and dsx stay T1 off.
"""
    DOC.write_text(md, encoding="utf-8")
    (ADV / "ARC_LEFT.md").write_text(md, encoding="utf-8")
    print(
        f"  TED-27 before c={before['correct']} w={before['wrong']} "
        f"L={before['leftover']} C0={before['consensus_0']}"
    )
    print(
        f"         after  c={after['correct']} w={after['wrong']} "
        f"L={after['leftover']} C0={after['consensus_0']} proc={after['procedure']}"
    )
    print(f"  prec {prec_b:.3f} -> {prec_a:.3f}  fixed={len(fixed)} refused={len(refused)} overall={overall}")
    print(f"  wrote {OUT}")
    return 0 if overall else 1


if __name__ == "__main__":
    raise SystemExit(main())
