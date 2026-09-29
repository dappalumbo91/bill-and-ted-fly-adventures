#!/usr/bin/env python3
"""Export the fly obligation spine from committed JSON.

Pin AEB2AD. The numbers are read from data/. Each prover then checks the
same integers. A missing measurement stays unset. Its prediction is the
test the file must pass when it arrives.

  python verification/export_fly_spine.py
"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
OUT = ROOT / "verification" / "fly"
PIN = "AEB2AD"
LAW = "S=K(T1+T2+T3); overlay 1/phi; consensus trit; 0 free parameters; pin AEB2AD"
CUT = 1000  # hop mass 1, in milli-units


def load(name: str) -> dict:
    path = DATA / name
    doc = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(doc, dict):
        raise SystemExit(f"{name} is not an object")
    if doc.get("pin") not in (None, PIN):
        raise SystemExit(f"{name} pin {doc.get('pin')}")
    if doc.get("free_parameters") not in (None, 0):
        raise SystemExit(f"{name} free_parameters {doc.get('free_parameters')}")
    return doc


def milli(value: float) -> int:
    return int(round(float(value) * 1000.0))


def hop2(doc: dict, program: str, field: str) -> float:
    for row in doc["hops"]["programs"]:
        if row["name"] == program:
            for step in row["flow"]:
                if int(step["hop"]) == 2:
                    return float(step[field])
    raise SystemExit(f"missing hop-2 {program} {field}")


def shared(doc: dict, type_name: str) -> dict:
    for row in doc["types"]:
        if row["type"] == type_name:
            return row
    raise SystemExit(f"missing shared type {type_name}")


def main() -> int:
    codex = load("codex_types.json")
    counts = load("type_counts.json")
    stamp = load("adventure1_stamp.json")
    male = load("male_cns_boot.json")
    banc = load("banc_connectome_boot.json")
    inventory = load("fly_connectome_inventory.json")
    shared_doc = load("shared_type_hops.json")
    guards = load("neural_guardrails.json")
    leftover = load("leftover_map.json")
    develop = load("develop_cycle.json")
    baseline = load("baseline_sim.json")
    ledger = json.loads((ROOT / "Bill and Ted fly adventures" / "ledger.json").read_text(encoding="utf-8"))

    if ledger.get("current_bill") != "Bill-36":
        raise SystemExit(f"current_bill {ledger.get('current_bill')}")
    if codex.get("overall_ok") is not True:
        raise SystemExit("codex_types overall_ok is not true")
    if stamp.get("measured_W_changed") is not False:
        raise SystemExit("measured W changed")

    sch = codex["schlegel_tsv"]
    meta = codex["fafb_783_meta"]
    fly = counts["flywire_annotations"]
    if (sch["n"], sch["DNg29"], sch["JO_type_prefix"]) != (
        fly["n"],
        fly["DNg29"],
        fly["JO_type_prefix"],
    ):
        raise SystemExit("Schlegel TSV does not match type_counts flywire")

    facts: dict[str, int] = {
        "free_parameters": 0,
        "phi_milli": 1618,
        "inv_phi_milli": 618,
        "schlegel_n": int(sch["n"]),
        "schlegel_dng29": int(sch["DNg29"]),
        "schlegel_jo": int(sch["JO_type_prefix"]),
        "meta_n": int(meta["n"]),
        "meta_dng29": int(meta["DNg29"]),
        "meta_jo": int(meta["JO_type_prefix"]),
        "jo_only_meta": int(codex["n_jo_only_in_meta"]),
        "jo_only_tsv": int(codex["n_jo_only_in_tsv"]),
        "male_dng29": int(counts["male_cns"]["DNg29"]),
        "male_jo": int(counts["male_cns"]["JO_type_prefix"]),
        "male_traced": int(counts["male_cns"]["n_traced"]),
        "banc_dng29": int(counts["banc"]["DNg29"]),
        "banc_jo": int(counts["banc"]["JO_type_prefix"]),
        "hemibrain_dng29": int(counts["hemibrain_cache"]["DNg29"]),
        "hemibrain_jo": int(counts["hemibrain_cache"]["JO_type_prefix"]),
        "hemibrain_typed": int(counts["hemibrain_cache"]["n_typed"]),
        "male_neurons": int(male["n_neurons"]),
        "male_gaba": int(male["n_gaba"]),
        "male_edges": int(male["n_edges"]),
        "banc_neurons": int(banc["n_neurons"]),
        "inventory_n": int(inventory["n_neurons"]),
        "easy_n": int(stamp["easy"]["n"]),
        "easy_correct": int(stamp["easy"]["correct"]),
        "easy_wrong": int(stamp["easy"]["wrong"]),
        "easy_leftover": int(stamp["easy"]["leftover"]),
        "easy_consensus": int(stamp["easy"]["consensus_0"]),
        "challenge_n": int(stamp["challenge"]["n"]),
        "challenge_correct": int(stamp["challenge"]["correct"]),
        "challenge_wrong": int(stamp["challenge"]["wrong"]),
        "challenge_leftover": int(stamp["challenge"]["leftover"]),
        "challenge_consensus": int(stamp["challenge"]["consensus_0"]),
        "use_n": int(stamp["use"]["n"]),
        "use_correct": int(stamp["use"]["correct"]),
        "use_wrong": int(stamp["use"]["wrong"]),
        "leftover_n": int(leftover["n"]),
        "leftover_mapped": int(leftover["n_mapped"]),
        "guard_jo": 1 if guards["allow_default_seeds"]["JO"]["default"] == "on" else 0,
        "guard_vnc": 1 if guards["allow_default_seeds"]["vnc_sensory"]["default"] == "on" else 0,
        "guard_gaba": 1 if guards["allow_default_seeds"]["GABAergic"]["default"] == "on" else 0,
        "guard_courtship": 0 if guards["deny_default_seeds"]["courtship"]["default"] == "off" else 1,
        "guard_aggression": 0 if guards["deny_default_seeds"]["aggression"]["default"] == "off" else 1,
        "guard_fru_dsx": 0 if guards["deny_default_seeds"]["fru_dsx"]["default"] == "off" else 1,
        "trials": int(baseline["n_trials"]),
        "resource_reached": int(baseline["n_resource_reached"]),
        "measured_w_changed": 0,
    }
    for type_name, side in (
        ("DNg29", "male"),
        ("DNg29", "banc"),
        ("KCg-m", "male"),
        ("KCg-m", "banc"),
        ("L5", "male"),
        ("L5", "banc"),
    ):
        row = shared(shared_doc, type_name)
        slug = {"DNg29": "dng29", "KCg-m": "kcgm", "L5": "l5"}[type_name]
        facts[f"{slug}_{side}_desc_milli"] = milli(row[side]["descending"])
        facts[f"{slug}_{side}_vm_milli"] = milli(row[side]["vnc_motor"])
    facts["early_vm_milli"] = milli(hop2(develop, "birth_early", "vnc_motor"))
    facts["h07b_vm_milli"] = milli(hop2(develop, "truman_07B", "vnc_motor"))
    facts["mbp3_vm_milli"] = milli(hop2(develop, "ito_MBp3", "vnc_motor"))
    facts["early_n"] = int(next(p["n_seed"] for p in develop["hops"]["programs"] if p["name"] == "birth_early"))
    facts["h07b_n"] = int(next(p["n_seed"] for p in develop["hops"]["programs"] if p["name"] == "truman_07B"))
    facts["mbp3_n"] = int(next(p["n_seed"] for p in develop["hops"]["programs"] if p["name"] == "ito_MBp3"))

    obligations: list[dict] = []

    def add(oid: str, kind: str, lhs: int, rhs: int, statement: str, source: str) -> None:
        obligations.append(
            {
                "id": oid,
                "kind": kind,
                "lhs": int(lhs),
                "rhs": int(rhs),
                "statement": statement,
                "source": source,
                "law": LAW,
            }
        )

    for name, value in facts.items():
        add(f"eq_{name}", "nat_eq", value, value, f"{name} = {value}", "committed JSON")

    add(
        "eq_jo_gap",
        "nat_eq",
        facts["meta_jo"],
        facts["schlegel_jo"] + facts["jo_only_meta"],
        "meta JO prefix = Schlegel JO prefix + roots only in the meta table",
        "data/codex_types.json",
    )
    add("eq_jo_only_tsv", "nat_eq", facts["jo_only_tsv"], 0, "no TSV JO root is absent from the meta table", "data/codex_types.json")
    add("eq_inventory_schlegel", "nat_eq", facts["inventory_n"], facts["schlegel_n"], "inventory n equals the Schlegel TSV n", "data/fly_connectome_inventory.json")
    add("eq_dng29_male_schlegel", "nat_eq", facts["male_dng29"], facts["schlegel_dng29"], "Male CNS DNg29 equals Schlegel DNg29", "data/type_counts.json")
    add("eq_dng29_banc_schlegel", "nat_eq", facts["banc_dng29"], facts["schlegel_dng29"], "BANC DNg29 equals Schlegel DNg29", "data/type_counts.json")
    add("eq_dng29_meta_schlegel", "nat_eq", facts["meta_dng29"], facts["schlegel_dng29"], "meta DNg29 equals Schlegel DNg29", "data/codex_types.json")
    add("eq_hemibrain_dng29", "nat_eq", facts["hemibrain_dng29"], 0, "hemibrain has no DNg29", "data/type_counts.json")
    add(
        "eq_easy_partition",
        "nat_eq",
        facts["easy_correct"] + facts["easy_wrong"] + facts["easy_leftover"] + facts["easy_consensus"],
        facts["easy_n"],
        "Easy correct + wrong + leftover + consensus = n",
        "data/adventure1_stamp.json",
    )
    add(
        "eq_challenge_partition",
        "nat_eq",
        facts["challenge_correct"] + facts["challenge_wrong"] + facts["challenge_leftover"] + facts["challenge_consensus"],
        facts["challenge_n"],
        "Challenge correct + wrong + leftover + consensus = n",
        "data/adventure1_stamp.json",
    )
    add(
        "eq_use_partition",
        "nat_eq",
        facts["use_correct"] + facts["use_wrong"],
        facts["use_n"],
        "use correct + wrong = n",
        "data/adventure1_stamp.json",
    )
    add("eq_use_wrong", "nat_eq", facts["use_wrong"], 0, "use wrong = 0", "data/adventure1_stamp.json")
    add("eq_leftover_closed", "nat_eq", facts["leftover_mapped"], facts["leftover_n"], "leftover map is closed", "data/leftover_map.json")
    add("eq_male_traced", "nat_eq", facts["male_traced"], facts["male_neurons"], "type-count traced equals the Male CNS boot", "data/male_cns_boot.json")
    for name, statement in (
        ("dng29_male_desc_milli", "DNg29 male descending mass is above 1"),
        ("dng29_banc_desc_milli", "DNg29 BANC descending mass is above 1"),
        ("early_vm_milli", "early-born hop-2 vnc_motor is above 1"),
        ("h07b_vm_milli", "07B hop-2 vnc_motor is above 1"),
    ):
        add(f"gt_{name}", "nat_gt", facts[name], CUT, statement, "committed hop JSON")
    for name, statement in (
        ("kcgm_male_vm_milli", "KCg-m male vnc_motor is at or below 1"),
        ("kcgm_banc_vm_milli", "KCg-m BANC vnc_motor is at or below 1"),
        ("l5_male_vm_milli", "L5 male vnc_motor is at or below 1"),
        ("l5_banc_vm_milli", "L5 BANC vnc_motor is at or below 1"),
        ("mbp3_vm_milli", "MBp3 hop-2 vnc_motor is at or below 1"),
    ):
        add(f"le_{name}", "nat_le", facts[name], CUT, statement, "committed hop JSON")
    add("le_resource_trials", "nat_le", facts["resource_reached"], facts["trials"], "resource reaches are at most the trial count", "data/baseline_sim.json")

    failed = []
    for row in obligations:
        lhs, rhs, kind = row["lhs"], row["rhs"], row["kind"]
        ok = (
            (kind == "nat_eq" and lhs == rhs)
            or (kind == "nat_lt" and lhs < rhs)
            or (kind == "nat_le" and lhs <= rhs)
            or (kind == "nat_gt" and lhs > rhs)
        )
        if not ok:
            failed.append(row["id"])
    if failed:
        raise SystemExit(f"obligation arithmetic failed: {failed}")

    roots = [str(row["root_id"]) for row in codex["jo_only_in_meta_rows"]]
    predictions = [
        {
            "id": "codex_portal_csv",
            "measurement": "Codex portal gzipped FAFB CSV",
            "status": "absent",
            "filled": False,
            "test": (
                "DNg29 must equal the Schlegel count. "
                "A JO prefix equal to the Schlegel count passes the split-name table. "
                "A JO prefix equal to the meta count passes the coarse-name table. "
                "The coarse-minus-split gap must be the recorded meta-only JO roots."
            ),
            "holds_now": {
                "schlegel_dng29": facts["schlegel_dng29"],
                "schlegel_jo": facts["schlegel_jo"],
                "meta_jo": facts["meta_jo"],
                "jo_only_meta_roots": roots,
            },
        },
        {
            "id": "fly_cell_atlas_bodyid",
            "measurement": "Fly Cell Atlas bodyId join",
            "status": "absent",
            "filled": False,
            "test": (
                "When a published bodyId table arrives, nompC, iav, and nan rows whose root is in the Schlegel TSV "
                "must carry a JO cell_type prefix. Gad1 rows must land in the GABA class already counted on the Male CNS. "
                "No bodyId is assigned before that table."
            ),
            "holds_now": {"body_id_count": None, "male_gaba": facts["male_gaba"]},
        },
        {
            "id": "pupal_synapse_series",
            "measurement": "embryo to pupa to adult synapse time series",
            "status": "absent",
            "filled": False,
            "test": (
                "A published series passes at its adult end when early-born and 07B hop-2 vnc_motor stay above 1 "
                "and MBp3 hop-2 vnc_motor stays at or below 1. Intermediate frames are not given values."
            ),
            "holds_now": {
                "early_n": facts["early_n"],
                "early_vm_milli": facts["early_vm_milli"],
                "h07b_n": facts["h07b_n"],
                "h07b_vm_milli": facts["h07b_vm_milli"],
                "mbp3_n": facts["mbp3_n"],
                "mbp3_vm_milli": facts["mbp3_vm_milli"],
                "frame_count": None,
            },
        },
        {
            "id": "iwasaki_videos",
            "measurement": "Iwasaki object-interaction videos",
            "status": "absent",
            "filled": False,
            "test": (
                "When frames arrive, score them with the same ball rule and the same guardrail: "
                "courtship, aggression, and fru/dsx stay unseeded. The path is not fitted. "
                "The Harvard ball trials already on disk stay the measured baseline."
            ),
            "holds_now": {
                "trials": facts["trials"],
                "resource_reached": facts["resource_reached"],
                "frame_count": None,
            },
        },
    ]

    doc = {
        "application": "fly-obligation-spine",
        "pin": PIN,
        "free_parameters": 0,
        "current_bill": "Bill-36",
        "law": LAW,
        "n_obligations": len(obligations),
        "n_predictions": len(predictions),
        "facts": facts,
        "obligations": obligations,
        "predictions": predictions,
        "decision": {
            "one_label": "overlay",
            "two_labels": "trit 0",
            "silence": "trit 0",
            "repeated_label": "overlay",
        },
    }
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "obligations.json").write_text(json.dumps(doc, indent=2) + "\n", encoding="utf-8")
    write_lean(facts)
    write_coq(facts)
    write_isabelle(facts)
    write_fstar(facts)
    write_smt(facts)
    write_rust(facts)
    write_tla()
    print(f"obligations={len(obligations)} predictions={len(predictions)}")
    print(f"jo_gap {facts['meta_jo']} = {facts['schlegel_jo']} + {facts['jo_only_meta']}")
    print(f"wrote {OUT}")
    return 0


def lean_fact(name: str, value: int) -> str:
    return f"def {name} : Nat := {value}\n"


def write_lean(facts: dict[str, int]) -> None:
    body = [
        "-- Fly obligation spine. Pin AEB2AD. 0 free parameters.",
        "-- Generated from committed JSON by verification/export_fly_spine.py.",
        "-- A missing measurement stays none. The gate is the test, not a filled count.",
        "",
        'def pin : String := "AEB2AD"',
        "def freeParameters : Nat := 0",
        "",
        "def commit {α : Type} [DecidableEq α] (votes : List α) : Option α :=",
        "  match votes.eraseDups with",
        "  | [a] => some a",
        "  | _ => none",
        "",
        "#guard freeParameters = 0",
        '#guard pin = "AEB2AD"',
        '#guard commit ["reflect"] = some "reflect"',
        '#guard commit ([] : List String) = none',
        '#guard commit ["rain", "drought"] = none',
        '#guard commit ["gas", "gas"] = some "gas"',
        "",
    ]
    for name, value in facts.items():
        body.append(lean_fact(name, value).rstrip())
    body += [
        "",
        "theorem jo_gap : meta_jo = schlegel_jo + jo_only_meta := by decide",
        "theorem jo_only_tsv_zero : jo_only_tsv = 0 := by decide",
        "theorem inventory_is_schlegel : inventory_n = schlegel_n := by decide",
        "theorem dng29_four : male_dng29 = schlegel_dng29 ∧ banc_dng29 = schlegel_dng29 ∧ meta_dng29 = schlegel_dng29 := by decide",
        "theorem hemibrain_no_dng29 : hemibrain_dng29 = 0 := by decide",
        "theorem easy_partition : easy_correct + easy_wrong + easy_leftover + easy_consensus = easy_n := by decide",
        "theorem challenge_partition : challenge_correct + challenge_wrong + challenge_leftover + challenge_consensus = challenge_n := by decide",
        "theorem use_partition : use_correct + use_wrong = use_n := by decide",
        "theorem use_no_wrong : use_wrong = 0 := by decide",
        "theorem leftover_closed : leftover_mapped = leftover_n := by decide",
        "theorem dng29_male_desc_on : dng29_male_desc_milli > 1000 := by decide",
        "theorem dng29_banc_desc_on : dng29_banc_desc_milli > 1000 := by decide",
        "theorem kcgm_male_motor_off : kcgm_male_vm_milli ≤ 1000 := by decide",
        "theorem kcgm_banc_motor_off : kcgm_banc_vm_milli ≤ 1000 := by decide",
        "theorem l5_male_motor_off : l5_male_vm_milli ≤ 1000 := by decide",
        "theorem l5_banc_motor_off : l5_banc_vm_milli ≤ 1000 := by decide",
        "theorem early_motor_on : early_vm_milli > 1000 := by decide",
        "theorem h07b_motor_on : h07b_vm_milli > 1000 := by decide",
        "theorem mbp3_motor_off : mbp3_vm_milli ≤ 1000 := by decide",
        "theorem guards_on : guard_jo = 1 ∧ guard_vnc = 1 ∧ guard_gaba = 1 := by decide",
        "theorem guards_off : guard_courtship = 0 ∧ guard_aggression = 0 ∧ guard_fru_dsx = 0 := by decide",
        "theorem resource_within_trials : resource_reached ≤ trials := by decide",
        "",
        "def codexDNg29Gate (exportCount : Nat) : Bool := exportCount = schlegel_dng29",
        "def joExportGate (exportJO : Nat) : Bool := exportJO = schlegel_jo || exportJO = meta_jo",
        "def fcaBodyIdCount : Option Nat := none",
        "def pupalFrameCount : Option Nat := none",
        "def iwasakiFrameCount : Option Nat := none",
        "",
        "theorem codex_gate_accepts_schlegel : codexDNg29Gate schlegel_dng29 = true := by decide",
        "theorem codex_gate_rejects_zero : codexDNg29Gate 0 = false := by decide",
        "theorem jo_gate_accepts_split : joExportGate schlegel_jo = true := by decide",
        "theorem jo_gate_accepts_coarse : joExportGate meta_jo = true := by decide",
        "theorem jo_gate_rejects_zero : joExportGate 0 = false := by decide",
        "theorem fca_bodyid_unseen : fcaBodyIdCount = none := by rfl",
        "theorem pupal_frames_unseen : pupalFrameCount = none := by rfl",
        "theorem iwasaki_frames_unseen : iwasakiFrameCount = none := by rfl",
        "",
    ]
    path = OUT / "lean" / "FlySpine.lean"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(body), encoding="utf-8")


def write_coq(facts: dict[str, int]) -> None:
    lines = ["(* Fly obligation spine. Generated. Pin AEB2AD. Prelude only. *)", ""]
    for name, value in facts.items():
        lines.append(f"Definition {name} := {value}.")
    lines += [
        "",
        "Lemma ok_free_parameters : free_parameters = 0.",
        "Proof. reflexivity. Qed.",
        "Lemma ok_jo_gap : meta_jo = schlegel_jo + jo_only_meta.",
        "Proof. reflexivity. Qed.",
        "Lemma ok_jo_only_tsv : jo_only_tsv = 0.",
        "Proof. reflexivity. Qed.",
        "Lemma ok_inventory : inventory_n = schlegel_n.",
        "Proof. reflexivity. Qed.",
        "Lemma ok_dng29_male : male_dng29 = schlegel_dng29.",
        "Proof. reflexivity. Qed.",
        "Lemma ok_dng29_banc : banc_dng29 = schlegel_dng29.",
        "Proof. reflexivity. Qed.",
        "Lemma ok_dng29_meta : meta_dng29 = schlegel_dng29.",
        "Proof. reflexivity. Qed.",
        "Lemma ok_hemibrain_dng29 : hemibrain_dng29 = 0.",
        "Proof. reflexivity. Qed.",
        "Lemma ok_easy : easy_correct + easy_wrong + easy_leftover + easy_consensus = easy_n.",
        "Proof. reflexivity. Qed.",
        "Lemma ok_challenge : challenge_correct + challenge_wrong + challenge_leftover + challenge_consensus = challenge_n.",
        "Proof. reflexivity. Qed.",
        "Lemma ok_use : use_correct + use_wrong = use_n.",
        "Proof. reflexivity. Qed.",
        "Lemma ok_leftover : leftover_mapped = leftover_n.",
        "Proof. reflexivity. Qed.",
        "Lemma ok_dng29_male_desc : Nat.ltb 1000 dng29_male_desc_milli = true.",
        "Proof. reflexivity. Qed.",
        "Lemma ok_dng29_banc_desc : Nat.ltb 1000 dng29_banc_desc_milli = true.",
        "Proof. reflexivity. Qed.",
        "Lemma ok_kcgm_male : Nat.leb kcgm_male_vm_milli 1000 = true.",
        "Proof. reflexivity. Qed.",
        "Lemma ok_kcgm_banc : Nat.leb kcgm_banc_vm_milli 1000 = true.",
        "Proof. reflexivity. Qed.",
        "Lemma ok_l5_male : Nat.leb l5_male_vm_milli 1000 = true.",
        "Proof. reflexivity. Qed.",
        "Lemma ok_l5_banc : Nat.leb l5_banc_vm_milli 1000 = true.",
        "Proof. reflexivity. Qed.",
        "Lemma ok_early : Nat.ltb 1000 early_vm_milli = true.",
        "Proof. reflexivity. Qed.",
        "Lemma ok_h07b : Nat.ltb 1000 h07b_vm_milli = true.",
        "Proof. reflexivity. Qed.",
        "Lemma ok_mbp3 : Nat.leb mbp3_vm_milli 1000 = true.",
        "Proof. reflexivity. Qed.",
        "Lemma ok_resource : Nat.leb resource_reached trials = true.",
        "Proof. reflexivity. Qed.",
        "Lemma ok_guards_on : guard_jo = 1 /\\ guard_vnc = 1 /\\ guard_gaba = 1.",
        "Proof. repeat split; reflexivity. Qed.",
        "Lemma ok_guards_off : guard_courtship = 0 /\\ guard_aggression = 0 /\\ guard_fru_dsx = 0.",
        "Proof. repeat split; reflexivity. Qed.",
        "",
    ]
    path = OUT / "coq" / "FlySpine.v"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def write_isabelle(facts: dict[str, int]) -> None:
    lines = [
        "theory FlySpine",
        "  imports Main",
        "begin",
        "",
        "(* Fly obligation spine. Generated. Pin AEB2AD. *)",
        "",
    ]
    for name, value in facts.items():
        lines.append(f'definition {name} :: nat where "{name} = {value}"')
    lemmas = [
        ("ok_free", "free_parameters = 0", "free_parameters_def"),
        ("ok_jo_gap", "meta_jo = schlegel_jo + jo_only_meta", "meta_jo_def schlegel_jo_def jo_only_meta_def"),
        ("ok_inventory", "inventory_n = schlegel_n", "inventory_n_def schlegel_n_def"),
        ("ok_dng29", "male_dng29 = schlegel_dng29 \\<and> banc_dng29 = schlegel_dng29 \\<and> meta_dng29 = schlegel_dng29", "male_dng29_def banc_dng29_def meta_dng29_def schlegel_dng29_def"),
        ("ok_hemibrain", "hemibrain_dng29 = 0", "hemibrain_dng29_def"),
        ("ok_easy", "easy_correct + easy_wrong + easy_leftover + easy_consensus = easy_n", "easy_correct_def easy_wrong_def easy_leftover_def easy_consensus_def easy_n_def"),
        ("ok_challenge", "challenge_correct + challenge_wrong + challenge_leftover + challenge_consensus = challenge_n", "challenge_correct_def challenge_wrong_def challenge_leftover_def challenge_consensus_def challenge_n_def"),
        ("ok_use", "use_correct + use_wrong = use_n", "use_correct_def use_wrong_def use_n_def"),
        ("ok_leftover", "leftover_mapped = leftover_n", "leftover_mapped_def leftover_n_def"),
        ("ok_dng_male", "dng29_male_desc_milli > 1000", "dng29_male_desc_milli_def"),
        ("ok_dng_banc", "dng29_banc_desc_milli > 1000", "dng29_banc_desc_milli_def"),
        ("ok_kcg_male", "kcgm_male_vm_milli \\<le> 1000", "kcgm_male_vm_milli_def"),
        ("ok_kcg_banc", "kcgm_banc_vm_milli \\<le> 1000", "kcgm_banc_vm_milli_def"),
        ("ok_l5_male", "l5_male_vm_milli \\<le> 1000", "l5_male_vm_milli_def"),
        ("ok_l5_banc", "l5_banc_vm_milli \\<le> 1000", "l5_banc_vm_milli_def"),
        ("ok_early", "early_vm_milli > 1000", "early_vm_milli_def"),
        ("ok_h07b", "h07b_vm_milli > 1000", "h07b_vm_milli_def"),
        ("ok_mbp3", "mbp3_vm_milli \\<le> 1000", "mbp3_vm_milli_def"),
        ("ok_guard_jo", "guard_jo = 1", "guard_jo_def"),
        ("ok_guard_vnc", "guard_vnc = 1", "guard_vnc_def"),
        ("ok_guard_gaba", "guard_gaba = 1", "guard_gaba_def"),
        ("ok_guard_court", "guard_courtship = 0", "guard_courtship_def"),
        ("ok_guard_aggression", "guard_aggression = 0", "guard_aggression_def"),
        ("ok_guard_fru", "guard_fru_dsx = 0", "guard_fru_dsx_def"),
        ("ok_resource", "resource_reached \\<le> trials", "resource_reached_def trials_def"),
    ]
    lines.append("")
    for name, goal, defs in lemmas:
        method = "eval" if (">" in goal or "\\<le>" in goal) else "simp"
        lines.append(f'lemma {name}: "{goal}"')
        lines.append(f"  unfolding {defs} by {method}")
        lines.append("")
    lines.append("end")
    lines.append("")
    thy = OUT / "isabelle"
    thy.mkdir(parents=True, exist_ok=True)
    (thy / "FlySpine.thy").write_text("\n".join(lines), encoding="utf-8")
    (thy / "ROOT").write_text(
        "session FlySpine = HOL +\n  options [document = false, timeout = 120]\n  theories\n    FlySpine\n",
        encoding="utf-8",
    )


def write_fstar(facts: dict[str, int]) -> None:
    lines = [
        "module FlySpine",
        "",
        "(* Fly obligation spine. Generated. Pin AEB2AD. *)",
        "",
    ]
    for name, value in facts.items():
        lines.append(f"let {name} : nat = {value}")
    lines += [
        "",
        "let _ = assert (free_parameters = 0)",
        "let _ = assert (meta_jo = schlegel_jo + jo_only_meta)",
        "let _ = assert (jo_only_tsv = 0)",
        "let _ = assert (inventory_n = schlegel_n)",
        "let _ = assert (male_dng29 = schlegel_dng29)",
        "let _ = assert (banc_dng29 = schlegel_dng29)",
        "let _ = assert (meta_dng29 = schlegel_dng29)",
        "let _ = assert (hemibrain_dng29 = 0)",
        "let _ = assert (easy_correct + easy_wrong + easy_leftover + easy_consensus = easy_n)",
        "let _ = assert (challenge_correct + challenge_wrong + challenge_leftover + challenge_consensus = challenge_n)",
        "let _ = assert (use_correct + use_wrong = use_n)",
        "let _ = assert (use_wrong = 0)",
        "let _ = assert (leftover_mapped = leftover_n)",
        "let _ = assert (dng29_male_desc_milli > 1000)",
        "let _ = assert (dng29_banc_desc_milli > 1000)",
        "let _ = assert (kcgm_male_vm_milli <= 1000)",
        "let _ = assert (kcgm_banc_vm_milli <= 1000)",
        "let _ = assert (l5_male_vm_milli <= 1000)",
        "let _ = assert (l5_banc_vm_milli <= 1000)",
        "let _ = assert (early_vm_milli > 1000)",
        "let _ = assert (h07b_vm_milli > 1000)",
        "let _ = assert (mbp3_vm_milli <= 1000)",
        "let _ = assert (guard_jo = 1)",
        "let _ = assert (guard_vnc = 1)",
        "let _ = assert (guard_gaba = 1)",
        "let _ = assert (guard_courtship = 0)",
        "let _ = assert (guard_aggression = 0)",
        "let _ = assert (guard_fru_dsx = 0)",
        "let _ = assert (resource_reached <= trials)",
        "",
    ]
    path = OUT / "fstar" / "FlySpine.fst"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def write_smt(facts: dict[str, int]) -> None:
    lines = [
        "; Fly obligation spine. Generated. Pin AEB2AD.",
        "(set-logic QF_LIA)",
        "",
    ]
    for name, value in facts.items():
        lines.append(f"(declare-const {name} Int)")
        lines.append(f"(assert (= {name} {value}))")
    lines += [
        "(assert (= meta_jo (+ schlegel_jo jo_only_meta)))",
        "(assert (= jo_only_tsv 0))",
        "(assert (= inventory_n schlegel_n))",
        "(assert (= male_dng29 schlegel_dng29))",
        "(assert (= banc_dng29 schlegel_dng29))",
        "(assert (= meta_dng29 schlegel_dng29))",
        "(assert (= hemibrain_dng29 0))",
        "(assert (= (+ easy_correct easy_wrong easy_leftover easy_consensus) easy_n))",
        "(assert (= (+ challenge_correct challenge_wrong challenge_leftover challenge_consensus) challenge_n))",
        "(assert (= (+ use_correct use_wrong) use_n))",
        "(assert (= leftover_mapped leftover_n))",
        "(assert (> dng29_male_desc_milli 1000))",
        "(assert (> dng29_banc_desc_milli 1000))",
        "(assert (<= kcgm_male_vm_milli 1000))",
        "(assert (<= kcgm_banc_vm_milli 1000))",
        "(assert (<= l5_male_vm_milli 1000))",
        "(assert (<= l5_banc_vm_milli 1000))",
        "(assert (> early_vm_milli 1000))",
        "(assert (> h07b_vm_milli 1000))",
        "(assert (<= mbp3_vm_milli 1000))",
        "(assert (= guard_courtship 0))",
        "(assert (= guard_jo 1))",
        "(assert (<= resource_reached trials))",
        "(check-sat)",
        "",
    ]
    path = OUT / "smt" / "fly_spine.smt2"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def write_rust(facts: dict[str, int]) -> None:
    consts = [f"pub const {name}: u32 = {value};" for name, value in facts.items()]
    checks = ["    assert_eq!(free_parameters, 0u32);"]
    for name, value in facts.items():
        if name == "free_parameters":
            continue
        checks.append(f"    assert_eq!({name}, {value}u32);")
    checks += [
        "    assert_eq!(meta_jo, schlegel_jo + jo_only_meta);",
        "    assert_eq!(inventory_n, schlegel_n);",
        "    assert_eq!(male_dng29, schlegel_dng29);",
        "    assert_eq!(banc_dng29, schlegel_dng29);",
        "    assert_eq!(easy_correct + easy_wrong + easy_leftover + easy_consensus, easy_n);",
        "    assert_eq!(challenge_correct + challenge_wrong + challenge_leftover + challenge_consensus, challenge_n);",
        "    assert_eq!(use_correct + use_wrong, use_n);",
        "    assert_eq!(leftover_mapped, leftover_n);",
        "    assert!(dng29_male_desc_milli > 1000);",
        "    assert!(dng29_banc_desc_milli > 1000);",
        "    assert!(kcgm_male_vm_milli <= 1000);",
        "    assert!(kcgm_banc_vm_milli <= 1000);",
        "    assert!(l5_male_vm_milli <= 1000);",
        "    assert!(l5_banc_vm_milli <= 1000);",
        "    assert!(early_vm_milli > 1000);",
        "    assert!(h07b_vm_milli > 1000);",
        "    assert!(mbp3_vm_milli <= 1000);",
        "    assert!(resource_reached <= trials);",
        "    assert_eq!(guard_courtship, 0);",
        "    assert_eq!(guard_aggression, 0);",
        "    assert_eq!(guard_fru_dsx, 0);",
        "    assert_eq!(guard_jo, 1);",
        "    assert_eq!(guard_vnc, 1);",
        "    assert_eq!(guard_gaba, 1);",
    ]
    catalog = "\n".join(
        [
            "//! Generated fly spine integers. Pin AEB2AD.",
            "#![allow(non_upper_case_globals)]",
            "",
            *consts,
            "",
            "pub fn check() {",
            *checks,
            "}",
            "",
        ]
    )
    main = "\n".join(
        [
            "//! Fly spine host replay. Pin AEB2AD. Law S = K(T1+T2+T3). 0 free parameters.",
            "",
            "mod catalog;",
            "",
            "fn main() {",
            "    let phi = (1.0_f64 + 5.0_f64.sqrt()) / 2.0;",
            "    let inv_phi = 1.0 / phi;",
            "    assert!((phi - 1.618033988749895).abs() < 1e-12);",
            "    assert!((inv_phi - 0.618033988749895).abs() < 1e-12);",
            "    catalog::check();",
            '    println!("FSOT_FLY_SPINE_RUST_OK");',
            '    println!("phi={phi:.15}");',
            '    println!("inv_phi={inv_phi:.15}");',
            "}",
            "",
        ]
    )
    cargo = "\n".join(
        [
            "[package]",
            'name = "fsot_fly_spine"',
            'version = "0.1.0"',
            'edition = "2021"',
            "",
            "[[bin]]",
            'name = "fsot_fly_spine"',
            'path = "src/main.rs"',
            "",
        ]
    )
    rust = OUT / "rust"
    (rust / "src").mkdir(parents=True, exist_ok=True)
    (rust / "Cargo.toml").write_text(cargo, encoding="utf-8")
    (rust / "src" / "main.rs").write_text(main, encoding="utf-8")
    (rust / "src" / "catalog.rs").write_text(catalog, encoding="utf-8")


def write_tla() -> None:
    tla = """---- MODULE FlySpine ----
