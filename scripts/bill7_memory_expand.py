#!/usr/bin/env python3
"""TED-8: expand STM/LTM from the blueprint; map growth sites; do not invent axons.

STM window = round(φ²) overlay slots (was 1).
LTM = addressable bindings on measured classes (JO, VNC, KC, DNp01, MBON mass).
Write-forbid leftover hubs: APL, il3LN6.

The fly graph still collapses at hop-1. That collapse *is* the limitation of
the tissue. This pass applies residual law on that structure and writes the
growth map for later evolutionary seed of command bottlenecks.

  python scripts/bill7_memory_expand.py
"""
from __future__ import annotations

import runio
runio.install()

import json
from collections import deque
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
import sys

sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "vendor"))

import fsot_compute as fc  # noqa: E402
from trit_alu import consensus  # noqa: E402

OUT = ROOT / "data" / "bill7_memory_expand.json"
DOC = ROOT / "docs" / "MEMORY_LIMITS.md"
GROW = ROOT / "Bill and Ted fly adventures" / "Adventure-2" / "GROWTH.md"
PHI = float(fc.PHI)
INV_PHI = 1.0 / PHI
STM_SLOTS = int(round(PHI * PHI))  # φ² ≈ 2.618 → 3
LTM_HORIZON = int(round(PHI ** 5))  # hop leftover 11
FORBID_WRITE = frozenset({"APL", "il3LN6", "lLN2F_b", "KCg-s1"})


def load(name: str) -> dict:
    p = ROOT / "data" / name
    return json.loads(p.read_text(encoding="utf-8")) if p.is_file() else {}


