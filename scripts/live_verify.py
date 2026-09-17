#!/usr/bin/env python3
"""Live public APIs against this fly pack.

  python scripts/live_verify.py

Does not need a Codex download token. Allen Brain Atlas is mouse — recorded as such.
"""
from __future__ import annotations

import json
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "live_verify.json"
UA = {"User-Agent": "FSOT-fly-pack (mailto:local)", "Accept": "application/json"}


def get(url: str, timeout: int = 45) -> tuple[int, bytes]:
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=timeout) as fh:
        return fh.status, fh.read()


def rec(name: str, ok: bool, detail: dict) -> dict:
    print(f"{'OK   ' if ok else 'FAIL '} {name}")
    return {"name": name, "ok": ok, **detail}


def main() -> int:
    rows = []

    # UniProt nompC
    try:
        st, raw = get("https://rest.uniprot.org/uniprotkb/Q7KIQ2.json")
        u = json.loads(raw.decode())
        gn = ""
        genes = u.get("genes") or []
        if genes:
            gn = str((genes[0].get("geneName") or {}).get("value") or "")
        ok = st == 200 and u.get("primaryAccession") == "Q7KIQ2" and gn.lower() == "nompc"
        rows.append(rec("uniprot_nompC", ok, {"status": st, "gene": gn, "accession": u.get("primaryAccession")}))
    except Exception as e:
        rows.append(rec("uniprot_nompC", False, {"error": str(e)}))

    # Ensembl / FlyBase id for nompC
    try:
        st, raw = get(
            "https://rest.ensembl.org/lookup/symbol/drosophila_melanogaster/nompC?content-type=application/json"
        )
        e = json.loads(raw.decode())
        ok = st == 200 and e.get("display_name") == "nompC" and str(e.get("id") or "").startswith("FBgn")
        rows.append(rec("ensembl_nompC", ok, {"status": st, "id": e.get("id"), "display_name": e.get("display_name")}))
    except Exception as e:
        rows.append(rec("ensembl_nompC", False, {"error": str(e)}))

    # Janelia neuPrint hemibrain (independent fly EM graph)
    try:
        st, raw = get("https://neuprint.janelia.org/api/version")
        ver = json.loads(raw.decode())
        st2, raw2 = get("https://neuprint.janelia.org/api/dbmeta/datasets")
        dsets = json.loads(raw2.decode())
        has = any(str(k).startswith("hemibrain") for k in dsets)
        ok = st == 200 and has
        rows.append(
            rec(
                "neuprint_hemibrain",
                ok,
                {"status": st, "version": ver, "has_hemibrain": has, "n_datasets": len(dsets)},
            )
        )
    except Exception as e:
        rows.append(rec("neuprint_hemibrain", False, {"error": str(e)}))

    # Codex listing (HTML app; token needed for CSV dumps)
    try:
        req = urllib.request.Request(
            "https://codex.flywire.ai/api/download?dataset=fafb",
            headers={"User-Agent": UA["User-Agent"]},
        )
        with urllib.request.urlopen(req, timeout=45) as fh:
            html = fh.read(8000).decode("utf-8", errors="replace")
            st = fh.status
        has_fafb = "FAFB" in html or "fafb" in html.lower()
        has_mcns = "MCNS" in html or "Male" in html
        rows.append(
            rec(
                "codex_download_page",
                st == 200 and has_fafb,
                {"status": st, "has_fafb": has_fafb, "has_mcns": has_mcns, "note": "CSV dumps need Codex api_token"},
            )
        )
    except Exception as e:
        rows.append(rec("codex_download_page", False, {"error": str(e)}))

    # Allen Brain Atlas — mouse, not fly
    try:
        st, raw = get(
            "https://api.brain-map.org/api/v2/data/query.json?criteria=model::Atlas&num_rows=1"
        )
        a = json.loads(raw.decode())
        msg = (a.get("msg") or [{}])[0]
        desc = str(msg.get("description") or "")
        ok = bool(a.get("success")) and st == 200
        rows.append(
            rec(
                "allen_brain_atlas",
                ok,
                {
                    "status": st,
                    "success": a.get("success"),
                    "sample": desc[:80],
                    "note": "Allen Atlas is mouse/human. Fly synapses are FlyWire/CAVE, not this atlas.",
                },
            )
        )
    except Exception as e:
        rows.append(rec("allen_brain_atlas", False, {"error": str(e)}))

    # GitHub spine repos
    for repo in (
        "FSOT-Genetics",
        "FSOT-2.1-Lean",
        "FSOT-2.1-Neural",
        "fsot-neuron-zig",
    ):
        try:
            st, raw = get(f"https://api.github.com/repos/dappalumbo91/{repo}")
            g = json.loads(raw.decode())
            ok = st == 200 and g.get("name") == repo
            rows.append(rec(f"github_{repo}", ok, {"status": st, "html_url": g.get("html_url")}))
        except Exception as e:
            rows.append(rec(f"github_{repo}", False, {"error": str(e)}))

    failed = [r for r in rows if not r["ok"]]
    doc = {
        "pin": "AEB2AD",
        "free_parameters": 0,
        "n": len(rows),
        "fail": len(failed),
        "overall_ok": len(failed) == 0,
        "checks": rows,
    }
    OUT.write_text(json.dumps(doc, indent=2), encoding="utf-8")
    print(f"  wrote {OUT}  fail={len(failed)}")
    return 0 if doc["overall_ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
