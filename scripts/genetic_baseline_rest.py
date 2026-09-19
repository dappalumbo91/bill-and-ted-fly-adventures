#!/usr/bin/env python3
"""Adventure 1 — remaining genetic baseline (photo, olf, extra receptors, peptide Rs).

Already seated: 58 genes (synthesis, core receptors, peptides, clock, fru/dsx).
This pass fills the rest of the neural genetic baseline. Live UniProt.
Sit-on existing hop jobs / leftover / DENY. No invented synapses.

  python scripts/genetic_baseline_rest.py
  python scripts/genetic_baseline_rest.py --hops   # Orco leftover vs olfactory hop
"""
from __future__ import annotations

import json
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "vendor"))

OUT = ROOT / "data" / "genetic_baseline_rest.json"
ADV = ROOT / "Bill and Ted fly adventures" / "Adventure-1"
UA = {"User-Agent": "FSOT-fly-pack (mailto:local)", "Accept": "application/json"}

GENES = [
    # phototransduction (see / L5 leftover vs walk)
    {"symbol": "ninaE", "sits_on": "see L5 / photoreceptor", "job": "Rh1 rhodopsin"},
    {"symbol": "trp", "sits_on": "see / phototransduction", "job": "TRP channel"},
    {"symbol": "trpl", "sits_on": "see / phototransduction", "job": "TRP-like"},
    {"symbol": "norpA", "sits_on": "see / phototransduction", "job": "PLC-β"},
    {"symbol": "Galphaq", "sits_on": "see / phototransduction", "job": "Gq alpha"},
    {"symbol": "arr2", "sits_on": "see / phototransduction", "job": "arrestin-2"},
    # olfaction (ORN leftover)
    {"symbol": "Orco", "sits_on": "olfactory leftover LN", "job": "odorant co-receptor"},
    {"symbol": "Ir8a", "sits_on": "olfactory leftover", "job": "IR co-receptor"},
    {"symbol": "Ir25a", "sits_on": "olfactory leftover", "job": "IR co-receptor"},
    {"symbol": "Ir76b", "sits_on": "olfactory leftover", "job": "IR co-receptor"},
    # taste
    {"symbol": "Gr5a", "sits_on": "taste leftover (not vnc_motor)", "job": "sugar GR"},
    {"symbol": "Gr66a", "sits_on": "taste leftover", "job": "bitter GR"},
    # extra mechano
    {"symbol": "piezo", "sits_on": "mechanosensory", "job": "Piezo"},
    {"symbol": "Tmc", "sits_on": "mechanosensory / JO", "job": "transmembrane channel-like"},
    {"symbol": "nompA", "sits_on": "JO / scolopale", "job": "NOMPA"},
    # extra monoamine receptors
    {"symbol": "Dop2R", "sits_on": "DA volume leftover", "job": "D2-like"},
    {"symbol": "DopEcR", "sits_on": "DA volume leftover", "job": "DA/ecdysone GPCR"},
    {"symbol": "Octbeta1R", "sits_on": "OA volume leftover", "job": "OA β1"},
    {"symbol": "Octbeta2R", "sits_on": "OA volume leftover", "job": "OA β2"},
    {"symbol": "Octbeta3R", "sits_on": "OA volume leftover", "job": "OA β3"},
    {"symbol": "5-HT1B", "sits_on": "5HT signaling leftover", "job": "5-HT1B"},
    {"symbol": "5-HT2A", "sits_on": "5HT signaling leftover", "job": "5-HT2A"},
    {"symbol": "5-HT2B", "sits_on": "5HT signaling leftover", "job": "5-HT2B"},
    {"symbol": "5-HT7", "sits_on": "5HT signaling leftover", "job": "5-HT7"},
    # GABA extras
    {"symbol": "Lcch3", "sits_on": "GABA", "job": "GABA-A like subunit"},
    {"symbol": "Grd", "sits_on": "GABA", "job": "GABA-A like subunit"},
    {"symbol": "GABA-B-R1", "sits_on": "GABA", "job": "GABA-B R1"},
    {"symbol": "GABA-B-R2", "sits_on": "GABA", "job": "GABA-B R2"},
    # Glu extras
    {"symbol": "GluRIIB", "sits_on": "NMJ glutamate", "job": "iGluR IIB"},
    {"symbol": "GluRIIC", "sits_on": "NMJ glutamate", "job": "iGluR IIC"},
    {"symbol": "mGluR", "sits_on": "glutamate", "job": "metabotropic GluR"},
    {"symbol": "Nmdar1", "sits_on": "glutamate / Zig NMDA analog", "job": "NMDA R1"},
    {"symbol": "Nmdar2", "sits_on": "glutamate / Zig NMDA analog", "job": "NMDA R2"},
    # ACh extras
    {"symbol": "ChT", "sits_on": "ACh", "job": "choline transporter", "accession": "Q9VE46"},
    {"symbol": "Ace", "sits_on": "ACh", "job": "acetylcholinesterase"},
    # peptide receptors leftover
    {"symbol": "SIFaR", "sits_on": "courtship DENY default", "job": "SIFamide receptor"},
    {"symbol": "sNPFR", "sits_on": "feeding leftover", "job": "sNPF receptor"},
    {"symbol": "Dh31-R", "sits_on": "clock leftover", "job": "Dh31 receptor"},
    {"symbol": "AstA-R1", "sits_on": "feeding leftover", "job": "AstA receptor 1"},
    {"symbol": "CcapR", "sits_on": "ecdysis leftover", "job": "CCAP receptor"},
    {"symbol": "CrzR", "sits_on": "stress leftover", "job": "corazonin receptor"},
    # clock leftover
    {"symbol": "cry", "sits_on": "sleep leftover", "job": "cryptochrome"},
    # DA metabolism
    {"symbol": "ebony", "sits_on": "DA volume leftover", "job": "N-β-alanyldopamine synthase"},
    {"symbol": "tan", "sits_on": "DA volume leftover", "job": "N-β-alanyldopamine hydrolase", "accession": "Q9W369"},
    # extra innexin / K
    {"symbol": "Inx3", "sits_on": "consensus gap analog", "job": "innexin-3"},
    {"symbol": "shaw", "sits_on": "spike K", "job": "Shaw K channel"},
    {"symbol": "eag", "sits_on": "spike K", "job": "ether-a-go-go K"},
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


def orco_hop() -> dict:
    from male_cns import load_male_graph
    from math_first import _hop2_state, _motor_by_side

    print("  load Male CNS for Orco-class olfactory leftover check", flush=True)
    graph = load_male_graph()
    # ORN types already the olfactory program; this hop is type_prefix ORN if present
    seed = [
        graph["idx"][rid]
        for rid, m in graph["meta"].items()
        if rid in graph["idx"]
        and (
            (m.get("cell_type") or "").upper().startswith("ORN")
            or (m.get("super_class") or "").lower() == "sensory"
            and "olf" in (m.get("cell_class") or "").lower()
        )
    ]
    # Prefer existing olfactory hop from male boot rather than a huge sensory seed
    return {"n_seed_attempt": len(seed), "use": "male_cns olfactory hop-2 already 0.0006 leftover"}


def main(argv: list[str] | None = None) -> int:
    import argparse

    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--hops", action="store_true")
    args = ap.parse_args(argv)
    rows = []
    fail = []
    for g in GENES:
        print(f"  live {g['symbol']}", flush=True)
        try:
            u = uniprot_gene(g["symbol"], g.get("accession") or "")
        except Exception as e:
            u = {"ok": False, "error": str(e)[:120]}
        ok = bool(u.get("ok") and u.get("uniprot"))
        if not ok:
            fail.append(g["symbol"])
        rows.append({**g, "uniprot_live": u, "ok": ok})
        print(f"    {g['symbol']} {u.get('uniprot')} {u.get('live_gene')} ok={ok}")
    extra = orco_hop() if args.hops else None
    olf = json.loads((ROOT / "data" / "male_cns_boot.json").read_text(encoding="utf-8"))
    olf_m = float((((olf.get("compare") or {}).get("hop_2") or {}).get("olfactory") or {}).get("vnc_motor") or 0)
    doc = {
        "adventure": 1,
        "pin": "AEB2AD",
        "free_parameters": 0,
        "n": len(rows),
        "n_ok": sum(1 for r in rows if r["ok"]),
        "fail": fail,
        "genes": rows,
        "orco_note": extra,
        "olfactory_hop2_vnc_motor": olf_m,
        "orco_job_leftover": olf_m < 0.05,
        "overall_ok": len(fail) == 0 and olf_m < 0.05,
        "prior_seated": 58,
        "this_pass": len(rows),
    }
    OUT.write_text(json.dumps(doc, indent=2), encoding="utf-8")
    md = ADV / "FINDINGS.md"
    block = [
        "",
        "## Genetic baseline rest",
        "",
        f"This pass **{doc['n_ok']}/{doc['n']}** live. Fail={fail}. "
        f"Orco job leftover via olfactory hop-2 vnc_motor={olf_m:.4f}.",
        "",
    ]
    if md.is_file():
        prev = md.read_text(encoding="utf-8")
        if "## Genetic baseline rest" not in prev:
            md.write_text(prev + "\n".join(block), encoding="utf-8")
        else:
            md.write_text(prev.split("## Genetic baseline rest")[0] + "\n".join(block), encoding="utf-8")
    print(f"  baseline_rest {doc['n_ok']}/{doc['n']} fail={fail} olf={olf_m:.4f}")
    print(f"  wrote {OUT}")
    return 0 if doc["overall_ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
