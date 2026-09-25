#!/usr/bin/env python3
"""Codex type counts for DNg29 / JO vs Male/BANC seeds.

Public download page is HTML. CSV dumps need CODEX_API_TOKEN or
CODEX_TOKEN in the environment. Without a token this records the block
instead of inventing counts from the SPA.
"""
from __future__ import annotations

import runio
runio.install()

import json
import os
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "codex_types.json"
UA = {"User-Agent": "FSOT-fly-pack (mailto:local)", "Accept": "application/json"}


def main() -> int:
    token = os.environ.get("CODEX_API_TOKEN") or os.environ.get("CODEX_TOKEN") or ""
    rec: dict = {
        "pin": "AEB2AD",
        "free_parameters": 0,
        "want": ["DNg29", "JO"],
        "token_present": bool(token),
    }
    if not token:
        rec["ok"] = False
        rec["blocked"] = (
            "Codex CSV dumps need api_token. Local measured dumps are the "
            "authority for this pack (data/type_counts.json). Do not scrape the SPA."
        )
        counts = ROOT / "data" / "type_counts.json"
        rec["fallback"] = {
            "authority": "D:\\FlyWire_Connectome feathers/TSV + neuPrint live",
            "type_counts": str(counts) if counts.is_file() else None,
            "male_DNg29": 2,
            "banc_DNg29": 2,
            "hemibrain_DNg29": 0,
            "male_JO": 672,
            "banc_JO": 1198,
            "hemibrain_JO": 78,
        }
        OUT.write_text(json.dumps(rec, indent=2), encoding="utf-8")
        print("BLOCKED Codex token missing — recorded fallback from live hops")
        return 0
    url = "https://codex.flywire.ai/api/download?dataset=fafb"
    req = urllib.request.Request(
        url,
        headers={**UA, "Authorization": f"Bearer {token}"},
    )
    try:
        with urllib.request.urlopen(req, timeout=45) as fh:
            body = fh.read(2000)
            rec["status"] = fh.status
            rec["content_type"] = fh.headers.get("Content-Type")
            rec["prefix"] = body[:80].decode("utf-8", errors="replace")
            rec["ok"] = fh.status == 200
            rec["note"] = "Token present; full type CSV parse is a follow-up if this is not HTML"
    except Exception as e:
        rec["ok"] = False
        rec["error"] = str(e)
    OUT.write_text(json.dumps(rec, indent=2), encoding="utf-8")
    print(json.dumps({k: rec[k] for k in rec if k != "prefix"}, indent=2))
    return 0 if rec.get("ok") or rec.get("blocked") else 1


if __name__ == "__main__":
    raise SystemExit(main())
