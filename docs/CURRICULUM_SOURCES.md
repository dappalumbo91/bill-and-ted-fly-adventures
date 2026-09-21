# Curriculum sources for this organism (not LLM pretrain)

Gemini’s list is the right **shape**: sequential textbooks, algorithmic math, structured Q&A. It is the wrong **ingest** if we dump raw text into FlyWire \(W\). This pack reads **JSON Q&A + steps** the trit ALU, grammar senses, and DA leftover reward can take.

## What Gemini named → how we use it

| Source | Format | For this fly | Status |
|--------|--------|----------------|--------|
| OpenStax / BCcampus | CC textbooks XML/PDF | TED-22 Prealgebra 2e Be Prepared + word problems **15/15** sequential Ch.1→3. | **ingested** |
| DeepMind Mathematics Dataset | algorithmic K-12 strings | TED-21 ingested **48** template items (G: zips empty). Plus/minus/times/div/pct/times-as-many/eq/less **48/48**. | **ingested** |
| ARC (AI2 science MCQ) | question + choices + key | TED-24 ARC-Easy: study train, exam val. One fact → letter; else leftover. Precision **68.6%** when answered (48/70); **500/570** leftover. | **ingested** |
| Simple English Wikipedia dumps | encyclopedic frames | Research observer later; overlay/consensus; **never over \(W\)**. | leftover |
| Gutenberg | public-domain reading | Reading curriculum later; closed-lexicon decode first. | leftover |
| OpenML education | arrays | Numeric rule arrays if they match ALU. | analog |
| **G:\\AI_Datasets** (on disk) | flickr, python snippets, text.zip, CORD-19 | Zips **0-byte / not zip**. Folders empty. Cannot extract. | blocked dump |

## What this model reads easiest

1. **JSON Q&A** `{id, prompt, want, steps?}` — native (TED-16/18/19/20).
2. **Numeric rule arrays** / trit expressions — ALU.
3. **Not** raw text blocks, not conversational corpora.

Start subjects (Adventure 1 teaching): **elementary math + closed-lexicon reading/writing**. Science MCQ (ARC) after MCQ leftover is named. OpenStax sequence after DeepMind-style JSON exists.

## Self-study hub (later)

Leftover → dictionary/grammar lookup (TED-17/18). API hub = same leftover query, optional retrieved text as overlay. Consensus 0 vs measured \(W\). Not a human at a browser.
