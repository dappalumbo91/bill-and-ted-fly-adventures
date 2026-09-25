#!/usr/bin/env python3
"""Hook named fly genes to hop jobs + live UniProt/Ensembl.

  python scripts/genetics_hook.py

Does not invent a Fly Cell Atlas bodyId join.
"""
from __future__ import annotations

import runio
runio.install()

import json
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
JOIN = ROOT / "data" / "fly_genetics_join.json"
WALK = ROOT / "data" / "fly_walking_product.json"
MALE = ROOT / "data" / "male_cns_boot.json"
BANC = ROOT / "data" / "banc_connectome_boot.json"
HOMO = ROOT / "data" / "homolog_correspondence.json"
OUT = ROOT / "data" / "genetics_hook.json"
UA = {"User-Agent": "FSOT-fly-pack (mailto:local)", "Accept": "application/json"}

# Gene → residual job on the measured fly graph.
JOB = {
    "nompC": {"seed": "JO", "job": "mechanotransduction"},
    "iav": {"seed": "JO", "job": "JO TRPV"},
    "nan": {"seed": "JO", "job": "JO TRPV"},
    "Gad1": {"seed": "vnc_sensory", "job": "inhibitory GABA residual"},
    "ChAT": {"seed": "vnc_sensory", "job": "cholinergic excitatory default (ACh edges)"},
    "VGlut": {"seed": "vnc_sensory", "job": "glutamatergic vnc_motor NMJ"},
    "Mhc": {"seed": "", "job": "muscle effector (not a CNS cell)"},
}


def get_json(url: str) -> dict:
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=45) as fh:
        return json.loads(fh.read().decode())


def hop2(path: Path, program: str) -> dict:
    d = json.loads(path.read_text(encoding="utf-8"))
    rec = ((d.get("compare") or {}).get("hop_2") or {}).get(program) or {}
    top = rec.get("top") or {}
    return {
        "vnc_motor": rec.get("vnc_motor"),
        "descending": rec.get("descending"),
        "top": top.get("cell_type") or top.get("name"),
    }


def uniprot_live(acc: str) -> dict:
    u = get_json(f"https://rest.uniprot.org/uniprotkb/{acc}.json")
    gn = ""
    genes = u.get("genes") or []
    if genes:
        gn = str((genes[0].get("geneName") or {}).get("value") or "")
    org = (u.get("organism") or {}).get("scientificName")
    n = int(((u.get("sequence") or {}).get("length")) or 0)
    flybase_ids = [
        str(x.get("id") or "")
        for x in (u.get("uniProtKBCrossReferences") or [])
        if x.get("database") == "FlyBase" and x.get("id")
    ]
    return {
        "accession": u.get("primaryAccession"),
        "gene": gn,
        "organism": org,
        "length": n,
        "reviewed": u.get("entryType") == "UniProtKB reviewed (Swiss-Prot)",
        "flybase": flybase_ids[0] if flybase_ids else "",
        "flybase_all": flybase_ids,
    }


def ensembl_live(symbol: str) -> dict | None:
    url = (
        "https://rest.ensembl.org/lookup/symbol/drosophila_melanogaster/"
        f"{symbol}?content-type=application/json"
    )
    try:
        e = get_json(url)
    except Exception:
        return None
    return {"id": e.get("id"), "display_name": e.get("display_name"), "biotype": e.get("biotype")}


def main() -> int:
    from runio import offline_exit

    cached = offline_exit(OUT)
    if cached is not None:
        return cached
    join = json.loads(JOIN.read_text(encoding="utf-8")) if JOIN.is_file() else {}
    walk = {g["symbol"]: g for g in (json.loads(WALK.read_text(encoding="utf-8")).get("genes") or [])} if WALK.is_file() else {}
    homo = []
    if HOMO.is_file():
        homo = json.loads(HOMO.read_text(encoding="utf-8")).get("homologs") or []
    rows = []
    failed = []
    for g in join.get("genes") or []:
        sym = g["symbol"]
        acc = g["uniprot"]
        live = uniprot_live(acc)
        ens = ensembl_live(sym)
        job = JOB.get(sym) or {}
        seed = job.get("seed") or ""
        fb = g.get("flybase") or ""
        fb_sec = g.get("flybase_secondary") or ""
        live_fb = str(live.get("flybase") or "")
        aliases = {x for x in (fb, fb_sec, live_fb) if x}
        ok_gene = live.get("gene", "").lower() == sym.lower() or live.get("accession") == acc
        # Ensembl uses current FlyBase IDs. Frozen secondary IDs are aliases, not a miss.
        current_fb = live_fb or fb
        if ens and ens.get("id") and current_fb and ens["id"] != current_fb and ens["id"] not in aliases:
            ok_gene = False
            failed.append(f"{sym} FlyBase {current_fb} ≠ Ensembl {ens.get('id')}")
        if live_fb and fb and live_fb != fb and fb != fb_sec:
            # Frozen current ID drifted vs UniProt FlyBase xref.
            ok_gene = False
            failed.append(f"{sym} frozen FlyBase {fb} ≠ UniProt xref {live_fb}")
        if not ok_gene:
            failed.append(sym)
        transfers = [
            {
                "organism": h.get("target_organism"),
                "uniprot": h.get("uniprot"),
                "template_pdb": h.get("template_pdb"),
                "template_identity": h.get("template_identity"),
            }
            for h in homo
            if h.get("source_symbol") == sym and h.get("status") == "measured_homolog"
        ]
        rec = {
            **g,
            "job": job.get("job"),
            "hop_seed": seed,
            "male_hop2": hop2(MALE, seed) if seed and MALE.is_file() else None,
            "banc_hop2": hop2(BANC, seed if seed != "JO" else "JO") if seed and BANC.is_file() else None,
            "uniprot_live": live,
            "ensembl_live": ens,
            "walking_product": {
                "template_pdb": (walk.get(sym) or {}).get("template_pdb"),
                "template_identity": (walk.get(sym) or {}).get("template_identity"),
                "structure_mode": (walk.get(sym) or {}).get("structure_mode"),
            },
            "homolog_transfers": transfers,
            "ok": bool(ok_gene and live.get("accession") == acc),
        }
        rows.append(rec)
        print(
            f"{'OK' if rec['ok'] else 'FAIL'} {sym} {acc} live_gene={live.get('gene')} "
            f"ensembl={ens.get('id') if ens else '-'} tmpl={(walk.get(sym) or {}).get('template_pdb')}",
            flush=True,
        )
    doc = {
        "pin": "AEB2AD",
        "free_parameters": 0,
        "rule": "Fold and hop only where measured. No Fly Cell Atlas bodyId invent.",
        "n": len(rows),
        "fail": failed,
        "overall_ok": len(failed) == 0,
        "genes": rows,
    }
    OUT.write_text(json.dumps(doc, indent=2), encoding="utf-8")
    print(f"  wrote {OUT} fail={failed}")
    return 0 if doc["overall_ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
