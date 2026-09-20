# Memory as the structure sits — limits and growth map

Pin **AEB2AD**. 0 free parameters. Human-facing intelligence. Courtship/aggression/fru/dsx stay \(T_1\) off.

This is the map **before** we add connective tissue. Stress is hop-1 collapse \(\ge \varphi\). Expansion later is residual on a **measured** command type. We do not invent synapses. We do not grow leftover hubs.

## What the tissue actually is

The fly net is measured \(W\) (synapse counts; GABA outgoing \(-\)). Thinking is

\[
a \leftarrow rWa,\qquad r=1+|S|\cdot P_{\mathrm{NEW}},\qquad a \leftarrow a/\|a\|_\infty
\]

Overlay on \(\iff |x|>1/\varphi\). Consensus trit \(0\) is superposition, not a vote. Hop horizon \(\mathrm{round}(\varphi^5)=11\).

**The graph still collapses.** After one residual hop, thousands of seeds become a handful of active cells. That collapse *is* short-term memory as the brain sits. TED-7 measured it: STM held **one** ALU/observer word; the first encode item was gone.

| Locus (Male / hemibrain) | n_seed | hop-1 n_active | collapse | Kind |
|--------------------------|-------:|---------------:|---------:|------|
| olfactory → **il3LN6** | 2639 | 2 | 1319× | leftover hub |
| Kenyon → **APL** | 1927 | 2 | 964× | leftover hub |
| JO → **DNg29** | 672 | 3 | 224× | command (already hopped) |
| VNC / mechanosensory **IN01B001** | 5832 | 17 | 343× | command bottleneck |
| early birth **PS100** | 7890 | 14 | 564× | command bottleneck |

Kenyon/MBON/DAN already exist as address space: **n_kc=1927**, **n_mbon=71**, **n_dan=317**. Hop-2 vnc_motor on KC is leftover. DA is volume leftover (T1), not walk LTM.

## Stores (after TED-7, before this expand)

| Store | Object | Limit as the structure sits |
|-------|--------|-----------------------------|
| STM register | last ALU word / last observer | **capacity 1**; next problem overwrites |
| STM overlay | \(n_{\mathrm{active}}\) after hop, cut \(1/\varphi\) | JO 3 cells, KC 2 cells, VNC 19 cells |
| LTM \(W\) | measured synapses | does not forget; retrieval = re-seed |
| LTM KC | Kenyon residual | associative leftover; **APL is the hub** |

Procedural LTM (trit ALU recompute) was already 10/10 after interference. Episodic STM was not: first item missed. Two observers that disagree go to consensus 0 — they do not share one register.

## What TED-8 expanded (no new axons)

**STM.** Working overlay of \(\mathrm{round}(\varphi^2)=3\) slots. Last three encode items recall. Item 0 and 1 evict. Dual-hold when both observers walk (\(\mathrm{cons}(+1,+1)=+1\)). Walk vs smell leftover stays superposed (\(\mathrm{cons}(+1,0)=0\)), which does **not** edit \(W\).

**LTM.** Addressable bindings on **measured classes**: JO, vnc_sensory, KCg-m, DNp01, mechanosensory. Payload is the problem + pathway. Writes to **APL** and **il3LN6** are refused. Olfactory interference does not steal the JO binding.

This is residual law on existing types. It is the overlay a human-facing AI can use now. It is **not** yet extra connective tissue.

## Never grow (leftover hubs)

Do not add axons here. Collapse is leftover, not a thought, not a language token.

| Type | Program | Collapse | Rule |
|------|---------|---------:|------|
| il3LN6 | olfactory | 1319.5 | never — leftover hub |
| APL | kenyon | 963.5 | never — leftover hub |
| KCg-s1 | kenyon_subgraph | 963.5 | never — leftover hub |
| APL | kc_full_hemibrain | 963.5 | never — leftover hub |
| APL | kc_mb_subgraph | 963.5 | never — leftover hub |
| il3LN6 | olfactory | 751.8 | never — leftover hub |
| APL | ito_MBp3 | 519.0 | never — leftover hub |
| lLN2F_b | olfactory | 429.5 | never — leftover hub |

Language / coding tokens remain **deferred** (`docs/LEFTOVER.md`): trit ALU and parser exist; they are not an LLM observer on \(W\). Off-domain text stays leftover.

## Grow later (command bottlenecks) — evolutionary analog

TED-9 residual-seeded these types (live hops). That is how a brain adds connective tissue under stress: more residual on the command bottleneck, not a new invented region, not APL, not il3LN6. This pack is **not required to stay a fly-only brain**; splice-in regions later still need a named job and the same law. See `docs/GROWTH_REGIONS.md`.

| Type | Program | Collapse | n_seed→h1 | How |
|------|---------|---------:|-----------|-----|
| PS100 | birth_early | 563.6 | 7890→14 | residual seed this type later |
| AN05B009 | vnc_sensory | 560.4 | 7845→14 | residual seed this type later |
| INXXX007 | chordotonal | 356.0 | 2136→6 | residual seed this type later |
| IN01B001 | mechanosensory | 343.1 | 5832→17 | residual seed this type later |

JO hop-1 silent **669** (672−3): expand on **DNg29**, not the 669 silent cells.

Human-facing AI path (later, not this TED): STM window + LTM class index + residual on command types under stress. Still 0 free parameters. Still no courtship/aggression default. Still not a trained net on FlyWire.

## How a human would use this (eventual)

Like an LLM from the outside: you ask, it retrieves. Inside it is not backprop.

1. STM overlay holds the last \(\varphi^2\) turns of work.
2. LTM re-seeds JO / VNC / KC / DNp01 for facts bound to those jobs.
3. If two jobs disagree, consensus 0 — say leftover, do not collapse.
4. If a command bottleneck is chronically over threshold (collapse \(\ge\varphi\)), **later** residual-seed that type (growth).
5. Never write memory into APL or il3LN6.

TED-8 score and freeze: `data/bill7_memory_expand.json`. Stress authority: `data/stress_map.json`. Guardrails: `docs/NEURAL_GUARDRAILS.md`.
