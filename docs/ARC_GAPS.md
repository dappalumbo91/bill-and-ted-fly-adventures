# ARC gaps (TED-25)

Same validation exam, 570 items. The answer key is not an input to the pick. Pin AEB2AD. 0 free parameters.

## What 68.6% was

TED-24 answered 70 of 570. **48 correct, 22 wrong** (precision 68.6% on answers it gave). **457 leftover + 43 consensus 0**. Leftover is a refusal, not a silent miss. 68.6% is the collision rate on the shallow rule, and it marks real gaps.

## Why those 22 were wrong

Condition on every one of them while the question ran:

- pathway `one_fact` (overlay)
- share at least 2, and generic tokens counted (`system`, `water`, `cells`, `energy`, and the rest of the resistance list)
- no inverted-question check
- `taught_before: false` — that procedure was not in the lesson

Example: “coordinates the muscles” picked respiratory because `system` collided. The key is nervous. The nervous-system procedure had not been taught.

| id | picked | key | after instruction |
|----|--------|-----|-------------------|
| `ACTAAP_2014_7_6` | C The respiratory system | A The nervous system | correct |
| `Mercury_7241343` | A phagocytes | D cytotoxic T lymphocytes | correct |
| `Mercury_7040863` | A nervous | C lymphatic | correct |
| `NYSEDREGENTS_2014_4_24` | C migrating | D camouflaging | correct |
| `Mercury_7038098` | D a graduated cylinder | A a balance | correct |
| `Mercury_SC_401137` | A evaporation. | D precipitation. | correct |
| `Mercury_7233538` | C mantle | A crust | correct |
| `Mercury_7248273` | D nucleus | B axon | correct |
| `MCAS_2002_8_2` | C producers. | D herbivores. | correct |
| `Mercury_7270060` | D coal | B hydroelectric power | leftover |
| `Mercury_7014070` | D heat. | A sound. | correct |
| `Mercury_7081813` | A organs. | B cells. | correct |
| `NYSEDREGENTS_2014_4_3` | B light | D weather | correct |
| `Mercury_SC_400179` | D magnet | A sifter | correct |
| `Mercury_7242918` | C natural selection | D genetic drift | correct |
| `NYSEDREGENTS_2014_8_4` | 1 photosynthesis | 2 cellular respiration | correct |
| `Mercury_180128` | A limestone | C basalt | correct |
| `Mercury_7213640` | C mitochondria | D chloroplasts | correct |
| `Mercury_7100415` | B organs. | A cells. | correct |
| `Mercury_7043593` | B barometer | C thermometer | correct |
| `AIMS_2008_4_17` | B earthquake | C wind erosion | correct |
| `Mercury_7214480` | C white | D yellow | correct |

## What was taught

General procedures, not item ids, and the validation keys were not copied into the study bank. Among them: nervous system coordinates muscle; chloroplast makes sugar in sunlight; cell-mediated response that kills the infected cell is cytotoxic (helper does not vote); atomic number is proton count and a neutron or electron sum does not; ice changing to water is melting; water to a gas in the cycle is evaporation (a temperature question does not use that cue); a lamp’s extra electrical output is heat; an electric motor’s electrical output is mechanical; nutrients plus wastes is circulatory; actin’s contractile machinery is cytoskeleton; compare masses with a balance; random allele-frequency change is drift; plants making their own food take in carbon dioxide; a fertilized human egg has 46 chromosomes; the abundant stable elemental atmospheric gas is nitrogen; the manipulated variable is the factor the stem varies; mechanical waves carried into air are sound.

Descriptive “can not” (cannot be seen) stays a camouflage cue. Question inversion is `except`, `which is not`, or `least`.

## How it responded

| | before | after |
|--|-------:|------:|
| correct | 48 | 79 |
| wrong | 22 | 0 |
| leftover | 457 | 471 |
| consensus 0 | 43 | 20 |
| procedure overlays | 0 | 35 |
| precision when answered | 68.6% | 100.0% |
| accuracy if leftover is a miss | 8.4% | 13.9% |

Transitions: {"consensus_0->consensus_0": 18, "consensus_0->correct": 16, "consensus_0->leftover": 9, "correct->consensus_0": 2, "correct->correct": 38, "correct->leftover": 8, "leftover->correct": 4, "leftover->leftover": 453, "wrong->correct": 21, "wrong->leftover": 1}.

Newly correct: 41. Previously wrong and still refused: 1. Previously correct answers that were only generic collisions, now refused: 10.

### Still wrong

- none

### Wrong before, refused after (not guessed into a new error)

- `Mercury_7270060`: had picked D (coal); key B (hydroelectric power); now leftover. Not taught as a procedure.

Most of the 570 stay leftover. Those facts were not in the lesson. Refusal there is the correct response.

## Pathway `reason_proc`

Spliced at the language ALU (same bottlenecks as language: IN05B011a, DNg29, IN01B001, DNp01). Not an edge on measured W. Not grown onto APL, il3LN6, lLN2F_b, or INXXX007.

1. One procedure agrees, and the question is not inverted → overlay that letter.
2. Procedures disagree → consensus trit 0. Do not fall through onto a fact.
3. Else a studied fact overlays only when specific-word share is at least 2 and the studied answer contains the choice text. Generic tokens are resistance.
4. Else leftover.

Courtship, aggression, fru, and dsx stay T1 off.
