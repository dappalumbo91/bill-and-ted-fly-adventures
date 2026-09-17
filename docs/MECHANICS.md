# Mathematical mechanics of the fly pack (reverse map)

Pin **AEB2AD**. Law does not change. Every function below is the same scalar, residual, overlay, and trit. **0 free parameters.** Reverse: from an outcome, read the observer — do not fit a new net.

Living log: `RUNNING.md`. Hub: [FSOT-2.1-Lean](https://github.com/dappalumbo91/FSOT-2.1-Lean).

---

## Engine (one)

\[
S = K(T_1+T_2+T_3),\qquad r = 1+|S|\cdot P_{\mathrm{NEW}}
\]

Biochemistry nest \(D_{\mathrm{eff}}=10\) → \(r \approx 1.284069\).

Hop on measured \(W\) (synapse counts; GABA outgoing \(-\)):

\[
a \leftarrow r\,Wa,\qquad a \leftarrow a/\|a\|_\infty
\]

Inf-norm cancels global \(r\). The split is signed \(W\).

| Object | Formula | Reverse |
|--------|---------|---------|
| Overlay | \(\lvert x\rvert > 1/\varphi\) | Below cut → leftover, do not collapse |
| Active | \(\lvert a_i\rvert > \max\lvert a\rvert/\varphi\) | Sparse leftover after hop-1 |
| Consensus trit | \(a\) if \(a=b\) else \(0\) | Disagreement stays superposed |
| Leftover hops | \(\mathrm{round}(\varphi^5)=11\) | Horizon, not a fitted \(T\) |
| Integer | balanced ternary on \(\mathbb{T}=\{-1,0,+1\}\) | Carry is a trit |
| Wingbeat (plant) | \(200\,\mathrm{Hz}\) in band \(150\)–\(250\) | Species fact; not this clip |

---

## Functions → mechanics

| Function | Observer (measured) | hop-2 readout | Mechanic | Reverse |
|----------|---------------------|---------------|----------|---------|
| Rest | no afferent | 0, 0 | leftover | odor off ∧ motion under MAD+\(\varphi\) |
| Walk | VNC sensory | vnc_motor **10.74**, desc **11.39** | legs ∧ descending already on | ball hid takeoff |
| Hear / steer | JO | vnc **7.77**, desc **24.21** | strongest descending | hop-1 **DNg29** |
| Object | mechanosensory | 7.55 / 13.89 | tarsus/bristle | Iwasaki analog |
| See | L5 lamina | vnc **0.001**, desc **1.92** | **flight_only** | visual DNs, not legs |
| Smell | ORN | vnc **0.001**, desc 0.57 | leftover LN **il3LN6** | not a thought |
| Mushroom | KCg-m | ~0 / 0.05 | leftover **APL** | not a thought |
| Escape | DNp01 (n=2) | vnc 5.80, desc **15.77** | giant-fiber analog | do not swap with hg3 |
| Steering muscle | hg3 MN (n=2) | vnc **4.82**, desc 1.51 | local VNC | song/steer, not GF |
| Sleep | DAM leftover-long inactivity | — | leftover rest | ~17% bins, night/day \(\varphi\)-ish |
| Courtship / aggression | fru / labeled | — | **DENY** default | labels stay; observer off |
| Wings (clip) | Th-lWing / Th-rWing 400 Hz | peak 4–9 Hz | **parked** | glue + Nyquist |
| Wings (plant) | descending > 1 | 200 Hz @ 2 kHz | untethered sinusoid | camera 400 Hz aliases 200 Hz |

Untethered walk is **takeoff_both**: the graph already sent descending 11.4. L5 is the clean **flight_only** test.

---

## Spatial / trit (the fly’s arithmetic)

Laterality is in \(W\): VNC sensory L → motor L bias **+0.342**; R → **−0.362**. JO L **+0.246**; R **−0.239**.

Integer ALU: 128/128 unit tests; 27/27 hop-count word problems; 10/10 multi-step chains; 21/21 typed expressions (`JO_L + JO_R - JO_h1`).

Heading leftover: trial-mean (R−L) under \(1/\varphi\) on all three clips. Fly02 miss = 28 right vs 16 left **frames**. `cons(T001, Fly02)=0` — do not vote.

---

## Stress ≠ new axons

Hop-1 collapse \(\ge \varphi\) is pressure.

| Locus | Collapse | Kind | Expansion |
|-------|----------:|------|-----------|
| olfactory → il3LN6 | 1319× | leftover hub | **do not** |
| Kenyon → APL | 963× | leftover hub | **do not** |
| VNC / mechanosensory IN | ~335–560× | command bottleneck | residual on that **measured** type |
| JO → DNg29 | 672→3 | walking/steer command | already hopped both sexes |
| DNp01 | n=2 | escape | plant driver |

Evolutionary analog: seed the measured bottleneck type. Never invent edges.

---

## Advice (from the outcomes) → next tests

1. Dual effectors (walk∧fly) are a feature. Ball hid takeoff.
2. L5 = visual flight without legs.
3. DNp01 ≠ hg3 MN.
4. Do not grow APL / il3LN6.
5. Watch consensus 0 (heading leftover) as thought-stress.
6. **Yaw from JO_L vs JO_R** (measured cells) — `scripts/yaw_jo.py`.

Reverse recipe: outcome → which observer was on → overlay → trit. If leftover, say leftover.

Every leftover we owe is named in `docs/LEFTOVER.md`. Solved under ToE in `data/leftover_solve.json`. Lean margin: `data/leftover_margin.json` (classifier ≥99.5%, scalar ≤0.5%).
