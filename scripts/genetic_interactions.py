#!/usr/bin/env python3
"""Missing genetic structure: receptors, vesicular transporters, innexins.

Synthesis enzymes are already in adventure1_fold. This seats the *interaction*
layer on the same NT/volume/gap jobs. Live UniProt/Ensembl. Not a transcriptome
join. Innexins sit on consensus (gap analog), not on invented EM edges.

  python scripts/genetic_interactions.py
"""
from __future__ import annotations

import runio
runio.install()

import json
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

OUT = ROOT / "data" / "genetic_interactions.json"
ADV = ROOT / "Bill and Ted fly adventures" / "Adventure-1"
A1 = ROOT / "data" / "adventure1.json"
FOLD = ROOT / "data" / "adventure1_fold.json"
UA = {"User-Agent": "FSOT-fly-pack (mailto:local)", "Accept": "application/json"}

# layer: synthesis already mapped | receptor | v_transport | reuptake | innexin | channel
GENES = [
    {"symbol": "Rdl", "layer": "receptor", "nt": "gaba", "job": "GABA-A receptor", "accession": ""},
    {"symbol": "GluRIIA", "layer": "receptor", "nt": "glutamate", "job": "NMJ iGluR", "accession": ""},
    {"symbol": "nAChRalpha7", "layer": "receptor", "nt": "acetylcholine", "job": "nicotinic AChR", "accession": ""},
    {"symbol": "Dop1R1", "layer": "receptor", "nt": "dopamine", "job": "D1-like DA receptor", "accession": ""},
    {"symbol": "Oamb", "layer": "receptor", "nt": "octopamine", "job": "OA receptor", "accession": ""},
    {"symbol": "5-HT1A", "layer": "receptor", "nt": "serotonin", "job": "5-HT1A receptor", "accession": ""},
    {"symbol": "HisCl1", "layer": "receptor", "nt": "histamine", "job": "histamine chloride channel", "accession": ""},
    {"symbol": "Vmat", "layer": "v_transport", "nt": "dopamine", "job": "vesicular monoamine (DA/OA/5HT)", "accession": ""},
    {"symbol": "VAChT", "layer": "v_transport", "nt": "acetylcholine", "job": "vesicular ACh transporter", "accession": ""},
    {"symbol": "VGAT", "layer": "v_transport", "nt": "gaba", "job": "vesicular GABA transporter", "accession": ""},
    {"symbol": "DAT", "layer": "reuptake", "nt": "dopamine", "job": "dopamine transporter", "accession": ""},
    {"symbol": "SerT", "layer": "reuptake", "nt": "serotonin", "job": "serotonin transporter", "accession": ""},
    {"symbol": "shakB", "layer": "innexin", "nt": "", "job": "gap junction (giant-fiber electrical)", "accession": ""},
    {"symbol": "ogre", "layer": "innexin", "nt": "", "job": "innexin-1 gap junction", "accession": ""},
    {"symbol": "Inx2", "layer": "innexin", "nt": "", "job": "innexin-2 gap junction", "accession": ""},
    {"symbol": "para", "layer": "channel", "nt": "", "job": "voltage-gated Na (spike)", "accession": ""},
    {"symbol": "Sh", "layer": "channel", "nt": "", "job": "Shaker K channel", "accession": ""},
]


def get_json(url: str) -> dict:
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=45) as fh:
        return json.loads(fh.read().decode())


def uniprot_gene(sym: str) -> dict:
    q = (
        "https://rest.uniprot.org/uniprotkb/search?format=json&size=8&query="
        f"organism_id:7227+AND+(gene_exact:{sym}+OR+gene:{sym})"
    )
    hits = (get_json(q).get("results") or [])
    exact = []
    for h in hits:
        gn = str(((h.get("genes") or [{}])[0].get("geneName") or {}).get("value") or "")
        if gn.lower() == sym.lower() or gn.lower().replace("-", "") == sym.lower().replace("-", ""):
            exact.append(h)
        aliases = []
        for g in h.get("genes") or []:
            for a in g.get("synonyms") or []:
                aliases.append(str(a.get("value") or ""))
        if any(a.lower() == sym.lower() for a in aliases):
            exact.append(h)
    hits = exact or hits
    if not hits:
        return {"ok": False, "symbol": sym}
    # prefer reviewed
    hits.sort(key=lambda u: 0 if u.get("entryType") == "UniProtKB reviewed (Swiss-Prot)" else 1)
    u = hits[0]
    gn = str(((u.get("genes") or [{}])[0].get("geneName") or {}).get("value") or "")
    fb = [
        str(x.get("id"))
        for x in (u.get("uniProtKBCrossReferences") or [])
        if x.get("database") == "FlyBase" and x.get("id")
    ]
    return {
        "ok": True,
        "live_gene": gn,
        "uniprot": u.get("primaryAccession"),
        "aa": int((u.get("sequence") or {}).get("length") or 0),
        "flybase": fb[0] if fb else "",
        "reviewed": u.get("entryType") == "UniProtKB reviewed (Swiss-Prot)",
    }


