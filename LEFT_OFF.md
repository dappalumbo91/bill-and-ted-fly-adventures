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

Default human-facing seeds: JO / VNC sensory / GABA **on**. Courtship, aggression, *fru*/*dsx* **off** (\(T_1\)): this pack is for human-facing AI; that family opposes human safety; labels stay measured. Consensus trit = agree or superpose. Overlay cut \(1/\varphi\). Do not delete types. Do not call olfactory leftover a thought. New brain regions = residual on **measured** classes (Kenyon), not invented axons.

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

Adventure 1 extras: Ledger B on dump N, GABA n, CRC transmitter AA — **17/17** green, median **0.076%**. Blueprint through FSOT: **120/120** genes (hop residual / overlay / trit / DENY / excitatory \(W\) / effector); pathways **5/5** (F02 precursor → enzyme → \(a\leftarrow rWa\)). Orco leftover 0.0006. fru/dsx/courtship/aggression DENY: \(T_1\) off — this pack is for human-facing AI; that family opposes human safety; labels stay. Hops already r=1+\|S\|P_NEW.

**TED-3 (still Adventure 1, not Adventure 2):** blueprint verification vs Bill-2 **28/28**. Bill function holds. Lean gates hold. **Promoted → Bill-3.** `python scripts/adventure1_verify.py` · `python scripts/bill_ted.py ted-3`

**TED-4 / Adventure 2:** Bill-3 through math environments + thinking traces **37/37**. Maze/yaw/walk/smell/neuromod/trit ring/PhD (φ, ALPHA, nest \(D_{\mathrm{eff}}\), \(S\), look-split, F02). Monitor: residual hops on measured \(W\); types lit include JO-A2, DNg29, IN05B011a, il3LN6. Courtship/aggression not seeded. **Promoted → Bill-4.** `python scripts/bill3_math_env.py` · `python scripts/bill_ted.py ted-4`

**TED-5:** conventional math courses on the same substrate **58/58**. Integers, rationals, algebra, geometry, trig, combinatorics, number theory, 2×2 linear algebra, polynomial calculus, stats on JO counts, logic/sets. Answers in community notation. **Promoted → Bill-5.** `python scripts/bill4_math_courses.py` · `python scripts/bill_ted.py ted-5`

**TED-6:** real analysis (series, IVT, MVT, Taylor, ε-δ), multivariable (partials, Clairaut, Green, chain), ODEs on the 200 Hz wing plant \(\ddot y+\omega^2 y=0\) when descending \(>1\). Smell leftover = rest. L5 flight_only. **46/46. Promoted → Bill-6.** `python scripts/bill5_analysis.py` · `python scripts/bill_ted.py ted-6`

**TED-7:** more math (complex, Fourier, probability, generating functions) + STM/LTM exam. STM = last ALU/observer (first item missed after overwrite). LTM = measured \(W\) (10/10 delayed recall after interference; JO/VNC/KC pathways unchanged). KC hop-1 **APL** leftover — do not expand. **36/36. Promoted → Bill-7.** `python scripts/bill6_memory.py` · `python scripts/bill_ted.py ted-7`

**TED-8:** STM window \(\mathrm{round}(\varphi^2)=3\); LTM bindings on measured classes (JO, VNC, KCg-m, DNp01, mechanosensory); APL/il3LN6 write refused. Growth map: leftover hubs never; command bottlenecks (IN01B001, PS100, AN05B009, INXXX007) later residual seed. Document: `docs/MEMORY_LIMITS.md`. **28/28. Promoted → Bill-8.** `python scripts/bill7_memory_expand.py` · `python scripts/bill_ted.py ted-8`

**TED-9:** live residual-seed command types **5/6**. DNg29 desc 9.20/7.81 both sexes; PS100 vm 3.27; AN05B009 desc 1.14; IN01B001/IN05B011a command at hop 3–4. INXXX007 isolated leftover (chordotonal *class* is the job). Splice law: not fly-only forever; new regions later = named job + residual, not APL. `docs/GROWTH_REGIONS.md`. **Promoted → Bill-9.** `python scripts/bill8_grow_bottlenecks.py` · `python scripts/bill_ted.py ted-9`

**TED-10:** INXXX007 leftover **solved**. Chordotonal class n=2136 hop-2 vm **5.01** command; INXXX007 n=2 leftover (XXX unlabeled); DNg29 n=2 still commands (contrast). Class hop-3 effector **tibia_extensor_FETi**; live BANC n=6 hop-2 vm **9.19**. Do not grow INXXX007. Splice **class → FETi**. **9/9. Promoted → Bill-10.** `python scripts/bill9_inxxx_leftover.py` · `python scripts/bill_ted.py ted-10`

**TED-11:** remaining leftovers **18/18**. Map **26/35**. Blocked 4 wait (free-flight, Codex, Berlin, Iwasaki). Refused 2. Sibling pins. Language deferred splice. VNC 5 trit 0. Male FETi analog BANC. `docs/LEFTOVER_REMAINING.md`. **Promoted → Bill-11.** `python scripts/bill10_remaining_leftovers.py` · `python scripts/bill_ted.py ted-11`

**TED-12:** **why 26/35** = 26 `status=mapped` + 9 blocked/refused/sibling/deferred. Those 9 analog-joined. Map **35/35**. Dumps still missing. **21/21. Promoted → Bill-12.** `python scripts/bill11_map_all.py` · `python scripts/bill_ted.py ted-12`

**TED-13:** language spliced as invented region. Trit ALU + closed lexicon. Commands at **IN05B011a / DNg29 / IN01B001 / DNp01**. Unknown leftover. Courtship DENY. Not on FlyWire \(W\). Never APL/il3LN6. **61/61. Promoted → Bill-13.** `python scripts/bill12_language_splice.py` · `python scripts/bill_ted.py ted-13`

**TED-14:** coding tokens on that region: `let` / `if`/`else` / `while` (horizon \(\varphi^5=11\)) + trit functions. `let a = JO_L + JO_R` → 672. Courtship names DENY. Not on \(W\). **41/41. Promoted → Bill-14.** `python scripts/bill13_coding_tokens.py` · `python scripts/bill_ted.py ted-14`

**TED-15:** host-eval trit coding vs restricted Python sandbox **7/7**. Unrestricted eval/import is host attack surface. Safety hops T1 off: pC1 n=156 desc **30.94**, TN1 n=35 vm **10.07**, fru/dsx n=5012 desc **35.21** — family *would* command if seeded. Language/code still DENY. **33/33. Promoted → Bill-15.** `python scripts/bill14_host_eval.py` · `python scripts/bill_ted.py ted-15`

**TED-16:** unseen open math (NAEP G4 sample + IM CC BY). Blind language+ALU **0/22** (word leftover; some false ALU on "times"). Named leftover jobs (percent, ratio, linear) **22/22**. Not an LLM test. **Promoted → Bill-16.** `python scripts/bill15_unseen_math.py` · `python scripts/bill_ted.py ted-16`

**TED-17:** Blind was leftover + “times” misfire, not a retry. Dictionary/grammar senses: *times as many* = divide. Wikipedia leftover, not over \(W\). Pack-new vs known connectomics: `docs/DISCOVERIES.md`. **13/13. Promoted → Bill-17.** `python scripts/bill16_word_sense.py` · `python scripts/bill_ted.py ted-17`

**TED-18 (Adventure 1 teaching):** adaptive grammar on the prompt, **not** one schema per item. Unseen IM/NAEP **22/22**, LTM bind 22. Teaching trajectory (hops that held across Bills) is data: `docs/LEARNING.md`. **Promoted → Bill-18.** `python scripts/bill17_adaptive.py` · `python scripts/bill_ted.py ted-18`

**TED-19:** teach the procedure, then new numbers. Overlay vs leftover = usable vs resistance. Reward trit +1/0/−1; DA leftover \(T_1\) binds LTM; 5HT leftover on error. No new synapses. Transfer **6/6**, retention after interference. **Promoted → Bill-19.** `python scripts/bill18_bio_teach.py` · `python scripts/bill_ted.py ted-19`

**TED-20:** read decode + write encode; school exam **11/11** (math, commands, code, deny, retain). Capability ledger vs LLM end. Curriculum sources (OpenStax, DeepMind math, ARC, G:\\AI_Datasets) mapped as JSON Q&A analog. **Promoted → Bill-20.** `python scripts/bill19_read_write.py` · `python scripts/bill_ted.py ted-20`

**TED-21:** G:\\AI_Datasets zips empty. Ingested DeepMind-style algorithmic JSON **48/48** (8 kinds × 6). Mix read/write/deny 3/3. Bank `data/ingest_deepmind_style.json`. **Promoted → Bill-21.** `python scripts/bill20_ingest.py` · `python scripts/bill_ted.py ted-21`

**TED-22:** OpenStax Prealgebra 2e (CC BY-NC-SA) **15/15**. Sequential Ch.1 then integers. `1683+49` computed **1732** (published key 2162 does not match those addends). **Promoted → Bill-22.** `python scripts/bill21_openstax.py` · `python scripts/bill_ted.py ted-22`
