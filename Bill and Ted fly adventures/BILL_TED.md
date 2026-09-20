# Bill and Ted’s fly adventures

Two copies of the **same FSOT residual organism**. Not trained weights. Not a second theory.

| Name | Role |
|------|------|
| **Bill** | Baseline frozen fly “net” — measured \(W\), pin AEB2AD, Lean gates. Saved state. |
| **TED-\(n\)** | Experiment \(n\): new observer, leftover solve, or plant. Same law, no new knobs. |
| **Bill-\(k\)** | A TED that **earned** promotion: Lean classifier ≥99.5% / scalar ≤0.5% *or* same function sign as Bill on empirical hops, without violating 0 free parameters. |

Pin **AEB2AD**. Law \(S=K(T_1+T_2+T_3)\). Residual hops on measured synapses. Overlay \(1/\varphi\). Consensus trit.

## How a TED becomes a Bill

1. Freeze current Bill (hash `data/*.json` + `vendor/fsot_compute.py`).
2. Run TED-\(n\) (one change).
3. Compare: function (ipsi sign, motor_on, overlay leftover) vs Bill; Lean margin if it’s a classifier/scalar.
4. If TED wins or **extends** Bill without breaking gates → copy the experiment into **Bill-\(k\)** (\(k\) counts up).
5. If TED fails → keep the JSON; Bill stays. Leftover, not a fit.

## Roster

| ID | What | Outcome |
|----|------|---------|
| **Bill-0** | Pack freeze at predicted-side solve, AEB2AD, leftover_margin 5/5 | baseline |
| **TED-1** | 9 predicted VNC sides as hop observers | ipsi_pair; R overlay −0.84; L sign + | → **Bill-1** |
| **Bill-1** | Bill-0 + predicted observers (labels still *predicted*, not EM) | promoted from TED-1 |
| **TED-2 / Adventure 1** | DA/5HT/OA hops as volume observers; gap analog; snapshot; off-domain bound | volume leftover vs VNC walk → **Bill-2** |
| **Bill-2** | neuromod is observer/volume, not step micro-management | promoted from TED-2 |
| **TED-3 / Adventure 1 verification** | genetic blueprint through FSOT (F02, residual hops, overlay, trit). Not Adventure 2. | Bill-2 function + Lean 0.5%/99.5% hold → **Bill-3** |
| **Bill-3** | Adventure 1 blueprint verified | promoted from TED-3 |
| **TED-4 / Adventure 2** | Bill-3 math environments + hop thinking traces; PhD FSOT identities | **37/37** → **Bill-4** |
| **Bill-4** | Bill-3 under math/thinking test | promoted from TED-4 |
| **TED-5 / Adventure 2** | conventional math courses (Z, Q, algebra, geometry, trig, calculus, lin alg, stats, logic) on trit ALU | **58/58** → **Bill-5** |
| **Bill-5** | community mathematics on the same substrate | promoted from TED-5 |
| **TED-6 / Adventure 2** | real analysis, multivariable calculus, ODEs on the 200 Hz wing plant | **46/46** → **Bill-6** |
| **Bill-6** | analysis + plant oscillator | promoted from TED-6 |
| **TED-7 / Adventure 2** | math expansion + STM/LTM exam (encode, interfere, retrieve) | **36/36** → **Bill-7** |
| **Bill-7** | memory stores mapped: STM register, LTM \(W\), KC leftover | promoted from TED-7 |
| **TED-8 / Adventure 2** | STM \(\varphi^2\) window + LTM class index; growth map; no new axons | **28/28** → **Bill-8** |
| **Bill-8** | STM 3 slots; LTM bindings; `docs/MEMORY_LIMITS.md` | promoted from TED-8 |
| **TED-9 / Adventure 2** | residual-seed command bottlenecks as splice-ready modules | **5/6** live hops → **Bill-9** |
| **Bill-9** | current | DNg29, IN01B001, IN05B011a, PS100, AN05B009 grown; INXXX007 leftover |

Scripts: `python scripts/bill_ted.py freeze` · `ted-1` … `ted-8` · `python scripts/bill8_grow_bottlenecks.py` · `ted-9` · `ledger`

Data: `Bill and Ted fly adventures/ledger.json`
