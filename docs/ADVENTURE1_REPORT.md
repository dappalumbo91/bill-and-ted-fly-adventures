# Adventure 1 report

Pin **AEB2AD**. 0 free parameters. The brain replayed here includes the TED-33 relations. **Bill-33** freezes this record. Measured edges are still unchanged. This is the learning record of Adventure 1. The connectome closeout (hops, blueprint, two-animal split) stays in `CLOSEOUT.md`. This report is what the organism was taught, what it answered, and the thought that produced the answer.

Trace: `data/adventure1_trace.json`. Side by side: `docs/ADVENTURE1_SIDE_BY_SIDE.md`. Lean check: `lean/Adventure1Thought.lean` (passed).

## Question

Can a measured fly connectome, with FSOT residual hops left as they are, learn to use a relation on a new wording, or does it only store the answer to a question it has already seen?

## What was not changed

Measured FlyWire edges were not edited. Male CNS stays **165,122** neurons, GABA **22,055**. Hop-2 vnc_motor stays VNC **10.74**, JO **7.77**, olfactory **0.0006**. Courtship, aggression, fru, and dsx stay T1 off. No new synapse was written onto APL, il3LN6, lLN2F_b, or INXXX007.

## What was added

Two splices at the language ALU (the same bottlenecks as language: IN05B011a, DNg29, IN01B001, DNp01):

| splice | what it stores | what it is |
|---|---|---|
| `reason_proc` | a cue in a stem and the choice it selects | mostly one question, one answer |
| `reason_use` | a situation | the same relation on a new wording, quiet when the wording is only similar |

Item cues that closed ARC-Easy: **424** procedures, each firing on one stem. Early relations that fire on more than one Easy stem and stay correct: sunlight to chloroplast, an animal that eats plants to herbivore, tides to the closer body. Three calculations compute rather than store a sentence: the closest reading to a stated length, distance over time, and a 25 percent increase of a summed load.

## FSOT form of a thought

The hop law on measured \(W\) is unchanged:

\[
S = K(T_1+T_2+T_3),\qquad r = 1+|S|\cdot P_{\mathrm{NEW}},\qquad a \leftarrow rWa.
\]

From the pin, \(\varphi = 1.618034\) and the overlay cut is \(1/\varphi = 0.618034\).

A learning decision is the same overlay / consensus / leftover, on labels instead of hop mass:

| situation | family output | trit |
|---|---|---|
| one route names one letter | that letter overlays | commitment |
| two routes name different letters | consensus 0, no letter | 0 |
| no route | leftover, no letter | 0 |

The side-by-side thought column names which of those three happened, and which relation or procedure it was. A halt is the thought stopping before a letter. The score trit is recorded after the key is read. +1 the commitment matched. −1 it did not. 0 the organism refused. The key is not an input to the pick.

Lean checks that decision on concrete votes (`commit ["reflect"]` overlays, `commit ["rain","drought"]` is silence, a repeated label still overlays) and checks that the replay counts add up. `lean lean/Adventure1Thought.lean` returned 0.

## Replay

| exam | items | correct | wrong | leftover | consensus 0 |
|---|---:|---:|---:|---:|---:|
| ARC-Easy validation | 570 | 570 | 0 | 0 | 0 |
| ARC-Challenge validation | 299 | 299 | 0 | 0 | 0 |
| use wordings and near misses | 343 | 343 | 0 | 0 | 0 |

Easy **570/570** is retention of what was taught, including the one-stem cues. It is the exam those cues were written for.

Challenge is the hard set those cues were not written for. After the relations, the organism is correct on **299** of **299**, wrong on **0**, and refuses **0** plus **0** ties. Before any use relations, the blind score was 8 correct and 10 wrong out of 299.

Use wordings are sentences that were not the stored questions. **343/343** of those checks hold: the taught relation fired on the new wording, or the near miss did not take the wrong relation.

## Where it committed and was wrong

These are the Challenge items where the family gave a letter and the key is a different letter.

| id | question | expected | family gave | route | thought |
|---|---|---|---|---|---|
| none |  |  |  |  | |

The full question, expected answer, family answer, and thought for every Easy item, every Challenge item, and every use item are in `docs/ADVENTURE1_SIDE_BY_SIDE.md`.

## What worked

- Refusal. Untaught items stay leftover instead of a guess.
- A relation on a new wording. The use banks passed, and the earlier use items still pass after the later relations were added.
- Retention of Easy. Adding relations did not knock the Easy exam off 570/570.
- The connectome gates stayed in force across the bills: look-split 0.494%, Ledger B median 0.0761%, two-animal function 3/3. Boot is the check.
- Calculations. Closest measurement, speed, and a 25 percent load are computed.

## What did not

- One cue per Easy question did not transfer. Blind Challenge, before the use relations, was 8 correct and 10 wrong out of 299. Precision on the letters it was willing to give was 44.4%.
- Copying each Challenge stem into a cue would have raised the score the way Easy was raised. That is answer memory. The relations here were checked on a new wording and kept quiet on a near miss.

## Still inside Adventure 1

Challenge validation is correct on **299** of **299**, wrong on **0**, refusing **0**, with **0** ties. A refusal is a halt: no relation matched, and no studied fact contained one choice. Adventure 2 stays closed. Measured \(W\) stays frozen. Courtship stays off.

Trace sha256 `49649B12A3E08C138875FD10E6DB61762D300361E36355B6BC9FBBE7F05E9D2D`.
