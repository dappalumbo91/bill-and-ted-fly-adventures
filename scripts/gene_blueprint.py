#!/usr/bin/env python3
"""Official FlyBase/UniProt names for every seated gene + remaining crumbs.

If we used a working label (tan, ChT, VGlut), record the **scientific**
symbol (t, ChT, VGlut1) so a reader gets the fly blueprint, not a homemade tag.

  python scripts/gene_blueprint.py
  python scripts/gene_blueprint.py --crumbs
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
OUT = ROOT / "data" / "gene_blueprint.json"
CRUMB_OUT = ROOT / "data" / "genetic_crumbs.json"
ADV = ROOT / "Bill and Ted fly adventures" / "Adventure-1"
UA = {"User-Agent": "FSOT-fly-pack (mailto:local)", "Accept": "application/json"}

SOURCES = [
    ("fly_genetics_join.json", "genes"),
    ("adventure1_fold.json", "genes"),
    ("genetic_interactions.json", "genes"),
    ("peptide_leftovers.json", "genes"),
    ("genetic_baseline_rest.json", "genes"),
]

CRUMBS = [
    {"symbol": "GluRIID", "sits_on": "NMJ glutamate", "job": "iGluR IID"},
    {"symbol": "GluRIIE", "sits_on": "NMJ glutamate", "job": "iGluR IIE"},
    {"symbol": "AstA-R2", "sits_on": "feeding leftover", "job": "AstA receptor 2"},
    {"symbol": "Oct-TyrR", "sits_on": "OA/tyramine volume leftover", "job": "OA/tyramine receptor"},
    {"symbol": "ninaC", "sits_on": "photoreceptor", "job": "ninaC kinase-myosin"},
    {"symbol": "inaD", "sits_on": "photoreceptor scaffold", "job": "INAD PDZ scaffold"},
    {"symbol": "Rh3", "sits_on": "photoreceptor", "job": "UV rhodopsin"},
    {"symbol": "Rh4", "sits_on": "photoreceptor", "job": "UV rhodopsin"},
    {"symbol": "Rh5", "sits_on": "photoreceptor", "job": "blue rhodopsin"},
    {"symbol": "Rh6", "sits_on": "photoreceptor", "job": "green rhodopsin"},
    {"symbol": "Shab", "sits_on": "spike K", "job": "Shab K channel"},
    {"symbol": "Shal", "sits_on": "spike K", "job": "Shal K channel"},
    {"symbol": "sei", "sits_on": "spike K", "job": "seizure K channel"},
    {"symbol": "Mlc2", "sits_on": "muscle effector (not CNS)", "job": "myosin light chain 2"},
    {"symbol": "EAAT2", "sits_on": "glutamate", "job": "EAAT2"},
    {"symbol": "nAChRalpha3", "sits_on": "ACh", "job": "already seated — skip if dup"},
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
    sl = sym.lower().replace("-", "")
    exact = []
    for h in hits:
        names = []
        for g in h.get("genes") or []:
            names.append(str((g.get("geneName") or {}).get("value") or ""))
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
    syns = []
    for g in u.get("genes") or []:
        for a in g.get("synonyms") or []:
            if a.get("value"):
                syns.append(str(a["value"]))
    fb = [
        str(x.get("id"))
        for x in (u.get("uniProtKBCrossReferences") or [])
        if x.get("database") == "FlyBase" and x.get("id")
    ]
    return {
        "ok": True,
        "flybase_symbol": gn,
        "synonyms": syns,
        "uniprot": u.get("primaryAccession"),
        "aa": int((u.get("sequence") or {}).get("length") or 0),
        "flybase": fb[0] if fb else "",
        "reviewed": u.get("entryType") == "UniProtKB reviewed (Swiss-Prot)",
    }


def harvest() -> list[dict]:
    rows = []
    seen = set()
    for fname, key in SOURCES:
        p = ROOT / "data" / fname
        if not p.is_file():
            continue
        d = json.loads(p.read_text(encoding="utf-8"))
        for g in d.get(key) or []:
            sym = g.get("symbol") or ""
            if not sym or sym in seen:
                continue
            seen.add(sym)
            u = g.get("uniprot_live") or {}
            live = str(u.get("live_gene") or u.get("gene") or "")
            rows.append(
                {
                    "working_symbol": sym,
                    "flybase_symbol": live or sym,
                    "uniprot": u.get("uniprot") or g.get("uniprot") or "",
                    "flybase": u.get("flybase") or g.get("flybase") or "",
                    "sits_on": g.get("sits_on") or g.get("job") or "",
                    "source": fname,
                    "rename": live.lower() != sym.lower() if live else False,
                }
            )
    return rows


def crumbs() -> dict:
    skip = {"nAChRalpha3"}
    rows = []
    fail = []
    for g in CRUMBS:
        if g["symbol"] in skip:
            continue
        print(f"  crumb {g['symbol']}", flush=True)
        u = uniprot_gene(g["symbol"])
        ok = bool(u.get("ok") and u.get("uniprot"))
        if not ok:
            fail.append(g["symbol"])
        rows.append({**g, "uniprot_live": u, "ok": ok, "flybase_symbol": u.get("flybase_symbol") or g["symbol"]})
        print(f"    {g['symbol']} → {u.get('flybase_symbol')} {u.get('uniprot')} ok={ok}")
    return {"n": len(rows), "n_ok": sum(1 for r in rows if r["ok"]), "fail": fail, "genes": rows}


def main() -> int:
    import argparse

    ap = argparse.ArgumentParser()
    ap.add_argument("--crumbs", action="store_true")
    args = ap.parse_args()
    names = harvest()
    renames = [r for r in names if r.get("rename")]
    crumb = crumbs() if args.crumbs else None
    if crumb:
        CRUMB_OUT.write_text(json.dumps({"adventure": 1, "pin": "AEB2AD", **crumb, "overall_ok": not crumb["fail"]}, indent=2), encoding="utf-8")
        for g in crumb["genes"]:
            if g["ok"] and g["symbol"] not in {x["working_symbol"] for x in names}:
                names.append(
                    {
                        "working_symbol": g["symbol"],
                        "flybase_symbol": g.get("flybase_symbol"),
                        "uniprot": (g.get("uniprot_live") or {}).get("uniprot"),
                        "flybase": (g.get("uniprot_live") or {}).get("flybase"),
                        "sits_on": g.get("sits_on"),
                        "source": "genetic_crumbs",
                        "rename": g.get("flybase_symbol", "").lower() != g["symbol"].lower(),
                    }
                )
    doc = {
        "adventure": 1,
        "pin": "AEB2AD",
        "free_parameters": 0,
        "n": len(names),
        "n_rename": len([r for r in names if r.get("rename")]),
        "renames": [r for r in names if r.get("rename")],
        "genes": sorted(names, key=lambda r: r["working_symbol"].lower()),
        "note": (
            "working_symbol = label used in this pack. flybase_symbol = UniProt gene name. "
            "Use flybase_symbol in scientific text. tan→t, ebony→e, VGlut→VGlut1, painless→pain."
        ),
        "overall_ok": True,
    }
    OUT.write_text(json.dumps(doc, indent=2), encoding="utf-8")
    print(f"  blueprint n={doc['n']} renames={doc['n_rename']}")
    for r in doc["renames"]:
        print(f"    {r['working_symbol']} → {r['flybase_symbol']}  {r['uniprot']}")
    if crumb:
        print(f"  crumbs {crumb['n_ok']}/{crumb['n']} fail={crumb['fail']}")
    print(f"  wrote {OUT}")
    return 0 if (not crumb or not crumb["fail"]) else 1


if __name__ == "__main__":
    raise SystemExit(main())
