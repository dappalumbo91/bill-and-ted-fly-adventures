# Cross-verification — genetics formula branch

The fly pack's own gauntlet is `python verification/run_fly_spine.py`. It writes `data/fly_spine_report.json` under pin **AEB2AD**. See `docs/FLY_SPINE.md`. The commands below are the genetics sibling, pin **D1D38A**.

Modeled on **FSOT-2.1-Lean** multi-prover / green-gate discipline:

- Stored genetics report pin is **D1D38A**. The law is the same `S=K(T1+T2+T3)` the Lean hub carries under **AEB2AD**.
- Hard CI exit on pin drift, free parameters, or grind-time regression.
- Scoreboards are evidence, not marketing.

## Local

```powershell
cd FSOT-Genetics
python scripts/verify_cross.py
python verification/run_cross_proof.py
# optional (network):
python scripts/run_fsot_vs_alphafold_structure.py --max-proteins 8 --rounds 24 --sleep 0.2
python scripts/run_fsot_distogram_contact_eval.py
```

Full gauntlet (Lean · Coq · Isabelle · F* · SMT · Rust · TLA+) writes `data/cross_proof_report.json`. Labeled solves: `docs/VERIFIED_SOLVES.md`.

## What is *not* a green gate

| Item | Status |
|------|--------|
| Median Cα RMSD beating AlphaFold | **Open research goal** — tracked, not required for CI green |
| Full proteome dump | Out of scope (storage) |
| Neural weight training | Forbidden on claim path |

CI green means: **law pin + zero free params + formula path runs**.  
Campaign green (AF) means: **median RMSD / lDDT competitive** — see `BEAT_ALPHAFOLD_PLAN.md`.

## Sibling verification map

```
FSOT-2.1-Lean     → Lean / multi-prover / domain margins
fsot-neuron-zig   → seed + genetic pair geometry parity
FSOT-Genetics     → F01–F15 + fold + AF H2H (genetics sibling, pin D1D38A)
fly pack          → obligation spine, pin AEB2AD, docs/FLY_SPINE.md
```
