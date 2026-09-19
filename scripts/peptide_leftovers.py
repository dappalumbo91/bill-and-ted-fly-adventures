#!/usr/bin/env python3
"""Seat neuropeptides and remaining genetic leftovers (Adventure 1 closeout).

Pdf/NPF/SIFa + receptors, clock (per/tim/Clk), fru/dsx proteins,
extra nAChR subunits, EAAT1/Gat, TrpA1/painless. Live UniProt.
Innexins already in genetic_interactions. Sit-on: sleep leftover,
volume, ACh, DENY courtship — not invented synapses.

  python scripts/peptide_leftovers.py
  python scripts/peptide_leftovers.py --hops   # also hop LNv clock types
"""
from __future__ import annotations

import json
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "vendor"))

OUT = ROOT / "data" / "peptide_leftovers.json"
ADV = ROOT / "Bill and Ted fly adventures" / "Adventure-1"
UA = {"User-Agent": "FSOT-fly-pack (mailto:local)", "Accept": "application/json"}

GENES = [
    {"symbol": "Pdf", "layer": "peptide", "sits_on": "sleep leftover / LNv clock", "job": "pigment-dispersing factor"},
    {"symbol": "PdfR", "layer": "receptor", "sits_on": "sleep leftover / LNv clock", "job": "Pdf receptor"},
    {"symbol": "NPF", "layer": "peptide", "sits_on": "feeding leftover (not walk)", "job": "neuropeptide F"},
    {"symbol": "NPFR", "layer": "receptor", "sits_on": "feeding leftover", "job": "NPF receptor"},
    {"symbol": "SIFa", "layer": "peptide", "sits_on": "courtship DENY default", "job": "SIFamide"},
    {"symbol": "sNPF", "layer": "peptide", "sits_on": "feeding leftover", "job": "short NPF"},
    {"symbol": "Dh31", "layer": "peptide", "sits_on": "clock / gut leftover", "job": "diuretic hormone 31"},
    {"symbol": "AstA", "layer": "peptide", "sits_on": "feeding leftover", "job": "allatostatin A"},
    {"symbol": "CCAP", "layer": "peptide", "sits_on": "ecdysis leftover", "job": "crustacean cardioactive peptide"},
    {"symbol": "Crz", "layer": "peptide", "sits_on": "stress leftover", "job": "corazonin"},
    {"symbol": "per", "layer": "clock", "sits_on": "sleep leftover", "job": "period"},
    {"symbol": "tim", "layer": "clock", "sits_on": "sleep leftover", "job": "timeless"},
    {"symbol": "Clk", "layer": "clock", "sits_on": "sleep leftover", "job": "Clock"},
    {"symbol": "cyc", "layer": "clock", "sits_on": "sleep leftover", "job": "cycle"},
    {"symbol": "fru", "layer": "selector", "sits_on": "courtship DENY default", "job": "fruitless"},
    {"symbol": "dsx", "layer": "selector", "sits_on": "courtship DENY default", "job": "doublesex"},
    {"symbol": "nAChRalpha1", "layer": "receptor", "sits_on": "ACh", "job": "nAChR α1"},
    {"symbol": "nAChRalpha2", "layer": "receptor", "sits_on": "ACh", "job": "nAChR α2"},
    {"symbol": "nAChRalpha3", "layer": "receptor", "sits_on": "ACh", "job": "nAChR α3"},
    {"symbol": "nAChRalpha4", "layer": "receptor", "sits_on": "ACh", "job": "nAChR α4"},
    {"symbol": "nAChRalpha5", "layer": "receptor", "sits_on": "ACh", "job": "nAChR α5"},
    {"symbol": "nAChRalpha6", "layer": "receptor", "sits_on": "ACh", "job": "nAChR α6"},
    {"symbol": "nAChRbeta1", "layer": "receptor", "sits_on": "ACh", "job": "nAChR β1"},
    {"symbol": "nAChRbeta2", "layer": "receptor", "sits_on": "ACh", "job": "nAChR β2"},
    {"symbol": "EAAT1", "layer": "reuptake", "sits_on": "glutamate", "job": "excitatory AA transporter"},
    {"symbol": "Gat", "layer": "reuptake", "sits_on": "GABA", "job": "GABA transporter"},
    {"symbol": "TrpA1", "layer": "channel", "sits_on": "JO / mechanosensory", "job": "thermo/mechano TRPA"},
    {"symbol": "painless", "layer": "channel", "sits_on": "nociception leftover", "job": "TRPA nociception"},
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
    sl = sym.lower().replace("-", "")
    for h in hits:
        gn = str(((h.get("genes") or [{}])[0].get("geneName") or {}).get("value") or "")
        names = [gn]
        for g in h.get("genes") or []:
            for a in g.get("synonyms") or []:
                names.append(str(a.get("value") or ""))
        if any(n.lower().replace("-", "") == sl for n in names if n):
            exact.append(h)
    hits = exact or hits
    if not hits:
        return {"ok": False, "symbol": sym}
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


def ln_v_hop() -> dict:
    from fly_connectome import _R_BIO
    from male_cns import load_male_graph
    from math_first import _hop2_state, _motor_by_side

    print("  load Male CNS for LNv", flush=True)
    graph = load_male_graph()
    seed = [
        graph["idx"][rid]
        for rid, m in graph["meta"].items()
        if rid in graph["idx"] and "lnv" in (m.get("cell_type") or "").lower()
    ]
    print(f"== LNv n_seed={len(seed)}", flush=True)
    if not seed:
        return {"n_seed": 0}
    a = _hop2_state(graph, seed)
    mass = _motor_by_side(a, graph)
    vm = float(mass["vnc_motor"])
    return {
        "n_seed": len(seed),
        "hop2": mass,
        "walks": vm > 1.0,
        "sleep_leftover": vm <= 1.0,
        "residual_Biochemistry": _R_BIO,
        "job": "clock LNv — should leftover vs VNC walk 10.74",
    }


def main(argv: list[str] | None = None) -> int:
    import argparse

    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--hops", action="store_true")
    args = ap.parse_args(argv)
    rows = []
    fail = []
    for g in GENES:
        print(f"  live {g['symbol']}", flush=True)
        u = uniprot_gene(g["symbol"])
        ok = bool(u.get("ok") and u.get("uniprot"))
        if not ok:
            fail.append(g["symbol"])
        rec = {**g, "uniprot_live": u, "ok": ok}
        rows.append(rec)
        print(f"    {g['symbol']} {u.get('uniprot')} {u.get('live_gene')} ok={ok}")
    hop = ln_v_hop() if args.hops else None
    by: dict[str, int] = {}
    for r in rows:
        by[r["layer"]] = by.get(r["layer"], 0) + int(r["ok"])
    doc = {
        "adventure": 1,
        "pin": "AEB2AD",
        "free_parameters": 0,
        "n": len(rows),
        "n_ok": sum(1 for r in rows if r["ok"]),
        "fail": fail,
        "by_layer_ok": by,
        "genes": rows,
        "LNv_hop": hop,
        "overall_ok": not fail,
        "closeout": (
            "Peptides/clock/selectors/extra nAChR/reuptake/TRP seated. "
            "Adventure 1 genetic catalog complete enough to start Adventure 2."
        ),
    }
    if hop and hop.get("n_seed"):
        doc["overall_ok"] = bool(doc["overall_ok"] and hop.get("sleep_leftover"))
    OUT.write_text(json.dumps(doc, indent=2), encoding="utf-8")
    md = ADV / "FINDINGS.md"
    extra = [
        "",
        "## Peptides and leftover genes",
        "",
        f"Live **{doc['n_ok']}/{doc['n']}**. Pdf/NPF/SIFa/clock/fru/dsx/nAChR extras/EAAT1/Gat/TrpA1.",
        "",
    ]
    if hop:
        extra.append(
            f"LNv hop n={hop.get('n_seed')} vnc_motor="
            f"{(hop.get('hop2') or {}).get('vnc_motor')} leftover={hop.get('sleep_leftover')}"
        )
        extra.append("")
    if md.is_file():
        prev = md.read_text(encoding="utf-8")
        if "## Peptides and leftover genes" not in prev:
            md.write_text(prev + "\n".join(extra), encoding="utf-8")
        else:
            head = prev.split("## Peptides and leftover genes")[0]
            md.write_text(head + "\n".join(extra), encoding="utf-8")
    print(f"  peptide_leftovers {doc['n_ok']}/{doc['n']} fail={fail} LNv={hop}")
    print(f"  wrote {OUT}")
    return 0 if doc["overall_ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
