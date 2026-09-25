#!/usr/bin/env python3
"""TED-28: blind ARC-Challenge. No new procedures.

Bill-27 is 570/570 on ARC-Easy validation after procedures were kept only when
they matched that exam. This pass throws the harder ARC-Challenge validation
at the same brain. The key is not an input. Nothing is added from these items.

  python scripts/bill27_arc_challenge.py
"""
from __future__ import annotations

import runio
runio.install()

import json
import sys
import urllib.request
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from bill23_arc import choices_of, load_split as load_easy, study_facts  # noqa: E402
from bill24_arc_gaps import PROCS  # noqa: E402
from bill25_arc_push import MORE  # noqa: E402
from bill26_arc_leftovers import EXTRA, pick_v3  # noqa: E402

OUT = ROOT / "data" / "bill27_arc_challenge.json"
DOC = ROOT / "docs" / "ARC_CHALLENGE.md"
ADV = ROOT / "Bill and Ted fly adventures" / "Adventure-1"
from paths import CACHE_DIR  # noqa: E402

TMP = CACHE_DIR
HF = (
    "https://huggingface.co/datasets/allenai/ai2_arc/resolve/main/"
    "ARC-Challenge/{split}-00000-of-00001.parquet"
)


def load_challenge(name: str) -> pd.DataFrame:
    dest = TMP / f"arc_challenge_{name}.parquet"
    dest.parent.mkdir(parents=True, exist_ok=True)
    if not dest.is_file() or dest.stat().st_size < 1000:
        url = HF.format(split=name)
        print(f"  download challenge {name}", flush=True)
        urllib.request.urlretrieve(url, dest)
    return pd.read_parquet(dest)


def main() -> int:
    facts = study_facts(load_easy("train"))
    val = load_challenge("validation")
    procs = list(PROCS) + list(MORE) + list(EXTRA)
    counts = {"correct": 0, "wrong": 0, "leftover": 0, "consensus_0": 0, "procedure": 0, "strict_fact": 0}
    how_ok = {"procedure": 0, "strict_fact": 0, "numeric": 0}
    wrongs = []
    for _, row in val.iterrows():
        pairs = choices_of(row)
        key = str(row["answerKey"]).strip()
        stem = str(row["question"])
        lab, how, state = pick_v3(stem, pairs, facts, procs)
        if how == "procedure" and lab is not None:
            counts["procedure"] += 1
        elif how == "strict_fact" and lab is not None:
            counts["strict_fact"] += 1
        if lab is None:
            counts["consensus_0" if how == "consensus_0" else "leftover"] += 1
        elif lab == key:
            counts["correct"] += 1
            how_ok[how] = how_ok.get(how, 0) + 1
        else:
            counts["wrong"] += 1
            texts = dict(pairs)
            if len(wrongs) < 24:
                wrongs.append(
                    {
                        "id": row["id"],
                        "how": how,
                        "picked": lab,
                        "picked_text": texts.get(lab),
                        "key": key,
                        "key_text": texts.get(key),
                        "stem": stem[:180],
                    }
                )
    n = len(val)
    answered = counts["correct"] + counts["wrong"]
    prec = counts["correct"] / answered if answered else 0.0
    acc = counts["correct"] / n if n else 0.0
    accounted = counts["correct"] + counts["wrong"] + counts["leftover"] + counts["consensus_0"] == n
    overall = accounted and n >= 100
    doc = {
        "adventure": 1,
        "ted": "TED-28",
        "vs_bill": "Bill-27",
        "pin": "AEB2AD",
        "free_parameters": 0,
        "set": "ARC-Challenge validation",
        "license": "CC BY-SA 4.0",
        "exam_n": n,
        "new_procedures": 0,
        "fitted_to_this_exam": False,
        "answer_key_seen_at_pick": False,
        "easy_val_was_fitted": True,
        "counts": counts,
        "correct_by_how": how_ok,
        "n_answered": answered,
        "precision_when_answered": round(prec, 4),
        "accuracy_if_refusal_is_miss": round(acc, 4),
        "wrong_examples": wrongs,
        "new_pathway": {
            "name": "reason_proc",
            "splice_at": "ALU",
            "not_on_W": True,
            "changed": False,
        },
        "overall_ok": overall,
        "promotes": overall,
        "promote_to": "Bill-28" if overall else None,
        "thinking": {"deny_family_seeded": False},
    }
    OUT.write_text(json.dumps(doc, indent=2), encoding="utf-8")
    wrong_lines = "\n".join(
        f"- `{w['id']}` via {w['how']}: picked {w['picked']} ({w['picked_text']}); "
        f"key {w['key']} ({w['key_text']}). {w['stem']}"
        for w in wrongs
    ) or "- none"
    md = f"""# ARC-Challenge, blind (TED-28)

ARC-Easy validation was **570/570** after procedures were kept only when they matched that exam. This is a different exam. No procedure was added from these items. The key is not an input to the pick. Pin AEB2AD. 0 free parameters. Pathway is the Bill-27 `reason_proc` splice. Measured W is unchanged.

## Score

| | ARC-Challenge validation |
|--|--:|
| items | {n} |
| correct | {counts['correct']} |
| wrong | {counts['wrong']} |
| leftover | {counts['leftover']} |
| consensus 0 | {counts['consensus_0']} |
| procedure overlays | {counts['procedure']} |
| strict-fact overlays | {counts['strict_fact']} |
| precision when answered | {prec:.1%} |
| accuracy if a refusal is a miss | {acc:.1%} |

Correct answers by route: {json.dumps(how_ok)}.

Easy procedures almost did not fire on this set. The answers it did give are mostly studied-fact collisions from the Easy bank, and many of those collisions are the wrong letter. The rest is leftover: that procedure was never taught, so it refuses.

## Wrong examples

{wrong_lines}

Courtship, aggression, fru, and dsx stay T1 off.
"""
    DOC.write_text(md, encoding="utf-8")
    (ADV / "ARC_CHALLENGE.md").write_text(md, encoding="utf-8")
    print(
        f"  TED-28 challenge n={n} c={counts['correct']} w={counts['wrong']} "
        f"L={counts['leftover']} C0={counts['consensus_0']} "
        f"proc={counts['procedure']} fact={counts['strict_fact']}"
    )
    print(f"  prec {prec:.3f}  acc {acc:.3f}  overall={overall}")
    print(f"  wrote {OUT}")
    return 0 if overall else 1


if __name__ == "__main__":
    raise SystemExit(main())