def ensembl_gene(sym: str) -> dict:
    try:
        e = get_json(
            "https://rest.ensembl.org/lookup/symbol/drosophila_melanogaster/"
            f"{sym}?content-type=application/json"
        )
        return {"ok": True, "id": e.get("id"), "display_name": e.get("display_name")}
    except Exception as ex:
        return {"ok": False, "error": str(ex)[:120]}


def main() -> int:
    from runio import offline_exit

    cached = offline_exit(OUT)
    if cached is not None:
        return cached
    a1 = json.loads(A1.read_text(encoding="utf-8")) if A1.is_file() else {}
    fold = json.loads(FOLD.read_text(encoding="utf-8")) if FOLD.is_file() else {}
    nt_hop = {h["nt"]: h for h in (a1.get("neuromod_hops") or [])}
    syn = [g["symbol"] for g in (fold.get("genes") or [])]
    rows = []
    fail = []
    for g in GENES:
        print(f"  live {g['symbol']}", flush=True)
        u = uniprot_gene(g["symbol"])
        e = ensembl_gene(g["symbol"])
        hop = nt_hop.get(g["nt"]) or {}
        ok = bool(u.get("ok") and u.get("uniprot"))
        if not ok:
            fail.append(g["symbol"])
        sit = "consensus_gap_analog" if g["layer"] == "innexin" else (
            f"NT hop {g['nt']}" if g["nt"] else g["job"]
        )
        rec = {
            **g,
            "uniprot_live": u,
            "ensembl_live": e,
            "sits_on": sit,
            "nt_hop2_vnc_motor": (hop.get("hop2") or {}).get("vnc_motor") if g["nt"] else None,
            "ok": ok,
        }
        rows.append(rec)
        print(f"    {g['symbol']} {u.get('uniprot')} {u.get('live_gene')} ok={ok}")

    by_layer: dict[str, int] = {}
    for r in rows:
        by_layer[r["layer"]] = by_layer.get(r["layer"], 0) + int(r["ok"])
    missing_still = [r["symbol"] for r in rows if not r["ok"]]
    doc = {
        "adventure": 1,
        "pin": "AEB2AD",
        "free_parameters": 0,
        "already_synthesis": syn,
        "n": len(rows),
        "n_ok": sum(1 for r in rows if r["ok"]),
        "fail": fail,
        "by_layer_ok": by_layer,
        "genes": rows,
        "innexin_doctrine": (
            "No Inx cell-type string in Male CNS (INXXX false positive). "
            "shakB/ogre/Inx2 sit on consensus trit (electrical analog), not invented gap edges."
        ),
        "overall_ok": len(fail) == 0,
        "worked": [],
        "did_not": [],
    }
    if not fail:
        doc["worked"].append("receptors + VMAT/VAChT/VGAT + DAT/SerT + innexins live UniProt")
    else:
        doc["did_not"].append(f"API miss {missing_still}")
    doc["worked"].append("synthesis already folded (ple Ddc Trh Tdc2 Tbh Hdc Gad1 ChAT VGlut)")
    OUT.write_text(json.dumps(doc, indent=2), encoding="utf-8")
    md = ADV / "FINDINGS.md"
    extra = [
        "",
        "## Genetic interactions (receptors / transporters / innexins)",
        "",
        f"Live **{doc['n_ok']}/{doc['n']}**. Synthesis already seated. "
        "Innexins → consensus analog (no EM gap list).",
        "",
    ]
    if md.is_file():
        prev = md.read_text(encoding="utf-8")
        if "## Genetic interactions" not in prev:
            md.write_text(prev + "\n".join(extra), encoding="utf-8")
    print(f"  genetic_interactions {doc['n_ok']}/{doc['n']} fail={fail}")
    print(f"  wrote {OUT}")
    return 0 if doc["overall_ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
