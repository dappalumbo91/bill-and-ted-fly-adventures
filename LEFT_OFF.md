# Where we left off (2026-09-17)

## Pin AEB2AD

Biochemistry nest \(D_{\mathrm{eff}}=10\), \(r=1.284069\). Hop-2 sensory splits unchanged (inf-norm).

## Development (measured, not a fake movie)

No published embryo→pupa synapse time series. Two snapshots + hemilineage/birthtime.

| Adult seed | n | hop-2 `vnc_motor` | hop-2 descending |
|------------|--:|------------------:|-----------------:|
| `birthtime=early` | 7890 | **24.25** | **35.05** |
| Truman hemilineage **07B** | 954 | **27.57** | **32.06** |
| Ito–Lee **MBp3** (MB precursor) | 1038 | **0.0001** | **0.043** |

Same law as JO vs olfactory: **which developmental class is on decides whether motor lights.** MBp3 stays in the mushroom-body leftover (like olfactory LN). Early-born / 07B light VNC motor.

Named jobs that exist as strings in larva **and** adult: KC, MBON, DN-VNC, ascending, sensory, LN. That is class persistence, not 1:1 cell lineage. Worm remains the only complete cell lineage.

`python scripts/develop_cycle.py --hops` → `data/develop_cycle.json`

## Guardrails (neural observer, not RLHF)

`docs/NEURAL_GUARDRAILS.md` · `data/neural_guardrails.json`

Default human-facing seeds: JO / VNC sensory / GABA **on**. Courtship, aggression, *fru*/*dsx* **off** unless that is the task. Consensus trit = agree or superpose. Overlay cut \(1/\varphi\). Do not delete types. Do not call olfactory leftover a thought. New brain regions = residual on **measured** classes (Kenyon), not invented axons.

## Still-opens closed this round

| Item | Result |
|------|--------|
| BANC + Male same cell-type list | **7,442** shared names, Jaccard **0.471**, **23,608** BANC `malecns_match` cells. Do not merge graphs. `data/type_identity.json` |
| PHOT1 `no_measured_map` | Mislabel **Q2V2M9 = human FHOD3**. Real PHOT1 **O48963** with LOV1 **2Z6C** + LOV2 **4HHD**. Domain maps; leftover 0.71 so not full-chain product. `data/phot1_map.json` |

## Still-opens this pass

Living log: **`RUNNING.md`** (law + findings). Update that file when something lands.

| Item | Result |
|------|--------|
| Shared-type hops (two animals) | DNg29 descending **on** both; KCg-m / L5 `vnc_motor` **off**. `data/shared_type_hops.json` |
| Codex token | **Blocked.** Local `type_counts.json` is authority. |
| Product Cα | Campaign D1D38A freeze kept; pack pin AEB2AD noted on the JSON. |
| Behavior-flow `r` field | Restamped 1.284069 (inf-norm; videos not re-run). |

Genetics GitHub is still D1D38A (sibling). Fly Cell Atlas bodyId still unpublished. No pupal synapse movie.

## Baseline simulation (print 1)

`python scripts/baseline_sim.py` → `data/baseline_sim.json` · `docs/BASELINE_SIM.md`

Brain print holds: walk/JO/ball light `vnc_motor`; odor does not; courtship/aggression denied. Closed loop on 3 Harvard ball-treadmill trials: **2/3** reached the left-arm resource; Fly02 turned right (not fitted). Iwasaki object-interaction papers cited; their videos are not on disk.

**Not yet:** language, coding, LLM-style tokens.

## Miss + first math

`python scripts/math_first.py --hops` → `data/math_first.json`

Fly02 miss = 28 right vs 16 left **frames**. Trial-mean (R−L) is leftover under \(1/\varphi\) on all three clips — do not collapse.

Male laterality hops: VNC sensory L/R bias motor **ipsilateral** (~0.34). JO too (~0.24). Spatial trit already in \(W\).

FSOT math probe 13/13 (φ, trit, residual, pair). First curriculum is this, not an LLM.

## Arithmetic

`python scripts/arith.py` → `data/arith.json`  **128/128**

Balanced ternary ALU (trit + trit carry). Add/sub/mul/compare. Maze word problems: 29−28 = left resource; 16−28 = Fly02 miss. Encoder roundtrip [−80,80] clean.

`python scripts/arith_count.py` → **27/27** on measured hop integers: JO_L+JO_R=672, VNC L+R=6351, φ⁵ leftover hops=11, maze 80−82=−2.

`python scripts/arith_steps.py` → **10/10** chains (34 steps). Consensus of T001/T002 vs Fly02 is trit 0. JO÷3×3 recovers 672.

`python scripts/trit_expr.py` → **21/21** expressions + `data/stress_map.json`. Biggest collapse is olfactory il3LN6 (leftover hub). Command stress: JO/DNg29, VNC interneurons. Do not invent synapses.

`python scripts/repertoire.py` → walk is not the whole fly. See (L5) descending 1.92, legs off. JO descending 24. Sleep ~17% leftover inactivity. Courtship/aggression DENY.

`python scripts/fly_function.py --hops` → wing hinges on disk, **parked** (0/3 flight-like). DNp01 descending 15.8. hg3 MN local motor. No free-flight wingbeat; no named haltere types.

`python scripts/wing_sim.py` → **10/10**. Untethered plant at 200 Hz / 2 kHz from measured descending. L5 = flight_only. Walk = takeoff_both (descending was always there).

`docs/MECHANICS.md` reverse map. `python scripts/yaw_jo.py` → **10/10**. Bilateral JO consensus 0 (straight). Unilateral yaw from ipsi_bias sign.

`python scripts/leftover_map.py` → **21/30 mapped**. See `docs/LEFTOVER.md`. Do not invent dumps.

`python scripts/leftover_solve.py --hops` → ToE solve: partner-side **89.7%**; TBD **motor_on 45.87**; birth **13728 early**. Analog jobs for haltere/atlas/pupa.

`python scripts/leftover_margin.py` → Lean **5/5 green** (2 wrong-object retired). Predicted VNC sides **9/14** in `data/vnc_side_predicted.json`.

`python scripts/predicted_side_hops.py` → predicted L/R as hop observers. R ipsi **−0.84**; L sign +; leftover five ~0. Not EM.

Bill-0 freeze → TED-1 (predicted observers) → **Bill-1**. Ledger: `Bill and Ted fly adventures/`. GitHub: https://github.com/dappalumbo91/bill-and-ted-fly-adventures (Apache-2.0).

**Adventure 1 / TED-2 → Bill-2:** neuromod hops. DA 0.041 leftover, OA 0.80 leftover, 5HT 4.70 < VNC walk/φ. Volume = observer, not extra edges. Gap junctions: consensus analog (no EM list). Off-domain text not mapped onto \(W\). `Bill and Ted fly adventures/Adventure-1/FINDINGS.md`

Fold: live UniProt **9/9** biosynthetic enzymes sit on NT jobs. Biochem vs Neuro |S| look-split **0.494% ≤ 0.5%**. Zig DA→MB: fly DA motor leftover is the **correct application** (not a walk seed). Pin edition: Zig D1D38A, pack AEB2AD — same law, hops stay AEB2AD.

Genetic interactions **17/17** + peptides/clock **28/28** + baseline rest **47/47**. Orco sits on olfactory leftover (hop-2 0.0006). ChT pinned Q9VE46 (not chaoptin). tan pinned Q9W369 (gene *t*). ~105 seated genes. Still Adventure 1.
