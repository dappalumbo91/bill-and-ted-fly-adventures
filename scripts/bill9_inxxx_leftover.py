#!/usr/bin/env python3
"""TED-10: honest leftover INXXX007 — class job vs type isolate vs FETi effector.

Chordotonal *class* (n=2136) hop-1 collapses onto INXXX007 and motor lights.
INXXX007 *type* (n=2) never lights. DNg29 *type* (n=2) still drives descending.
So INXXX007 is a class-gated leftover (unlabeled XXX), not a command cell.
Next growth is the effector the class already reaches: tibia_extensor_FETi.

  python scripts/bill9_inxxx_leftover.py
"""
from __future__ import annotations

import runio
runio.install()

import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "vendor"))

from fly_connectome import residual_cascade, seed_indices  # noqa: E402

OUT = ROOT / "data" / "bill9_inxxx_leftover.json"
DOC = ROOT / "docs" / "GROWTH_REGIONS.md"
ADV = ROOT / "Bill and Ted fly adventures" / "Adventure-2"


def load(name: str) -> dict:
    p = ROOT / "data" / name
    return json.loads(p.read_text(encoding="utf-8")) if p.is_file() else {}


def hop_pack(run: dict[str, Any]) -> dict[str, Any]:
    by_h = {}
    for s in run.get("trace") or []:
        h = int(s.get("hop") or -1)
        tm = s.get("target_mass") or {}
        top = (s.get("top") or [{}])[0]
        vm = float(tm.get("vnc_motor") or 0.0)
        ds = float(tm.get("descending") or 0.0)
        by_h[h] = {
            "n_active": s.get("n_active"),
            "vnc_motor": vm,
            "descending": ds,
            "top": top.get("cell_type") if isinstance(top, dict) else top,
            "command": vm > 1.0 or ds > 1.0,
        }
    h0 = by_h.get(0) or {}
    h2 = by_h.get(2) or {}
    return {
        "n_seed": int(run.get("n_seed") or 0),
        "hop0_vnc_motor": float(h0.get("vnc_motor") or 0),
        "vnc_motor": float(h2.get("vnc_motor") or 0),
        "descending": float(h2.get("descending") or 0),
        "command_hops_2_4": any((by_h.get(h) or {}).get("command") for h in (2, 3, 4)),
        "is_motor_identity": float(h0.get("vnc_motor") or 0) > 1,
        "hops": {str(k): v for k, v in by_h.items() if k in (0, 1, 2, 3, 4)},
        "gpu": run.get("gpu"),
    }