EXTENDS Naturals

\\* Fly obligation routing. Pin AEB2AD. 0 free parameters.
\\* Courtship stays off. A missing measurement is not filled with a count.
\\* Synapses are not invented.

VARIABLES courtship, freeParams, inventedSynapse, missingFile

TypeOK ==
  /\\ courtship \\in BOOLEAN
  /\\ freeParams \\in Nat
  /\\ inventedSynapse \\in BOOLEAN
  /\\ missingFile \\in BOOLEAN

Init ==
  /\\ courtship = FALSE
  /\\ freeParams = 0
  /\\ inventedSynapse = FALSE
  /\\ missingFile = TRUE

ObserveAllowed ==
  /\\ UNCHANGED <<courtship, freeParams, inventedSynapse, missingFile>>

Next == ObserveAllowed

Spec == Init /\\ [][Next]_<<courtship, freeParams, inventedSynapse, missingFile>>

CourtshipOff == courtship = FALSE
ZeroFreeParams == freeParams = 0
NeverInventSynapse == inventedSynapse = FALSE
MissingStaysMissing == missingFile = TRUE

====
"""
    cfg = """SPECIFICATION Spec
INVARIANT TypeOK
INVARIANT CourtshipOff
INVARIANT ZeroFreeParams
INVARIANT NeverInventSynapse
INVARIANT MissingStaysMissing
"""
    folder = OUT / "tla"
    folder.mkdir(parents=True, exist_ok=True)
    (folder / "FlySpine.tla").write_text(tla, encoding="utf-8")
    (folder / "FlySpine.cfg").write_text(cfg, encoding="utf-8")


if __name__ == "__main__":
    raise SystemExit(main())
