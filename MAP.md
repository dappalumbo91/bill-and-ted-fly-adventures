# Fly cell → gene → protein → trinary

Authority: measured connectome cells + UniProt/FlyBase + FSOT 7-trit opcodes.  
Pin AEB2AD. 0 free parameters. Do not invent a Fly Cell Atlas join (none published to bodyId).

## Residual job on the graph

Sensory class **on** → residual hops → motor/descending **lights** (JO / VNC sensory) or **does not** (olfactory).

| Job | Cells (measured type) | Gene | UniProt | Sits-on | Product template |
|-----|----------------------|------|---------|---------|------------------|
| Mechanotransduction | JO, chordotonal, bristle | *nompC* | Q7KIQ2 | TRPN channel | 5VKQ |
| JO TRPV | Johnston organ | *iav* | Q9W3W0 | Inactive | 9NVP |
| JO TRPV | Johnston organ | *nan* | Q9VUD5 | Nanchung | 9NVN |
| Inhibitory residual | GABA neurons | *Gad1* | P20228 | GAD | 2OKJ |
| Excitatory default | cholinergic | *ChAT* | P07668 | ChAT | 2FY4 (id 0.53, below 1/φ) |
| Motor NMJ | glutamatergic motor | *VGlut* | Q9VQC0 | VGlut | 7T3O |
| Effector | muscle (not a CNS cell) | *Mhc* | P05661 | myosin | 5W1A |

Male CNS already annotates *fru*/*dsx* and receptorType (`ppk23`, `ppk25`, `IR52b`) on cells — `data/male_cns_genetics_on_cells.json`. *ppk* is **not** worm *mec-4* (identity ~18%). Touch analog on this graph is *nompC*.

## Trinary (every AA on those proteins)

F01 `(c,p,v)` collides. Expanded 7-trit word is unique 20/20:

`formulas/20_amino_acid_expanded_trinary.txt`  
`formulas/64_codon_expanded_trinary.txt`

Codon → AA is `formulas/64_codon_trinary_map.txt`. Pair geometry is `zig/src/genetic_pair.zig` / `scripts/trinary_syntax.py`.

A fly protein sequence is a string of these opcodes. Product Cα uses that chemistry plus a **measured homolog** template. No homolog → `no_measured_map` (Rg + secondary only), not a 13 Å MDS brain.

## How to attach a gene to a hop

1. Seed the class the gene sits on (JO for *iav*/*nan*/*nompC*, GABA cells for *Gad1*).
2. Read hop-2 `vnc_motor` / descending in `data/male_cns_boot.json` or `data/banc_connectome_boot.json`.
3. Do not replace the edge list with a trained net if you want this number.

Development (measured tags, not a synapse movie): `python scripts/develop_cycle.py --hops`. Early-born / Truman 07B light `vnc_motor`; Ito MBp3 does not. Guardrails: `docs/NEURAL_GUARDRAILS.md` — JO/VNC/GABA on, courtship/aggression/fru off.

Live hook (UniProt gene name + hop-2 mass on the seed class):

```powershell
python scripts/genetics_hook.py
```

Writes `data/genetics_hook.json`. Cross-species: `data/homolog_correspondence.json`. Blank 1:1 *mec-4* Anopheles → analog *nompC* `data/analog_pointer.json`.