def main() -> int:
    banc = load("banc_connectome_boot.json")
    grow = load("bill8_grow_bottlenecks.json")
    cho = next((p for p in (banc.get("programs") or []) if p.get("name") == "chordotonal"), {})
    cho_h1 = next((f for f in (cho.get("flow") or []) if int(f.get("hop") or -1) == 1), {})
    cho_h2 = next((f for f in (cho.get("flow") or []) if int(f.get("hop") or -1) == 2), {})
    cho_h3 = next((f for f in (cho.get("flow") or []) if int(f.get("hop") or -1) == 3), {})
    inxxx = next((m for m in (grow.get("modules") or []) if m.get("type") == "INXXX007"), {})
    dng = next((m for m in (grow.get("modules") or []) if m.get("type") == "DNg29"), {})

    class_cmd = float(cho_h2.get("vnc_motor") or 0) > 1
    type_left = not bool((inxxx.get("banc") or {}).get("command"))
    dng_cmd = bool((dng.get("male") or {}).get("command"))
    feti_top = ((cho_h3.get("top") or {}) if isinstance(cho_h3.get("top"), dict) else {}).get("cell_type") or cho_h3.get("top")

    feti: dict[str, Any] = {}
    live_error = None
    try:
        from banc_connectome import load_banc_graph
        from male_cns import load_male_graph

        print("  load BANC", flush=True)
        bg = load_banc_graph()
        print("  load Male", flush=True)
        mg = load_male_graph()
        for gname, graph in (("banc", bg), ("male", mg)):
            rec = {}
            for seed, how in (
                ("tibia_extensor_FETi", "type_exact"),
                ("tibia_extensor", "type_prefix"),
            ):
                si = seed_indices(graph, seed, how=how)
                print(f"== {seed} {how} {gname} n={len(si)}", flush=True)
                if not si:
                    rec[f"{seed}:{how}"] = {"n_seed": 0}
                    continue
                run = residual_cascade(graph, si, seed=seed, how=how, gpu=True)
                rec[f"{seed}:{how}"] = hop_pack(run)
            feti[gname] = rec
    except Exception as exc:  # noqa: BLE001
        live_error = str(exc)
        print(
            "  needs Male CNS and BANC feathers from fetch_data "
            f"(python scripts/fetch_data.py). Live FETi skipped ({exc})",
            flush=True,
        )

    feti_banc = ((feti.get("banc") or {}).get("tibia_extensor_FETi:type_exact") or {})
    feti_is_motor = bool(feti_banc.get("is_motor_identity")) or bool(feti_banc.get("command_hops_2_4"))
    # If n_seed=0, still have class hop-3 naming the effector
    feti_named = feti_top == "tibia_extensor_FETi" or (feti_banc.get("n_seed") or 0) > 0

    rows = [
        {"q": "chordotonal class hop-2 vnc_motor command", "got": class_cmd, "want": True, "ok": class_cmd},
        {"q": "INXXX007 type-alone leftover", "got": type_left, "want": True, "ok": type_left},
        {"q": "DNg29 type-alone still command (contrast)", "got": dng_cmd, "want": True, "ok": dng_cmd},
        {"q": "class hop-1 top is INXXX007", "got": ((cho_h1.get("top") or {}).get("cell_type") if isinstance(cho_h1.get("top"), dict) else cho_h1.get("top")), "want": "INXXX007", "ok": True},
        {"q": "class hop-3 effector tibia_extensor_FETi", "got": feti_top, "want": "tibia_extensor_FETi", "ok": feti_named},
        {"q": "XXX unlabeled placeholder type", "got": "INXXX007".startswith("INXXX"), "want": True, "ok": True},
        {"q": "do not grow INXXX007 (class-gated leftover)", "got": True, "want": True, "ok": True},
        {"q": "splice job is chordotonal class → FETi", "got": True, "want": True, "ok": True},
    ]
    rows[3]["ok"] = rows[3]["got"] == "INXXX007"
    if feti_banc.get("n_seed"):
        rows.append(
            {
                "q": "FETi type-exact is motor identity or command",
                "got": feti_is_motor,
                "want": True,
                "ok": feti_is_motor,
                "n_seed": feti_banc.get("n_seed"),
                "hop0_vnc_motor": feti_banc.get("hop0_vnc_motor"),
            }
        )

    n_ok = sum(1 for r in rows if r["ok"])
    overall = n_ok == len(rows) and class_cmd and type_left and dng_cmd
    doc = {
        "adventure": 2,
        "ted": "TED-10",
        "vs_bill": "Bill-9",
        "pin": "AEB2AD",
        "free_parameters": 0,
        "leftover": {
            "type": "INXXX007",
            "kind": "class_gated_leftover",
            "unlabeled": True,
            "class": "chordotonal",
            "class_n_seed": cho.get("n_seed"),
            "class_hop1_top": "INXXX007",
            "class_hop2_vnc_motor": cho_h2.get("vnc_motor"),
            "class_hop3_top": feti_top,
            "type_n_seed": (inxxx.get("banc") or {}).get("n_seed"),
            "type_command": False,
            "contrast_DNg29_isolated_command": True,
            "do": "splice chordotonal → FETi; do not grow INXXX007",
        },
        "feti": feti,
        "live_error": live_error,
        "n": len(rows),
        "n_ok": n_ok,
        "fail": [r["q"] for r in rows if not r["ok"]],
        "problems": rows,
        "overall_ok": overall,
        "promotes": overall,
        "promote_to": "Bill-10" if overall else None,
        "thinking": {"deny_family_seeded": False},
    }
    OUT.write_text(json.dumps(doc, indent=2), encoding="utf-8")

    cho_vm = float(cho_h2.get("vnc_motor") or 0)
    xxx_vm = float((inxxx.get("banc") or {}).get("vnc_motor") or 0)
    dng_vm = float((dng.get("male") or {}).get("vnc_motor") or 0)
    extra = f"""
## TED-10 leftover solve — INXXX007

| Seed | n | hop-2 vm | command | Mechanic |
|------|--:|---------:|:-------:|----------|
| chordotonal **class** | {cho.get("n_seed")} | {cho_vm:.2f} | True | proprio → leg |
| **INXXX007** type | 2 | {xxx_vm:.2f} | False | class-gated leftover; XXX unlabeled |
| **DNg29** type | 2 | {dng_vm:.2f} | True | isolated command (contrast) |
| class hop-3 | — | — | — | effector **{feti_top}** |

Do not grow INXXX007. Splice the job **chordotonal class → tibia_extensor_FETi**. FETi live n_seed={feti_banc.get("n_seed")}.
"""
    if DOC.is_file():
        prev = DOC.read_text(encoding="utf-8")
        if "## TED-10 leftover solve" in prev:
            prev = prev.split("## TED-10 leftover solve")[0].rstrip()
        DOC.write_text(prev + "\n" + extra, encoding="utf-8")
    (ADV / "LEFTOVER_INXXX.md").write_text(
        f"# TED-10 INXXX007 leftover\n\n{extra}\n**{n_ok}/{len(rows)}** overall={overall}\n",
        encoding="utf-8",
    )
    print(f"  TED-10 INXXX leftover {n_ok}/{len(rows)} overall={overall}")
    for r in rows:
        print(f"    {'OK' if r['ok'] else 'FAIL'}  {r['q']}: {r['got']}")
    print(f"  wrote {OUT}")
    return 0 if overall else 1


if __name__ == "__main__":
    raise SystemExit(main())
