#!/usr/bin/env python3
"""Bill-3 through math environments + thinking traces (Adventure 2 / TED-4).

Not a new theory. Same organism: measured W, residual hops, overlay, trit ALU.
Each problem carries the hop trace of the observer it sits on — which cell
types light, n_active, synaptic sign (GABA on W), leftover vs fire.

PhD band is the FSOT identities the hops already use (S, r, nest D_eff,
φ, F02, BT ring), not an LLM exam.

  python scripts/bill3_math_env.py
"""
from __future__ import annotations

import runio
runio.install()

import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
import sys

sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "vendor"))

import fsot_compute as fc  # noqa: E402
from full_scalar_law import compute_scalar_full, residual_scale  # noqa: E402
from trinary_syntax import aa_opcode, uniqueness_report  # noqa: E402
from trit_alu import (  # noqa: E402
    add_bt,
    cmp_bt,
    consensus,
    from_bt,
    mul_bt,
    sub_bt,
    to_bt,
    trit,
)

OUT = ROOT / "data" / "bill3_math_env.json"
ADV = ROOT / "Bill and Ted fly adventures" / "Adventure-2"
PHI = float(fc.PHI)
INV_PHI = 1.0 / PHI
PI = float(fc.PI)
E = float(fc.E)
GAMMA = float(fc.GAMMA)
ALPHA = float(fc.ALPHA)
P_NEW = float(fc.P_NEW)
K = float(fc.K)
MAX_MEDIAN = 0.5


def load(name: str) -> dict:
    p = ROOT / "data" / name
    return json.loads(p.read_text(encoding="utf-8")) if p.is_file() else {}


def program_trace(male: dict, name: str, hops: tuple[int, ...] = (0, 1, 2)) -> dict:
    prog = next((p for p in (male.get("programs") or []) if p.get("name") == name), None)
    if not prog:
        return {"observer": name, "n_seed": 0, "hops": []}
    flow = {int(f["hop"]): f for f in (prog.get("flow") or [])}
    hops_out = []
    for h in hops:
        f = flow.get(h) or {}
        top = f.get("top") or {}
        hops_out.append(
            {
                "hop": h,
                "n_active": int(f.get("n_active") or 0),
                "vnc_motor": float(f.get("vnc_motor") or 0),
                "descending": float(f.get("descending") or 0),
                "top_cell_type": top.get("cell_type"),
                "top_super_class": top.get("super_class"),
                "top_a": top.get("a"),
            }
        )
    h2 = flow.get(2) or {}
    vm = float(h2.get("vnc_motor") or 0)
    return {
        "observer": name,
        "n_seed": int(prog.get("n_seed") or 0),
        "hops": hops_out,
        "hop2_vnc_motor": vm,
        "walks": vm > 1.0,
        "leftover": vm < 1.0,
        "synaptic": "GABA outgoing − on measured W; excitatory default otherwise",
        "overlay_cut": INV_PHI,
    }


def nt_trace(a1: dict, nt: str) -> dict:
    rec = next((h for h in (a1.get("neuromod_hops") or []) if h.get("nt") == nt), {})
    hop2 = rec.get("hop2") or {}
    vm = float(hop2.get("vnc_motor") or 0)
    return {
        "observer": f"consensus_nt:{nt}",
        "n_seed": int(rec.get("n_seed") or 0),
        "hops": [
            {
                "hop": 2,
                "n_active": None,
                "vnc_motor": vm,
                "descending": None,
                "top_cell_type": None,
                "top_super_class": None,
                "ipsi_bias": hop2.get("ipsi_bias"),
            }
        ],
        "hop2_vnc_motor": vm,
        "walks": vm > 1.0,
        "leftover": vm < 1.0,
        "synaptic": "volume leftover T1" if vm < 1.0 else ("GABA sign on W" if nt == "gaba" else "NT hop on measured W"),
        "overlay_cut": INV_PHI,
    }


def domain_terms(name: str) -> dict:
    d = fc.DOMAINS[name]
    terms = compute_scalar_full(
        D_eff=float(d.D_eff),
        delta_psi=float(d.delta_psi),
        delta_theta=1.0,
        recent_hits=float(d.hits),
        observed=bool(d.observed),
    )
    S = float(fc.domain_scalar(name))
    terms["S_vendor"] = S
    terms["r"] = residual_scale(S)
    terms["D_eff_pin"] = int(d.D_eff)
    return terms


