# Fly obligation spine

Pin **AEB2AD**. Bill-36. Law `S=K(T1+T2+T3)`, overlay `1/φ`, consensus trit, 0 free parameters. Measured edges stay as they were. Courtship, aggression, and fru/dsx stay off.

```powershell
python verification/export_fly_spine.py
python verification/run_fly_spine.py
```

The run writes `data/fly_spine_report.json`. **89** obligations. **4** predictions. **overall_ok = true** through Python, the decision rule, Z3, Lean 4, Coq/Rocq, Isabelle/HOL, F*, Rust, and TLA+. A missing prover fails the run. This report does not inherit the genetics sibling (`data/cross_proof_report.json`, pin D1D38A, 42 obligations).

The obligations are the counts already on disk. Schlegel TSV `139248` neurons, DNg29 `2`, JO prefix `1104`. Lee-lab meta sits beside it: `144837` rows, DNg29 `2`, JO prefix `1107`. The gap is `1107 = 1104 + 3`, and the three meta-only JO-B roots are `720575940626741265`, `720575940628159081`, `720575940636488667`. Male CNS `165122` traced, `25563197` edges, GABA `22055`. BANC `175401`. Hemibrain typed `22704`, DNg29 `0`. Adventure 1 is Easy `570/570`, Challenge `299/299` with `0` wrong, use `343/343`. Leftover map `35/35`. One agreed label overlays. Silence, or two different labels, stays trit 0. A repeated label still overlays.

Male CNS and BANC stay separate graphs. DNg29 descending mass is above 1 on both (milli `9204` and `7813`). KCg-m and L5 vnc_motor mass stays at or below 1 on both. Adult-end hop-2 vnc_motor: early-born `7890` seeds at milli `24254`, Truman 07B `954` seeds at milli `27566`, Ito MBp3 `1038` seeds at milli `0`.

## Predictions

The law is already fixed. The open items are measurements this pack does not have a file for yet. Each item below is the test that file has to pass. The spine keeps `status: absent` and `filled: false`. It does not write the missing count, and it does not treat an unseen file as already true.

| File still absent | Pass | Fail |
|---|---|---|
| Codex portal gzipped FAFB CSV | DNg29 equals Schlegel `2`. A JO prefix of `1104` passes the split-name table. A JO prefix of `1107` passes the coarse-name table. The coarse-minus-split gap is the three JO-B roots already recorded. | DNg29 differs from `2`, or the JO prefix is outside `{1104, 1107}`. Lean `codexDNg29Gate` and `joExportGate` reject `0`. |
| Fly Cell Atlas bodyId join | A published bodyId table is present. nompC, iav, and nan rows whose root is in the Schlegel TSV carry a JO cell_type prefix. Gad1 rows land in the GABA class already counted on the Male CNS (`22055`). | Any of those rows is assigned a bodyId before that table exists, or a joined nompC/iav/nan root in the TSV lacks a JO prefix, or Gad1 lands outside that GABA class. `fcaBodyIdCount` stays `none` until the table is published. |
| Embryo-to-pupa synapse series | At the adult end, early-born and 07B hop-2 vnc_motor stay above 1, and MBp3 hop-2 vnc_motor stays at or below 1. | The adult end of a published series breaks that split. Intermediate frames are not given values here. `pupalFrameCount` stays `none`. |
| Iwasaki object-interaction videos | Frames are scored with the ball rule already on disk: forelimb share at least `1/φ` counts as mechanosensory. Courtship, aggression, and fru/dsx stay unseeded. | The path is fitted to the clip, or those programs are seeded to make a frame score. The measured baseline stays the Harvard ball trials: `3` trials, `2` resource reaches. `iwasakiFrameCount` stays `none`. |

`python scripts/boot_pack.py --check` re-reads the report headlines. It does not rebuild the proofs and it does not load the Male CNS weight table.
