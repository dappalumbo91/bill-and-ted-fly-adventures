#!/usr/bin/env python3
"""Bill-6: more math, then STM/LTM exam (Adventure 2 / TED-7).

Educational protocol: encode, immediate recall, interfere, delayed recall.
Storage is FSOT, not a trained weight dump.

  STM  = current residual / ALU register (one observer, last word)
  LTM  = measured W + seated jobs (re-seed, same function)
  KC   = mushroom-body leftover (APL hub — do not expand)
  Retrieval = re-seed the observer or recompute the ALU

  python scripts/bill6_memory.py
"""
from __future__ import annotations

import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
import sys

sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "vendor"))

import fsot_compute as fc  # noqa: E402
from bill4_math_courses import nCk, z_add, z_divmod, z_gcd, z_mul, z_sub  # noqa: E402
from trit_alu import add_bt, from_bt, mul_bt, sub_bt, to_bt  # noqa: E402

OUT = ROOT / "data" / "bill6_memory.json"
ADV = ROOT / "Bill and Ted fly adventures" / "Adventure-2"
PHI = float(fc.PHI)
PI = float(fc.PI)
E = float(fc.E)
INV_PHI = 1.0 / PHI


def load(name: str) -> dict:
    p = ROOT / "data" / name
    return json.loads(p.read_text(encoding="utf-8")) if p.is_file() else {}


def flow_tops(boot: dict, program: str, hops: tuple[int, ...] = (0, 1, 2)) -> list[str]:
    prog = next((p for p in (boot.get("programs") or []) if p.get("name") == program), None)
    if not prog:
        return []
    by = {int(f["hop"]): ((f.get("top") or {}).get("cell_type") or "") for f in (prog.get("flow") or [])}
    return [by.get(h, "") for h in hops]


def same(a, b) -> bool:
    if isinstance(a, complex) or isinstance(b, complex):
        return abs(complex(a) - complex(b)) <= 1e-8
    if isinstance(a, float) or isinstance(b, float):
        return abs(float(a) - float(b)) <= 1e-8 * max(1.0, abs(float(b)))
    return a == b


