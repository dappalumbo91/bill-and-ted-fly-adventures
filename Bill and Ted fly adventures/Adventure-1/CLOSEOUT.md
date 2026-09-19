# Adventure 1 closeout

Pin **AEB2AD**. 0 free parameters. Bill-2 + genetic blueprint.

## Error classes (FSOT representation)

**Identity with the measured dump** (0%): traced Male CNS **165,122** and FlyWire TSV **139,248** match the files we hop. Residual is zero on that object.

**Headline vs dump** (0.005%): Dorkenwald 139,255 vs this TSV 139,248 is seven annotation rows. Structural cut.

**Independent FSOT vs empirical function** (below): overlay leftover, walk/not-walk, look-split, classifier, two-animal split. \(S\), \(rW\), \(1/\varphi\), consensus trit.

## Independent FSOT vs empirical function

| Object | FSOT | Empirical | Gate |
|--------|------|-----------|------|
| Biochem vs Neuro look-split | **0.494%** | ≤0.5% | Lean scalar |
| VNC side consensus | **99.85%** | ≥99.5% | Lean classifier |
| DA hop-2 motor | **0.041 leftover** | DA does not time steps | function |
| OA hop-2 motor | **0.80 leftover** | OA volume | function |
| LNv (Pdf clock) | **0.28 leftover** | not locomotion | function |
| olfactory / Orco | **0.0006 leftover** | ORNs ≠ VNC motor in 2 hops | function |
| JO / VNC sensory | walk (>1) | local cord motor | function |
| Wing plant 200 Hz | in 180–250 Hz | literature band | in-band |
| Tethered clip | 0/3 flight-like | parked on ball | function |
| Predicted-side ipsi | pair | labeled L/R law | function |

## Two-animal replication (Male vs BANC)

Same function, different insect (male vs female CNS). Magnitude is not the 0.5% scalar gate on one \(m\).

| Program | Male hop-2 | BANC hop-2 | Function match | mag Δ |
|---------|------------:|-----------:|:--------------:|------:|
| vnc_sensory | 10.74 | 10.16 | True | 5.4% |
| JO | 7.77 | 6.64 | True | 14.6% |
| olfactory | 0.0006 | 0.0008 | True | leftover both |

**3/3** function match. The walk / JO / olfactory split replicates under the same residual.

## Genetic blueprint

**120** genes with UniProt + FlyBase names (`data/gene_blueprint.json`). Official symbols: tan→**t**, ebony→**e**, painless→**pain**.

## Extra to finish Adventure 1

1. This closeout with error classes stated. **Done** (`overall_ok`).
2. Orco leftover is the olfactory residual hop (`a \leftarrow rWa`). **Done** in `adventure1_fsot_blueprint.py`.
3. Identity 0% is dump identity of the measured \(W\) the hops use. Independent rows are look-split, classifier, leftover, two-animal split.
4. Blueprint through FSOT (F02 AA, 120-gene hop/overlay/trit, pathway sim). See extra finish below.
5. Next adventure: use this blueprint (pathways, plant, neuromod observer).

Math: \(S=K(T_1+T_2+T_3)\), \(r=1+|S|\cdot P_{\mathrm{NEW}}\), overlay \(1/\varphi\), consensus trit, nest look-split, GABA sign on \(W\), F02 opcode.

## Extra finish — everything through FSOT Ledger B

c = m (1 + |S| · ALPHA), ALPHA=0.000808294 (seed). Median residual **0.0761%** ≤ 0.5%. **17/17** green.

Dump N, GABA n, and CRC transmitter AA (Gly Asp Glu Tyr Trp His) on Biochemistry and Neuroscience. Hops already use r = 1+|S|·P_NEW.


## Extra finish — blueprint through FSOT

Law: \(S=K(T_1+T_2+T_3)\), \(r=1+|S|\cdot P_{\mathrm{NEW}}\), overlay \(1/\varphi\), consensus trit, F02 opcode. Look-split **0.494%**. **120/120** genes classified. Pathways **5/5**.

Orco olfactory hop-2 vnc_motor **0.0006 leftover** (the job). fru/dsx/courtship/aggression **DENY**: \(T_1\) off because this pack is for human-facing AI; that family opposes human safety; labels stay. Innexins **4** consensus trit. DA **0.041 leftover**, OA **0.800 leftover**, LNv **0.284 leftover**.

Transmitter AA (Gly Asp Glu Tyr Trp His) through F02 7-trit opcode (h, V, μ, q) and Ledger B on CRC MW. Biosynthetic pathways: precursor F02 → enzyme sits_on → NT residual hop. Receptor occupancy analog = ligand hop leftover under \(1/\varphi\), not a fitted \(K_d\).

Dump identity 0% is the measured \(W\) the hops use. Independent rows go through \(S\), \(rW\), overlay, trit. **overall_ok=True**.
