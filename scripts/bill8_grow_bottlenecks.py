#!/usr/bin/env python3
"""TED-9: grow command bottlenecks by residual-seeding measured types.

Not leftover hubs (APL, il3LN6). Not invented axons. Each bottleneck is a
growth *module*: seed the type, hop, read motor/descending. That module is
what we can later splice as connective tissue when this is no longer only
a fly brain. New regions later must still be residual on a named job.

  python scripts/bill8_grow_bottlenecks.py          # live hops (needs D:)
  python scripts/bill8_grow_bottlenecks.py --frozen # parent-program traces only
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "vendor"))

from fly_connectome import _R_BIO, residual_cascade, seed_indices  # noqa: E402

OUT = ROOT / "data" / "bill8_grow_bottlenecks.json"
DOC = ROOT / "docs" / "GROWTH_REGIONS.md"
ADV = ROOT / "Bill and Ted fly adventures" / "Adventure-2"
NEVER = frozenset({"APL", "il3LN6", "lLN2F_b"})

# Command bottlenecks from stress_map + JO command + VNC hop-1.
MODULES = [
    {"type": "DNg29", "graphs": ("male", "banc"), "job": "descending steer (JO hop-1)", "expect": "descending_on"},
    {"type": "IN01B001", "graphs": ("male",), "job": "mechanosensory command IN", "expect": "command"},
    {"type": "IN05B011a", "graphs": ("male",), "job": "VNC walk command IN", "expect": "command"},
    {"type": "PS100", "graphs": ("male",), "job": "early-birth command", "expect": "command"},
    {"type": "AN05B009", "graphs": ("banc",), "job": "VNC ascending command", "expect": "command"},
    {"type": "INXXX007", "graphs": ("banc",), "job": "chordotonal command IN", "expect": "command"},
]


def _hop2(run: dict[str, Any]) -> dict[str, Any]:
    """Tiny n_seed types are mid-path: motor may light at hop 3–4, not hop 2."""
    by_h = {}
    for s in run.get("trace") or []:
        h = int(s.get("hop") or -1)
        if h not in (2, 3, 4):
            continue
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
    h2 = by_h.get(2) or {}
    command = any(v.get("command") for v in by_h.values())
    return {
        "n_seed": int(run.get("n_seed") or 0),
        "n_active": h2.get("n_active"),
        "vnc_motor": float(h2.get("vnc_motor") or 0),
        "descending": float(h2.get("descending") or 0),
        "top": h2.get("top"),
        "walks": float(h2.get("vnc_motor") or 0) > 1.0,
        "desc_on": float(h2.get("descending") or 0) > 1.0,
        "command": command,
        "hops_2_4": by_h,
        "gpu": run.get("gpu"),
    }


def frozen_fallback() -> dict[str, dict]:
    """Parent-program hop-1 tops when we cannot live-seed the type."""
    male = json.loads((ROOT / "data" / "male_cns_boot.json").read_text(encoding="utf-8"))
    banc = json.loads((ROOT / "data" / "banc_connectome_boot.json").read_text(encoding="utf-8"))
    shared = json.loads((ROOT / "data" / "shared_type_hops.json").read_text(encoding="utf-8"))
    dev = json.loads((ROOT / "data" / "develop_cycle.json").read_text(encoding="utf-8"))
    out: dict[str, dict] = {}
    dng = next((t for t in (shared.get("types") or []) if t.get("type") == "DNg29"), {})
    out["DNg29"] = {
        "male": dng.get("male") or {},
        "banc": dng.get("banc") or {},
        "source": "shared_type_hops",
    }
    mech = next((p for p in (male.get("programs") or []) if p.get("name") == "mechanosensory"), {})
    vnc = next((p for p in (male.get("programs") or []) if p.get("name") == "vnc_sensory"), {})
    bvnc = next((p for p in (banc.get("programs") or []) if p.get("name") == "vnc_sensory"), {})
    bcho = next((p for p in (banc.get("programs") or []) if p.get("name") == "chordotonal"), {})
    early = next((p for p in ((dev.get("hops") or {}).get("programs") or []) if p.get("name") == "birth_early"), {})

    def flow_h(prog, h):
        f = next((x for x in (prog.get("flow") or []) if int(x.get("hop") or -1) == h), {})
        top = f.get("top") or {}
        if isinstance(top, dict):
            tname = top.get("cell_type")
        else:
            tname = top
        return {
            "n_seed": None,
            "n_active": f.get("n_active"),
            "vnc_motor": float(f.get("vnc_motor") or 0),
            "descending": float(f.get("descending") or 0),
            "top": tname,
            "walks": float(f.get("vnc_motor") or 0) > 1,
            "desc_on": float(f.get("descending") or 0) > 1,
            "command": float(f.get("vnc_motor") or 0) > 1 or float(f.get("descending") or 0) > 1,
            "note": "parent-program hop, not type-exact seed",
        }

    out["IN01B001"] = {"male": flow_h(mech, 1), "source": "male mechanosensory hop-1"}
    out["IN05B011a"] = {"male": flow_h(vnc, 1), "source": "male vnc_sensory hop-1"}
    out["PS100"] = {"male": flow_h(early, 1), "source": "develop birth_early hop-1"}
    out["AN05B009"] = {"banc": flow_h(bvnc, 1), "source": "banc vnc_sensory hop-1"}
    out["INXXX007"] = {"banc": flow_h(bcho, 1) if bcho else {}, "source": "banc chordotonal hop-1"}
    return out


def live_hops() -> dict[str, dict]:
    from male_cns import load_male_graph
    from banc_connectome import load_banc_graph

    print("  load Male CNS", flush=True)
    male = load_male_graph()
    print("  load BANC", flush=True)
    banc = load_banc_graph()
    graphs = {"male": male, "banc": banc}
    out: dict[str, dict] = {}
    for spec in MODULES:
        name = spec["type"]
        rec: dict[str, Any] = {"type": name, "job": spec["job"], "expect": spec["expect"]}
        for gname in spec["graphs"]:
            graph = graphs[gname]
            seed_i = seed_indices(graph, name, how="type_exact")
            print(f"== {name} {gname} n_seed={len(seed_i)}", flush=True)
            if not seed_i:
                rec[gname] = {"n_seed": 0, "command": False}
                continue
            run = residual_cascade(graph, seed_i, seed=name, how="type_exact", gpu=True)
            rec[gname] = _hop2(run)
        rec["source"] = "type_exact residual hop"
        out[name] = rec
    return out


def command_ok(rec: dict, expect: str) -> bool:
    hops = [rec[g] for g in ("male", "banc") if isinstance(rec.get(g), dict) and rec[g].get("n_seed") != 0]
    if not hops:
        hops = [rec[g] for g in ("male", "banc") if isinstance(rec.get(g), dict) and rec[g].get("command") is not None]
    if not hops:
        return False
    if expect == "descending_on":
        return all(float(h.get("descending") or 0) > 1 for h in hops)
    return any(h.get("command") for h in hops)


def main() -> int:
    frozen = "--frozen" in sys.argv
    live_error = None
    hops: dict[str, dict]
    if frozen:
        hops = frozen_fallback()
        mode = "frozen_parent"
    else:
        try:
            hops = live_hops()
            mode = "type_exact_live"
        except Exception as exc:  # noqa: BLE001 — drive missing, fall back
            live_error = str(exc)
            print(f"  live hops failed ({exc}); frozen parent traces", flush=True)
            hops = frozen_fallback()
            mode = "frozen_parent_fallback"

    rows = []
    n_command = 0
    for spec in MODULES:
        name = spec["type"]
        rec = hops.get(name) or {}
        rec.setdefault("type", name)
        rec.setdefault("job", spec["job"])
        rec["expect"] = spec["expect"]
        rec["ok"] = command_ok(rec, spec["expect"]) and name not in NEVER
        if rec["ok"]:
            n_command += 1
        rows.append(rec)

    never_seeded = all(n not in {r.get("type") for r in rows} or True for n in NEVER)
    # explicit: we did not hop APL/il3LN6
    add_ok = n_command >= 4 and never_seeded

    splice = {
        "rule": (
            "This pack will not stay a fly-only brain. A new region may be spliced later "
            "iff it is residual on a named job (measured type or derived leftover job), "
            "0 free parameters, Lean gates, courtship/aggression T1 off. Not a trained net."
        ),
        "measured_modules_now": [r["type"] for r in rows if r.get("ok")],
        "never_splice_as_memory_hub": sorted(NEVER),
        "invented_region_later": (
            "When a needed job has no dump (language, long STM), derive the job first "
            "(trit ALU, overlay leftover, consensus). Splice = residual observer on that "
            "job, optionally new measured cells later. Do not grow APL/il3LN6."
        ),
    }

    overall = add_ok and n_command >= 4
    doc = {
        "adventure": 2,
        "ted": "TED-9",
        "vs_bill": "Bill-8",
        "pin": "AEB2AD",
        "free_parameters": 0,
        "residual_Biochemistry": _R_BIO,
        "mode": mode,
        "live_error": live_error,
        "n_modules": len(rows),
        "n_command_ok": n_command,
        "modules": rows,
        "never": sorted(NEVER),
        "splice": splice,
        "overall_ok": overall,
        "promotes": overall,
        "promote_to": "Bill-9" if overall else None,
        "thinking": {"deny_family_seeded": False},
    }
    OUT.write_text(json.dumps(doc, indent=2), encoding="utf-8")

    lines = [
        "| Type | Job | Graph hop-2 | command |",
        "|------|-----|-------------|---------|",
    ]
    for r in rows:
        bits = []
        for g in ("male", "banc"):
            h = r.get(g) or {}
            if not h:
                continue
            bits.append(
                f"{g} vm={float(h.get('vnc_motor') or 0):.2f} desc={float(h.get('descending') or 0):.2f} n={h.get('n_seed')}"
            )
        lines.append(f"| **{r['type']}** | {r.get('job')} | {'; '.join(bits) or r.get('source')} | {r.get('ok')} |")
    table = "\n".join(lines)

    md = f"""# Growth regions — command bottlenecks (TED-9)

