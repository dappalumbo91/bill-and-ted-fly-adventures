#!/usr/bin/env python3
"""Adventure 1, still open: census, interference, one blind chapter.

No new relation is added. Challenge validation is not mined again.
OpenStax Prealgebra 2e Chapter 6 Be Prepared is scored with the math
already in the organism. A miss stays a refusal.

  python scripts/bill33_before_a2.py
"""
from __future__ import annotations

import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "vendor"))

from bill18_bio_teach import reward_trit  # noqa: E402
from bill21_openstax import BANK_ITEMS, openstax_work  # noqa: E402
from bill23_arc import choices_of, load_split, study_facts  # noqa: E402
from bill26_arc_leftovers import _numeric, _vote, pick_v3  # noqa: E402
from bill27_arc_challenge import load_challenge  # noqa: E402
from bill28_use import BANK as BANK29, EARLY, ITEM_CUES, PROCS_ALL  # noqa: E402
from bill29_use_more import BANK as BANK30  # noqa: E402
from bill31_use_gaps import BANK as BANK32  # noqa: E402
from bill32_use_finish import BANK as BANK33, latest_pick, latest_votes  # noqa: E402
from trit_expr import ParseError, eval_expr  # noqa: E402
import fsot_compute as fsot  # noqa: E402

OUT = ROOT / "data" / "bill33_before_a2.json"
DOC = ROOT / "docs" / "BEFORE_A2.md"
ADV = ROOT / "Bill and Ted fly adventures" / "Adventure-1" / "BEFORE_A2.md"

CALC = {
    "wave_speed",
    "light_seconds",
    "magnified_length",
    "moon_year_count",
    "balanced_equation",
    "sealed_returns",
}

# OpenStax Prealgebra 2e, Chapter 6 Percents, Be Prepared. CC BY-NC-SA 4.0.
# https://openstax.org/details/books/prealgebra-2e
# Wording is the published exercise. No new cue was written for these.
BLIND = [
    {
        "id": "os6-6.1",
        "prompt": 'Translate "the ratio of 33 to 5" into an algebraic expression.',
        "want": "33/5",
        "kind": "expr",
        "cite": "Be Prepared 6.1; key is the ratio 33/5",
    },
    {
        "id": "os6-6.2",
        "prompt": "Write 3/5 as a decimal.",
        "want": 0.6,
        "kind": "number",
        "cite": "Be Prepared 6.2",
    },
    {
        "id": "os6-6.3",
        "prompt": "Write 0.62 as a fraction.",
        "want": "31/50",
        "kind": "expr",
        "cite": "Be Prepared 6.3",
    },
    {
        "id": "os6-6.4",
        "prompt": "Translate and solve: 3/4 of x is 24.",
        "want": 32,
        "kind": "number",
        "cite": "Be Prepared 6.4",
    },
    {
        "id": "os6-6.5",
        "prompt": "Simplify: (4.5)(2.38)",
        "want": 10.71,
        "kind": "number",
        "cite": "Be Prepared 6.5",
    },
    {
        "id": "os6-6.6",
        "prompt": "Solve: 3.5 = 0.7n",
        "want": 5,
        "kind": "number",
        "cite": "Be Prepared 6.6",
    },
    {
        "id": "os6-6.7",
        "prompt": "Solve 0.0875(720) through multiplication.",
        "want": 63,
        "kind": "number",
        "cite": "Be Prepared 6.7",
    },
    {
        "id": "os6-6.8",
        "prompt": "Solve 12.96 / 0.04 through division.",
        "want": 324,
        "kind": "number",
        "cite": "Be Prepared 6.8",
    },
    {
        "id": "os6-6.9",
        "prompt": "Solve: 0.6y = 45",
        "want": 75,
        "kind": "number",
        "cite": "Be Prepared 6.9; 0.6y = 45",
    },
    {
        "id": "os6-6.10",
        "prompt": "Solve: n / 1.45 = 4.6",
        "want": 6.67,
        "kind": "number",
        "cite": "Be Prepared 6.10",
    },
    {
        "id": "os6-6.12",
        "prompt": "Solve: x / 4 = 20",
        "want": 80,
        "kind": "number",
        "cite": "Be Prepared 6.12",
    },
    {
        "id": "os6-6.13",
        "prompt": "Write as a rate: Sale rode his bike 24 miles in 2 hours.",
        "want": 12,
        "kind": "number",
        "cite": "Be Prepared 6.13; the key prints 24 miles in 2 hours. The unit rate is 12 miles per hour.",
    },
]


def _same_number(got, want) -> bool:
    try:
        return abs(float(got) - float(want)) < 1e-6
    except (TypeError, ValueError):
        return False


