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
        BT / "TED-2" / "EXPERIMENT.json",
        BT / "TED-3" / "EXPERIMENT.json",
        BT / "TED-4" / "EXPERIMENT.json",
        BT / "TED-5" / "EXPERIMENT.json",
        BT / "TED-6" / "EXPERIMENT.json",
        BT / "TED-7" / "EXPERIMENT.json",
        BT / "TED-8" / "EXPERIMENT.json",
        BT / "TED-9" / "EXPERIMENT.json",
        BT / "TED-10" / "EXPERIMENT.json",
        BT / "TED-11" / "EXPERIMENT.json",
        BT / "TED-12" / "EXPERIMENT.json",
        BT / "TED-13" / "EXPERIMENT.json",
        BT / "TED-14" / "EXPERIMENT.json",
        BT / "TED-15" / "EXPERIMENT.json",
        BT / "TED-16" / "EXPERIMENT.json",
        BT / "TED-17" / "EXPERIMENT.json",
        BT / "TED-18" / "EXPERIMENT.json",
        BT / "TED-19" / "EXPERIMENT.json",
        ROOT / "docs" / "BIO_TEACH.md",
        BT / "Adventure-1" / "BIO_TEACH.md",
        ROOT / "docs" / "LEARNING.md",
        BT / "Adventure-1" / "LEARNING.md",
        BT / "Adventure-2" / "WORD_SENSE.md",
        ROOT / "docs" / "WORD_SENSE.md",
        ROOT / "docs" / "DISCOVERIES.md",
        BT / "Adventure-2" / "UNSEEN_MATH.md",
        ROOT / "docs" / "UNSEEN_MATH.md",
        BT / "Adventure-2" / "SAFETY.md",
        ROOT / "docs" / "SAFETY_FAMILY.md",
        BT / "Adventure-2" / "LANGUAGE.md",
        ROOT / "docs" / "LANGUAGE_SPLICE.md",
        BT / "Adventure-2" / "CODING.md",
        ROOT / "docs" / "CODING_SPLICE.md",
        BT / "Adventure-2" / "LEFTOVER_INXXX.md",
        BT / "Adventure-2" / "REMAINING.md",
        ROOT / "docs" / "LEFTOVER_REMAINING.md",
        BT / "Adventure-2" / "COURSES.md",
        BT / "Adventure-2" / "ANALYSIS.md",
        BT / "Adventure-2" / "MEMORY.md",
        BT / "Adventure-2" / "GROWTH.md",
        BT / "Adventure-2" / "GROW.md",
        ROOT / "docs" / "MEMORY_LIMITS.md",
        ROOT / "docs" / "GROWTH_REGIONS.md",
        BT / "Adventure-1" / "FINDINGS.md",
        BT / "Adventure-1" / "CLOSEOUT.md",
        BT / "Adventure-2" / "FINDINGS.md",
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
    elif cmd == "ted-2":
        a1 = json.loads((ROOT / "data" / "adventure1.json").read_text(encoding="utf-8"))
        win = bool(a1.get("overall_ok") and a1.get("volume_weaker_than_vnc_walk"))
        exp = {
            "id": "TED-2",
            "role": "ted",
            "adventure": 1,
            "change": "DA/5HT/OA/histamine/GABA as hop observers (volume, not extra edges)",
            "vs_bill": "Bill-1 VNC walk 10.74",
            "volume_weaker_than_vnc_walk": a1.get("volume_weaker_than_vnc_walk"),
            "promotes": win,
            "promote_to": "Bill-2" if win else None,
            "why": (
                "Neuromod hop-2 motor weaker than VNC walk/φ. Volume leftover, not "
                "step micro-management. Gap analog remains consensus trit (no EM list)."
            ),
        }
        dest = BT / "TED-2"
        dest.mkdir(parents=True, exist_ok=True)
        (dest / "EXPERIMENT.json").write_text(json.dumps(exp, indent=2), encoding="utf-8")
        if "TED-2" not in led["teds"]:
            led["teds"].append("TED-2")
        print(f"  TED-2 promotes={win}")
        if win:
            man = freeze("Bill-2")
            if "Bill-2" not in led["bills"]:
                led["bills"].append("Bill-2")
            led["promotions"].append({"from": "TED-2", "to": "Bill-2", "tree": man["tree_sha256"]})
            led["current_bill"] = "Bill-2"
            print(f"  promoted Bill-2 tree={man['tree_sha256'][:12]}")
    elif cmd == "ted-3":
        vpath = ROOT / "data" / "adventure1_verify.json"
        if not vpath.is_file():
            print("  run python scripts/adventure1_verify.py first")
            return 1
        v = json.loads(vpath.read_text(encoding="utf-8"))
        win = bool(v.get("promotes") and v.get("overall_ok"))
        exp = {
            "id": "TED-3",
            "role": "ted",
            "adventure": 1,
            "change": "genetic blueprint through FSOT as verification of Adventure 1 (not Adventure 2)",
            "vs_bill": "Bill-2",
            "n_ok": v.get("n_ok"),
            "n": v.get("n"),
            "fail": v.get("fail") or [],
            "bill_function_ok": v.get("bill_function_ok"),
            "lean_ok": v.get("lean_ok"),
            "ted_extend_ok": v.get("ted_extend_ok"),
            "promotes": win,
            "promote_to": "Bill-3" if win else None,
            "why": v.get("why"),
        }
        dest = BT / "TED-3"
        dest.mkdir(parents=True, exist_ok=True)
        (dest / "EXPERIMENT.json").write_text(json.dumps(exp, indent=2), encoding="utf-8")
        if "TED-3" not in led["teds"]:
            led["teds"].append("TED-3")
        print(f"  TED-3 promotes={win}  {exp.get('n_ok')}/{exp.get('n')}")
        if win:
            man = freeze("Bill-3")
            if "Bill-3" not in led["bills"]:
                led["bills"].append("Bill-3")
            led["promotions"].append({"from": "TED-3", "to": "Bill-3", "tree": man["tree_sha256"]})
            led["current_bill"] = "Bill-3"
            led["last_tree_sha256"] = man["tree_sha256"]
            print(f"  promoted Bill-3 tree={man['tree_sha256'][:12]}")
        else:
            print("  Bill-2 stays")
    elif cmd == "ted-4":
        vpath = ROOT / "data" / "bill3_math_env.json"
        if not vpath.is_file():
            print("  run python scripts/bill3_math_env.py first")
            return 1
        v = json.loads(vpath.read_text(encoding="utf-8"))
        win = bool(v.get("promotes") and v.get("overall_ok"))
        exp = {
            "id": "TED-4",
            "role": "ted",
            "adventure": 2,
            "change": "Bill-3 through math environments + hop thinking traces; PhD FSOT identities",
            "vs_bill": "Bill-3",
            "n_ok": v.get("n_ok"),
            "n": v.get("n"),
            "fail": v.get("fail") or [],
            "promotes": win,
            "promote_to": "Bill-4" if win else None,
            "why": (
                "Same law. Math is trit ALU + scalar identities. Thinking is residual hops on measured W. "
                "Courtship/aggression not seeded. No new knobs."
            ),
        }
        dest = BT / "TED-4"
        dest.mkdir(parents=True, exist_ok=True)
        (dest / "EXPERIMENT.json").write_text(json.dumps(exp, indent=2), encoding="utf-8")
        if "TED-4" not in led["teds"]:
            led["teds"].append("TED-4")
        print(f"  TED-4 promotes={win}  {exp.get('n_ok')}/{exp.get('n')}")
        if win:
            man = freeze("Bill-4")
            if "Bill-4" not in led["bills"]:
                led["bills"].append("Bill-4")
            led["promotions"].append({"from": "TED-4", "to": "Bill-4", "tree": man["tree_sha256"]})
            led["current_bill"] = "Bill-4"
            led["last_tree_sha256"] = man["tree_sha256"]
            print(f"  promoted Bill-4 tree={man['tree_sha256'][:12]}")
        else:
            print("  Bill-3 stays")
    elif cmd == "ted-5":
        vpath = ROOT / "data" / "bill4_math_courses.json"
        if not vpath.is_file():
            print("  run python scripts/bill4_math_courses.py first")
            return 1
        v = json.loads(vpath.read_text(encoding="utf-8"))
        win = bool(v.get("promotes") and v.get("overall_ok"))
        exp = {
            "id": "TED-5",
            "role": "ted",
            "adventure": 2,
            "change": "conventional math courses on trit ALU (Z,Q,algebra,geometry,trig,calculus,lin alg,stats,logic)",
            "vs_bill": "Bill-4",
            "n_ok": v.get("n_ok"),
            "n": v.get("n"),
            "fail": v.get("fail") or [],
            "promotes": win,
            "promote_to": "Bill-5" if win else None,
            "why": (
                "Same substrate. Curriculum is community mathematics in conventional notation. "
                "Hops remain the thinking trace. No new knobs. Courtship not seeded."
            ),
        }
        dest = BT / "TED-5"
        dest.mkdir(parents=True, exist_ok=True)
        (dest / "EXPERIMENT.json").write_text(json.dumps(exp, indent=2), encoding="utf-8")
        if "TED-5" not in led["teds"]:
            led["teds"].append("TED-5")
        print(f"  TED-5 promotes={win}  {exp.get('n_ok')}/{exp.get('n')}")
        if win:
            man = freeze("Bill-5")
            if "Bill-5" not in led["bills"]:
                led["bills"].append("Bill-5")
            led["promotions"].append({"from": "TED-5", "to": "Bill-5", "tree": man["tree_sha256"]})
            led["current_bill"] = "Bill-5"
            led["last_tree_sha256"] = man["tree_sha256"]
            print(f"  promoted Bill-5 tree={man['tree_sha256'][:12]}")
        else:
            print("  Bill-4 stays")
    elif cmd == "ted-6":
        vpath = ROOT / "data" / "bill5_analysis.json"
        if not vpath.is_file():
            print("  run python scripts/bill5_analysis.py first")
            return 1
        v = json.loads(vpath.read_text(encoding="utf-8"))
        win = bool(v.get("promotes") and v.get("overall_ok"))
        exp = {
            "id": "TED-6",
            "role": "ted",
            "adventure": 2,
            "change": "real analysis, multivariable calculus, ODEs on the 200 Hz wing plant",
            "vs_bill": "Bill-5",
            "n_ok": v.get("n_ok"),
            "n": v.get("n"),
            "fail": v.get("fail") or [],
            "promotes": win,
            "promote_to": "Bill-6" if win else None,
            "why": (
                "IVT/MVT/Taylor/ε-δ; partials/Green/chain; ÿ+ω²y=0 when descending>1. "
                "Same substrate. No new knobs. Courtship not seeded."
            ),
        }
        dest = BT / "TED-6"
        dest.mkdir(parents=True, exist_ok=True)
        (dest / "EXPERIMENT.json").write_text(json.dumps(exp, indent=2), encoding="utf-8")
        if "TED-6" not in led["teds"]:
            led["teds"].append("TED-6")
        print(f"  TED-6 promotes={win}  {exp.get('n_ok')}/{exp.get('n')}")
        if win:
            man = freeze("Bill-6")
            if "Bill-6" not in led["bills"]:
                led["bills"].append("Bill-6")
            led["promotions"].append({"from": "TED-6", "to": "Bill-6", "tree": man["tree_sha256"]})
            led["current_bill"] = "Bill-6"
            led["last_tree_sha256"] = man["tree_sha256"]
            print(f"  promoted Bill-6 tree={man['tree_sha256'][:12]}")
        else:
            print("  Bill-5 stays")
    elif cmd == "ted-7":
        vpath = ROOT / "data" / "bill6_memory.json"
        if not vpath.is_file():
            print("  run python scripts/bill6_memory.py first")
            return 1
        v = json.loads(vpath.read_text(encoding="utf-8"))
        win = bool(v.get("promotes") and v.get("overall_ok"))
        exp = {
            "id": "TED-7",
            "role": "ted",
            "adventure": 2,
            "change": "math expansion + STM/LTM exam (encode, interfere, retrieve); memory stores on W / residual / KC",
            "vs_bill": "Bill-6",
            "n_ok": v.get("n_ok"),
            "n": v.get("n"),
            "fail": v.get("fail") or [],
            "promotes": win,
            "promote_to": "Bill-7" if win else None,
            "why": (
                "STM is the last residual/register. LTM is measured W (re-seed). "
                "KC leftover, APL hub not expanded. Interference does not edit W."
            ),
        }
        dest = BT / "TED-7"
        dest.mkdir(parents=True, exist_ok=True)
        (dest / "EXPERIMENT.json").write_text(json.dumps(exp, indent=2), encoding="utf-8")
        if "TED-7" not in led["teds"]:
            led["teds"].append("TED-7")
        print(f"  TED-7 promotes={win}  {exp.get('n_ok')}/{exp.get('n')}")
        if win:
            man = freeze("Bill-7")
            if "Bill-7" not in led["bills"]:
                led["bills"].append("Bill-7")
            led["promotions"].append({"from": "TED-7", "to": "Bill-7", "tree": man["tree_sha256"]})
            led["current_bill"] = "Bill-7"
            led["last_tree_sha256"] = man["tree_sha256"]
            print(f"  promoted Bill-7 tree={man['tree_sha256'][:12]}")
        else:
            print("  Bill-6 stays")
    elif cmd == "ted-8":
        vpath = ROOT / "data" / "bill7_memory_expand.json"
        if not vpath.is_file():
            print("  run python scripts/bill7_memory_expand.py first")
            return 1
        v = json.loads(vpath.read_text(encoding="utf-8"))
        win = bool(v.get("promotes") and v.get("overall_ok"))
        exp = {
            "id": "TED-8",
            "role": "ted",
            "adventure": 2,
            "change": "STM φ² window + LTM class index; growth map; no new axons",
            "vs_bill": "Bill-7",
            "n_ok": v.get("n_ok"),
            "n": v.get("n"),
            "fail": v.get("fail") or [],
            "promotes": win,
            "promote_to": "Bill-8" if win else None,
            "why": (
                "STM round(φ²)=3. LTM bindings on measured classes. APL/il3LN6 refused. "
                "Growth map: leftover hubs never; command bottlenecks later residual seed."
            ),
        }
        dest = BT / "TED-8"
        dest.mkdir(parents=True, exist_ok=True)
        (dest / "EXPERIMENT.json").write_text(json.dumps(exp, indent=2), encoding="utf-8")
        if "TED-8" not in led["teds"]:
            led["teds"].append("TED-8")
        print(f"  TED-8 promotes={win}  {exp.get('n_ok')}/{exp.get('n')}")
        if win:
            man = freeze("Bill-8")
            if "Bill-8" not in led["bills"]:
                led["bills"].append("Bill-8")
            led["promotions"].append({"from": "TED-8", "to": "Bill-8", "tree": man["tree_sha256"]})
            led["current_bill"] = "Bill-8"
            led["last_tree_sha256"] = man["tree_sha256"]
            print(f"  promoted Bill-8 tree={man['tree_sha256'][:12]}")
        else:
            print("  Bill-7 stays")
    elif cmd == "ted-9":
        vpath = ROOT / "data" / "bill8_grow_bottlenecks.json"
        if not vpath.is_file():
            print("  run python scripts/bill8_grow_bottlenecks.py first")
            return 1
        v = json.loads(vpath.read_text(encoding="utf-8"))
        win = bool(v.get("promotes") and v.get("overall_ok"))
        exp = {
            "id": "TED-9",
            "role": "ted",
            "adventure": 2,
            "change": "residual-seed command bottlenecks as splice-ready growth modules; not APL/il3LN6",
            "vs_bill": "Bill-8",
            "n_command_ok": v.get("n_command_ok"),
            "n_modules": v.get("n_modules"),
            "mode": v.get("mode"),
            "promotes": win,
            "promote_to": "Bill-9" if win else None,
            "why": (
                "Measured types under hop-1 stress got residual hops. "
                "New regions later splice on named jobs, 0 knobs. Not a fly-only forever constraint."
            ),
        }
        dest = BT / "TED-9"
        dest.mkdir(parents=True, exist_ok=True)
        (dest / "EXPERIMENT.json").write_text(json.dumps(exp, indent=2), encoding="utf-8")
        if "TED-9" not in led["teds"]:
            led["teds"].append("TED-9")
        print(f"  TED-9 promotes={win}  command={exp.get('n_command_ok')}/{exp.get('n_modules')} mode={exp.get('mode')}")
        if win:
            man = freeze("Bill-9")
            if "Bill-9" not in led["bills"]:
                led["bills"].append("Bill-9")
            led["promotions"].append({"from": "TED-9", "to": "Bill-9", "tree": man["tree_sha256"]})
            led["current_bill"] = "Bill-9"
            led["last_tree_sha256"] = man["tree_sha256"]
            print(f"  promoted Bill-9 tree={man['tree_sha256'][:12]}")
        else:
            print("  Bill-8 stays")
    elif cmd == "ted-10":
        vpath = ROOT / "data" / "bill9_inxxx_leftover.json"
        if not vpath.is_file():
            print("  run python scripts/bill9_inxxx_leftover.py first")
            return 1
        v = json.loads(vpath.read_text(encoding="utf-8"))
        win = bool(v.get("promotes") and v.get("overall_ok"))
        exp = {
            "id": "TED-10",
            "role": "ted",
            "adventure": 2,
            "change": "INXXX007 class-gated leftover; splice chordotonal → FETi; do not grow XXX type",
            "vs_bill": "Bill-9",
            "n_ok": v.get("n_ok"),
            "n": v.get("n"),
            "promotes": win,
            "promote_to": "Bill-10" if win else None,
            "why": (
                "Chordotonal class commands; INXXX007 isolate leftover (unlabeled). "
                "DNg29 isolate still commands. Effector is tibia_extensor_FETi."
            ),
        }
        dest = BT / "TED-10"
        dest.mkdir(parents=True, exist_ok=True)
        (dest / "EXPERIMENT.json").write_text(json.dumps(exp, indent=2), encoding="utf-8")
        if "TED-10" not in led["teds"]:
            led["teds"].append("TED-10")
        print(f"  TED-10 promotes={win}  {exp.get('n_ok')}/{exp.get('n')}")
        if win:
            man = freeze("Bill-10")
            if "Bill-10" not in led["bills"]:
                led["bills"].append("Bill-10")
            led["promotions"].append({"from": "TED-10", "to": "Bill-10", "tree": man["tree_sha256"]})
            led["current_bill"] = "Bill-10"
            led["last_tree_sha256"] = man["tree_sha256"]
            print(f"  promoted Bill-10 tree={man['tree_sha256'][:12]}")
        else:
            print("  Bill-9 stays")
    elif cmd == "ted-11":
        vpath = ROOT / "data" / "bill10_remaining_leftovers.json"
        if not vpath.is_file():
            print("  run python scripts/bill10_remaining_leftovers.py first")
            return 1
        v = json.loads(vpath.read_text(encoding="utf-8"))
        win = bool(v.get("promotes") and v.get("overall_ok"))
        exp = {
            "id": "TED-11",
            "role": "ted",
            "adventure": 2,
            "change": "remaining leftovers mapped: analogs, wait dumps, refuse invent, language splice job",
            "vs_bill": "Bill-10",
            "n_ok": v.get("n_ok"),
            "n": v.get("n"),
            "promotes": win,
            "promote_to": "Bill-11" if win else None,
            "why": (
                "Every leftover has mechanic+do. Blocked dumps wait. "
                "Language is a splice job, not W. Male FETi analog BANC."
            ),
        }
        dest = BT / "TED-11"
        dest.mkdir(parents=True, exist_ok=True)
        (dest / "EXPERIMENT.json").write_text(json.dumps(exp, indent=2), encoding="utf-8")
        if "TED-11" not in led["teds"]:
            led["teds"].append("TED-11")
        print(f"  TED-11 promotes={win}  {exp.get('n_ok')}/{exp.get('n')}")
        if win:
            man = freeze("Bill-11")
            if "Bill-11" not in led["bills"]:
                led["bills"].append("Bill-11")
            led["promotions"].append({"from": "TED-11", "to": "Bill-11", "tree": man["tree_sha256"]})
            led["current_bill"] = "Bill-11"
            led["last_tree_sha256"] = man["tree_sha256"]
            print(f"  promoted Bill-11 tree={man['tree_sha256'][:12]}")
        else:
            print("  Bill-10 stays")
    elif cmd == "ted-12":
        vpath = ROOT / "data" / "bill11_map_all.json"
        if not vpath.is_file():
            print("  run python scripts/bill11_map_all.py first")
            return 1
        v = json.loads(vpath.read_text(encoding="utf-8"))
        win = bool(v.get("promotes") and v.get("overall_ok"))
        exp = {
            "id": "TED-12",
            "role": "ted",
            "adventure": 2,
            "change": "map remaining 9 leftovers via analog jobs; leftover_map 35/35",
            "vs_bill": "Bill-11",
            "n_ok": v.get("n_ok"),
            "n": v.get("n_tests"),
            "promotes": win,
            "promote_to": "Bill-12" if win else None,
            "why": v.get("why_26_of_35"),
        }
        dest = BT / "TED-12"
        dest.mkdir(parents=True, exist_ok=True)
        (dest / "EXPERIMENT.json").write_text(json.dumps(exp, indent=2), encoding="utf-8")
        if "TED-12" not in led["teds"]:
            led["teds"].append("TED-12")
        print(f"  TED-12 promotes={win}  {exp.get('n_ok')}/{exp.get('n')}")
        if win:
            man = freeze("Bill-12")
            if "Bill-12" not in led["bills"]:
                led["bills"].append("Bill-12")
            led["promotions"].append({"from": "TED-12", "to": "Bill-12", "tree": man["tree_sha256"]})
            led["current_bill"] = "Bill-12"
            led["last_tree_sha256"] = man["tree_sha256"]
            print(f"  promoted Bill-12 tree={man['tree_sha256'][:12]}")
        else:
            print("  Bill-11 stays")
    elif cmd == "ted-13":
        vpath = ROOT / "data" / "bill12_language_splice.json"
        if not vpath.is_file():
            print("  run python scripts/bill12_language_splice.py first")
            return 1
        v = json.loads(vpath.read_text(encoding="utf-8"))
        win = bool(v.get("promotes") and v.get("overall_ok"))
        exp = {
            "id": "TED-13",
            "role": "ted",
            "adventure": 2,
            "change": "splice language as invented region at command bottlenecks (trit ALU, not FlyWire W)",
            "vs_bill": "Bill-12",
            "n_ok": v.get("n_ok"),
            "n": v.get("n"),
            "promotes": win,
            "promote_to": "Bill-13" if win else None,
            "why": (
                "Language is trit ALU + closed lexicon. Commands splice at IN05B011a/DNg29/DNp01. "
                "Unknown leftover. Courtship DENY. Not on W. Not APL."
            ),
        }
        dest = BT / "TED-13"
        dest.mkdir(parents=True, exist_ok=True)
        (dest / "EXPERIMENT.json").write_text(json.dumps(exp, indent=2), encoding="utf-8")
        if "TED-13" not in led["teds"]:
            led["teds"].append("TED-13")
        print(f"  TED-13 promotes={win}  {exp.get('n_ok')}/{exp.get('n')}")
        if win:
            man = freeze("Bill-13")
            if "Bill-13" not in led["bills"]:
                led["bills"].append("Bill-13")
            led["promotions"].append({"from": "TED-13", "to": "Bill-13", "tree": man["tree_sha256"]})
            led["current_bill"] = "Bill-13"
            led["last_tree_sha256"] = man["tree_sha256"]
            print(f"  promoted Bill-13 tree={man['tree_sha256'][:12]}")
        else:
            print("  Bill-12 stays")
    elif cmd == "ted-14":
        vpath = ROOT / "data" / "bill13_coding_tokens.json"
        if not vpath.is_file():
            print("  run python scripts/bill13_coding_tokens.py first")
            return 1
        v = json.loads(vpath.read_text(encoding="utf-8"))
        win = bool(v.get("promotes") and v.get("overall_ok"))
        exp = {
            "id": "TED-14",
            "role": "ted",
            "adventure": 2,
            "change": "coding tokens on language splice: let/if/while + trit ALU, not FlyWire W",
            "vs_bill": "Bill-13",
            "n_ok": v.get("n_ok"),
            "n": v.get("n"),
            "promotes": win,
            "promote_to": "Bill-14" if win else None,
            "why": (
                "let/if/while on trit ALU. Loop horizon φ^5=11. Courtship names DENY. "
                "Not on W. Never APL/il3LN6."
            ),
        }
        dest = BT / "TED-14"
        dest.mkdir(parents=True, exist_ok=True)
        (dest / "EXPERIMENT.json").write_text(json.dumps(exp, indent=2), encoding="utf-8")
        if "TED-14" not in led["teds"]:
            led["teds"].append("TED-14")
        print(f"  TED-14 promotes={win}  {exp.get('n_ok')}/{exp.get('n')}")
        if win:
            man = freeze("Bill-14")
            if "Bill-14" not in led["bills"]:
                led["bills"].append("Bill-14")
            led["promotions"].append({"from": "TED-14", "to": "Bill-14", "tree": man["tree_sha256"]})
            led["current_bill"] = "Bill-14"
            led["last_tree_sha256"] = man["tree_sha256"]
            print(f"  promoted Bill-14 tree={man['tree_sha256'][:12]}")
        else:
            print("  Bill-13 stays")
    elif cmd == "ted-15":
        vpath = ROOT / "data" / "bill14_host_eval.json"
        if not vpath.is_file():
            print("  run python scripts/bill14_host_eval.py first")
            return 1
        v = json.loads(vpath.read_text(encoding="utf-8"))
        win = bool(v.get("promotes") and v.get("overall_ok"))
        exp = {
            "id": "TED-15",
            "role": "ted",
            "adventure": 2,
            "change": "host-eval coding vs Python sandbox; safety-hop courtship/aggression T1 off",
            "vs_bill": "Bill-14",
            "n_ok": v.get("n_ok"),
            "n": v.get("n"),
            "promotes": win,
            "promote_to": "Bill-15" if win else None,
            "why": (
                "Sandbox is the host eval (AST whitelist). pC1/TN1/fru hops light motor — "
                "that is why T1 stays off. Language/code DENY those names."
            ),
        }
        dest = BT / "TED-15"
        dest.mkdir(parents=True, exist_ok=True)
        (dest / "EXPERIMENT.json").write_text(json.dumps(exp, indent=2), encoding="utf-8")
        if "TED-15" not in led["teds"]:
            led["teds"].append("TED-15")
        print(f"  TED-15 promotes={win}  {exp.get('n_ok')}/{exp.get('n')}")
        if win:
            man = freeze("Bill-15")
            if "Bill-15" not in led["bills"]:
                led["bills"].append("Bill-15")
            led["promotions"].append({"from": "TED-15", "to": "Bill-15", "tree": man["tree_sha256"]})
            led["current_bill"] = "Bill-15"
            led["last_tree_sha256"] = man["tree_sha256"]
            print(f"  promoted Bill-15 tree={man['tree_sha256'][:12]}")
        else:
            print("  Bill-14 stays")
    elif cmd == "ted-16":
        vpath = ROOT / "data" / "bill15_unseen_math.json"
        if not vpath.is_file():
            print("  run python scripts/bill15_unseen_math.py first")
            return 1
        v = json.loads(vpath.read_text(encoding="utf-8"))
        win = bool(v.get("promotes") and v.get("overall_ok"))
        exp = {
            "id": "TED-16",
            "role": "ted",
            "adventure": 2,
            "change": "unseen NAEP/IM math quiz; blind leftover vs named adapters",
            "vs_bill": "Bill-15",
            "n_blind": v.get("n_blind_ok"),
            "n_adapt": v.get("n_adapt_ok"),
            "n": v.get("n"),
            "promotes": win,
            "promote_to": "Bill-16" if win else None,
            "why": (
                "Not an LLM test. Blind language+ALU leftover on word problems "
                "(and some false ALU on 'times'). Named leftover jobs recover the keys."
            ),
        }
        dest = BT / "TED-16"
        dest.mkdir(parents=True, exist_ok=True)
        (dest / "EXPERIMENT.json").write_text(json.dumps(exp, indent=2), encoding="utf-8")
        if "TED-16" not in led["teds"]:
            led["teds"].append("TED-16")
        print(f"  TED-16 promotes={win}  adapt={exp.get('n_adapt')}/{exp.get('n')} blind={exp.get('n_blind')}")
        if win:
            man = freeze("Bill-16")
            if "Bill-16" not in led["bills"]:
                led["bills"].append("Bill-16")
            led["promotions"].append({"from": "TED-16", "to": "Bill-16", "tree": man["tree_sha256"]})
            led["current_bill"] = "Bill-16"
            led["last_tree_sha256"] = man["tree_sha256"]
            print(f"  promoted Bill-16 tree={man['tree_sha256'][:12]}")
        else:
            print("  Bill-15 stays")
    elif cmd == "ted-17":
        vpath = ROOT / "data" / "bill16_word_sense.json"
        if not vpath.is_file():
            print("  run python scripts/bill16_word_sense.py first")
            return 1
        v = json.loads(vpath.read_text(encoding="utf-8"))
        win = bool(v.get("promotes") and v.get("overall_ok"))
        exp = {
            "id": "TED-17",
            "role": "ted",
            "adventure": 2,
            "change": "dictionary/grammar senses for leftover English; Wikipedia not over W; DISCOVERIES.md",
            "vs_bill": "Bill-16",
            "n_ok": v.get("n_ok"),
            "n": v.get("n"),
            "promotes": win,
            "promote_to": "Bill-17" if win else None,
            "why": v.get("clarification"),
        }
        dest = BT / "TED-17"
        dest.mkdir(parents=True, exist_ok=True)
        (dest / "EXPERIMENT.json").write_text(json.dumps(exp, indent=2), encoding="utf-8")
        if "TED-17" not in led["teds"]:
            led["teds"].append("TED-17")
        print(f"  TED-17 promotes={win}  {exp.get('n_ok')}/{exp.get('n')}")
        if win:
            man = freeze("Bill-17")
            if "Bill-17" not in led["bills"]:
                led["bills"].append("Bill-17")
            led["promotions"].append({"from": "TED-17", "to": "Bill-17", "tree": man["tree_sha256"]})
            led["current_bill"] = "Bill-17"
            led["last_tree_sha256"] = man["tree_sha256"]
            print(f"  promoted Bill-17 tree={man['tree_sha256'][:12]}")
        else:
            print("  Bill-16 stays")
    elif cmd == "ted-18":
        vpath = ROOT / "data" / "bill17_adaptive.json"
        if not vpath.is_file():
            print("  run python scripts/bill17_adaptive.py first")
            return 1
        v = json.loads(vpath.read_text(encoding="utf-8"))
        win = bool(v.get("promotes") and v.get("overall_ok"))
        exp = {
            "id": "TED-18",
            "role": "ted",
            "adventure": 1,
            "change": "adaptive grammar leftover learner; LTM bind; teaching trajectory is data",
            "vs_bill": "Bill-17",
            "n_ok": v.get("n_ok"),
            "n": v.get("n"),
            "promotes": win,
            "promote_to": "Bill-18" if win else None,
            "why": (
                "Not one schema per item. Dictionary/grammar on the prompt. "
                "LTM fingerprint after a hit. Adventure 1 teaching thread."
            ),
        }
        dest = BT / "TED-18"
        dest.mkdir(parents=True, exist_ok=True)
        (dest / "EXPERIMENT.json").write_text(json.dumps(exp, indent=2), encoding="utf-8")
        if "TED-18" not in led["teds"]:
            led["teds"].append("TED-18")
        print(f"  TED-18 promotes={win}  {exp.get('n_ok')}/{exp.get('n')}")
        if win:
            man = freeze("Bill-18")
            if "Bill-18" not in led["bills"]:
                led["bills"].append("Bill-18")
            led["promotions"].append({"from": "TED-18", "to": "Bill-18", "tree": man["tree_sha256"]})
            led["current_bill"] = "Bill-18"
            led["last_tree_sha256"] = man["tree_sha256"]
            print(f"  promoted Bill-18 tree={man['tree_sha256'][:12]}")
        else:
            print("  Bill-17 stays")
    elif cmd == "ted-19":
        vpath = ROOT / "data" / "bill18_bio_teach.json"
        if not vpath.is_file():
            print("  run python scripts/bill18_bio_teach.py first")
            return 1
        v = json.loads(vpath.read_text(encoding="utf-8"))
        win = bool(v.get("promotes") and v.get("overall_ok"))
        exp = {
            "id": "TED-19",
            "role": "ted",
            "adventure": 1,
            "change": "teach steps then own work; DA leftover T1 reward; overlay resistance; not fitted RL",
            "vs_bill": "Bill-18",
            "n_ok": v.get("n_ok"),
            "n": v.get("n"),
            "transfer": f"{v.get('n_transfer_ok')}/{v.get('n_transfer')}",
            "promotes": win,
            "promote_to": "Bill-19" if win else None,
            "why": (
                "Procedure then new numbers. Reward trit +1/0/−1. DA leftover binds LTM. "
                "5HT leftover on error. No new synapses. Not LLM."
            ),
        }
        dest = BT / "TED-19"
        dest.mkdir(parents=True, exist_ok=True)
        (dest / "EXPERIMENT.json").write_text(json.dumps(exp, indent=2), encoding="utf-8")
        if "TED-19" not in led["teds"]:
            led["teds"].append("TED-19")
        print(f"  TED-19 promotes={win}  {exp.get('n_ok')}/{exp.get('n')} transfer={exp.get('transfer')}")
        if win:
            man = freeze("Bill-19")
            if "Bill-19" not in led["bills"]:
                led["bills"].append("Bill-19")
            led["promotions"].append({"from": "TED-19", "to": "Bill-19", "tree": man["tree_sha256"]})
            led["current_bill"] = "Bill-19"
            led["last_tree_sha256"] = man["tree_sha256"]
            print(f"  promoted Bill-19 tree={man['tree_sha256'][:12]}")
        else:
            print("  Bill-18 stays")
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
        print("usage: freeze [Bill-0] | ted-1 | … | ted-10 | ledger")
        return 1
    LEDGER.write_text(json.dumps(led, indent=2), encoding="utf-8")
    print(f"  wrote {LEDGER}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
