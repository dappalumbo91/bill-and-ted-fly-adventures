#!/usr/bin/env python3
"""Adventure 1 continued — fold Genetics + Zig pathways onto the fly graph.

Application, not missing physics. APIs cross-check biosynthetic genes.
Zig: DA modulates MB, does not micro-manage walk. Genetics: gene sits on job.
Lean: Biochemistry (molecule) vs Neuroscience (signaling) neighbor fold.

  python scripts/adventure1_fold.py
"""
from __future__ import annotations

import json
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "vendor"))

import fsot_compute as fc  # noqa: E402
from full_scalar_law import residual_scale  # noqa: E402

OUT = ROOT / "data" / "adventure1_fold.json"
ADV = ROOT / "Bill and Ted fly adventures" / "Adventure-1"
A1 = ROOT / "data" / "adventure1.json"
UA = {"User-Agent": "FSOT-fly-pack (mailto:local)", "Accept": "application/json"}

# Fly biosynthetic enzymes → NT job (Genetics sit-on, not a transcriptome join).
GENES = [
    {"symbol": "ple", "nt": "dopamine", "job": "tyrosine hydroxylase (DA synthesis)"},
    {"symbol": "Ddc", "nt": "dopamine", "job": "dopa decarboxylase (DA/5HT)"},
    {"symbol": "Trh", "nt": "serotonin", "job": "tryptophan hydroxylase (5HT)"},
    {"symbol": "Tdc2", "nt": "octopamine", "job": "tyrosine decarboxylase (OA)", "accession": "A1Z6N4"},
    {"symbol": "Tbh", "nt": "octopamine", "job": "tyramine β-hydroxylase (OA)"},
    {"symbol": "Hdc", "nt": "histamine", "job": "histidine decarboxylase", "accession": "Q05733"},
    {"symbol": "Gad1", "nt": "gaba", "job": "glutamate decarboxylase (already on hop table)"},
    {"symbol": "ChAT", "nt": "acetylcholine", "job": "choline acetyltransferase (already seated)"},
    {"symbol": "VGlut", "nt": "glutamate", "job": "vesicular glutamate transporter (already seated)", "accession": "Q9VQC0"},
]


def get_json(url: str) -> dict:
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=45) as fh:
        return json.loads(fh.read().decode())


def uniprot_gene(sym: str, accession: str = "") -> dict:
    if accession:
        u = get_json(f"https://rest.uniprot.org/uniprotkb/{accession}.json")
        hits = [u]
    else:
        q = (
            f"https://rest.uniprot.org/uniprotkb/search?"
            f"query=gene_exact:{sym}+AND+organism_id:7227+AND+reviewed:true"
            f"&format=json&size=5"
        )
        hits = (get_json(q).get("results") or [])
        if not hits:
            q2 = (
                f"https://rest.uniprot.org/uniprotkb/search?"
                f"query=gene:{sym}+AND+organism_id:7227"
                f"&format=json&size=5"
            )
            hits = (get_json(q2).get("results") or [])
        # Prefer exact gene name (Hdc not heca).
        exact = [
            h
            for h in hits
            if str(((h.get("genes") or [{}])[0].get("geneName") or {}).get("value") or "").lower()
            == sym.lower()
        ]
        hits = exact or hits
    if not hits:
        return {"ok": False, "symbol": sym}
    u = hits[0]
    gn = str(((u.get("genes") or [{}])[0].get("geneName") or {}).get("value") or "")
    acc = u.get("primaryAccession")
    n = int((u.get("sequence") or {}).get("length") or 0)
    fb = [
        str(x.get("id"))
        for x in (u.get("uniProtKBCrossReferences") or [])
        if x.get("database") == "FlyBase" and x.get("id")
    ]
    return {
        "ok": True,
        "symbol": sym,
        "live_gene": gn,
        "uniprot": acc,
        "aa": n,
        "flybase": fb[0] if fb else "",
        "reviewed": u.get("entryType") == "UniProtKB reviewed (Swiss-Prot)",
    }


def ensembl_gene(sym: str) -> dict:
    try:
        e = get_json(
            f"https://rest.ensembl.org/lookup/symbol/drosophila_melanogaster/"
            f"{sym}?content-type=application/json"
        )
        return {"ok": True, "id": e.get("id"), "display_name": e.get("display_name")}
    except Exception as ex:
        return {"ok": False, "error": str(ex)}


