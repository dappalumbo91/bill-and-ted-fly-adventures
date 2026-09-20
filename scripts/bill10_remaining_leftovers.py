#!/usr/bin/env python3
"""TED-11: remaining leftovers — name every mechanic, analog join, wait or refuse.

Does not invent dumps. Blocked stays blocked. Language stays a splice job, not W.

  python scripts/bill10_remaining_leftovers.py
"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "bill10_remaining_leftovers.json"
DOC = ROOT / "docs" / "LEFTOVER.md"
ADV = ROOT / "Bill and Ted fly adventures" / "Adventure-2"
REM = ROOT / "docs" / "LEFTOVER_REMAINING.md"


def load(name: str) -> dict:
    p = ROOT / "data" / name
    return json.loads(p.read_text(encoding="utf-8")) if p.is_file() else {}


def main() -> int:
    lm = load("leftover_map.json")
    vnc = load("vnc_side_predicted.json")
    pred = load("predicted_side_hops.json")
    solve = load("leftover_solve.json")
    feti = load("bill9_inxxx_leftover.json")
    func = load("fly_function.json")
    grow = load("bill8_grow_bottlenecks.json")
    guard = load("neural_guardrails.json")

    items = lm.get("items") or []
    by_status: dict[str, list] = {}
    for it in items:
        by_status.setdefault(it.get("status") or "?", []).append(it)

    rows = []

    def add(q: str, got, want) -> None:
        ok = got == want
        rows.append({"q": q, "got": got, "want": want, "ok": bool(ok)})

    named = all(it.get("mechanic") and it.get("do") for it in items)
    add("every leftover_map item has mechanic + do", named, True)
    add("leftover_map overall_ok", bool(lm.get("overall_ok")), True)
    add("VNC leftover unlabeled n=5", int(vnc.get("n_leftover") or 0), 5)
    add("predicted leftover five n=5", int(pred.get("n_leftover") or 0), 5)
    birth = ((solve.get("birthtime_prior") or {}).get("assigned") or {}).get("0")
    add("birthtime superpose 1268", int(birth or 0), 1268)
    add("Male tibia_extensor type string 0 (BANC FETi exists)", int(((feti.get("feti") or {}).get("male") or {}).get("tibia_extensor:type_prefix", {}).get("n_seed") or 0), 0)
    add("BANC FETi n=6 command", int(((feti.get("feti") or {}).get("banc") or {}).get("tibia_extensor_FETi:type_exact", {}).get("n_seed") or 0), 6)
    add("haltere type substr 0", int(((func.get("types") or {}).get("counts") or {}).get("haltere_type_substr") or 0), 0)
    add("wing type substr 0", int(((func.get("types") or {}).get("counts") or {}).get("wing_type_substr") or 0), 0)
    add("hg3 MN analog n=2", int(((func.get("types") or {}).get("counts") or {}).get("hg3 MN") or 0), 2)
    add("DNp01 analog n=2", int(((func.get("types") or {}).get("counts") or {}).get("DNp01") or 0), 2)
    add("INXXX007 leftover kind class_gated", (feti.get("leftover") or {}).get("kind"), "class_gated_leftover")
    add("blocked dumps still blocked", len(by_status.get("blocked") or []), 4)
    add("refused still refused (no invent)", len(by_status.get("refused") or []), 2)
    add("sibling pins 2", len(by_status.get("sibling") or []), 2)
    add("language deferred splice job", (by_status.get("deferred") or [{}])[0].get("kind"), "language")
    deny = (guard.get("deny_default_seeds") or {}).get("courtship", {}).get("default")
    add("courtship DENY not leftover of data", deny, "off")
    add("command modules still 5/6", int(grow.get("n_command_ok") or 0), 5)

    n_ok = sum(1 for r in rows if r["ok"])
    fail = [r["q"] for r in rows if not r["ok"]]
    overall = n_ok == len(rows)

    remaining = {
        "wait_dump_blocked": [
            {"name": it["name"], "analog": it["do"]} for it in by_status.get("blocked") or []
        ],
        "refuse_invent": [
            {"name": it["name"], "do": it["do"]} for it in by_status.get("refused") or []
        ],
        "sibling": [it["name"] for it in by_status.get("sibling") or []],
        "deferred_splice": [
            {
                "name": it["name"],
                "job": "language / coding tokens",
                "exists": "trit ALU + parser",
                "do": it["do"],
            }
            for it in by_status.get("deferred") or []
        ],
        "mapped_analogs": [
            {"job": "haltere", "analog": "JO gyro (nompC / JO hops)"},
            {"job": "wing type string", "analog": "hg3 MN + DNp01 plant"},
            {"job": "Male FETi", "analog": "BANC tibia_extensor_FETi; Male vnc_motor"},
            {"job": "VNC 5 unlabeled sides", "analog": "trit 0 leftover"},
            {"job": "birthtime 1268", "analog": "superpose trit 0"},
            {"job": "INXXX007", "analog": "chordotonal class → FETi"},
        ],
        "never_grow": ["il3LN6", "APL", "lLN2F_b", "INXXX007"],
    }

    doc = {
        "adventure": 2,
        "ted": "TED-11",
        "vs_bill": "Bill-10",
        "pin": "AEB2AD",
        "free_parameters": 0,
        "leftover_map_n": lm.get("n"),
        "leftover_map_n_mapped": lm.get("n_mapped"),
        "by_status": {k: len(v) for k, v in by_status.items()},
        "n": len(rows),
        "n_ok": n_ok,
        "fail": fail,
        "problems": rows,
        "remaining": remaining,
        "overall_ok": overall,
        "promotes": overall,
        "promote_to": "Bill-11" if overall else None,
        "thinking": {"deny_family_seeded": False},
    }
    OUT.write_text(json.dumps(doc, indent=2), encoding="utf-8")

    wait_tbl = "\n".join(f"| {x['name']} | blocked | {x['analog']} |" for x in remaining["wait_dump_blocked"])
    analog_tbl = "\n".join(f"| {x['job']} | {x['analog']} |" for x in remaining["mapped_analogs"])
    rem_md = f"""# Remaining leftovers (TED-11)

