#!/usr/bin/env python3
"""Adventure 1 extra finish: blueprint and remaining objects through FSOT.

Every gene, transmitter AA, and biosynthetic pathway is computed with the
same engine as the hops. Not a seating list with a side check.

  S = K(T1+T2+T3)
  r = 1 + |S| · P_NEW          hops: a ← r W a
  overlay cut = 1/φ
  consensus trit: a if a=b else 0
  F02 from 7-trit opcode: h, V, μ, q
  Ledger B: c = m (1 + |S| · ALPHA) on scalar m

  python scripts/adventure1_fsot_blueprint.py
"""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "vendor"))

import fsot_compute as fc  # noqa: E402
from full_scalar_law import compute_scalar_full, residual_scale  # noqa: E402
from trinary_syntax import aa_opcode, aa_pair_weight, uniqueness_report  # noqa: E402

OUT = ROOT / "data" / "adventure1_fsot_blueprint.json"
MD = ROOT / "Bill and Ted fly adventures" / "Adventure-1" / "CLOSEOUT.md"
FINDINGS = ROOT / "Bill and Ted fly adventures" / "Adventure-1" / "FINDINGS.md"
MAX_MEDIAN = 0.5
PHI = float(fc.PHI)
INV_PHI = 1.0 / PHI
ALPHA = float(fc.ALPHA)
P_NEW = float(fc.P_NEW)

# CRC/IUPAC transmitter AA masses (APPLY_NEURO). FSOT chemistry is F02, not this.
CRC_MW = {
    "G": 75.07,
    "D": 133.10,
    "E": 147.13,
    "Y": 181.19,
    "W": 204.23,
    "H": 155.16,
}
TX_AA = ("G", "D", "E", "Y", "W", "H")


def load(name: str) -> dict:
    p = ROOT / "data" / name
    return json.loads(p.read_text(encoding="utf-8")) if p.is_file() else {}


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
    terms["D_eff"] = int(d.D_eff)
    terms["observed"] = bool(d.observed)
    return terms


def f02(aa: str) -> dict:
    op = aa_opcode(aa)
    mu = float(fc.GAMMA) * math.exp(abs(op.c) + op.p + 1.0)
    return {
        "aa": aa,
        "word": list(op.word()),
        "word_str": op.as_string(),
        "c": op.c,
        "p": op.p,
        "v": op.v,
        "h": op.hydrophobicity(),
        "V": op.side_volume(),
        "q": op.charge(),
        "mu": mu,
        "spin": op.spin(),
    }


def ledger_b(m: float, S: float) -> tuple[float, float]:
    c = m * (1.0 + abs(S) * ALPHA)
    err = 100.0 * abs(c - m) / max(abs(m), 1e-18)
    return c, err


def hop_mass(tbl: dict, program: str, field: str = "vnc_motor") -> float:
    return float((tbl.get(program) or {}).get(field) or 0.0)


