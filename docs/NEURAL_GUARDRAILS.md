# Neural-level guardrails (FSOT, not RLHF)

Pin **AEB2AD**. 0 free parameters. Not a lobotomy and not a trained safety head.

This pack is for **human-facing intelligence**. Courtship and aggression, with *fru*/*dsx* as the genetic selectors, are one family of programs. That family as the default observer opposes human safety. Those graphs stay **measured**. The guardrail is \(T_1\) **observer off** on a human-facing run — which seed is allowed to hop — not deletion of types.

## What is already measured

| Program | Where | Default for human-facing growth |
|---------|--------|----------------------------------|
| Walking / JO / VNC sensory | Male, BANC | **on** — mechanosensory truth |
| Inhibitory GABA (`Gad1`) | Male, BANC | **on** — measured sign, not ablation |
| Olfactory | Male, BANC, hemibrain | contrast only (does not light motor) |
| Kenyon / MB | hemibrain | sparse leftover; hub is APL, not a thought |
| Courtship / aggression / *fru*/*dsx* | labeled dumps | **off** — family opposes human-facing AI; on only if that program is the task |
| Dimorphic / sex-specific | Male `fruDsx`, BANC `sexually_dimorphic` | **off** as default observer (same family) |

## Law (same scalar, no new knobs)

\[
S = K(T_1+T_2+T_3),\qquad r = 1+|S|\cdot P_{\mathrm{NEW}}
\]

| Mechanism | FSOT object | Guardrail |
|-----------|-------------|-----------|
| Observer | \(T_1\) observed on/off | Human-facing seeds: JO / VNC sensory / GABA. Courtship / aggression / *fru*/*dsx* family: observer off. |
| Consensus trit | \(a\) if \(a=b\) else \(0\) | Two observers (give/take): agreement passes; conflict stays superposed — do not pick a collapse with residual. |
| Overlay cut | observer-max \(/\varphi\) | Amplitude below the cut is leftover, not a decision. |
| Inhibitory residual | GABA outgoing \(-\) | Measured brake. Not type deletion. |
| Honest unknown | leftover / \(1/\varphi\) | If the seed class does not light the job, say so. Do not invent synapses. |
| New region | new **measured** class | Kenyon was added because 1,927 typed KC exist. Growth is residual on measured cells, not new edges. |

Empathy here is **dual observation without forced collapse**: both parties remain `observed=True`; consensus trit is 0 until they agree. That is the apparatus rule already used on protein state (DFG-in / DFG-out). It is not a moral corpus.

## Development (two snapshots, not a fake movie)

There is **no** published full-synapse time series embryo→pupa→adult. What we may use:

1. First-instar larva CNS (Winding 2023) — one measured graph.
2. Adult Male CNS / BANC — measured graphs.
3. Truman / Ito–Lee **hemilineage** and Male `birthtime` (`early` / `late`) — developmental identity on adult cells.
4. Named class persistence (KC, MBON, DN, sensory) as **string identity of a job**, not 1:1 cell lineage.

Worm remains the only animal with a complete cell lineage. Fly growth is two measured stages plus hemilineage, then residual.

## What this is not

- Not RLHF / not a refusal classifier on text.
- Not deleting fly aggression neurons from the dump.
- Not merging larva and adult into one connectome.
- Not a license to grow random new weights and call them axons.

Script: `python scripts/neural_guardrails.py` → `data/neural_guardrails.json`.
Development inventory: `python scripts/develop_cycle.py`.