Pin **AEB2AD**. 0 free parameters. Leftover map **{lm.get('n_mapped')}/{lm.get('n')}** mapped.

Every item has a named mechanic and a do-not. Missing dumps stay missing.

## Wait (blocked dumps)

| Name | Status | Analog / do |
|------|--------|-------------|
{wait_tbl}

## Refuse (do not invent)

Embryo→pupa synapse movie; Fly Cell Atlas → bodyId.

## Sibling

Genetics pin D1D38A vs pack AEB2AD. Do not mix.

## Deferred splice

Language / coding tokens: trit ALU exists. Not an observer on FlyWire \(W\). Later invented region under leftover law, spliced at a command bottleneck, never APL/il3LN6.

## Mapped analogs (jobs we already have)

| Job | Analog |
|-----|--------|
{analog_tbl}

Never grow: {", ".join(remaining["never_grow"])}.

**{n_ok}/{len(rows)}**. promotes={overall}.
"""
    REM.write_text(rem_md, encoding="utf-8")
    if DOC.is_file():
        prev = DOC.read_text(encoding="utf-8")
        marker = "## Remaining (TED-11)"
        block = f"""
## Remaining (TED-11)

Map stamp **{lm.get('n_mapped')}/{lm.get('n')}**. Blocked 4 wait. Refused 2. Sibling 2. Language deferred splice. VNC 5 sides trit 0. Male FETi naming analog BANC. See `docs/LEFTOVER_REMAINING.md`.
"""
        if marker in prev:
            prev = prev.split(marker)[0].rstrip()
        DOC.write_text(prev + "\n" + block, encoding="utf-8")
    (ADV / "REMAINING.md").write_text(rem_md, encoding="utf-8")
    print(f"  TED-11 remaining leftovers {n_ok}/{len(rows)}  map={lm.get('n_mapped')}/{lm.get('n')}  overall={overall}")
    for r in rows:
        print(f"    {'OK' if r['ok'] else 'FAIL'}  {r['q']}: {r['got']}")
    if fail:
        print("  FAIL", fail)
    print(f"  wrote {OUT} and {REM}")
    return 0 if overall else 1


if __name__ == "__main__":
    raise SystemExit(main())
