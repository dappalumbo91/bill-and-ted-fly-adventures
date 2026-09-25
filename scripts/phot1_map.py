#!/usr/bin/env python3
"""PHOT1 measured map — correct accession, measured LOV crystals.

The plant panel stamped Q2V2M9 as PHOT1. Live UniProt Q2V2M9 is human
FHOD3 (formin), not Arabidopsis phototropin. Real PHOT1 is O48963 with
two measured LOV-domain crystals on the same protein.

Not a full-chain product (kinase/linker leftover). Not bulk MDS.
Domain maps are Biochemistry observations.

  python scripts/phot1_map.py
"""
from __future__ import annotations

import runio
runio.install()

import json
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "phot1_map.json"
UA = {"User-Agent": "FSOT-fly-pack (mailto:local)", "Accept": "application/json"}
WRONG = "Q2V2M9"
RIGHT = "O48963"
PHI = 1.618033988749895
LEFTOVER = 1.0 / (PHI * PHI)


def get(url: str) -> dict:
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=60) as fh:
        return json.loads(fh.read().decode())


def main() -> int:
    wrong = get(f"https://rest.uniprot.org/uniprotkb/{WRONG}.json")
    right = get(f"https://rest.uniprot.org/uniprotkb/{RIGHT}.json")
    wgn = str(((wrong.get("genes") or [{}])[0].get("geneName") or {}).get("value") or "")
    rgn = str(((right.get("genes") or [{}])[0].get("geneName") or {}).get("value") or "")
    worg = (wrong.get("organism") or {}).get("scientificName")
    rorg = (right.get("organism") or {}).get("scientificName")
    n = int((right.get("sequence") or {}).get("length") or 0)
    pdbs = []
    covered = 0
    for x in right.get("uniProtKBCrossReferences") or []:
        if x.get("database") != "PDB":
            continue
        props = {p.get("key"): p.get("value") for p in (x.get("properties") or [])}
        chains = str(props.get("Chains") or "")
        # e.g. A/B=180-308
        span = 0
        if "=" in chains and "-" in chains.split("=")[-1]:
            a, b = chains.split("=")[-1].split("-")[:2]
            try:
                lo, hi = int(a), int(b)
                span = max(0, hi - lo + 1)
            except ValueError:
                span = 0
        covered += span
        pdbs.append(
            {
                "pdb": x.get("id"),
                "method": props.get("Method"),
                "resolution_A": props.get("Resolution"),
                "chains": chains,
                "n_res": span,
            }
        )
    cov = covered / n if n else 0.0
    leftover = 1.0 - cov
    doc = {
        "pin": "AEB2AD",
        "free_parameters": 0,
        "mislabel": {
            "stamped_as": "PHOT1",
            "accession": WRONG,
            "live_gene": wgn,
            "live_organism": worg,
            "note": "Human formin FHOD3 — not Arabidopsis phototropin.",
        },
        "phot1": {
            "accession": RIGHT,
            "gene": rgn,
            "organism": rorg,
            "length": n,
            "uniprot_reviewed": right.get("entryType") == "UniProtKB reviewed (Swiss-Prot)",
        },
        "measured_domains": pdbs,
        "domain_residues": covered,
        "template_coverage": cov,
        "leftover": leftover,
        "leftover_floor_1_over_phi2": LEFTOVER,
        "close_homolog": True,
        "structure_mode": "measured_domains",
        "full_chain_product": leftover <= LEFTOVER,
        "rule": (
            "Same-protein crystals are measured maps. LOV1 2Z6C and LOV2 4HHD "
            "are Biochemistry observations. Kinase/linker leftover stays unmapped. "
            "Not no_measured_map. Not bulk MDS."
        ),
    }
    OUT.write_text(json.dumps(doc, indent=2), encoding="utf-8")
    print(
        f"PHOT1 {RIGHT} {rgn} {rorg} n={n}  "
        f"domains={len(pdbs)} cov={cov:.3f} leftover={leftover:.3f} "
        f"full_chain={doc['full_chain_product']}"
    )
    print(f"  mislabel {WRONG} is {wgn} ({worg})")
    print(f"  wrote {OUT}")
    return 0 if rgn.upper() == "PHOT1" and pdbs else 1


if __name__ == "__main__":
    raise SystemExit(main())