def score_blind(item) -> dict:
    got, how = openstax_work(item["prompt"])
    if got == "leftover" or how == "leftover":
        status = "leftover"
    elif item["kind"] == "expr":
        text = str(got).replace(" ", "")
        status = "correct" if item["want"].replace(" ", "") == text else "wrong"
    elif _same_number(got, item["want"]):
        status = "correct"
    else:
        status = "wrong"
    return {
        "id": item["id"],
        "prompt": item["prompt"],
        "want": item["want"],
        "cite": item["cite"],
        "got": got if isinstance(got, (int, float, str)) else str(got),
        "how": how,
        "status": status,
    }


def use_signature(bank) -> list[tuple]:
    out = []
    for item in bank:
        lab, law = latest_pick(item["stem"], item["choices"])
        out.append((item["id"], lab, law))
    return out


def touch_unrelated(easy_frame, facts) -> dict:
    """Other curriculum, then the Easy cue pile. Relations are not rewritten."""
    os_rows = []
    for it in BANK_ITEMS:
        got, how = openstax_work(it["prompt"])
        os_rows.append({"id": it["id"], "got": got if isinstance(got, (int, float, str)) else str(got), "how": how})
    alu = []
    for expr in ("2+3", "11-4", "6*7", "20/4"):
        try:
            alu.append({"expr": expr, "got": eval_expr(expr, {})})
        except (ParseError, ZeroDivisionError, ValueError) as exc:
            alu.append({"expr": expr, "got": str(exc)})
    n_easy = 0
    for _, row in easy_frame.iterrows():
        pairs = choices_of(row)
        stem = str(row["question"])
        latest_pick(stem, pairs)
        pick_v3(stem, pairs, facts, PROCS_ALL)
        n_easy += 1
    return {"openstax_touched": len(os_rows), "alu": alu, "easy_replayed": n_easy}


def walk(exam: str, frame, facts, law_stems: dict) -> list[dict]:
    n_early = len(EARLY)
    rows = []
    for _, row in frame.iterrows():
        pairs = choices_of(row)
        key = str(row["answerKey"]).strip()
        stem = str(row["question"])
        votes = latest_votes(stem, pairs)
        labels = sorted({lab for _, lab in votes})
        names = sorted({name for name, _ in votes})
        num = _numeric(stem, pairs)
        early_hits = []
        item_hits = []
        for i, proc in enumerate(PROCS_ALL):
            lab = _vote(stem, pairs, proc)
            if lab is None:
                continue
            bucket = early_hits if i < n_early else item_hits
            bucket.append(lab)
        base_lab, base_how, _ = pick_v3(stem, pairs, facts, PROCS_ALL)
        if len(labels) == 1:
            route = "use"
            final = labels[0]
            primary = names[0]
        elif len(labels) > 1:
            route = "conflict"
            final = None
            primary = None
        else:
            route = base_how
            final = base_lab
            primary = base_how
        if route == "use":
            for name, _lab in votes:
                law_stems[name].add((exam, row["id"]))
        kind = "correct" if final == key else ("leftover" if final is None else "wrong")
        rows.append(
            {
                "exam": exam,
                "id": row["id"],
                "route": route,
                "primary": primary,
                "names": names,
                "n_relations": len(names),
                "numeric": num is not None,
                "n_early_cues": len(early_hits),
                "n_item_cues": len(item_hits),
                "procedure_letter": base_lab if base_how == "procedure" else None,
                "final": final,
                "key": key,
                "kind": kind,
            }
        )
    return rows


def bucket_use(row, stem_n: dict) -> str:
    names = row["names"]
    if row["route"] == "use":
        if any(name in CALC for name in names):
            return "calculation"
        widest = max(stem_n.get(name, 1) for name in names)
        if widest >= 2:
            return "reused_relation"
        return "single_exam_relation"
    if row["route"] == "procedure":
        if row["numeric"]:
            return "calculation"
        if row["n_item_cues"] and not row["n_early_cues"]:
            return "one_stem_cue"
        if row["n_early_cues"]:
            return "early_procedure"
        return "procedure"
    if row["route"] == "strict_fact":
        return "studied_fact"
    if row["route"] == "consensus_0":
        return "consensus"
    return "leftover"


