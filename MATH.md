# FSOT mathematics on this fly pack

Pin **AEB2AD** (`vendor/fsot_compute.py`). **0 free parameters.**  
Hub: [FSOT-2.1-Lean](https://github.com/dappalumbo91/FSOT-2.1-Lean). Genetics twin: [FSOT-Genetics](https://github.com/dappalumbo91/FSOT-Genetics).

## Scalar law

\[
S = K(T_1 + T_2 + T_3)
\]

| Term | What it is here |
|------|-----------------|
| \(T_1\) | Observer-modulated base. Backbone geometry: observer **off**. Chemical links: observer **on**. |
| \(T_2\) | Scale · amplitude (pin defaults). |
| \(T_3\) | Valve + chaos \((D-25)/25\) + poof/suction + acoustic \(\delta\theta\). |

Seeds \(\{\pi,e,\varphi,\gamma\}\) only. Domain \(D_{\mathrm{eff}}\) is the **AEB2AD nest** (not a fitted dimension, not a free continuous \(D\)). Genetics decimal-knob edition D1D38A used named pin-table rows; this pack follows Lean hub nest depths.

## Residual (the hop)

\[
r = 1 + |S|\cdot P_{\mathrm{NEW}}
\]

On Biochemistry (nest \(D_{\mathrm{eff}}=10\)), live value **\(r \approx 1.284069\)**. Each hop:

\[
a \leftarrow r\, W a,\qquad a \leftarrow a / \|a\|_\infty
\]

The inf-norm reset makes a **global** \(r\) cancel: Male/BANC/hemibrain hop-2 masses on AEB2AD match the D1D38A freeze to \(\sim 10^{-15}\). Signed GABA and measured \(W\) set the split. ChemLink \(D_{\mathrm{eff}}\) still changed with the nest.

\(W_{ij}\) = **measured synapse count** (GABA outgoing is inhibitory). Hop count leftover \(\varphi^5\). Active if amplitude \(> 1/\varphi\). Overlay cut = observer-max \(/\varphi\).

This is the fly “net.” It is not backprop.

## Chem-link \(D_{\mathrm{eff}}\) (Lean)

| Link | Domain | \(D_{\mathrm{eff}}\) (AEB2AD nest) |
|------|--------|---------------------:|
| backbone | Physical_Chemistry | 6 |
| disulfide | Atomic_Physics | 6 |
| salt bridge | Electromagnetism | 7 |
| hydrophobic pack | Condensed_Matter | 11 |
| H-bond secondary | Chemistry | 6 |
| molecular sidechain | Molecular_Chemistry | 7 |
| tertiary biochem | Biochemistry | 10 |

Theorems in `lean/ChemLink.lean`, `lean/Observer.lean` (backbone unobserved), `lean/SeedsReal.lean` (residual \(\ge 1\)).

## Trinary genetics

\[
\text{codon} \to (\text{primary},\text{secondary})\ \text{trits} \to \text{AA} \to \text{7-trit opcode }(c,p,v,\mathrm{aro},\mathrm{br},\mathrm{het},\mathrm{det})
\]

F01 \((c,p,v)\) collides. Expanded word is **20/20 unique**. Pair weight:

\[
\begin{aligned}
\mathrm{geom} &= \varphi\cdot d^{-1/\pi} \\
\mathrm{base} &= \tau_i\tau_j\, e + (1-|\tau_i\tau_j|)\,\pi \\
\mathrm{elec} &= -q_i q_j e \\
\mathrm{env} &= d/(d+\pi e) \\
w &= \mathrm{geom}\cdot(\mathrm{base}+0.15\,\mathrm{elec})\cdot(0.35+0.65\,\mathrm{env})
\end{aligned}
\]

Check: \(w(F,W,d{=}8)=1.670052\). Code: `scripts/trinary_syntax.py`. Maps: `formulas/`.

## Product Cα (proteins on the graph)

Measured homolog template + residual packing. Same-data freeze: **0.13 Å** vs AF **0.47 Å** (\(n=10\)). No homolog → `no_measured_map` (Rg + secondary), not MDS bulk.

Close-homolog identity \(\ge 1/\varphi\). Leftover coverage floor \(1/\varphi^2\).

## What a hop number is

Not RMSD. Seed a **measured** sensory class. After two residual hops, does `vnc_motor` light?

| Seed | Male hop-2 | BANC hop-2 |
|------|-----------:|-----------:|
| VNC sensory | 10.74 | 10.16 |
| JO | 7.77 | 6.64 |
| olfactory | 0.001 | 0.0008 |

Genes sit on those classes (`MAP.md`). They do not replace synapses.

Reverse map of **all** pack functions (walk, see, hear, wings, stress, trit): `docs/MECHANICS.md`.