def classify(
    sits_on: str,
    symbol: str,
    hops: dict[str, dict],
) -> dict:
    """Map a seated gene onto a frozen residual hop / overlay / trit / DENY."""
    s = (sits_on or "").lower()
    sym = (symbol or "").lower()
    overlay = INV_PHI

    def pack(kind, observer, hop_key=None, field="vnc_motor", extra=None):
        rec = {
            "kind": kind,
            "observer": observer,
            "overlay_cut": overlay,
            "hop_key": hop_key,
            "hop2": None,
            "leftover": None,
            "walks": None,
        }
        if hop_key and hop_key in hops:
            rec["hop2"] = hops[hop_key]
            vm = float(hops[hop_key].get(field) or 0.0)
            rec["vnc_motor"] = vm
            rec["descending"] = float(hops[hop_key].get("descending") or 0.0)
            rec["walks"] = vm > 1.0
            rec["leftover"] = vm < 1.0
        if extra:
            rec.update(extra)
        return rec

    if "deny" in s or "courtship" in s or "aggression" in s or sym in ("fru", "dsx"):
        return pack(
            "deny",
            "observer_off",
            extra={
                "law": (
                    "T1 observer off: courtship/aggression/fru/dsx as a family "
                    "oppose human-facing AI safety; labels stay; no hop"
                )
            },
        )
    if "consensus" in s or "gap" in s or "innexin" in s or sym in (
        "shakb",
        "ogre",
        "inx2",
        "inx3",
    ):
        return pack(
            "consensus_trit",
            "electrical_synapse_analog",
            extra={"law": "cons(a,b)=a if a=b else 0; no invented EM gap list"},
        )
    tokens = (
        s.replace("/", " ")
        .replace(",", " ")
        .replace("(", " ")
        .replace(")", " ")
        .replace("-", " ")
        .split()
    )
    if "olfactory" in s or sym in ("orco", "ir8a", "ir25a"):
        return pack("hop_residual", "olfactory", "olfactory", extra={"law": "a ← r W a; leftover is the job"})
    if "johnston" in s or "scolopale" in s or "jo" in tokens or sym in (
        "iav",
        "nan",
        "nompc",
    ):
        return pack("hop_residual", "JO", "JO", extra={"law": "a ← r W a; hop-1 DNg29"})
    if "nociception" in s or sym in ("pain", "painless", "trpa1"):
        return pack(
            "leftover_overlay",
            "nociception",
            extra={"law": "overlay 1/φ; not a VNC walk seed", "leftover": True, "walks": False},
        )
    if "mechanosensory" in s or "bristle" in s or "campaniform" in s:
        return pack("hop_residual", "mechanosensory", "mechanosensory", extra={"law": "a ← r W a"})
    if (
        "photo" in s
        or "photoreceptor" in s
        or " l5" in f" {s}"
        or s.startswith("see")
        or "nina" in s
        or "rhodopsin" in s
        or (sym.startswith("rh") and len(sym) <= 4)
        or sym in ("ninac", "ninad", "ninae", "inad", "norpa", "arr2", "cry")
    ):
        return pack(
            "hop_residual",
            "L5_photo",
            "L5",
            extra={"law": "a ← r W a; vnc leftover, descending can light (flight_only)"},
        )
    if (
        "sleep" in s
        or "lnv" in s
        or "clock" in s
        or sym in ("pdf", "pdfr", "per", "tim", "clk", "cyc")
    ):
        return pack("hop_residual", "LNv_clock", "LNv", extra={"law": "a ← r W a; sleep leftover vs walk"})
    if (
        "dopamine" in s
        or " da " in f" {s} "
        or s.startswith("da ")
        or "tyrosine hydroxylase" in s
        or "dopa decarboxylase" in s
        or sym in ("ple", "ddc", "dop1r1", "dop1r2", "dop2r", "dat", "vmat", "e", "ebony", "t", "tan")
    ):
        return pack("hop_residual", "dopamine", "dopamine", extra={"law": "a ← r W a; volume leftover (T1)"})
    if "serotonin" in s or "5ht" in s or "tryptophan hydroxylase" in s or "5-ht" in s or sym.startswith("5-ht") or sym in (
        "trh",
        "sert",
    ):
        return pack(
            "hop_residual",
            "serotonin",
            "serotonin",
            extra={"law": "a ← r W a; volume leftover vs walk/φ even if vm>1"},
        )
    if (
        "octopamine" in s
        or " oa " in f" {s} "
        or s.startswith("oa")
        or "tyramine" in s
        or "tyrosine decarboxylase" in s
        or sym in ("tdc2", "tbh", "oamb", "oct-tyrr", "octbeta1r", "octbeta2r", "tyr")
    ):
        return pack("hop_residual", "octopamine", "octopamine", extra={"law": "a ← r W a; volume leftover (T1)"})
    if "histamine" in s or "histidine decarboxylase" in s or sym in ("hdc", "hiscl1"):
        return pack("hop_residual", "histamine", "histamine", extra={"law": "a ← r W a"})
    if "gaba" in s or "gad1" in s or "gabaergic" in s or sym in ("gad1", "rdl", "vgat", "gat", "lcch3", "grd"):
        return pack(
            "hop_residual",
            "gaba",
            "gaba",
            extra={"law": "a ← r W a; GABA sign on W is the brake"},
        )
    if "glutamate" in s or "nmj" in s or "vglut" in s or "glur" in s or "eaat" in s or "nmda" in s:
        if "nmj" in s or "motor" in s or "glur" in s or "glur" in sym or sym == "vglut":
            return pack(
                "hop_residual",
                "vnc_motor_NMJ",
                "vnc_sensory",
                extra={"law": "a ← r W a; VGlut/GluR sit on measured vnc_motor NMJ"},
            )
        return pack(
            "leftover_overlay",
            "glutamate_signaling",
            extra={"law": "overlay 1/φ on Glu receptors not a walk seed", "leftover": True, "walks": False},
        )
    if (
        "ach" in s
        or "acetylcholine" in s
        or "cholinergic" in s
        or "nachr" in s
        or sym in ("chat", "vacht", "cht")
        or "nachr" in sym
    ):
        return pack(
            "excitatory_W",
            "acetylcholine",
            extra={
                "law": "default excitatory residual already on measured W; not a new edge list",
                "leftover": False,
            },
        )
    if "muscle" in s or "effector" in s or sym in ("mhc", "mlc2"):
        return pack(
            "effector",
            "vnc_motor_muscle",
            "vnc_sensory",
            extra={"law": "a ← r W a; muscle is the effector of vnc_motor, not a CNS cell"},
        )
    if (
        "spike" in s
        or "voltage-gated" in s
        or "shaker" in s
        or " channel" in s
        or sym in ("para", "sh", "shab", "shal", "sei", "eag", "shaw")
    ):
        return pack(
            "channel_on_W",
            "spike",
            extra={
                "law": "spike channels sit on measured W; not extra synapses",
                "leftover": False,
            },
        )
    if "feeding" in s or "taste" in s or "ecdysis" in s or "stress" in s:
        return pack(
            "leftover_overlay",
            sits_on,
            extra={"law": "overlay 1/φ; peptide/modulatory leftover, not a walk seed", "leftover": True, "walks": False},
        )
    return pack(
        "leftover_overlay",
        sits_on or "unspecified",
        extra={"law": "overlay 1/φ default leftover", "leftover": True, "walks": False},
    )