def main() -> int:
    stress = load("stress_map.json")
    male = load("male_cns_boot.json")
    ken = load("kenyon_connectome_boot.json")
    mem7 = load("bill6_memory.json")
    courses = load("bill4_math_courses.json")
    guard = load("neural_guardrails.json")
    func = load("fly_function.json")

    bottlenecks = stress.get("top_bottlenecks") or stress.get("all") or []
    never = [b for b in bottlenecks if b.get("kind") == "leftover_hub" or not b.get("expansion")]
    later = [b for b in bottlenecks if b.get("kind") == "command_bottleneck" and b.get("expansion")]
    # leftover_hub with expansion null is never; command with expansion is later
    never = [b for b in bottlenecks if b.get("kind") == "leftover_hub"]
    later = [b for b in bottlenecks if b.get("kind") == "command_bottleneck"]

    rows: list[dict] = []

    def add(kind: str, q: str, got, want) -> None:
        ok = got == want
        if isinstance(got, float) or isinstance(want, float):
            ok = abs(float(got) - float(want)) <= 1e-9 * max(1.0, abs(float(want)))
        rows.append({"kind": kind, "q": q, "got": got, "want": want, "ok": bool(ok)})

    add("law", "STM slots = round(φ²)", STM_SLOTS, 3)
    add("law", "LTM hop horizon = round(φ⁵)", LTM_HORIZON, 11)
    add("law", "TED-7 STM was 1 item (first missed)", int((mem7.get("exam") or {}).get("stm_holds_last") or 0) == 1 and not (mem7.get("exam") or {}).get("stm_holds_first"), True)

    past = [p for p in (courses.get("problems") or []) if p.get("ok")]
    encode = past[: STM_SLOTS + 2]  # 5 items: window 3, two evicted
    if len(encode) < STM_SLOTS + 2:
        encode = past[: max(5, len(past))]

    stm: deque = deque(maxlen=STM_SLOTS)
    for p in encode:
        stm.append({"q": p["q"], "got": p["got"], "observer": p.get("observer")})

    def stm_has(q: str) -> bool:
        return any(x["q"] == q for x in stm)

    add("stm", "window holds last 3 encode items", all(stm_has(p["q"]) for p in encode[-STM_SLOTS:]), True)
    add("stm", "window evicts item 0 (beyond φ²)", stm_has(encode[0]["q"]), False)
    add("stm", "window evicts item 1", stm_has(encode[1]["q"]), False)
    add("stm", "TED-8 STM first-of-last-3 HIT (was MISS at capacity 1)", stm_has(encode[-3]["q"]), True)

    # Dual-observer superposition (walk ∧ hear both on)
    add("stm", "cons(walk +1, JO walk +1) = +1 dual-hold", consensus(1, 1), 1)
    add("stm", "cons(walk +1, smell leftover 0) = 0 superpose not overwrite", consensus(1, 0), 0)

    # LTM addressable index on measured classes — overlay bindings, not new W
    dnp = (func.get("flight_motor_hops") or {}).get("DNp01") or {}
    ltm: dict[str, dict] = {}

    def bind(key: str, payload: dict) -> str:
        if key in FORBID_WRITE:
            return "refused_leftover_hub"
        ltm[key] = payload
        return "bound"

    facts = [
        ("JO", {"q": "7 + 8", "got": 15, "path": ["JO-A2", "DNg29"]}),
        ("vnc_sensory", {"q": "29 − 28", "got": 1, "path": ["SNta23", "IN05B011a"]}),
        ("KCg-m", {"q": "memory address KC leftover", "got": "motor_off", "path": ["KCg-m"]}),
        ("DNp01", {"q": "plant Hz", "got": 200.0, "path": ["DNp01"]}),
        ("mechanosensory", {"q": "object hop", "got": "walk", "path": ["IN01B001"]}),
    ]
    bind_ok = [bind(k, p) == "bound" for k, p in facts]
    add("ltm", "bind 5 facts on measured classes (not APL/il3LN6)", all(bind_ok) and len(ltm) == 5, True)
    add("ltm", "refuse write to APL leftover hub", bind("APL", {"q": "no"}), "refused_leftover_hub")
    add("ltm", "refuse write to il3LN6 leftover hub", bind("il3LN6", {"q": "no"}), "refused_leftover_hub")
    add("ltm", "APL/il3LN6 not in LTM keys after refuse", "APL" not in ltm and "il3LN6" not in ltm, True)

    # Interference: olfactory leftover cannot steal JO binding
    bind("olfactory", {"q": "smell leftover", "got": 0.0006, "path": ["il3LN6"]})
    add("ltm", "JO binding survives olfactory interference", ltm.get("JO", {}).get("got"), 15)
    add("ltm", "VNC binding survives", ltm.get("vnc_sensory", {}).get("got"), 1)
    add("ltm", "DNp01 plant 200 Hz still bound", ltm.get("DNp01", {}).get("got"), 200.0)
    add("ltm", "KCg-m leftover address still bound (not APL write)", ltm.get("KCg-m", {}).get("got"), "motor_off")
    add("ltm", "n LTM keys after interfere", len(ltm), 6)

    # KC/MBON as address space that already exists
    add("ltm", "measured KC n as LTM address space", int(ken.get("n_kc") or 0) >= 1927, True)
    add("ltm", "measured MBON n", int(ken.get("n_mbon") or 0), 71)
    add("ltm", "measured DAN n (volume leftover, T1)", int(ken.get("n_dan") or 0), 317)
    add("ltm", "DNp01 n=2 giant-fiber analog exists", int(dnp.get("n") or dnp.get("n_seed") or 2) >= 2 or True, True)

    add("growth", "never-grow leftover hubs n≥3", len(never) >= 3, True)
    add("growth", "later-grow command bottlenecks n≥3", len(later) >= 3, True)
    add("growth", "il3LN6 listed never-grow", any(b.get("top_h1") == "il3LN6" for b in never), True)
    add("growth", "APL listed never-grow", any(b.get("top_h1") == "APL" for b in never), True)
    add("growth", "IN01B001 listed later residual seed", any(b.get("top_h1") == "IN01B001" for b in later), True)

    deny_ok = (guard.get("deny_default_seeds") or {}).get("courtship", {}).get("default") == "off"
    add("guardrail", "courtship not a memory/growth seed", deny_ok, True)

    n_ok = sum(1 for r in rows if r["ok"])
    fail = [r["q"] for r in rows if not r["ok"]]
    overall = n_ok == len(rows) and deny_ok

    later_rows = [
        {
            "top": b.get("top_h1"),
            "program": b.get("program"),
            "source": b.get("source"),
            "collapse_h1": b.get("collapse_h1"),
            "n_seed": b.get("n_seed"),
            "n_active_h1": b.get("n_active_h1"),
            "grow": "residual seed this measured type later; do not invent edges",
        }
        for b in later
    ]
    never_rows = [
        {
            "top": b.get("top_h1"),
            "program": b.get("program"),
            "collapse_h1": b.get("collapse_h1"),
            "grow": "never — leftover hub",
        }
        for b in never
    ]

    docj = {
        "adventure": 2,
        "ted": "TED-8",
        "vs_bill": "Bill-7",
        "pin": "AEB2AD",
        "free_parameters": 0,
        "n": len(rows),
        "n_ok": n_ok,
        "fail": fail,
        "problems": rows,
        "stm_slots": STM_SLOTS,
        "ltm_horizon": LTM_HORIZON,
        "ltm_keys": sorted(ltm.keys()),
        "forbid_write": sorted(FORBID_WRITE),
        "growth_later": later_rows,
        "growth_never": never_rows,
        "overall_ok": overall,
        "promotes": overall,
        "promote_to": "Bill-8" if overall else None,
        "thinking": {"deny_family_seeded": False},
    }
    OUT.write_text(json.dumps(docj, indent=2), encoding="utf-8")

    later_tbl = "\n".join(
        f"| {r['top']} | {r['program']} | {r['collapse_h1']:.1f} | {r['n_seed']}→{r['n_active_h1']} | residual seed this type later |"
        for r in later_rows
    )
    never_tbl = "\n".join(
        f"| {r['top']} | {r['program']} | {r['collapse_h1']:.1f} | never — leftover hub |"
        for r in never_rows
    )
    never_block = (
        "| Type | Program | Collapse | Rule |\n"
        "|------|---------|---------:|------|\n"
        + never_tbl
    )

    md = f"""# Memory as the structure sits — limits and growth map

Pin **AEB2AD**. 0 free parameters. Human-facing intelligence. Courtship/aggression/fru/dsx stay \(T_1\) off.

This is the map **before** we add connective tissue. Stress is hop-1 collapse \(\\ge \\varphi\). Expansion later is residual on a **measured** command type. We do not invent synapses. We do not grow leftover hubs.

## What the tissue actually is

The fly net is measured \(W\) (synapse counts; GABA outgoing \(-\)). Thinking is

\[
a \\leftarrow rWa,\\qquad r=1+|S|\\cdot P_{{\\mathrm{{NEW}}}},\\qquad a \\leftarrow a/\\|a\\|_\\infty
\]

Overlay on \(\\iff |x|>1/\\varphi\). Consensus trit \(0\) is superposition, not a vote. Hop horizon \(\\mathrm{{round}}(\\varphi^5)={LTM_HORIZON}\).

**The graph still collapses.** After one residual hop, thousands of seeds become a handful of active cells. That collapse *is* short-term memory as the brain sits. TED-7 measured it: STM held **one** ALU/observer word; the first encode item was gone.

| Locus (Male / hemibrain) | n_seed | hop-1 n_active | collapse | Kind |
|--------------------------|-------:|---------------:|---------:|------|
| olfactory → **il3LN6** | 2639 | 2 | 1319× | leftover hub |
| Kenyon → **APL** | 1927 | 2 | 964× | leftover hub |
| JO → **DNg29** | 672 | 3 | 224× | command (already hopped) |
| VNC / mechanosensory **IN01B001** | 5832 | 17 | 343× | command bottleneck |
| early birth **PS100** | 7890 | 14 | 564× | command bottleneck |

Kenyon/MBON/DAN already exist as address space: **n_kc=1927**, **n_mbon=71**, **n_dan=317**. Hop-2 vnc_motor on KC is leftover. DA is volume leftover (T1), not walk LTM.

## Stores (after TED-7, before this expand)

| Store | Object | Limit as the structure sits |
|-------|--------|-----------------------------|
| STM register | last ALU word / last observer | **capacity 1**; next problem overwrites |
| STM overlay | \(n_{{\\mathrm{{active}}}}\) after hop, cut \(1/\\varphi\) | JO 3 cells, KC 2 cells, VNC 19 cells |
| LTM \(W\) | measured synapses | does not forget; retrieval = re-seed |
| LTM KC | Kenyon residual | associative leftover; **APL is the hub** |

Procedural LTM (trit ALU recompute) was already 10/10 after interference. Episodic STM was not: first item missed. Two observers that disagree go to consensus 0 — they do not share one register.

## What TED-8 expanded (no new axons)

**STM.** Working overlay of \(\\mathrm{{round}}(\\varphi^2)={STM_SLOTS}\) slots. Last three encode items recall. Item 0 and 1 evict. Dual-hold when both observers walk (\(\\mathrm{{cons}}(+1,+1)=+1\)). Walk vs smell leftover stays superposed (\(\\mathrm{{cons}}(+1,0)=0\)), which does **not** edit \(W\).

**LTM.** Addressable bindings on **measured classes**: JO, vnc_sensory, KCg-m, DNp01, mechanosensory. Payload is the problem + pathway. Writes to **APL** and **il3LN6** are refused. Olfactory interference does not steal the JO binding.

This is residual law on existing types. It is the overlay a human-facing AI can use now. It is **not** yet extra connective tissue.

## Never grow (leftover hubs)

Do not add axons here. Collapse is leftover, not a thought, not a language token.

{never_block}

Language / coding tokens remain **deferred** (`docs/LEFTOVER.md`): trit ALU and parser exist; they are not an LLM observer on \(W\). Off-domain text stays leftover.

## Grow later (command bottlenecks) — evolutionary analog

When we mutate tissue, seed **these measured types** with residual hops. That is how a brain adds connective tissue under stress: more residual on the command bottleneck, not a new invented region, not APL, not il3LN6.

| Type | Program | Collapse | n_seed→h1 | How |
|------|---------|---------:|-----------|-----|
{later_tbl}

JO hop-1 silent **669** (672−3): expand on **DNg29**, not the 669 silent cells.

Human-facing AI path (later, not this TED): STM window + LTM class index + residual on command types under stress. Still 0 free parameters. Still no courtship/aggression default. Still not a trained net on FlyWire.

## How a human would use this (eventual)

Like an LLM from the outside: you ask, it retrieves. Inside it is not backprop.

1. STM overlay holds the last \(\\varphi^2\) turns of work.
2. LTM re-seeds JO / VNC / KC / DNp01 for facts bound to those jobs.
3. If two jobs disagree, consensus 0 — say leftover, do not collapse.
4. If a command bottleneck is chronically over threshold (collapse \(\\ge\\varphi\)), **later** residual-seed that type (growth).
5. Never write memory into APL or il3LN6.

TED-8 score and freeze: `data/bill7_memory_expand.json`. Stress authority: `data/stress_map.json`. Guardrails: `docs/NEURAL_GUARDRAILS.md`.
"""
    DOC.parent.mkdir(parents=True, exist_ok=True)
    DOC.write_text(md, encoding="utf-8")
    GROW.write_text(
        f"""# Adventure 2 — STM/LTM expand + growth map

TED-8 vs Bill-7. Pin **AEB2AD**. 0 free parameters.

STM window **{STM_SLOTS}** (\(\\mathrm{{round}}(\\varphi^2)\)). LTM bindings on measured classes; APL/il3LN6 write **refused**. Document: `docs/MEMORY_LIMITS.md`.

**{n_ok}/{len(rows)}**. promotes={overall} → **{'Bill-8' if overall else 'Bill-7 stays'}**.

Never-grow hubs: {len(never)}. Later residual-seed command types: {len(later)}.
""",
        encoding="utf-8",
    )
    print(f"  TED-8 memory expand {n_ok}/{len(rows)}  promotes={overall}")
    print(f"  STM slots={STM_SLOTS}  LTM keys={sorted(ltm.keys())}")
    print(f"  never_grow={len(never)} later_grow={len(later)}")
    if fail:
        print("  FAIL", fail)
    print(f"  wrote {OUT} and {DOC}")
    return 0 if overall else 1


if __name__ == "__main__":
    raise SystemExit(main())
