#!/usr/bin/env python3
"""Bill (baseline residual net) vs TED (numbered experiments).

Bill is the frozen FSOT fly organism. TED-n tries one change.
If TED matches empirical function and Lean gates, it promotes to Bill-k.

  python scripts/bill_ted.py freeze    # snapshot Bill-0
  python scripts/bill_ted.py ted-1     # record predicted-side hops vs Bill
  python scripts/bill_ted.py ledger
"""
from __future__ import annotations

import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BT = ROOT / "Bill and Ted fly adventures"
LEDGER = BT / "ledger.json"
PIN = ROOT / "vendor" / "fsot_compute.py"


def sha256(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest().upper()


def freeze_paths() -> list[Path]:
    paths = [PIN]
    for p in sorted((ROOT / "data").glob("*.json")):
        if p.name.startswith("_"):
            continue
        paths.append(p)
    for p in [
        ROOT / "MATH.md",
        ROOT / "docs" / "MECHANICS.md",
        ROOT / "docs" / "LEFTOVER.md",
        ROOT / "RUNNING.md",
        BT / "BILL_TED.md",
        BT / "TED-1" / "EXPERIMENT.json",
    ]:
        if p.is_file():
            paths.append(p)
    return paths


def freeze(bill_id: str) -> dict:
    files = []
    h = hashlib.sha256()
    for p in freeze_paths():
        digest = sha256(p)
        rel = str(p.relative_to(ROOT)).replace("\\", "/")
        files.append({"path": rel, "sha256": digest, "bytes": p.stat().st_size})
        h.update(digest.encode())
        h.update(rel.encode())
    man = {
        "id": bill_id,
        "role": "bill",
        "pin": "AEB2AD",
        "free_parameters": 0,
        "frozen_at": datetime.now(timezone.utc).isoformat(),
        "tree_sha256": h.hexdigest().upper(),
        "n_files": len(files),
        "files": files,
        "note": "Residual organism snapshot. Not trained weights. Synapse feathers stay on D:.",
    }
    dest = BT / bill_id
    dest.mkdir(parents=True, exist_ok=True)
    (dest / "MANIFEST.json").write_text(json.dumps(man, indent=2), encoding="utf-8")
    return man


def load_ledger() -> dict:
    if LEDGER.is_file():
        return json.loads(LEDGER.read_text(encoding="utf-8"))
    return {
        "pin": "AEB2AD",
        "free_parameters": 0,
        "bills": [],
        "teds": [],
        "promotions": [],
    }


def ted1() -> dict:
    ps = json.loads((ROOT / "data" / "predicted_side_hops.json").read_text(encoding="utf-8"))
    mg = json.loads((ROOT / "data" / "leftover_margin.json").read_text(encoding="utf-8"))
    by = {p["name"]: p for p in ps.get("programs") or []}
    pL = by.get("predicted_L") or {}
    pR = by.get("predicted_R") or {}
    win = bool(ps.get("ipsi_pair") and ps.get("overall_ok") and mg.get("overall_ok"))
    exp = {
        "id": "TED-1",
        "role": "ted",
        "change": "9 predicted VNC sides as hop observers (not EM)",
        "vs_bill": "Bill-0 labeled vnc_sensory L/R ipsi law",
        "ipsi_pair": ps.get("ipsi_pair"),
        "predicted_L_ipsi": (pL.get("hop2") or {}).get("ipsi_bias"),
        "predicted_R_ipsi": (pR.get("hop2") or {}).get("ipsi_bias"),
        "lean_margin_green": mg.get("overall_ok"),
        "promotes": win,
        "promote_to": "Bill-1" if win else None,
        "why": (
            "Same ipsilateral motor law as Bill-0 labeled VNC. "
            "R overlay −0.84; L sign +; leftover-five ~0. Labels remain predicted."
        ),
    }
    dest = BT / "TED-1"
    dest.mkdir(parents=True, exist_ok=True)
    (dest / "EXPERIMENT.json").write_text(json.dumps(exp, indent=2), encoding="utf-8")
    return exp


def main(argv: list[str] | None = None) -> int:
    argv = argv if argv is not None else sys.argv[1:]
    cmd = (argv[0] if argv else "ledger").lower()
    BT.mkdir(parents=True, exist_ok=True)
    led = load_ledger()
    if cmd == "freeze":
        bill_id = argv[1] if len(argv) > 1 else "Bill-0"
        man = freeze(bill_id)
        if bill_id not in led["bills"]:
            led["bills"].append(bill_id)
        led["current_bill"] = bill_id
        led["last_tree_sha256"] = man["tree_sha256"]
        print(f"  froze {bill_id} tree={man['tree_sha256'][:12]} n={man['n_files']}")
    elif cmd == "ted-1":
        exp = ted1()
        if "TED-1" not in led["teds"]:
            led["teds"].append("TED-1")
        print(f"  TED-1 promotes={exp['promotes']} → {exp.get('promote_to')}")
        if exp["promotes"]:
            man = freeze("Bill-1")
            if "Bill-1" not in led["bills"]:
                led["bills"].append("Bill-1")
            led["promotions"].append(
                {"from": "TED-1", "to": "Bill-1", "tree": man["tree_sha256"]}
            )
            led["current_bill"] = "Bill-1"
            print(f"  promoted Bill-1 tree={man['tree_sha256'][:12]}")
    elif cmd == "ledger":
        print(json.dumps({k: led[k] for k in led if k != "files"}, indent=2)[:2000])
    else:
        print("usage: freeze [Bill-0] | ted-1 | ledger")
        return 1
    LEDGER.write_text(json.dumps(led, indent=2), encoding="utf-8")
    print(f"  wrote {LEDGER}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
