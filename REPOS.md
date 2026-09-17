# GitHub repositories this fly pack sits on

Same pin **AEB2AD** as [FSOT-2.1-Lean](https://github.com/dappalumbo91/FSOT-2.1-Lean). This folder is a working copy of fly + genetics findings, not a new theory. Previous pack pin was D1D38A (Genetics decimal-knob edition).

## Required for this pack

| Repo | Role |
|------|------|
| [FSOT-Genetics](https://github.com/dappalumbo91/FSOT-Genetics) | Fly hops, product Cα, trinary, homologs, analog pointer |
| [FSOT-2.1-Lean](https://github.com/dappalumbo91/FSOT-2.1-Lean) | Scalar law hub, multi-prover gauntlet |
| [fsot-neuron-zig](https://github.com/dappalumbo91/fsot-neuron-zig) | Neural mind kernel; genetic pair geometry twin |
| [FSOT-2.1-Neural](https://github.com/dappalumbo91/FSOT-2.1-Neural) | Neural substrate / Allen bio lock (mouse wet-lab, not fly synapses) |

## Same-engine siblings (reference, not loaded here)

| Repo | Role |
|------|------|
| [FSOT-2.0-code](https://github.com/dappalumbo91/FSOT-2.0-code) | FSOT 2.0 source |
| [fsot-neuron-haskell](https://github.com/dappalumbo91/fsot-neuron-haskell) | Haskell neuron twin |
| [fsot-neuron-idris](https://github.com/dappalumbo91/fsot-neuron-idris) | Idris2 neuron twin |
| [FSOT-Reality-OS](https://github.com/dappalumbo91/FSOT-Reality-OS) | Host kernel |
| [FSOT-Chua-Circuit](https://github.com/dappalumbo91/FSOT-Chua-Circuit) | Circuit gauntlet pattern |
| [FSOT-Materials](https://github.com/dappalumbo91/FSOT-Materials) | Materials / fuel lab |
| [FSOT-Quantum](https://github.com/dappalumbo91/FSOT-Quantum) | Trinary spins on GPU |
| [FSOT-GPU](https://github.com/dappalumbo91/FSOT-GPU) | Sparse trinary on GPU |
| [Wavegazer-Net](https://github.com/dappalumbo91/Wavegazer-Net) | Visual net, zero trainable weights |
| [arxiv-paper-pipeline](https://github.com/dappalumbo91/arxiv-paper-pipeline) | Paper freeze / clean-clone |

User: [dappalumbo91](https://github.com/dappalumbo91). Live existence check: `python scripts/live_verify.py`.

## External measured data (not our repos)

| Source | What | API / dump |
|--------|------|------------|
| FlyWire / Codex | Adult brain types + connectivity | https://codex.flywire.ai (CAVE is Allen Institute software) |
| Male CNS | Brain+VNC Berg et al. Cell 2026 | `D:\FlyWire_Connectome\male_cns` |
| BANC | Female brain+VNC Bates et al. Nature 2026 | `D:\FlyWire_Connectome\banc` |
| Janelia neuPrint | Hemibrain v1.2.1 (independent fly graph) | https://neuprint.janelia.org/api |
| UniProt / Ensembl | Gene ↔ protein | REST (no token) |
| Allen Brain Atlas | **Mouse/human atlases**, not the fly connectome | https://api.brain-map.org |

Allen does not host FlyWire synapses. The honest Allen hook is (1) CAVE serving FlyWire, (2) Brain Atlas API up, (3) FSOT-2.1-Neural for wet-lab mouse work. Fly live checks use Codex + neuPrint + UniProt/Ensembl.
