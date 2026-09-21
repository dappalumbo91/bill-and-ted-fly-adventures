# FSOT fly neural connective net — experiment pack

Copy of **measured fly wiring + residual hops + trinary genetics** from FSOT-Genetics, for local exploration.

Pin **AEB2AD** (FSOT-2.1-Lean hub). Law \(S = K(T_1+T_2+T_3)\). Residual \(r = 1+|S|\cdot P_{\mathrm{NEW}}\) (Biochemistry, nest \(D_{\mathrm{eff}}=10\)). **0 free parameters.**

This pack is **not** a trained RNN and does not invent synapses. The graph is FlyWire / Male CNS / BANC measured edges. Residual hops are the FSOT signal. You can treat the hop field as a net to experiment on. Do not swap measured edges for learned weights and still call it the product.

Math: `MATH.md`. Reverse mechanics: `docs/MECHANICS.md`. Living findings log: `RUNNING.md`. Repos: `REPOS.md`. Genetics hook: `data/genetics_hook.json`. Live APIs: `data/live_verify.json`.

**Bill and Ted:** baseline residual net **Bill** vs numbered experiments **TED-\(n\)**. When TED earns Lean/function gates it promotes to **Bill-\(k\)**. Folder: `Bill and Ted fly adventures/`. License: Apache 2.0.