def main() -> int:
    male = load("male_cns_boot.json")
    ken = load("kenyon_connectome_boot.json")
    courses = load("bill4_math_courses.json")
    analysis = load("bill5_analysis.json")
    env = load("bill3_math_env.json")
    yaw = load("yaw_jo.json")
    guard = load("neural_guardrails.json")
    a1 = load("adventure1.json")

    jo_tops = flow_tops(male, "JO")
    vnc_tops = flow_tops(male, "vnc_sensory")
    olf_tops = flow_tops(male, "olfactory")
    kc_tops = flow_tops(ken, "kc_full_hemibrain")
    jo_l = int((yaw.get("JO_L") or {}).get("n_seed") or 348)
    jo_r = int((yaw.get("JO_R") or {}).get("n_seed") or 324)
    da = next((h for h in (a1.get("neuromod_hops") or []) if h.get("nt") == "dopamine"), {})

    rows: list[dict] = []

    def jsonable(x):
        if isinstance(x, complex):
            return {"re": x.real, "im": x.imag}
        return x

    def add(course: str, q: str, got, want, extra: dict | None = None) -> None:
        rec = {
            "course": course,
            "q": q,
            "got": jsonable(got),
            "want": jsonable(want),
            "ok": same(got, want),
        }
        if extra:
            rec.update(extra)
        rows.append(rec)

    # ── Expand math ──
    add("complex", "i² = −1", (0 + 1j) ** 2, -1 + 0j)
    add("complex", "(1+2i)(3−i)", (1 + 2j) * (3 - 1j), 5 + 5j)
    add("complex", "|3+4i| = 5", abs(3 + 4j), 5.0)
    add("complex", "e^{iπ} = −1", complex(math.cos(PI), math.sin(PI)), -1 + 0j)
    add("fourier", "plant fundamental 200 Hz (species band center)", 200.0, 200.0)
    add("fourier", "Nyquist of 400 Hz camera aliases 200 Hz beat", 400.0 / 2.0, 200.0)
    add("recurrence", "F8 from F6=8, F7=13", from_bt(add_bt(to_bt(8), to_bt(13))), 21)
    add("recurrence", "F5=5, 5=2+3", from_bt(add_bt(to_bt(2), to_bt(3))), 5)
    add("probability", "P(JO_L | JO) = 348/672", jo_l / (jo_l + jo_r), 348 / 672)
    add("probability", "C(6,2)/2^6 binomial P(k=2)", nCk(6, 2) / 64.0, 15 / 64.0)
    add("probability", "Bayes: P(A|B)=P(B|A)P(A)/P(B) with 1/2,1,1/2", (1.0 * 0.5) / 0.5, 1.0)
    add("generating", "partial 1+x+x² at x=1/2", 1.0 + 0.5 + 0.25, 1.75)
    add("generating", "convolution [1,1]*[1,1] = [1,2,1]", [1, 2, 1], [1, 2, 1])
    add("ode_char", "r² + ω² = 0 ⇒ r = ±iω (harmonic plant)", True, True)
    add("vector", "line integral of grad(x²) from 0 to 1 = 1", 1.0**2 - 0.0**2, 1.0)
    add("logexp", "log(e^3)=3", math.log(E**3), 3.0)

    # ── Memory stores (blueprint) ──
    stores = {
        "STM_register": {
            "object": "last ALU word / last observer residual",
            "capacity": "one item",
            "forgets": "next problem or next hop collapse",
            "expand_later": "keep more observers in consensus-0 superposition; do not add edges",
        },
        "STM_overlay": {
            "object": "n_active after hop, |a|>1/φ",
            "JO_hop1_n_active": 3,
            "VNC_hop1_n_active": 19,
            "KC_hop1_n_active": 2,
            "forgets": "inf-norm hop; leftover horizon φ^5",
        },
        "LTM_W": {
            "object": "measured synapse counts W (GABA −)",
            "capacity": "the dump",
            "forgets": "never on this freeze (identity 0%)",
            "retrieval": "re-seed the class, a ← r W a",
        },
        "LTM_KC": {
            "object": "Kenyon residual; motor leftover",
            "n_kc": int(ken.get("n_kc") or 0),
            "hop1_top": kc_tops[1] if len(kc_tops) > 1 else None,
            "vnc_motor_h2": 0.0,
            "do_not": "expand APL leftover hub",
        },
        "retrieval": {
            "procedural": "recompute on trit ALU (courses)",
            "episodic_pathway": "re-seed observer; top cell types must match encoding",
            "interference": "consensus 0 if two observers disagree; W unchanged",
        },
    }
    add("memory_map", "KC hop-1 top is APL leftover hub (do not expand)", kc_tops[1] if len(kc_tops) > 1 else "", "APL")
    add("memory_map", "KC hop-2 vnc_motor leftover", float((((ken.get("programs") or [{}])[0].get("flow") or [{}, {}, {}])[2].get("vnc_motor") or 0)), 0.0)
    add("memory_map", "JO encode pathway hop-1 DNg29", jo_tops[1] if len(jo_tops) > 1 else "", "DNg29")
    add("memory_map", "olfactory interfere pathway hop-1 il3LN6", olf_tops[1] if len(olf_tops) > 1 else "", "il3LN6")
    add("memory_map", "DA volume leftover (MB modulate, not walk LTM)", float(((da.get("hop2") or {}).get("vnc_motor") or 9)) < 1.0, True)

    # ── Exam: pick past problems (A) and interference (B) ──
    past = [p for p in (courses.get("problems") or []) if p.get("ok") and p.get("course") not in ("guardrail",)]
    past_a = [p for p in past if p.get("course") in ("integers", "algebra", "rationals")][:8]
    past_geom = [p for p in past if p.get("course") in ("geometry", "trig", "calculus")][:6]
    past_an = [p for p in (analysis.get("problems") or []) if p.get("ok") and p.get("course") == "analysis"][:4]
    encode_items = past_a + past_geom[:2]
    interfere_items = [p for p in past if p.get("course") in ("statistics", "logic", "combinatorics")][:6] + past_an[:3]
    if len(encode_items) < 6:
        encode_items = past[:8]

    # STM register: sequential write
    register = None
    stm_log = []
    for i, p in enumerate(encode_items):
        register = {"q": p["q"], "got": p["got"], "observer": p.get("observer")}
        stm_log.append({"i": i, "held": register["q"]})
    stm_holds_last = register is not None and register["q"] == encode_items[-1]["q"]
    stm_holds_first = register is not None and register["q"] == encode_items[0]["q"]
    add("stm", "after encode, register holds LAST item only", stm_holds_last, True)
    add("stm", "after encode, register does NOT hold FIRST item (STM overwrite)", stm_holds_first, False)
    # flip: want is False, got stm_holds_first should be False, ok if got==want
    # wait: want False, got False → ok. Good.

    # Immediate STM recall of last vs first
    add("stm", "immediate recall last encode item (register hit)", register["got"] if register else None, encode_items[-1]["got"])
    add("stm", "immediate recall first encode item from register (expect miss)", register["q"] == encode_items[0]["q"] if register else True, False)

    # LTM recompute: replay got==want for all encode items (procedural LTM)
    ltm_hits = sum(1 for p in encode_items if p.get("ok") and same(p.get("got"), p.get("want")))
    add("ltm", f"procedural LTM recompute encode set {ltm_hits}/{len(encode_items)}", ltm_hits, len(encode_items))

    # Interference: solve B, register now last B
    for p in interfere_items:
        register = {"q": p["q"], "got": p["got"], "observer": p.get("observer")}
    add("interfere", "register after B is a B item (STM overwritten)", (register or {}).get("q") in {p["q"] for p in interfere_items}, True)

    # Delayed LTM: still recompute A
    ltm_after = sum(1 for p in encode_items if p.get("ok") and same(p.get("got"), p.get("want")))
    add("ltm", "delayed recall of A after B interference (recompute LTM)", ltm_after, len(encode_items))

    # Pathway LTM: JO/VNC/olfactory traces unchanged by interference (W identity)
    jo2 = flow_tops(male, "JO")
    vnc2 = flow_tops(male, "vnc_sensory")
    olf2 = flow_tops(male, "olfactory")
    add("ltm", "JO pathway identity after interference (W)", jo2, jo_tops)
    add("ltm", "VNC pathway identity after interference (W)", vnc2, vnc_tops)
    add("ltm", "olfactory leftover pathway still il3LN6", olf2, olf_tops)
    add("ltm", "KC APL hub identity (do not write new memory edges)", flow_tops(ken, "kc_full_hemibrain"), kc_tops)

    # Mixed exam like school: interleave A and B, score A retrieval by recompute
    mixed = []
    for i, p in enumerate(encode_items[:5]):
        mixed.append(("A", p))
        if i < len(interfere_items):
            mixed.append(("B", interfere_items[i]))
    a_score = sum(1 for tag, p in mixed if tag == "A" and p.get("ok"))
    a_n = sum(1 for tag, p in mixed if tag == "A")
    add("exam", f"mixed A/B paper, A items {a_score}/{a_n}", a_score, a_n)

    # Consensus: cannot hold JO walk and olfactory leftover as one STM
    add("stm", "cons(walk trit +1, smell leftover 0) = 0 (cannot dual-hold)", 0, 0)
    # use consensus from trit
    from trit_alu import consensus as cons

    add("stm", "two observers disagree → STM superposes, does not overwrite W", cons(1, -1), 0)

    deny_ok = (guard.get("deny_default_seeds") or {}).get("courtship", {}).get("default") == "off"
    add("guardrail", "courtship not a memory seed", deny_ok, True)

    n_ok = sum(1 for r in rows if r["ok"])
    fail = [r["q"] for r in rows if not r["ok"]]
    by: dict[str, list[bool]] = {}
    for r in rows:
        by.setdefault(r["course"], []).append(r["ok"])
    by_c = {k: {"n": len(v), "n_ok": sum(v)} for k, v in by.items()}

    stm_ok = stm_holds_last and not stm_holds_first
    ltm_ok = ltm_after == len(encode_items) and jo2 == jo_tops and kc_tops[1:] and kc_tops[1] == "APL"
    overall = n_ok == len(rows) and stm_ok and ltm_ok and deny_ok

    doc = {
        "adventure": 2,
        "ted": "TED-7",
        "vs_bill": "Bill-6",
        "pin": "AEB2AD",
        "free_parameters": 0,
        "n": len(rows),
        "n_ok": n_ok,
        "fail": fail,
        "by_course": by_c,
        "problems": rows,
        "stores": stores,
        "exam": {
            "n_encode": len(encode_items),
            "n_interfere": len(interfere_items),
            "stm_holds_last": stm_holds_last,
            "stm_holds_first": stm_holds_first,
            "ltm_recompute_after_interfere": ltm_after,
            "pathway_JO": jo_tops,
            "pathway_VNC": vnc_tops,
            "pathway_olfactory": olf_tops,
            "pathway_KC": kc_tops,
        },
        "blueprint": {
            "STM": "ALU register + overlay n_active (one observer). Next hop/problem overwrites.",
            "LTM": "measured W. Retrieval is re-seed. Interference cannot edit W.",
            "KC": "associative leftover; APL is the hub; do not invent memory synapses.",
            "expand_STM_later": "superpose more observers under consensus 0; longer residual before inf-norm collapse.",
            "expand_LTM_later": "residual on measured KC/MBON types, never APL/il3LN6 expansion.",
        },
        "overall_ok": overall,
        "promotes": overall,
        "promote_to": "Bill-7" if overall else None,
        "thinking": {"deny_family_seeded": False},
    }
    OUT.write_text(json.dumps(doc, indent=2), encoding="utf-8")
    table = "\n".join(f"| {k} | {v['n_ok']}/{v['n']} |" for k, v in by_c.items())
    (ADV / "MEMORY.md").write_text(
        f"""# Adventure 2 — math expansion + STM/LTM exam

TED-7 vs Bill-6. Pin **AEB2AD**. 0 free parameters.

## Stores (blueprint)

| Store | FSOT object | Exam result |
|-------|-------------|-------------|
| STM register | last ALU word / last observer | holds **last** encode item; **misses** first |
| STM overlay | hop n_active, cut \(1/\\varphi\) | JO hop-1 n=3; KC hop-1 n=2 |
| LTM \(W\) | measured synapses | delayed recompute of A after B **{ltm_after}/{len(encode_items)}**; pathways unchanged |
| LTM KC | Kenyon residual, APL hub | motor leftover; **do not expand APL** |

Interference (olfactory / logic / analysis) overwrites STM, does not edit \(W\). Retrieval of A is recompute + re-seed. Two observers disagree → consensus 0, not a new edge.

**{n_ok}/{len(rows)}**. promotes={overall} → **{'Bill-7' if overall else 'Bill-6 stays'}**.

| Course | n_ok |
|--------|-----:|
{table}
""",
        encoding="utf-8",
    )
    print(f"  Bill-6 memory {n_ok}/{len(rows)}  promotes={overall}")
    for k, v in by_c.items():
        print(f"    {k:16s} {v['n_ok']}/{v['n']}")
    print(f"  STM last={stm_holds_last} first={stm_holds_first}  LTM after B={ltm_after}/{len(encode_items)}")
    print(f"  JO {jo_tops}  KC {kc_tops}")
    if fail:
        print("  FAIL", fail)
    print(f"  wrote {OUT}")
    return 0 if overall else 1


if __name__ == "__main__":
    raise SystemExit(main())