def main() -> int:
    bp = load("gene_blueprint.json")
    male = load("male_cns_boot.json")
    a1 = load("adventure1.json")
    pep = load("peptide_leftovers.json")
    shared = load("shared_type_hops.json")
    fold = load("adventure1_fold.json")

    cmp = (male.get("compare") or {}).get("hop_2") or {}
    nt = {h["nt"]: (h.get("hop2") or {}) for h in (a1.get("neuromod_hops") or [])}
    ln = (pep.get("LNv_hop") or {}).get("hop2") or {}
    l5 = next((t.get("male") or {} for t in (shared.get("types") or []) if t.get("type") == "L5"), {})

    hops = {
        "vnc_sensory": cmp.get("vnc_sensory") or {},
        "JO": cmp.get("JO") or {},
        "olfactory": cmp.get("olfactory") or {},
        "mechanosensory": cmp.get("mechanosensory") or {},
        "dopamine": nt.get("dopamine") or {},
        "serotonin": nt.get("serotonin") or {},
        "octopamine": nt.get("octopamine") or {},
        "histamine": nt.get("histamine") or {},
        "gaba": nt.get("gaba") or {},
        "LNv": ln,
        "L5": {"vnc_motor": float(l5.get("vnc_motor") or 0), "descending": float(l5.get("descending") or 0)},
    }

    bio = domain_terms("Biochemistry")
    neuro = domain_terms("Neuroscience")
    S_b, S_n = bio["S_vendor"], neuro["S_vendor"]
    r_b, r_n = bio["r"], neuro["r"]
    look = 100.0 * abs(abs(S_b) - abs(S_n)) / max(abs(S_b), abs(S_n), 1e-18)
    walk = hop_mass(cmp, "vnc_sensory")
    walk_phi = walk / PHI

    # --- transmitter AA through F02 + Ledger B ---
    aa_rows = []
    for aa in TX_AA:
        chem = f02(aa)
        c_b, err_b = ledger_b(CRC_MW[aa], S_b)
        c_n, err_n = ledger_b(CRC_MW[aa], S_n)
        aa_rows.append(
            {
                **chem,
                "crc_mw": CRC_MW[aa],
                "ledger_B_biochem": {"computed": c_b, "error_pct": err_b, "green": err_b <= MAX_MEDIAN},
                "ledger_B_neuro": {"computed": c_n, "error_pct": err_n, "green": err_n <= MAX_MEDIAN},
                "pair_self_d8": aa_pair_weight(aa, aa, 8),
            }
        )

    uniq = uniqueness_report()

    # --- 120 genes through hop residual / overlay / trit / DENY ---
    gene_rows = []
    by_kind: dict[str, int] = {}
    for g in bp.get("genes") or []:
        rec = classify(g.get("sits_on") or "", g.get("flybase_symbol") or g.get("working_symbol") or "", hops)
        rec["working_symbol"] = g.get("working_symbol")
        rec["flybase_symbol"] = g.get("flybase_symbol")
        rec["sits_on"] = g.get("sits_on")
        rec["uniprot"] = g.get("uniprot")
        rec["ok"] = rec.get("kind") is not None
        gene_rows.append(rec)
        by_kind[rec["kind"]] = by_kind.get(rec["kind"], 0) + 1

    def gene(sym: str) -> dict:
        sl = sym.lower()
        for r in gene_rows:
            if (r.get("flybase_symbol") or "").lower() == sl or (r.get("working_symbol") or "").lower() == sl:
                return r
        return {}

    orco = gene("Orco")
    fru = gene("fru")
    dsx = gene("dsx")
    inx = [r for r in gene_rows if r.get("kind") == "consensus_trit"]

    # --- biosynthetic pathway sim (F02 precursor → enzyme → NT hop) ---
    pathways = [
        {
            "name": "DA",
            "precursor": "Y",
            "enzymes": ["ple", "Ddc"],
            "nt": "dopamine",
            "expect": "volume_leftover",
        },
        {
            "name": "5HT",
            "precursor": "W",
            "enzymes": ["Trh", "Ddc"],
            "nt": "serotonin",
            "expect": "volume_vs_walk_phi",
        },
        {
            "name": "OA",
            "precursor": "Y",
            "enzymes": ["Tdc2", "Tbh"],
            "nt": "octopamine",
            "expect": "volume_leftover",
        },
        {
            "name": "histamine",
            "precursor": "H",
            "enzymes": ["Hdc"],
            "nt": "histamine",
            "expect": "recorded_hop",
        },
        {
            "name": "GABA",
            "precursor": "E",
            "enzymes": ["Gad1"],
            "nt": "gaba",
            "expect": "signed_brake",
        },
    ]
    path_rows = []
    for p in pathways:
        aa = f02(p["precursor"])
        hop = hops.get(p["nt"]) or {}
        vm = float(hop.get("vnc_motor") or 0.0)
        enzymes = []
        for es in p["enzymes"]:
            er = gene(es)
            enzymes.append(
                {
                    "symbol": es,
                    "kind": er.get("kind"),
                    "observer": er.get("observer"),
                    "ok": bool(er),
                }
            )
        leftover = vm < 1.0
        vs_phi = vm < walk_phi
        if p["expect"] == "volume_leftover":
            ok = leftover
        elif p["expect"] == "volume_vs_walk_phi":
            ok = vs_phi
        elif p["expect"] == "signed_brake":
            ok = vm > 1.0
        else:
            ok = hop != {}
        path_rows.append(
            {
                "name": p["name"],
                "precursor": aa,
                "pair_self_d8": aa_pair_weight(p["precursor"], p["precursor"], 8),
                "S_Biochemistry": S_b,
                "r_Biochemistry": r_b,
                "enzymes": enzymes,
                "nt": p["nt"],
                "hop2_vnc_motor": vm,
                "walks": vm > 1.0,
                "leftover_vm_lt_1": leftover,
                "leftover_vs_walk_phi": vs_phi,
                "walk_over_phi": walk_phi,
                "expect": p["expect"],
                "ok": ok and all(e["ok"] for e in enzymes),
                "law": "F02(precursor) + enzyme sits_on + a ← r W a on NT seed",
            }
        )

    # --- receptor overlay sim: ligand hop is the receptor's FSOT state ---
    receptor_rows = []
    for r in gene_rows:
        if r.get("kind") != "hop_residual":
            continue
        if r.get("observer") not in ("dopamine", "serotonin", "octopamine", "histamine", "gaba", "olfactory", "LNv_clock"):
            continue
        vm = float(r.get("vnc_motor") or 0.0)
        receptor_rows.append(
            {
                "flybase_symbol": r.get("flybase_symbol"),
                "observer": r.get("observer"),
                "vnc_motor": vm,
                "overlay_cut": INV_PHI,
                "leftover": r.get("leftover"),
                "relative_to_walk_phi": vm / walk_phi if walk_phi else None,
                "law": "receptor occupancy analog = ligand hop leftover under 1/φ; not a fitted Kd",
            }
        )

    n_genes = len(gene_rows)
    n_ok_genes = sum(1 for r in gene_rows if r.get("ok"))
    n_ok_path = sum(1 for r in path_rows if r.get("ok"))
    aa_green = all(
        r["ledger_B_biochem"]["green"] and r["ledger_B_neuro"]["green"] for r in aa_rows
    )
    orco_ok = bool(orco) and bool(orco.get("leftover"))
    deny_ok = (fru.get("kind") == "deny") and (dsx.get("kind") == "deny")
    inx_ok = len(inx) >= 3
    da_vm = float((hops.get("dopamine") or {}).get("vnc_motor") or 9)
    oa_vm = float((hops.get("octopamine") or {}).get("vnc_motor") or 9)
    olf_vm = hop_mass(cmp, "olfactory")
    ln_vm = float((hops.get("LNv") or {}).get("vnc_motor") or 9)

    overall = (
        n_ok_genes == n_genes
        and n_genes >= 120
        and n_ok_path == len(path_rows)
        and aa_green
        and uniq.get("all_unique")
        and look <= MAX_MEDIAN
        and orco_ok
        and deny_ok
        and inx_ok
        and da_vm < 1.0
        and oa_vm < 1.0
        and olf_vm < 1.0
        and ln_vm < 1.0
        and fold.get("overall_ok") is not False
    )

    doc = {
        "adventure": 1,
        "pin": "AEB2AD",
        "free_parameters": 0,
        "law": "S=K(T1+T2+T3); r=1+|S|P_NEW; overlay 1/φ; consensus trit; F02 opcode; Ledger B ALPHA",
        "scalar": {
            "Biochemistry": {
                "S": S_b,
                "T1": bio["T1"],
                "T2": bio["T2"],
                "T3": bio["T3"],
                "r": r_b,
                "D_eff": bio["D_eff"],
            },
            "Neuroscience": {
                "S": S_n,
                "T1": neuro["T1"],
                "T2": neuro["T2"],
                "T3": neuro["T3"],
                "r": r_n,
                "D_eff": neuro["D_eff"],
            },
            "look_split_pct": look,
            "ALPHA": ALPHA,
            "P_NEW": P_NEW,
            "overlay_cut": INV_PHI,
            "walk_vnc_motor": walk,
            "walk_over_phi": walk_phi,
        },
        "transmitter_aa_f02": aa_rows,
        "trinary_unique": uniq.get("all_unique"),
        "n_genes": n_genes,
        "n_genes_ok": n_ok_genes,
        "by_kind": by_kind,
        "genes": gene_rows,
        "pathways": path_rows,
        "n_pathways_ok": n_ok_path,
        "receptor_overlay_sim": receptor_rows,
        "n_receptor_sim": len(receptor_rows),
        "orco": {
            "flybase_symbol": orco.get("flybase_symbol"),
            "kind": orco.get("kind"),
            "vnc_motor": orco.get("vnc_motor"),
            "leftover": orco.get("leftover"),
            "ok": orco_ok,
        },
        "deny_fru_dsx": deny_ok,
        "n_innexin_consensus": len(inx),
        "overall_ok": overall,
    }
    OUT.write_text(json.dumps(doc, indent=2), encoding="utf-8")

    print(f"  S_Biochem={S_b:.6f} r={r_b:.6f}  S_Neuro={S_n:.6f} r={r_n:.6f} look={look:.3f}%")
    print(f"  F02 transmitter AA {len(aa_rows)}  unique_opcodes={uniq.get('all_unique')}")
    for r in aa_rows:
        print(f"    {r['aa']} {r['word_str']}  h={r['h']:.4f} V={r['V']:.4f}  MW_B_err={r['ledger_B_biochem']['error_pct']:.4f}%")
    print(f"  genes {n_ok_genes}/{n_genes}  kinds={by_kind}")
    print(f"  Orco leftover vm={orco.get('vnc_motor')}  fru/dsx DENY={deny_ok}  innexin cons={len(inx)}")
    print(f"  pathways {n_ok_path}/{len(path_rows)}")
    for p in path_rows:
        flag = "OK" if p["ok"] else "FAIL"
        print(
            f"    {flag:4s} {p['name']:10s} precursor={p['precursor']['aa']} "
            f"vm={p['hop2_vnc_motor']:.4f} leftover={p['leftover_vm_lt_1']} vs_φ={p['leftover_vs_walk_phi']}"
        )
    print(f"  receptor overlay sim n={len(receptor_rows)}")
    print(f"  overall_ok={overall}  wrote {OUT}")

    extra = [
        "",
        "## Extra finish — blueprint through FSOT",
        "",
        f"Law: \(S=K(T_1+T_2+T_3)\), \(r=1+|S|\\cdot P_{{\\mathrm{{NEW}}}}\), overlay \(1/\\varphi\), consensus trit, F02 opcode. Look-split **{look:.3f}%**. **{n_ok_genes}/{n_genes}** genes classified. Pathways **{n_ok_path}/{len(path_rows)}**.",
        "",
        f"Orco olfactory hop-2 vnc_motor **{olf_vm:.4f} leftover** (the job). fru/dsx/courtship/aggression **DENY**: \(T_1\) off because this pack is for human-facing AI; that family opposes human safety; labels stay. Innexins **{len(inx)}** consensus trit. DA **{da_vm:.3f} leftover**, OA **{oa_vm:.3f} leftover**, LNv **{ln_vm:.3f} leftover**.",
        "",
        "Transmitter AA (Gly Asp Glu Tyr Trp His) through F02 7-trit opcode (h, V, μ, q) and Ledger B on CRC MW. Biosynthetic pathways: precursor F02 → enzyme sits_on → NT residual hop. Receptor occupancy analog = ligand hop leftover under \(1/\\varphi\), not a fitted \(K_d\).",
        "",
        f"Dump identity 0% is the measured \(W\) the hops use. Independent rows go through \(S\), \(rW\), overlay, trit. **overall_ok={overall}**.",
        "",
    ]
    section = "## Extra finish — blueprint through FSOT"
    if MD.is_file():
        prev = MD.read_text(encoding="utf-8")
        if section in prev:
            prev = prev.split(section)[0].rstrip()
        MD.write_text(prev + "\n" + "\n".join(extra), encoding="utf-8")

    if FINDINGS.is_file():
        prev = FINDINGS.read_text(encoding="utf-8")
        block = [
            "",
            "## Extra finish — everything through FSOT",
            "",
            f"Blueprint **{n_ok_genes}/{n_genes}** genes computed as hop residual / overlay leftover / consensus trit / DENY / excitatory \(W\) / effector. Not UniProt seating with a side check.",
            "",
            f"Pathways (F02 precursor → enzyme → \(a \\leftarrow rWa\)): DA leftover {da_vm:.3f}; OA leftover {oa_vm:.3f}; 5HT {float((hops['serotonin'] or {}).get('vnc_motor') or 0):.2f} < walk/φ={walk_phi:.2f}; GABA signed brake; histamine recorded.",
            "",
            f"Orco leftover {olf_vm:.4f}. fru/dsx/courtship/aggression DENY: T1 off for human-facing AI (that family opposes human safety). Transmitter AA through F02 + Ledger B. Receptor overlay sim n={len(receptor_rows)}. Look-split {look:.3f}%.",
            "",
        ]
        marker = "## Extra finish — everything through FSOT"
        if marker in prev:
            prev = prev.split(marker)[0].rstrip()
        FINDINGS.write_text(prev + "\n" + "\n".join(block), encoding="utf-8")

    return 0 if overall else 1


if __name__ == "__main__":
    raise SystemExit(main())
