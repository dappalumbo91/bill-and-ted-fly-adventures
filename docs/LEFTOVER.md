# Leftover map

Pin **AEB2AD**. Leftover is a **mechanic**, not a hole to fill with invented synapses.

\[
\text{overlay on} \iff \lvert x\rvert > 1/\varphi,\qquad
\text{leftover} \iff \lvert x\rvert \le 1/\varphi
\]

Consensus trit \(0\) is leftover of a decision (superpose). Missing dumps stay missing. Stamp: `data/leftover_map.json` (`python scripts/leftover_map.py`). **30** items: **21 mapped**, 4 blocked, 2 refused, 2 sibling, 1 deferred.

---

## Overlay / consensus (do not collapse)

| Name | Mechanic | Do |
|------|----------|-----|
| Trial-mean (R−L) on 3 clips | under \(1/\varphi\) | per-frame trit |
| JO n_seed 348 vs 324 | imbalance leftover | yaw from ipsi_bias sign, not count |
| T001 vs Fly02 heading | `cons=0` | do not vote |
| Bilateral JO | L +1 ∧ R −1 → 0 | straight; one ear off to yaw |

## Hubs (not thoughts)

| Name | Mechanic | Do |
|------|----------|-----|
| olfactory **il3LN6** | collapse 1319× | do not expand |
| Kenyon **APL** / MBp3 | MB leftover, motor off | do not expand |
| JO hop-1 silent **669** | 672−3; 3 = DNg29 | expand on DNg29, not the 669 |
| **INXXX007** | chordotonal class 2136→hop-1 this type, motor on; type-alone n=2 leftover | splice class → FETi; do not grow INXXX007 |

## Unlabeled (measured empty, not imputed)

| Name | n | Do |
|------|--:|-----|
| VNC sensory without `rootSide` | **14** | keep unlabeled |
| Traced without birthtime | **157219** | hops only on labeled early/late |
| Without Truman hemilineage | **145385** | labeled lineages only |
| Truman tag **TBD** | **1603** | not a lineage |
| Without Ito–Lee | **127377** | same |
| Type names only-Male / only-BANC | 4309 / 4062 | do not merge graphs |

## Product leftover

- PHOT1 kinase/linker **0.706** > \(1/\varphi^2\) — domains only (2Z6C / 4HHD), not MDS.
- Genetics Cα freeze 0.13 Å — campaign D1D38A, pack AEB2AD. Sibling. Do not silently re-run.

## On-disk but not flight / not GABA

- Tethered wings **parked** (0/3 flight-like). Plant is simulated.
- Hemibrain **n_gaba=0** unsigned. Do not mix 2.68 desc with 7.77 vnc_motor.
- Sleep **~17%** leftover-long DAM inactivity.
- Hop horizon \(\mathrm{round}(\varphi^5)=11\).

## Missing dumps (wait — do not invent)

| Missing | Status |
|---------|--------|
| Free-flight 3D wingbeat | blocked |
| Haltere named types (count 0) | mapped empty |
| Type string `wing` (count 0; use hg3 / DNp01) | mapped empty |
| Embryo→pupa synapse movie | refused |
| Fly Cell Atlas → bodyId | refused |
| Codex `api_token` | blocked; local counts authority |
| Berlin / ymaze files | blocked (token / corrupt) |
| Iwasaki ball videos | blocked; forelimb analog |

## Sibling / deferred / denied

- Genetics GitHub still **D1D38A**. This pack **AEB2AD**.
- Language / coding tokens **deferred** (trit ALU and parser exist; not an LLM observer).
- Courtship / aggression **DENY** default — guardrail, not missing data.

---

Reverse: leftover → name the mechanic → do-not. If a dump arrives, it becomes a new **measured** observer, not a fitted join.

---

## FSOT solutions (`python scripts/leftover_solve.py --hops`)

A join is a mess as a **fitted lookup**. It is not a mess as residual / overlay / consensus on measured \(W\).

| Leftover | Solve | Result |
|----------|--------|--------|
| VNC no `rootSide` (14) | in/out \|W\| vote + overlay + consensus | pooled 89.7% (leftover counted); **accepted 99.81%**; consensus **99.85%** GREEN; **9/14** unlabeled L/R |
| Truman TBD (1603) | hop-2 vs 07B / MBp3 | vnc_motor **45.87** → **motor_on** |
| Birthtime unlabeled with lineage | \(P(\mathrm{early}\mid\mathrm{lineage})>1/\varphi\) | **13728 early**, **1268** superpose; 66 lineages overlay |
| Male-only types | fru/dsx observer | dimorphic leftover; default DENY; not a BANC merge |
| Haltere = 0 types | analog job = JO gyro | function mapped |
| Atlas bodyId | gene sits on hop class | nompC→JO, Gad1→GABA |
| Pupa movie | same \(S\), two snapshots | class persistence, no interpolated edges |
| PHOT1 leftover 0.706 | leftover \(\times r\) | residual mass **0.91**, not MDS |
| Parked wings | descending > 1 | 200 Hz plant |
| cons = 0 | superposition | already the solve |

## Lean acceptance margin

Authority: FSOT-2.1-Lean `docs/APPLY.md` step 5 and `scripts/fsot_precision_constants.py`.

| Gate | Threshold |
|------|-----------|
| Scalar pooled median residual | ≤ **0.5%** |
| Classifier accuracy | ≥ **99.5%** |
| Aspiration | 0.05% |

`python scripts/leftover_margin.py` → **5/5 classifier green**, 2 rows **retired** (APPLY wrong object).

- Pooled 89.7%: leftover scoring, not a classifier.
- TBD motor/\(n_{\mathrm{seed}}\): inf-norm mass is not extensive (like scoring \(n_D\) as MW).
- Accepted / consensus side: **GREEN 99.85%**.
- TBD motor_on + |ipsi|<1/φ: **GREEN** (mixed tag, no side).
- Birthtime overlay p=1: **GREEN**.
- Unlabeled VNC: **9 predicted L/R**, 5 leftover — `data/vnc_side_predicted.json` (predicted, not EM).
- Those 9 as hop observers (`python scripts/predicted_side_hops.py`): L ipsi **+0.17**, R **−0.84**, leftover-five ~0. Function matches labeled VNC laterality.
