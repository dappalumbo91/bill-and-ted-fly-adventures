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

Scripts: `python scripts/bill_ted.py freeze` · `python scripts/bill_ted.py ted-1` · `python scripts/bill_ted.py ledger`

Data: `Bill and Ted fly adventures/ledger.json`