Source: `C:\Users\damia\Desktop\FSOT-Genetics` · [FSOT-Genetics](https://github.com/dappalumbo91/FSOT-Genetics) · hub [FSOT-2.1-Lean](https://github.com/dappalumbo91/FSOT-2.1-Lean)

Synapse dumps stay on `D:\FlyWire_Connectome` (too large for this folder). Boot JSON in `data/` is the residual result.

## What is in here

| Path | What |
|------|------|
| `data/*_boot.json` | Residual hops already run (Male CNS, BANC, FlyWire, larva) |
| `data/fly_genetics_join.json` | Named proteins on named walking cells |
| `data/fly_walking_product.json` | Product Cα of those proteins |
| `data/male_cns_genetics_on_cells.json` | fru/dsx/receptorType already on Male CNS cells |
| `data/analog_pointer.json` | Blank 1:1 (mec-4) points at nompC on this graph |
| `data/homolog_correspondence.json` | Bee/mosquito/beetle product transfers |
| `formulas/` | Codon → trit → AA opcode (20/20 unique expanded words) |
| `scripts/` | Live hop engines (need `D:\FlyWire_Connectome` for full graph) |
| `lean/` | ChemLink D_eff, observer (backbone unobserved), residual ≥ 1 |
| `zig/` | Codon / genetic pair geometry |
| `vendor/` | `fsot_compute.py` pin AEB2AD |
| `MAP.md` | Cell class → gene → protein → trinary |

## Core finding (copy this into any net experiment)

On the **measured** graph, which sensory class is on decides whether motor/descending lights.

| Seed | Male CNS hop-2 `vnc_motor` | BANC hop-2 `vnc_motor` |
|------|---------------------------:|-----------------------:|
| VNC sensory | **10.74** | **10.16** |
| Johnston organ | **7.77** | **6.64** |
| olfactory | **0.001** | **0.0008** |

JO hop-1 peaks **DNg29**. Olfactory stays at antennal-lobe LNs. GABA is the measured inhibitory transmitter, not a claimed thought.

Proteins that **sit on** that job: `nompC` (mechanosensory/JO), `iav`/`nan` (JO TRPV), `Gad1` (GABA), `VGlut`/`Mhc` (motor/muscle). Folded as product Cα where a homolog exists.

## Trinary map (genes → structure)

```
codon → PRIMARY/SECONDARY trits → amino acid → 7-trit opcode → pair weight → fold
```

`python scripts/trinary_syntax.py` (from this folder, `PYTHONPATH` includes `vendor/`). Expanded words **20/20 unique**. Pair law: `fsotPairWeight = geom · (base + 0.15·elec) · (0.35 + 0.65·env)` with `geom = φ · dist^(-1/π)`.

See `MAP.md` and `formulas/`.

## Lean

`lean/` is the genetics formal face (Mathlib session lives in the source repo). Theorems: 7 chem-link D_eff, backbone unobserved, residual factor ≥ 1, freeParameters = 0.

Full gauntlet: in FSOT-Genetics run `python verification/run_cross_proof.py`.

## Boot / tests (from this folder)

```powershell
cd "C:\Users\damia\Desktop\fsot fly nuron net"
python scripts/boot_pack.py                 # pin, trinary, frozen hops vs RESULTS
python scripts/boot_pack.py --live          # + FlyWire TSV + Male CNS feathers on D:
python scripts/boot_pack.py --apis          # UniProt, Ensembl, neuPrint, Allen, GitHub
python scripts/genetics_hook.py             # genes on hop jobs, live IDs
python scripts/live_verify.py
python scripts/trinary_syntax.py
python scripts/analog_pointer.py
python scripts/type_identity.py             # BANC ∩ Male types (do not merge graphs)
python scripts/develop_cycle.py --hops      # hemilineage / birthtime residual
python scripts/phot1_map.py                 # real PHOT1 O48963 LOV crystals
python scripts/neural_guardrails.py         # observer allow/deny, not RLHF
python scripts/baseline_sim.py              # closed-loop baseline print (not an LLM)
python scripts/math_first.py --hops         # miss audit + trit/φ probe + L/R hops
python scripts/arith.py                     # balanced-ternary add/sub/mul/cmp + maze problems
python scripts/arith_count.py               # word problems on measured hop counts
python scripts/arith_steps.py               # multi-step trit chains (worksheets)
python scripts/trit_expr.py                 # expression parser + stress map
python scripts/repertoire.py                # walk/hear/see/smell/object/sleep (courtship DENY)
python scripts/fly_function.py --hops       # wing hinges + DNp01 / hg3 MN
python scripts/wing_sim.py                  # untethered 200 Hz plant from descending hops
python scripts/yaw_jo.py                    # JO_L vs JO_R yaw (advice)
python scripts/leftover_map.py              # overlay/hubs/unlabeled/missing dumps
python scripts/leftover_solve.py --hops     # FSOT join: side vote, TBD hops, birth prior
python scripts/leftover_margin.py           # Lean 0.5% / 99.5% gates on those solves
python scripts/predicted_side_hops.py       # 9 predicted VNC sides as hop observers
python scripts/adventure1.py                # Adventure 1: neuromod volume vs walk
python scripts/adventure1_fold.py           # Genetics/Zig/Lean API fold onto NT jobs
python scripts/genetic_interactions.py      # receptors, VMAT/VAChT/VGAT, innexins, channels
python scripts/peptide_leftovers.py --hops  # Pdf/NPF/clock/fru + LNv leftover hop
python scripts/genetic_baseline_rest.py     # photo/olf/extra receptors/peptide Rs
python scripts/gene_blueprint.py --crumbs   # official names + GluRIID/Rh3–6 crumbs
python scripts/accuracy_sim.py              # FSOT vs empirical fly measurements
python scripts/adventure1_fsot_apply.py     # Ledger B on dump N, GABA n, CRC transmitter AA MW
python scripts/adventure1_fsot_blueprint.py # F02 AA + 120-gene residual hops + pathway sim
python scripts/adventure1_verify.py         # TED-3 vs Bill-2 (Adventure 1 verification, not Adventure 2)
python scripts/bill_ted.py ted-3            # promote TED-3 → Bill-3 if verify holds
python scripts/bill3_math_env.py            # Bill-3 math labs + hop thinking traces (Adventure 2)
python scripts/bill_ted.py ted-4            # promote TED-4 → Bill-4 if math env holds
python scripts/bill4_math_courses.py        # conventional math courses (Z,Q,algebra,calc,…)
python scripts/bill_ted.py ted-5            # promote TED-5 → Bill-5 if courses hold
python scripts/bill5_analysis.py            # analysis, multivariable, 200 Hz plant ODEs
python scripts/bill_ted.py ted-6            # promote TED-6 → Bill-6 if analysis holds
python scripts/bill6_memory.py              # math expand + STM/LTM encode-interfere-retrieve
python scripts/bill_ted.py ted-7            # promote TED-7 → Bill-7 if memory exam holds
python scripts/bill7_memory_expand.py       # STM φ² window, LTM class index, growth map
python scripts/bill_ted.py ted-8            # promote TED-8 → Bill-8
python scripts/bill8_grow_bottlenecks.py    # residual-seed command bottleneck types (needs D:)
python scripts/bill_ted.py ted-9            # promote TED-9 → Bill-9
python scripts/bill9_inxxx_leftover.py      # INXXX007 leftover; chordotonal → FETi
python scripts/bill_ted.py ted-10           # promote TED-10 → Bill-10
python scripts/bill10_remaining_leftovers.py
python scripts/bill_ted.py ted-11           # remaining leftovers mapped
python scripts/bill11_map_all.py            # analog-join remaining 9 → 35/35
python scripts/bill_ted.py ted-12
python scripts/bill12_language_splice.py    # splice language at command bottlenecks
python scripts/bill_ted.py ted-13
python scripts/bill13_coding_tokens.py      # let/if/while coding tokens
python scripts/bill_ted.py ted-14
python scripts/bill14_host_eval.py          # host-eval vs sandbox; safety hops T1 off
python scripts/bill_ted.py ted-15
python scripts/bill15_unseen_math.py        # unseen NAEP/IM math quiz
python scripts/bill_ted.py ted-16
python scripts/bill16_word_sense.py         # dictionary senses; not Wikipedia over W
python scripts/bill_ted.py ted-17
python scripts/bill17_adaptive.py           # adaptive leftover learner (Adventure 1)
python scripts/bill_ted.py ted-18
python scripts/bill18_bio_teach.py          # steps then own work; DA leftover reward
python scripts/bill_ted.py ted-19
python scripts/bill19_read_write.py         # read/write school exam
python scripts/bill_ted.py ted-20
python scripts/bill20_ingest.py             # DeepMind-style JSON ingest
python scripts/bill_ted.py ted-21
python scripts/bill21_openstax.py           # OpenStax Prealgebra JSON
python scripts/bill_ted.py ted-22
python scripts/bill22_openstax_fractions.py # OpenStax Ch.4–5
python scripts/bill_ted.py ted-23
python scripts/bill23_arc.py                # ARC-Easy study then exam
python scripts/bill_ted.py ted-24
python scripts/bill24_arc_gaps.py           # ARC miss analysis + reason_proc
python scripts/bill_ted.py ted-25
python scripts/bill_ted.py ted-2            # promote TED-2 → Bill-2 if gates hold
```

`--live` re-reads `D:\FlyWire_Connectome` and checks neuron/edge/GABA counts match the frozen boots (165,122 / 25,563,197 / 22,055). Hop-2 split stays JO/VNC on, olfactory off.

## Re-run hops (needs game drive)

```powershell
cd "C:\Users\damia\Desktop\fsot fly nuron net"
python scripts\male_cns.py
python scripts\banc_connectome.py
python scripts\hemibrain_connectome.py
python scripts\larva_connectome.py --boot
python scripts\type_counts.py
python scripts\fly_connectome.py --boot --seed sensory
```

## Experiment as a net

Allowed: take `data/*_boot.json` hop fields, or the measured edgelist on `D:`, and try alternative observers / seeds.

Not allowed if you still want the FSOT product: replace synapse counts with trained weights, invent contacts, or call leftover olfactory LN mass a thought.

## What to add next (this pack)

| Add | Why | Do not |
|-----|-----|--------|
| Genetics GitHub pin | Sibling still D1D38A | Silently mix pins |

BANC ∩ Male type identity is **done** (`data/type_identity.json`): **7,442** shared type names, Jaccard **0.471**, **23,608** BANC cells with a measured `malecns_match`. Graphs stay separate.

PHOT1 is **done as measured domains**: live UniProt **O48963** (Arabidopsis PHOT1) with LOV1 **2Z6C** and LOV2 **4HHD**. The old stamp **Q2V2M9** is human **FHOD3**, not phototropin. Full-chain leftover 0.71 > 1/φ² — not a full product, not bulk MDS.

Development: `data/develop_cycle.json`. Early-born adult cells hop-2 `vnc_motor` **24.25**; Truman **07B** **27.57**; Ito **MBp3** (mushroom-body precursor) **0.0001**. Same split as JO vs olfactory, now on **birth/lineage**. Larva→adult named jobs that persist: KC, MBON, DN-VNC, ascending, sensory, LN. No embryo→pupa synapse movie exists.

Neural guardrails: `docs/NEURAL_GUARDRAILS.md`. Default observer JO/VNC/GABA **on**; courtship/aggression/fru/dsx **off** (\(T_1\)) because this pack is for human-facing AI and that family opposes human safety. Labels stay. Consensus trit for give/take. Not a lobotomy.

Hemibrain residual hops are **done** (`data/hemibrain_connectome_boot.json`): JO hop-2 descending **2.68** (Giant Fiber) vs olfactory **0.072**. No VNC, DNg29 absent, unsigned (no predictedNt).

Kenyon hops are **done** (`data/kenyon_connectome_boot.json`): KC hop-2 kenyon **35.1**, descending **0.003**, leftover hub **APL**. Not a thought.

ChAT / VGlut / Mhc are **seated** on the hop table (`data/genetics_hook.json`). Mhc is muscle, not a CNS cell.

Allen Brain Atlas is **mouse**. Fly live verification is Codex + neuPrint + UniProt/Ensembl. CAVE (Allen Institute software) is how FlyWire is served.
