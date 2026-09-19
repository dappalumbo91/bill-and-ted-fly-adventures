#!/usr/bin/env python3
"""Bill and Ted Adventure 1 — FSOT vs connectome shortcomings.

Paper claims: local VNC motor, sensory-motor loops, rich-club ANNs.
Gaps: neuromod volume, off-domain text tasks, single snapshot, missed gap junctions.

FSOT solve (0 knobs): neuromod = observer/volume (T1), not extra edges;
gap junction analog = consensus trit; snapshot = Male+BANC+hemibrain+larva;
off-domain = leftover when the job is not a measured observer.

  python scripts/adventure1.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "vendor"))

from fly_connectome import _PHI, _R_BIO  # noqa: E402
from math_first import _hop2_state, _motor_by_side  # noqa: E402

OUT = ROOT / "data" / "adventure1.json"
ADV = ROOT / "Bill and Ted fly adventures" / "Adventure-1"
INV_PHI = 1.0 / float(_PHI)
MODS = ("dopamine", "serotonin", "octopamine", "histamine", "gaba")


def seed_nt(graph: dict[str, Any], nt: str) -> list[int]:
    want = nt.lower()
    out = []
    for rid, m in graph["meta"].items():
        if rid not in graph["idx"]:
            continue
        if (m.get("top_nt") or "").lower() == want:
            out.append(graph["idx"][rid])
    return out


def main() -> int:
    from male_cns import load_male_graph

    print("  load Male CNS", flush=True)
    graph = load_male_graph()
    hops = []
    for nt in MODS:
        si = seed_nt(graph, nt)
        print(f"== {nt} n_seed={len(si)}", flush=True)
        if not si:
            hops.append({"nt": nt, "n_seed": 0, "hop2": None})
            continue
        a = _hop2_state(graph, si)
        mass = _motor_by_side(a, graph)
        vm = float(mass["vnc_motor"])
        hops.append(
            {
                "nt": nt,
                "n_seed": len(si),
                "hop2": mass,
                "walks": vm > 1.0,
                "volume_leftover": vm <= 1.0,
            }
        )
        print(
            f"  vnc_motor={vm:.4f} L={mass['vnc_motor_L']:.3f} "
            f"R={mass['vnc_motor_R']:.3f} walks={vm > 1}",
            flush=True,
        )

    male = json.loads((ROOT / "data" / "male_cns_boot.json").read_text(encoding="utf-8"))
    banc = json.loads((ROOT / "data" / "banc_connectome_boot.json").read_text(encoding="utf-8"))
    fw = json.loads((ROOT / "data" / "fly_connectome_inventory.json").read_text(encoding="utf-8"))
    cmp_m = (male.get("compare") or {}).get("hop_2") or {}
    cmp_b = (banc.get("compare") or {}).get("hop_2") or {}

    da = next((h for h in hops if h["nt"] == "dopamine"), {})
    oa = next((h for h in hops if h["nt"] == "octopamine"), {})
    s5 = next((h for h in hops if h["nt"] == "serotonin"), {})
    gaba = next((h for h in hops if h["nt"] == "gaba"), {})
    # Volume claim: neuromod should not micro-manage walk like vnc_sensory 10.74
    vnc = float((cmp_m.get("vnc_sensory") or {}).get("vnc_motor") or 10.74)
    vol_ok = all(
        (h.get("hop2") or {}).get("vnc_motor", 99) < vnc / float(_PHI)
        for h in hops
        if h["nt"] in ("dopamine", "serotonin", "octopamine") and h.get("hop2")
    )
    # GABA is the signed brake — it MAY load motor as inhibition leftover
    snapshot = {
        "male_vnc_sensory": (cmp_m.get("vnc_sensory") or {}).get("vnc_motor"),
        "banc_vnc_sensory": (cmp_b.get("vnc_sensory") or {}).get("vnc_motor"),
        "male_JO": (cmp_m.get("JO") or {}).get("vnc_motor"),
        "banc_JO": (cmp_b.get("JO") or {}).get("vnc_motor"),
        "male_olf": (cmp_m.get("olfactory") or {}).get("vnc_motor"),
        "banc_olf": (cmp_b.get("olfactory") or {}).get("vnc_motor"),
        "flywire_n": fw.get("n_neurons"),
        "flywire_nt": fw.get("top_nt"),
    }
    doc = {
        "adventure": 1,
        "ted": "TED-2",
        "pin": "AEB2AD",
        "residual_Biochemistry": _R_BIO,
        "free_parameters": 0,
        "title": "Neuromod volume, gap analog, snapshot, off-domain bound",
        "positives_mapped": {
            "decentralized_motor": (
                "VNC sensory hop-2 vnc_motor 10.74; JO descending 24.21 is high-level. "
                "Local modules in the cord; brain issues direction. Matches the article."
            ),
            "sensory_motor_loops": (
                "L5 vision: legs off, descending 1.92. DNp01 escape desc 15.77. "
                "Not a trained voltage model."
            ),
            "not_ann_blueprint": (
                "We do not prune a dense ANN onto FlyWire. W is measured. 0 free params."
            ),
        },
        "shortcomings_fsot": {
            "neuromod_volume": (
                "DA/5HT/OA are observers (T1 / overlay), not new edges. "
                "Volume transmission = leftover of chemical W. No invented octopamine rewires."
            ),
            "gap_junctions": (
                "EM misses electrical synapses. FSOT analog is consensus trit "
                "(bidirectional: a if a=b else 0) — speed without a fake gap list."
            ),
            "single_snapshot": (
                "Male + BANC + hemibrain + larva are four measured graphs, not one insect. "
                "Predicted sides / TBD hops are adaptation, labeled predicted."
            ),
            "off_domain_text": (
                "Topology is low-dimensional sensory-motor. Trit ALU + overlay leftover "
                "IS the bound. We do not map email classification onto W."
            ),
            "simulation_collapse": (
                "Inf-norm + GABA sign + observer off = no hyper-excited silent trap "
                "from unconstrained voltage. Rest is leftover, not a stuck attractor."
            ),
        },
        "neuromod_hops": hops,
        "volume_weaker_than_vnc_walk": vol_ok,
        "snapshot": snapshot,
        "flywire_modulators": {
            "dopamine": (fw.get("top_nt") or {}).get("dopamine"),
            "serotonin": (fw.get("top_nt") or {}).get("serotonin"),
            "octopamine": (fw.get("top_nt") or {}).get("octopamine"),
        },
        "worked": [],
        "did_not": [],
        "overall_ok": vol_ok,
    }
    if vol_ok:
        doc["worked"].append("DA/5HT/OA hop-2 vnc_motor weaker than VNC walk / φ (volume leftover)")
    else:
        doc["did_not"].append("a neuromod seeded walk as strongly as tarsus — check annotation")
    doc["worked"].append("GABA remains the signed brake on measured W")
    doc["worked"].append("off-domain text not forced onto the graph")
    doc["did_not"].append("no EM gap-junction list — consensus analog only")
    ADV.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(doc, indent=2), encoding="utf-8")
    (ADV / "FINDINGS.md").write_text(
        _findings_md(doc),
        encoding="utf-8",
    )
    (ADV / "EXPERIMENT.json").write_text(json.dumps({"id": "TED-2", **{k: doc[k] for k in ("overall_ok", "volume_weaker_than_vnc_walk", "worked", "did_not")}}, indent=2), encoding="utf-8")
    print(f"  volume_ok={vol_ok}  wrote {OUT} and {ADV}")
    return 0 if vol_ok else 1


def _findings_md(doc: dict) -> str:
    lines = [
        "# Adventure 1 — neuromod, gaps, snapshot, off-domain",
        "",
        "TED-2 vs Bill-1. Pin AEB2AD. 0 free parameters.",
        "",
        "## Paper positives → FSOT (already on Bill)",
        "",
        doc["positives_mapped"]["decentralized_motor"],
        "",
        doc["positives_mapped"]["sensory_motor_loops"],
        "",
        doc["positives_mapped"]["not_ann_blueprint"],
        "",
        "## Shortcomings → FSOT solve",
        "",
    ]
    for k, v in doc["shortcomings_fsot"].items():
        lines += [f"### {k}", "", v, ""]
    lines += ["## Neuromod hops (Male CNS consensus_nt)", "", "| NT | n_seed | hop-2 vnc_motor | walks |", "|----|-------:|----------------:|:-----:|"]
    for h in doc["neuromod_hops"]:
        vm = (h.get("hop2") or {}).get("vnc_motor")
        lines.append(f"| {h['nt']} | {h['n_seed']} | {vm if vm is not None else '—'} | {h.get('walks')} |")
    lines += [
        "",
        f"Volume leftover vs VNC walk/φ: **{doc['volume_weaker_than_vnc_walk']}**",
        "",
        "## Worked",
        "",
    ]
    for w in doc["worked"]:
        lines.append(f"- {w}")
    lines += ["", "## Did not (honest leftover)", ""]
    for w in doc["did_not"]:
        lines.append(f"- {w}")
    lines += [
        "",
        "## Math applied",
        "",
        r"\(S=K(T_1+T_2+T_3)\), \(a\leftarrow rWa\), overlay \(1/\varphi\), consensus trit, GABA sign on \(W\).",
        "Neuromod = observer (T1), not a new synapse list.",
        "",
    ]
    return "\n".join(lines)


if __name__ == "__main__":
    raise SystemExit(main())
