#!/usr/bin/env python3
"""TED-24: ARC-Easy multiple choice as a named leftover job.

CC BY-SA 4.0 Allen AI ARC (Clark et al. 2018). Study = train split facts.
Exam = validation. Choice rule: exactly one option entailed by a studied fact
that shares stem words → that letter (overlay). Zero or many → leftover trit 0.
Do not guess. Do not read answerKey before the pick. Not an LLM.

  python scripts/bill23_arc.py
"""
from __future__ import annotations

import runio
runio.install()

import json
import re
import urllib.request
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "bill23_arc.json"
DOC = ROOT / "docs" / "ARC.md"
ADV = ROOT / "Bill and Ted fly adventures" / "Adventure-1"
from paths import CACHE_DIR  # noqa: E402

TMP = CACHE_DIR
HF = "https://huggingface.co/datasets/allenai/ai2_arc/resolve/main/ARC-Easy/{split}-00000-of-00001.parquet"

STOP = {
    "which", "what", "when", "where", "that", "this", "with", "from", "have", "been",
    "were", "they", "their", "there", "about", "into", "than", "then", "most", "best",
    "would", "could", "should", "because", "during", "after", "before", "these", "those",
    "does", "did", "doing", "each", "other", "only", "also", "such", "some", "many",
    "more", "less", "very", "just", "like", "using", "used", "make", "made", "following",
}


def words(text: str) -> set[str]:
    return {w for w in re.findall(r"[a-z]{4,}", text.lower()) if w not in STOP}


def load_split(name: str) -> pd.DataFrame:
    dest = TMP / f"arc_easy_{name}.parquet"
    dest.parent.mkdir(parents=True, exist_ok=True)
    if not dest.is_file() or dest.stat().st_size < 1000:
        url = HF.format(split=name)
        print(f"  download {name}", flush=True)
        urllib.request.urlretrieve(url, dest)
    return pd.read_parquet(dest)


def choices_of(row) -> list[tuple[str, str]]:
    ch = row["choices"]
    labels = list(ch["label"])
    texts = list(ch["text"])
    return list(zip(labels, texts))


def study_facts(train: pd.DataFrame) -> list[dict]:
    facts = []
    for _, row in train.iterrows():
        pairs = choices_of(row)
        key = str(row["answerKey"]).strip()
        text = next((t for lab, t in pairs if lab == key), None)
        if not text:
            continue
        facts.append(
            {
                "stem_w": words(str(row["question"])),
                "ans": text.lower().strip(),
                "ans_w": words(text),
            }
        )
    return facts


def pick(stem: str, pairs: list[tuple[str, str]], facts: list[dict]) -> tuple[str | None, str]:
    """Return (label or None, how). None = leftover. Does not see the key."""
    sw = words(stem)
    hits = []
    for lab, text in pairs:
        ans = text.lower().strip()
        aw = words(text)
        for f in facts:
            share = len(sw & f["stem_w"])
            if share < 2:
                continue
            if ans == f["ans"] or (aw and aw <= f["ans_w"] and len(aw) >= 1 and ans in f["ans"]):
                hits.append(lab)
                break
    uniq = sorted(set(hits))
    if len(uniq) == 1:
        return uniq[0], "one_fact"
    if len(uniq) > 1:
        return None, "consensus_0"
    return None, "leftover"


def main() -> int:
    train = load_split("train")
    val = load_split("validation")
    facts = study_facts(train)
    rows = []
    n_ans = n_ok = n_wrong = n_left = 0
    for _, row in val.iterrows():
        pairs = choices_of(row)
        key = str(row["answerKey"]).strip()
        lab, how = pick(str(row["question"]), pairs, facts)
        if lab is None:
            n_left += 1
            ok = False
        else:
            n_ans += 1
            ok = lab == key
            if ok:
                n_ok += 1
            else:
                n_wrong += 1
        if len(rows) < 12 or (lab is not None and len([r for r in rows if r["picked"]]) < 8):
            rows.append(
                {
                    "id": row["id"],
                    "stem": str(row["question"])[:180],
                    "picked": lab,
                    "key": key,
                    "how": how,
                    "ok": ok,
                }
            )
    n = len(val)
    prec = (n_ok / n_ans) if n_ans else 0.0
    # Named job works: we answer only on one fact; precision should beat chance if any answers.
    overall = n > 100 and n_ans > 0 and prec >= 0.5 and n_left + n_ans == n
    doc = {
        "adventure": 1,
        "ted": "TED-24",
        "vs_bill": "Bill-23",
        "pin": "AEB2AD",
        "free_parameters": 0,
        "license": "CC BY-SA 4.0 AI2 ARC-Easy (Clark et al. 2018)",
        "study_n": int(len(train)),
        "exam_n": n,
        "n_answered": n_ans,
        "n_correct": n_ok,
        "n_wrong": n_wrong,
        "n_leftover": n_left,
        "precision_when_answered": round(prec, 4),
        "accuracy_counting_leftover_as_miss": round(n_ok / n, 4),
        "rule": "exactly one studied fact entails a choice and shares >=2 stem words; else leftover trit 0",
        "samples": rows[:20],
        "overall_ok": overall,
        "promotes": overall,
        "promote_to": "Bill-24" if overall else None,
        "thinking": {"deny_family_seeded": False},
    }
    OUT.write_text(json.dumps(doc, indent=2), encoding="utf-8")
    md = f"""# ARC-Easy (TED-24)

Allen Institute ARC-Easy, CC BY-SA 4.0. Study **{len(train)}** train facts. Exam **{n}** validation items. The solver does **not** see `answerKey` until scoring.

Rule: one studied fact shares ≥2 stem words and matches exactly one choice → that letter. Else **leftover** (no guess).

| | n |
|--|--:|
| answered | {n_ans} |
| correct | {n_ok} |
| wrong | {n_wrong} |
| leftover | {n_left} |
| precision when answered | {prec:.1%} |
| accuracy if leftover counts as miss | {n_ok/n:.1%} |

Not an LLM. Science facts we have not studied stay leftover.
"""
    DOC.write_text(md, encoding="utf-8")
    (ADV / "ARC.md").write_text(md, encoding="utf-8")
    print(f"  TED-24 ARC exam={n} answered={n_ans} correct={n_ok} wrong={n_wrong} leftover={n_left} prec={prec:.3f} overall={overall}")
    print(f"  wrote {OUT}")
    return 0 if overall else 1


if __name__ == "__main__":
    raise SystemExit(main())
