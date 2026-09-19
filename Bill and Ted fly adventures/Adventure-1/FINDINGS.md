# Adventure 1 — neuromod, gaps, snapshot, off-domain

TED-2 vs Bill-1. Pin AEB2AD. 0 free parameters.

## Paper positives → FSOT (already on Bill)

VNC sensory hop-2 vnc_motor 10.74; JO descending 24.21 is high-level. Local modules in the cord; brain issues direction. Matches the article.

L5 vision: legs off, descending 1.92. DNp01 escape desc 15.77. Not a trained voltage model.

We do not prune a dense ANN onto FlyWire. W is measured. 0 free params.

## Shortcomings → FSOT solve

### neuromod_volume

DA/5HT/OA are observers (T1 / overlay), not new edges. Volume transmission = leftover of chemical W. No invented octopamine rewires.

### gap_junctions

EM misses electrical synapses. FSOT analog is consensus trit (bidirectional: a if a=b else 0) — speed without a fake gap list.

### single_snapshot

Male + BANC + hemibrain + larva are four measured graphs, not one insect. Predicted sides / TBD hops are adaptation, labeled predicted.

### off_domain_text

Topology is low-dimensional sensory-motor. Trit ALU + overlay leftover IS the bound. We do not map email classification onto W.

### simulation_collapse

Inf-norm + GABA sign + observer off = no hyper-excited silent trap from unconstrained voltage. Rest is leftover, not a stuck attractor.

## Neuromod hops (Male CNS consensus_nt)

| NT | n_seed | hop-2 vnc_motor | walks |
|----|-------:|----------------:|:-----:|
| dopamine | 392 | 0.041395377371460616 | False |
| serotonin | 48 | 4.695936959278612 | True |
| octopamine | 101 | 0.799930297424188 | False |
| histamine | 5910 | 2.9700420343458376 | True |
| gaba | 22055 | 28.747975630228993 | True |

Volume leftover vs VNC walk/φ: **True**

## Worked

- DA/5HT/OA hop-2 vnc_motor weaker than VNC walk / φ (volume leftover)
- GABA remains the signed brake on measured W
- off-domain text not forced onto the graph

## Did not (honest leftover)

- no EM gap-junction list — consensus analog only

## Math applied

\(S=K(T_1+T_2+T_3)\), \(a\leftarrow rWa\), overlay \(1/\varphi\), consensus trit, GABA sign on \(W\).
Neuromod = observer (T1), not a new synapse list.
