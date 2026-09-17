#!/usr/bin/env python3
"""Local measured type counts for DNg29 / JO / KC.

Codex CSV dumps need an api_token. These counts come from the same
feathers / TSV already on D:\\FlyWire_Connectome — the authority dumps,
not the web UI.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FLY = Path(r"D:\FlyWire_Connectome")
OUT = ROOT / "data" / "type_counts.json"


def _lower(s) -> str:
    return str(s or "").strip().lower()


def male_counts() -> dict:
    import pandas as pd

    ann = pd.read_feather(FLY / "male_cns" / "body-annotations-male-cns-v1.0-minconf-0.5.feather")
    traced = ann[ann["status"] == "Traced"]
    types = traced["type"].fillna("").astype(str)
    return {
        "source": str(FLY / "male_cns" / "body-annotations-male-cns-v1.0-minconf-0.5.feather"),
        "n_traced": int(len(traced)),
        "n_annotated": int(len(ann)),
        "DNg29": int((types == "DNg29").sum()),
        "JO_type_prefix": int(types.str.startswith("JO").sum()),
        "jo_lower_prefix": int(types.str.lower().str.startswith("jo").sum()),
    }


def banc_counts() -> dict:
    import pandas as pd

    meta = pd.read_feather(FLY / "banc" / "banc_888_meta.feather")
    types = meta["cell_type"].fillna("").astype(str) if "cell_type" in meta.columns else meta.get("type")
    if types is None:
        for col in meta.columns:
            if "type" in col.lower():
                types = meta[col].fillna("").astype(str)
                break
    types = types.fillna("").astype(str)
    return {
        "source": str(FLY / "banc" / "banc_888_meta.feather"),
        "n": int(len(meta)),
        "type_column": types.name if hasattr(types, "name") else "cell_type",
        "DNg29": int((types == "DNg29").sum()),
        "JO_type_prefix": int(types.str.startswith("JO").sum()),
        "jo_lower_prefix": int(types.str.lower().str.startswith("jo").sum()),
    }


def flywire_counts() -> dict:
    import pandas as pd

    path = FLY / "Supplemental_file1_neuron_annotations.tsv"
    df = pd.read_csv(path, sep="\t", low_memory=False)
    col = "cell_type" if "cell_type" in df.columns else "type"
    types = df[col].fillna("").astype(str)
    return {
        "source": str(path),
        "n": int(len(df)),
        "DNg29": int((types == "DNg29").sum()),
        "JO_type_prefix": int(types.str.startswith("JO").sum()),
        "jo_lower_prefix": int(types.str.lower().str.startswith("jo").sum()),
    }


def hemibrain_counts() -> dict:
    import pandas as pd

    path = FLY / "hemibrain" / "neuprint_v1_2_1_typed_neurons.feather"
    if not path.is_file():
        return {"source": str(path), "missing": True}
    df = pd.read_feather(path)
    types = df["type"].fillna("").astype(str)
    return {
        "source": str(path),
        "n_typed": int(len(df)),
        "DNg29": int((types == "DNg29").sum()),
        "JO_type_prefix": int(types.str.startswith("JO").sum()),
        "KC_type_prefix": int(types.str.startswith("KC").sum()),
        "ORN_type_prefix": int(types.str.startswith("ORN").sum()),
        "Giant_Fiber": int((types == "Giant Fiber").sum()),
    }


def neuprint_hemibrain_live() -> dict:
    import urllib.request

    url = "https://neuprint.janelia.org/api/custom/custom"
    q = (
        "MATCH (n:Neuron) WHERE n.type IS NOT NULL "
        "WITH n.type AS t "
        "RETURN "
        "sum(CASE WHEN t = 'DNg29' THEN 1 ELSE 0 END) AS DNg29, "
        "sum(CASE WHEN t STARTS WITH 'JO' THEN 1 ELSE 0 END) AS JO, "
        "sum(CASE WHEN t STARTS WITH 'KC' THEN 1 ELSE 0 END) AS KC, "
        "sum(CASE WHEN t STARTS WITH 'ORN' THEN 1 ELSE 0 END) AS ORN, "
        "sum(CASE WHEN t = 'Giant Fiber' THEN 1 ELSE 0 END) AS GF, "
        "count(*) AS typed"
    )
    body = json.dumps({"cypher": q, "dataset": "hemibrain:v1.2.1"}).encode()
    req = urllib.request.Request(
        url,
        data=body,
        headers={
            "User-Agent": "FSOT-fly-pack",
            "Accept": "application/json",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as fh:
            raw = json.loads(fh.read().decode())
        cols = raw.get("columns") or []
        row = (raw.get("data") or [[]])[0]
        return {"ok": True, "counts": dict(zip(cols, row))}
    except Exception as e:
        return {"ok": False, "error": str(e)}


def main() -> int:
    doc = {
        "pin": "AEB2AD",
        "free_parameters": 0,
        "rule": "Counts from measured dumps on D:. Codex api_token not used.",
        "male_cns": male_counts(),
        "banc": banc_counts(),
        "flywire_annotations": flywire_counts(),
        "hemibrain_cache": hemibrain_counts(),
        "neuprint_hemibrain_live": neuprint_hemibrain_live(),
    }
    OUT.write_text(json.dumps(doc, indent=2), encoding="utf-8")
    print(json.dumps(doc, indent=2))
    print(f"  wrote {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