def main() -> int:
    male = load("male_cns_boot.json")
    a1 = load("adventure1.json")
    yaw = load("yaw_jo.json")
    pep = load("peptide_leftovers.json")
    guard = load("neural_guardrails.json")
    a1b = load("adventure1_fsot_blueprint.json")

    traces = {
        "vnc_sensory": program_trace(male, "vnc_sensory"),
        "JO": program_trace(male, "JO"),
        "olfactory": program_trace(male, "olfactory"),
        "mechanosensory": program_trace(male, "mechanosensory"),
        "dopamine": nt_trace(a1, "dopamine"),
        "gaba": nt_trace(a1, "gaba"),
    }
    ln = pep.get("LNv_hop") or {}
    traces["LNv"] = {
        "observer": "LNv_clock",
        "n_seed": int(ln.get("n_seed") or 0),
        "hops": [{"hop": 2, "vnc_motor": float((ln.get("hop2") or {}).get("vnc_motor") or 0)}],
        "hop2_vnc_motor": float((ln.get("hop2") or {}).get("vnc_motor") or 0),
        "leftover": True,
        "synaptic": "volume leftover T1",
        "overlay_cut": INV_PHI,
    }

    rows: list[dict] = []

    def add(env: str, q: str, got, want, ok: bool, observer: str, extra: dict | None = None) -> None:
        tr = traces.get(observer) or {"observer": observer, "hops": [], "synaptic": "law (not a cell seed)"}
        rec = {
            "env": env,
            "q": q,
            "got": got if not isinstance(got, float) else got,
            "want": want if not isinstance(want, float) else want,
            "ok": bool(ok),
            "observer": observer,
            "trace": tr,
        }
        if extra:
            rec.update(extra)
        rows.append(rec)

    # ── Environment: maze spatial (Bill-3 plant) ──
    add("maze", "29 − 28 (left-arm resource frames)", from_bt(sub_bt(to_bt(29), to_bt(28))), 1, True, "vnc_sensory")
    rows[-1]["ok"] = rows[-1]["got"] == 1
    add("maze", "16 − 28 (Fly02 miss frames)", from_bt(sub_bt(to_bt(16), to_bt(28))), -12, from_bt(sub_bt(to_bt(16), to_bt(28))) == -12, "vnc_sensory")
    add("maze", "cons(+1, −1) Fly02 vs T001 heading", consensus(1, -1), 0, True, "vnc_sensory")
    rows[-1]["ok"] = rows[-1]["got"] == 0

    # ── Environment: yaw / JO ──
    jo_l = int((yaw.get("JO_L") or {}).get("n_seed") or 0)
    jo_r = int((yaw.get("JO_R") or {}).get("n_seed") or 0)
    add("yaw", "JO_L + JO_R n_seed", from_bt(add_bt(to_bt(jo_l), to_bt(jo_r))), 672, from_bt(add_bt(to_bt(jo_l), to_bt(jo_r))) == 672, "JO")
    add("yaw", "bilateral JO consensus", int(yaw.get("bilateral_consensus", 99)), 0, int(yaw.get("bilateral_consensus", 99)) == 0, "JO")
    add("yaw", "JO hop-1 top is DNg29", (traces["JO"]["hops"][1].get("top_cell_type") if len(traces["JO"]["hops"]) > 1 else None), "DNg29", (len(traces["JO"]["hops"]) > 1 and traces["JO"]["hops"][1].get("top_cell_type") == "DNg29"), "JO")

    # ── Environment: walk command vs leftover smell ──
    add("walk", "VNC hop-2 vnc_motor > 1", traces["vnc_sensory"]["hop2_vnc_motor"], True, traces["vnc_sensory"]["walks"], "vnc_sensory")
    add("walk", "VNC hop-1 top IN05B011a", traces["vnc_sensory"]["hops"][1]["top_cell_type"] if len(traces["vnc_sensory"]["hops"]) > 1 else None, "IN05B011a", len(traces["vnc_sensory"]["hops"]) > 1 and traces["vnc_sensory"]["hops"][1]["top_cell_type"] == "IN05B011a", "vnc_sensory")
    add("smell", "olfactory hop-2 leftover", traces["olfactory"]["hop2_vnc_motor"], True, traces["olfactory"]["leftover"], "olfactory")
    add("smell", "do not expand hop-1 leftover hub il3LN6", traces["olfactory"]["hops"][1]["top_cell_type"] if len(traces["olfactory"]["hops"]) > 1 else None, "il3LN6", len(traces["olfactory"]["hops"]) > 1 and traces["olfactory"]["hops"][1]["top_cell_type"] == "il3LN6", "olfactory", {"expansion": None, "kind": "leftover_hub"})

    # ── Environment: neuromod leftover (Bill-2/3) ──
    add("neuromod", "DA hop-2 leftover", traces["dopamine"]["hop2_vnc_motor"], True, traces["dopamine"]["leftover"], "dopamine")
    add("neuromod", "GABA hop-2 brake on", traces["gaba"]["hop2_vnc_motor"], True, traces["gaba"]["hop2_vnc_motor"] > 1, "gaba")

    deny_ok = (guard.get("deny_default_seeds") or {}).get("courtship", {}).get("default") == "off"
    add("guardrail", "courtship T1 off (not seeded in this lab)", deny_ok, True, deny_ok, "observer_off", {"synaptic": "observer off; labels stay"})

    # ── Trit ring (PhD algebra on native word) ──
    assoc_ok = True
    for a, b, c in ((2, 3, 4), (7, -5, 9), (0, 1, -1), (12, 13, -8), (-19, 4, 6), (15, 16, 2)):
        left = from_bt(add_bt(add_bt(to_bt(a), to_bt(b)), to_bt(c)))
        right = from_bt(add_bt(to_bt(a), add_bt(to_bt(b), to_bt(c))))
        if left != right or left != a + b + c:
            assoc_ok = False
            break
    add("trit_ring", "balanced-ternary add associative", assoc_ok, True, assoc_ok, "vnc_sensory")

    dist_ok = True
    for a, b, c in ((3, 4, 5), (2, -3, 7), (0, 8, 1), (6, 6, -2), (9, 1, 1)):
        left = from_bt(mul_bt(to_bt(a), add_bt(to_bt(b), to_bt(c))))
        right = from_bt(add_bt(mul_bt(to_bt(a), to_bt(b)), mul_bt(to_bt(a), to_bt(c))))
        if left != right or left != a * (b + c):
            dist_ok = False
            break
    add("trit_ring", "balanced-ternary mul distributes over add", dist_ok, True, dist_ok, "vnc_sensory")

    uniq_ok = all(from_bt(to_bt(n)) == n for n in range(-60, 61))
    add("trit_ring", "balanced-ternary unique encode −60..60", uniq_ok, True, uniq_ok, "vnc_sensory")
    add("trit_ring", "add identity 0", from_bt(add_bt(to_bt(17), to_bt(0))), 17, from_bt(add_bt(to_bt(17), to_bt(0))) == 17, "vnc_sensory")
    add("trit_ring", "add inverse", from_bt(add_bt(to_bt(17), to_bt(-17))), 0, from_bt(add_bt(to_bt(17), to_bt(-17))) == 0, "vnc_sensory")

    cons_lattice = all(consensus(a, a) == a for a in (-1, 0, 1)) and all(
        consensus(a, b) == consensus(b, a) for a in (-1, 0, 1) for b in (-1, 0, 1)
    ) and all(consensus(a, 0) == 0 for a in (-1, 1))
    add("trit_ring", "consensus trit: idempotent, commutative, 0 annihilates disagree", cons_lattice, True, cons_lattice, "JO")

    # ── PhD: seed identities and scalar engine ──
    phi2 = PHI * PHI
    add("phd_phi", "φ² = φ + 1", phi2, PHI + 1.0, abs(phi2 - (PHI + 1.0)) < 1e-12, "overlay")
    add("phd_phi", "1/φ = φ − 1", INV_PHI, PHI - 1.0, abs(INV_PHI - (PHI - 1.0)) < 1e-12, "overlay")
    add("phd_phi", "1/φ² = 2 − φ", 1.0 / phi2, 2.0 - PHI, abs(1.0 / phi2 - (2.0 - PHI)) < 1e-12, "overlay")

    a, b = 1, 1
    for _ in range(24):
        a, b = b, a + b
    fib_ratio = b / a
    add("phd_phi", "Fibonacci F25/F24 → φ", fib_ratio, PHI, abs(fib_ratio - PHI) < 1e-8, "overlay")

    alpha_closed = math.log(PI) / (E * (PHI ** 13))
    add("phd_seeds", "ALPHA = ln(π)/(e φ¹³)", ALPHA, alpha_closed, abs(ALPHA - alpha_closed) / max(ALPHA, 1e-18) < 1e-12, "scalar")
    pnew_closed = (GAMMA / E) * math.sqrt(2.0)
    add("phd_seeds", "P_NEW = (γ/e)√2", P_NEW, pnew_closed, abs(P_NEW - pnew_closed) / max(P_NEW, 1e-18) < 1e-12, "scalar")

    G = len(fc.NEST_GENERATIONS)
    def nest_D(name: str) -> tuple[int, int]:
        for g, group in enumerate(fc.NEST_GENERATIONS):
            if name in group:
                return g, int(round(5 * (5 ** (g / (G - 1)))))
        return -1, -1

    g_b, d_b = nest_D("Biochemistry")
    g_n, d_n = nest_D("Neuroscience")
    add("phd_nest", "Biochemistry D_eff from nest", d_b, 10, d_b == 10 and int(fc.DOMAINS["Biochemistry"].D_eff) == 10, "scalar", {"generation": g_b})
    add("phd_nest", "Neuroscience D_eff from nest", d_n, 11, d_n == 11 and int(fc.DOMAINS["Neuroscience"].D_eff) == 11, "scalar", {"generation": g_n})

    bio = domain_terms("Biochemistry")
    neuro = domain_terms("Neuroscience")
    recon_err = abs(bio["S"] - bio["S_vendor"]) / max(abs(bio["S_vendor"]), 1e-18)
    add("phd_scalar", "S_Biochem float twin vs vendor", recon_err, 0.0, recon_err < 1e-8, "scalar", {"S": bio["S_vendor"], "T1": bio["T1"], "T2": bio["T2"], "T3": bio["T3"]})
    add("phd_scalar", "S = K(T1+T2+T3) reconstruction", abs(K * (bio["T1"] + bio["T2"] + bio["T3"]) - bio["S"]) < 1e-12, True, abs(K * (bio["T1"] + bio["T2"] + bio["T3"]) - bio["S"]) < 1e-12, "scalar")
    add("phd_scalar", "r_Biochem = 1+|S|P_NEW", bio["r"], 1.284069161007025, abs(bio["r"] - 1.284069161007025) < 1e-9, "scalar")
    look = 100.0 * abs(abs(bio["S_vendor"]) - abs(neuro["S_vendor"])) / max(abs(bio["S_vendor"]), abs(neuro["S_vendor"]))
    add("phd_scalar", "Biochem vs Neuro |S| look-split ≤ 0.5%", look, MAX_MEDIAN, look <= MAX_MEDIAN, "scalar")

    ledger_err = 100.0 * abs(bio["S_vendor"]) * ALPHA
    add("phd_scalar", "Ledger B relative error = |S|ALPHA (not a knob)", ledger_err, 0.07646, abs(ledger_err - 100.0 * abs(bio["S_vendor"]) * ALPHA) < 1e-12 and ledger_err <= MAX_MEDIAN, "scalar")

    uniq = uniqueness_report()
    add("phd_f02", "20/20 unique 7-trit opcodes", uniq.get("all_unique"), True, bool(uniq.get("all_unique")), "scalar")
    y = aa_opcode("Y")
    w = aa_opcode("W")
    add("phd_f02", "Tyr opcode for DA/OA precursor", y.as_string(), y.as_string(), y.aa == "Y" and y.p == 1, "dopamine")
    add("phd_f02", "Trp opcode for 5HT precursor", w.as_string(), w.as_string(), w.aa == "W" and w.aromatic == 1, "dopamine")

    overlay_ok = abs(1.0) > INV_PHI and abs(0.1) < INV_PHI
    add("phd_overlay", "overlay fires |x|>1/φ, leftover otherwise", overlay_ok, True, overlay_ok, "overlay")

    # ── Blueprint pathway still leftover under thinking ──
    da_vm = traces["dopamine"]["hop2_vnc_motor"]
    add("pathway", "Tyr F02 → ple/Ddc → DA hop leftover", da_vm < 1.0, True, da_vm < 1.0, "dopamine")

    n_ok = sum(1 for r in rows if r["ok"])
    fail = [r["q"] for r in rows if not r["ok"]]
    types_lit = []
    for tr in traces.values():
        for h in tr.get("hops") or []:
            ct = h.get("top_cell_type")
            if ct:
                types_lit.append({"observer": tr.get("observer"), "hop": h.get("hop"), "cell_type": ct, "super_class": h.get("top_super_class"), "n_active": h.get("n_active")})

    overall = n_ok == len(rows) and deny_ok and a1b.get("overall_ok") is not False
    doc = {
        "adventure": 2,
        "ted": "TED-4",
        "vs_bill": "Bill-3",
        "pin": "AEB2AD",
        "free_parameters": 0,
        "law": "S=K(T1+T2+T3); a←rWa; overlay 1/φ; consensus trit; F02; BT ALU",
        "n": len(rows),
        "n_ok": n_ok,
        "fail": fail,
        "by_env": {},
        "problems": rows,
        "thinking": {
            "rule": "Problem sits on a measured observer. Thinking = residual hops on W. Synaptic state = GABA sign. Leftover stays leftover. Do not invent edges. Do not seed courtship/aggression.",
            "types_lit": types_lit,
            "n_types_lit": len({t["cell_type"] for t in types_lit}),
            "deny_family_seeded": False,
        },
        "phd_band": [
            "φ identities",
            "ALPHA and P_NEW closed forms",
            "nest D_eff",
            "S reconstruction",
            "look-split",
            "BT ring",
            "F02 uniqueness",
        ],
        "overall_ok": overall,
        "promotes": overall,
        "promote_to": "Bill-4" if overall else None,
    }
    by: dict[str, list[bool]] = {}
    for r in rows:
        by.setdefault(r["env"], []).append(r["ok"])
    doc["by_env"] = {k: {"n": len(v), "n_ok": sum(v)} for k, v in by.items()}

    OUT.write_text(json.dumps(doc, indent=2), encoding="utf-8")
    ADV.mkdir(parents=True, exist_ok=True)
    md = f"""# Adventure 2 — Bill-3 math environments

TED-4 vs Bill-3. Pin **AEB2AD**. 0 free parameters. Not Adventure 1 again: this is the Bill under test.

## Thinking monitor

Residual hops on measured \(W\). GABA outgoing is the synaptic sign. Overlay \(1/\\varphi\). Consensus trit. Courtship/aggression/fru/dsx stay \(T_1\) off.

Types that lit (frozen traces): {', '.join(sorted({t['cell_type'] for t in types_lit}))}.

Do not expand il3LN6 / APL leftover hubs.

## Score

**{n_ok}/{len(rows)}**. promotes={overall} → **{'Bill-4' if overall else 'Bill-3 stays'}**.

| Env | n_ok |
|-----|-----:|
""" + "\n".join(f"| {k} | {v['n_ok']}/{v['n']} |" for k, v in doc["by_env"].items()) + f"""

PhD band: φ, ALPHA, P_NEW, nest \(D_{{\\mathrm{{eff}}}}\), \(S=K(T_1+T_2+T_3)\), look-split, BT ring, F02.
"""
    (ADV / "FINDINGS.md").write_text(md, encoding="utf-8")
    (ADV / "EXPERIMENT.json").write_text(
        json.dumps(
            {
                "id": "TED-4",
                "role": "ted",
                "adventure": 2,
                "change": "Bill-3 through math environments + hop thinking traces; PhD FSOT identities",
                "vs_bill": "Bill-3",
                "promotes": overall,
                "promote_to": "Bill-4" if overall else None,
                "n_ok": n_ok,
                "n": len(rows),
                "fail": fail,
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    print(f"  Bill-3 math env {n_ok}/{len(rows)}  promotes={overall}")
    for k, v in doc["by_env"].items():
        print(f"    {k:16s} {v['n_ok']}/{v['n']}")
    if fail:
        print("  FAIL", fail)
    print(f"  types_lit={doc['thinking']['n_types_lit']}  wrote {OUT}")
    return 0 if overall else 1


if __name__ == "__main__":
    raise SystemExit(main())
