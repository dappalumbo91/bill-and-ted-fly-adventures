# Baseline fly simulation (print first)

Pin **AEB2AD**. 0 free parameters. Not an LLM.

## What this is

A closed loop of **measured body** + **measured brain hops**:

1. Harvard tethered fly on a ball (Dataverse 10.7910/DVN/BBNPYX) — 6-leg tarsus + antenna 3D.
2. MAD+\(\varphi\) gates high-energy stepping / antennal motion.
3. Gates pick observers: VNC sensory (legs), JO (antenna), mechanosensory (forelimb share \(\ge 1/\varphi\) = ball-contact analog).
4. Observers read frozen Male CNS hop-2 fields (measured synapses). If `vnc_motor > 1`, the plant steps.
5. Y-maze: left/right tarsus consensus trit. Superpose (\(0\)) does not collapse the junction. Resource is on the **left** arm.

Iwasaki et al. *PNAS* 2025 and *Curr Biol* 2025 (ball walk / immobile sphere) are the object-interaction papers. Their videos are **not** on disk. Forelimb energy is the honest analog from the treadmill we do have.

## Brain print (Male hop-2)

| Condition | Seed | `vnc_motor` | Walks |
|-----------|------|------------:|:-----:|
| rest | none | 0 | no |
| walk_legs | vnc_sensory | **10.74** | yes |
| walk_JO | JO | **7.77** | yes |
| ball_contact | mechanosensory | **7.55** | yes |
| odor | olfactory | **0.001** | **no** |
| courtship / aggression | denied | 0 | no |

## Closed loop (3 trials)

| Trial | walk frames | ball-forelimb | resource (left) |
|-------|------------:|--------------:|-----------------|
| Fly01_T001 | 130 / 333 | 9 | **reached** |
| Fly01_T002 | 110 / 347 | 15 | **reached** |
| Fly02_T002 | 99 / 337 | 5 | missed (went right) |

Not fitted: Fly02’s right-biased tarsus turns the other arm. That is the baseline, not a bug to train away.

## Not this file

Language, coding, LLM tokens. Teach later by **new measured observers**, not backprop. Guardrail: fru/courtship/aggression never seeded.

`python scripts/baseline_sim.py` → `data/baseline_sim.json`