def main() -> int:
    phi = float(fsot.PHI)
    stm_slots = round(phi ** 2)
    facts = study_facts(load_split("train"))
    easy = load_split("validation")
    challenge = load_challenge("validation")
    use_bank = BANK29 + BANK30 + BANK32 + BANK33

    before = use_signature(use_bank)
    unrelated = touch_unrelated(easy, facts)
    after = use_signature(use_bank)
    forgotten = [
        {"id": a[0], "before": {"letter": a[1], "law": a[2]}, "after": {"letter": b[1], "law": b[2]}}
        for a, b in zip(before, after)
        if a != b
    ]

    law_stems: dict[str, set] = defaultdict(set)
    easy_rows = walk("easy", easy, facts, law_stems)
    chal_rows = walk("challenge", challenge, facts, law_stems)
    stem_n = {name: len({sid for exam, sid in pairs if exam in ("easy", "challenge")}) for name, pairs in law_stems.items()}
    # A relation reused on Easy and Challenge is wider than one exam.
    cross = {
        name: len({exam for exam, _sid in pairs})
        for name, pairs in law_stems.items()
    }

    def summarize(rows):
        counts = Counter(bucket_use(r, stem_n) for r in rows)
        routes = Counter(r["route"] for r in rows)
        multi = sum(1 for r in rows if r["n_relations"] > 1 and r["route"] == "use")
        override = sum(
            1
            for r in rows
            if r["route"] == "use" and r["procedure_letter"] not in (None, r["final"])
        )
        agree = sum(
            1
            for r in rows
            if r["route"] == "use" and r["procedure_letter"] == r["final"]
        )
        filled = sum(1 for r in rows if r["route"] == "use" and r["procedure_letter"] is None)
        return {
            "n": len(rows),
            "buckets": dict(counts),
            "routes": dict(routes),
            "several_relations_agreed": multi,
            "relation_replaced_a_procedure_letter": override,
            "relation_agreed_with_procedure": agree,
            "relation_where_procedure_was_silent": filled,
            "correct": sum(1 for r in rows if r["kind"] == "correct"),
            "wrong": sum(1 for r in rows if r["kind"] == "wrong"),
        }

    easy_sum = summarize(easy_rows)
    chal_sum = summarize(chal_rows)
    reused = sorted(
        ((name, stem_n[name], cross[name]) for name in stem_n if stem_n[name] >= 2),
        key=lambda t: (-t[1], t[0]),
    )
    single = sorted(name for name in stem_n if stem_n[name] == 1)

    # Early procedure reuse on Easy, same census as TED-29, recomputed.
    early_tally = [{"n": 0, "wrong": 0} for _ in EARLY]
    item_tally = [{"n": 0, "wrong": 0} for _ in ITEM_CUES]
    for _, row in easy.iterrows():
        pairs = choices_of(row)
        key = str(row["answerKey"]).strip()
        stem = str(row["question"])
        for i, proc in enumerate(EARLY):
            lab = _vote(stem, pairs, proc)
            if lab is None:
                continue
            early_tally[i]["n"] += 1
            early_tally[i]["wrong"] += int(lab != key)
        for i, proc in enumerate(ITEM_CUES):
            lab = _vote(stem, pairs, proc)
            if lab is None:
                continue
            item_tally[i]["n"] += 1
            item_tally[i]["wrong"] += int(lab != key)

    def cue_census(tallies):
        one = many_ok = many_bad = dead = 0
        for t in tallies:
            if t["n"] == 0:
                dead += 1
            elif t["n"] == 1 and t["wrong"] == 0:
                one += 1
            elif t["n"] >= 2 and t["wrong"] == 0:
                many_ok += 1
            else:
                many_bad += 1
        return {
            "n": len(tallies),
            "one_stem_correct": one,
            "many_stems_all_correct": many_ok,
            "fired_a_wrong_letter": many_bad,
            "silent_on_easy": dead,
        }

    blind_rows = [score_blind(it) for it in BLIND]
    # Also run the chapter through the interference block's worker only; already scored.
    blind_counts = Counter(r["status"] for r in blind_rows)

    # Existing chapters still score with the same worker, as the unrelated block.
    old_ok = 0
    for it in BANK_ITEMS:
        got, how = openstax_work(it["prompt"])
        if how == "leftover" or got == "leftover":
            continue
        try:
            old_ok += int(reward_trit(got, it["want"]) == 1)
        except (TypeError, ValueError):
            pass

    doc = {
        "adventure": 1,
        "ted": "TED-34",
        "vs_bill": "Bill-33",
        "pin": "AEB2AD",
        "free_parameters": 0,
        "promotes": False,
        "promote_to": None,
        "measured_W_changed": False,
        "new_relations_added": 0,
        "stm_overlay_slots": stm_slots,
        "relations_are_alu_procedures": True,
        "easy": easy_sum,
        "challenge": chal_sum,
        "early_cues_on_easy": cue_census(early_tally),
        "item_cues_on_easy": cue_census(item_tally),
        "reused_relations": [{"law": n, "stems": s, "exams": e} for n, s, e in reused],
        "single_exam_relations": single,
        "interference": {
            "use_items": len(before),
            "forgotten": len(forgotten),
            "changes": forgotten,
            "unrelated": unrelated,
            "openstax_already_taught_exact": old_ok,
            "openstax_already_taught_n": len(BANK_ITEMS),
        },
        "blind_ch6": {
            "license": "CC BY-NC-SA 4.0 OpenStax Prealgebra 2e",
            "n": len(blind_rows),
            "counts": dict(blind_counts),
            "items": blind_rows,
        },
    }
    OUT.write_text(json.dumps(doc, indent=2), encoding="utf-8")

    def line_bucket(title, summary):
        b = summary["buckets"]
        order = [
            "reused_relation",
            "single_exam_relation",
            "calculation",
            "one_stem_cue",
            "early_procedure",
            "procedure",
            "studied_fact",
            "consensus",
            "leftover",
        ]
        rows = "\n".join(f"| {name} | {b.get(name, 0)} |" for name in order if b.get(name, 0))
        return f"### {title}\n\n| thought kind | items |\n|---|---:|\n{rows}\n"

    reused_lines = "\n".join(
        f"| `{n}` | {s} | {e} |" for n, s, e in reused[:40]
    ) or "| none | 0 | 0 |"
    blind_lines = "\n".join(
        f"| `{r['id']}` | {r['status']} | {r['want']} | {r['got']} | {r['how']} |"
        for r in blind_rows
    )
    text = f"""# Before Adventure 2

Pin AEB2AD. 0 free parameters. Bill-33 brain, unchanged. No new relation was written for this pass. Measured edges stay as they were.

STM overlay slots are **{stm_slots}** (`round(φ²)`). The Challenge relations are procedures on the language ALU. They are not bindings in those three slots, so a later prompt cannot evict them.

## Census

Easy validation is **{easy_sum['correct']}** / **{easy_sum['n']}** correct, wrong **{easy_sum['wrong']}**.
Challenge validation is **{chal_sum['correct']}** / **{chal_sum['n']}** correct, wrong **{chal_sum['wrong']}**.

{line_bucket("Easy", easy_sum)}
{line_bucket("Challenge", chal_sum)}

On Easy, a relation and a procedure named the same letter on **{easy_sum['relation_agreed_with_procedure']}** items. A relation answered where the procedure was silent on **{easy_sum['relation_where_procedure_was_silent']}** items. A relation replaced the procedure's letter on **{easy_sum['relation_replaced_a_procedure_letter']}** items.

On Challenge, a relation and a procedure named the same letter on **{chal_sum['relation_agreed_with_procedure']}** items. A relation answered where the procedure was silent on **{chal_sum['relation_where_procedure_was_silent']}** items. A relation replaced the procedure's letter on **{chal_sum['relation_replaced_a_procedure_letter']}** items. Several relations agreed with each other on **{chal_sum['several_relations_agreed']}** items.

Early cues on Easy: **{doc['early_cues_on_easy']['one_stem_correct']}** fire on one stem and stay correct, **{doc['early_cues_on_easy']['many_stems_all_correct']}** fire on several stems and stay correct, **{doc['early_cues_on_easy']['fired_a_wrong_letter']}** include a wrong letter, **{doc['early_cues_on_easy']['silent_on_easy']}** stay silent. Item cues (the pile that closed Easy): **{doc['item_cues_on_easy']['one_stem_correct']}** one-stem correct, **{doc['item_cues_on_easy']['many_stems_all_correct']}** many-stem correct, **{doc['item_cues_on_easy']['fired_a_wrong_letter']}** with a wrong letter.

Relations that fire on two or more exam stems:

| law | stems | exams |
|---|---:|---:|
{reused_lines}

Relations that fire on one exam stem: **{len(single)}**. Each of those still has a new wording in the use bank. One exam stem means the Challenge file contained that situation once.

## Interference

Use items checked before the unrelated block: **{len(before)}**. After OpenStax chapters 1–5, four ALU expressions, and a full Easy replay, forgotten or changed: **{len(forgotten)}**.

Already-taught OpenStax items still exact: **{old_ok}** / **{len(BANK_ITEMS)}**.

## Blind Chapter 6

OpenStax Prealgebra 2e, Chapter 6 Percents, Be Prepared. CC BY-NC-SA 4.0. Scored with `openstax_work` as it stands. Correct **{blind_counts.get('correct', 0)}**, wrong **{blind_counts.get('wrong', 0)}**, leftover **{blind_counts.get('leftover', 0)}**, of **{len(blind_rows)}**.

| id | status | want | family gave | route |
|---|---|---|---|---|
{blind_lines}

A leftover is a refusal. No cue was added for these prompts.
"""
    DOC.write_text(text, encoding="utf-8")
    ADV.write_text(text, encoding="utf-8")
    print(
        f"  census easy {easy_sum['buckets']} challenge {chal_sum['buckets']} "
        f"forgotten {len(forgotten)} blind {dict(blind_counts)}"
    )
    print(f"  reused {len(reused)} single {len(single)} stm {stm_slots}")
    print(f"  wrote {DOC}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