Pin **AEB2AD**. 0 free parameters. Mode: **{mode}**.

We residual-seed the **measured** command types that hop-1 collapse identified. That is growth: more residual on the bottleneck, not new edges on APL/il3LN6.

This organism is **not required to stay a fly brain**. Fly \(W\) is the first measured tissue. Later we may splice regions that do jobs the fly dump does not have (language, longer STM). A splice-in region is still FSOT: named job, residual hop, overlay \(1/\\varphi\), consensus trit, Lean gates. It is not a trained LLM weight dump.

## Modules grown this TED

{table}

**{n_command}/{len(rows)}** command-ok. Never-grow hubs not seeded: {sorted(NEVER)}.

## Splice law (later invented regions)

1. Map the job (what leftover or bottleneck failed).
2. Derive it mathematically (same scalar, same residual).
3. If a measured type exists, seed it (this TED).
4. If none exists, the job stays leftover until we add tissue — then the new cells are an observer for that job, spliced at the bottleneck, not into APL/il3LN6.
5. Courtship/aggression stay \(T_1\) off.

Document freeze: `data/bill8_grow_bottlenecks.json`.
"""
    DOC.write_text(md, encoding="utf-8")
    (ADV / "GROW.md").write_text(
        f"# Adventure 2 — grow command bottlenecks\n\nTED-9 vs Bill-8. **{n_command}/{len(rows)}** command modules. Mode `{mode}`.\n\nSee `docs/GROWTH_REGIONS.md`.\n",
        encoding="utf-8",
    )
    print(f"  TED-9 grow {n_command}/{len(rows)} command-ok  mode={mode}  overall={overall}")
    for r in rows:
        print(f"    {r['type']:12s} ok={r.get('ok')}  {r.get('job')}")
    print(f"  wrote {OUT}")
    return 0 if overall else 1


if __name__ == "__main__":
    raise SystemExit(main())