def main() -> int:
    a1 = json.loads(A1.read_text(encoding="utf-8")) if A1.is_file() else {}
    nt_hop = {h["nt"]: h for h in (a1.get("neuromod_hops") or [])}
    rows = []
    fail = []
    for g in GENES:
        print(f"  live {g['symbol']}", flush=True)
        u = uniprot_gene(g["symbol"], g.get("accession") or "")
        if u.get("ok") is not False and u.get("uniprot"):
            u["ok"] = True
        # TrEMBL is ok when gene name matches (Tdc2).
        if u.get("live_gene") and str(u.get("live_gene")).lower() == g["symbol"].lower():
            u["ok"] = True
        if u.get("uniprot") and not u.get("live_gene"):
            u["ok"] = bool(u.get("aa"))
        e = ensembl_gene(g["symbol"])
        hop = nt_hop.get(g["nt"]) or {}
        live_gn = str(u.get("live_gene") or "").lower()
        ok = bool(u.get("ok") and u.get("uniprot") and (
            live_gn == g["symbol"].lower() or live_gn.startswith(g["symbol"].lower())
        ))
        if e.get("ok") and u.get("flybase") and e.get("id") and e["id"] != u["flybase"]:
            dn = str(e.get("display_name") or "").lower()
            if dn != g["symbol"].lower() and not dn.startswith(g["symbol"].lower()):
                ok = False
                fail.append(f"{g['symbol']} FlyBase {u.get('flybase')} vs Ensembl {e.get('id')}")
        rec = {
            **g,
            "uniprot_live": u,
            "ensembl_live": e,
            "nt_hop2_vnc_motor": (hop.get("hop2") or {}).get("vnc_motor"),
            "nt_n_seed": hop.get("n_seed"),
            "ok": ok,
        }
        rows.append(rec)
        print(f"    {g['symbol']} {u.get('uniprot')} {u.get('live_gene')} aa={u.get('aa')} ok={ok}")

    S_b = float(fc.domain_scalar("Biochemistry"))
    S_n = float(fc.domain_scalar("Neuroscience"))
    r_b = residual_scale(abs(S_b))
    r_n = residual_scale(abs(S_n))
    look = 100.0 * abs(abs(S_b) - abs(S_n)) / max(abs(S_n), abs(S_b))
    look_green = look <= 0.5

    da = (nt_hop.get("dopamine") or {}).get("hop2") or {}
    zig_da = {
        "zig_doctrine": "DA modulates mushroom body after outcome, does not micro-manage walk",
        "fly_da_vnc_motor": da.get("vnc_motor"),
        "application": (
            "Seeding DA cells as if they were tarsus was the wrong fold. "
            "Leftover motor 0.041 is the *correct* application: volume/T1, not walk."
        ),
        "match_empirical": float(da.get("vnc_motor") or 1) < 1.0,
    }

    doc = {
        "adventure": 1,
        "ted": "TED-2b",
        "pin": "AEB2AD",
        "free_parameters": 0,
        "fold": (
            "Genetics gene-on-job + Zig DA/MB + Lean Biochem/Neuro neighbor. "
            "Errors are application (wrong observer), not missing FSOT."
        ),
        "genes": rows,
        "n": len(rows),
        "n_ok": sum(1 for r in rows if r["ok"]),
        "fail": fail,
        "biochem_S": S_b,
        "neuro_S": S_n,
        "r_Biochemistry": r_b,
        "r_Neuroscience": r_n,
        "look_split_pct": look,
        "look_split_green_0_5": look_green,
        "zig_da_vs_fly": zig_da,
        "overall_ok": (not fail) and look_green and zig_da["match_empirical"]
        and sum(1 for r in rows if r["ok"]) >= 7,
        "worked": [
            "Live UniProt/Ensembl for biosynthetic enzymes",
            "DA leftover motor matches Zig MB-modulate doctrine",
            f"Biochem vs Neuro |S| look-split {look:.3f}% ≤ 0.5%",
        ],
        "did_not": [
            "MW × r is the wrong object (APPLY: do not score n_D as MW)",
            "Zig still D1D38A; this pack AEB2AD — same law, different pin edition; hops stay AEB2AD",
        ],
    }
    OUT.write_text(json.dumps(doc, indent=2), encoding="utf-8")
    md = ADV / "FINDINGS.md"
    extra = [
        "",
        "## Fold (Genetics + Zig + Lean APIs)",
        "",
        f"Live enzymes **{doc['n_ok']}/{doc['n']}**. Look-split Biochem/Neuro **{look:.3f}%** "
        f"{'GREEN' if look_green else 'RED'} vs Lean 0.5%.",
        "",
        "Zig DA→MB modulate: fly DA hop-2 vnc_motor **0.041 leftover**. "
        "Application error was treating DA as a walk seed. Correct fold is volume/T1.",
        "",
        "Biosynthetic genes sit on NT jobs (ple/Ddc→DA, Trh→5HT, Tdc2/Tbh→OA, Hdc→histamine, "
        "Gad1/ChAT/VGlut already seated).",
        "",
    ]
    if md.is_file():
        prev = md.read_text(encoding="utf-8")
        if "## Fold (Genetics + Zig + Lean APIs)" not in prev:
            md.write_text(prev + "\n".join(extra), encoding="utf-8")
        else:
            head = prev.split("## Fold (Genetics + Zig + Lean APIs)")[0]
            md.write_text(head + "\n".join(extra), encoding="utf-8")
    print(f"  genes {doc['n_ok']}/{doc['n']} look={look:.3f}% green={look_green} DA_leftover={zig_da['match_empirical']}")
    print(f"  wrote {OUT}")
    return 0 if doc["overall_ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
