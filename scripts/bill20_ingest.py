#!/usr/bin/env python3
"""TED-21: ingest DeepMind-style algorithmic math as JSON Q&A.

G:\\AI_Datasets zips on disk are empty/corrupt (0-byte). Ingest is the DeepMind
method: generate K-12 arithmetic from explicit templates, not scraped web.
The organism works each prompt (grammar + ALU). Not LLM pretrain.

  python scripts/bill20_ingest.py
"""
from __future__ import annotations

import json
import random
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
import sys

sys.path.insert(0, str(ROOT / "scripts"))

from bill17_adaptive import grammar_math  # noqa: E402
from bill18_bio_teach import reward_trit  # noqa: E402
from bill19_read_write import read_meaning, write_percent  # noqa: E402

OUT = ROOT / "data" / "bill20_ingest.json"
BANK = ROOT / "data" / "ingest_deepmind_style.json"
DOC = ROOT / "docs" / "INGEST.md"
ADV = ROOT / "Bill and Ted fly adventures" / "Adventure-1"


def generate(seed: int = 21, n: int = 48) -> list[dict]:
    rng = random.Random(seed)
    items: list[dict] = []

    def add(kind: str, prompt: str, want, steps: str) -> None:
        items.append(
            {
                "id": f"dm-{kind}-{len(items):03d}",
                "source": "DeepMind-style algorithmic template (not the GitHub dump; same rule-generation)",
                "kind": kind,
                "prompt": prompt,
                "want": want,
                "steps": steps,
            }
        )

    while len(items) < n:
        k = len(items) % 8
        if k == 0:
            a, b = rng.randint(13, 80), rng.randint(2, 40)
            add("plus", f"What is {a} plus {b}?", a + b, "a+b")
        elif k == 1:
            a, b = rng.randint(20, 90), rng.randint(1, 19)
            add("minus", f"What is {a} minus {b}?", a - b, "a-b")
        elif k == 2:
            a, b = rng.randint(3, 12), rng.randint(3, 12)
            add("times", f"Calculate {a} times {b}.", a * b, "a*b")
        elif k == 3:
            b = rng.choice([2, 3, 4, 5, 6, 8])
            q = rng.randint(3, 12)
            a = b * q
            add("div", f"Divide {a} by {b}.", q, "a/b")
        elif k == 4:
            n0 = rng.choice([20, 40, 50, 60, 80])
            p = rng.choice([10, 20, 25, 50])
            add("pct", f"{p}% of {n0}", (n0 * p) // 100, "N*P/100")
        elif k == 5:
            k0 = rng.choice([2, 3, 4, 5])
            tot = k0 * rng.randint(4, 15)
            add("times_as", f"{k0} times as many as {tot}", tot // k0, "total/k")
        elif k == 6:
            d = rng.randint(3, 15)
            s = rng.randint(20, 80)
            add("eq", f"What value of n makes n+{d}={s} true?", s - d, "s-d")
        else:
            d = rng.randint(4, 20)
            a = rng.randint(25, 90)
            add("less", f"{d} less than {a}", a - d, "a-d")
    return items[:n]


def main() -> int:
    bank = generate()
    BANK.write_text(json.dumps({"pin": "AEB2AD", "n": len(bank), "items": bank}, indent=2), encoding="utf-8")

    rows = []
    by_kind: dict[str, list[bool]] = {}
    for it in bank:
        got, how = grammar_math(it["prompt"])
        trit = reward_trit(got, it["want"])
        ok = trit == 1
        by_kind.setdefault(it["kind"], []).append(ok)
        rows.append(
            {
                "id": it["id"],
                "kind": it["kind"],
                "prompt": it["prompt"],
                "want": it["want"],
                "got": got,
                "how": how,
                "reward_trit": trit,
                "ok": ok,
            }
        )

    # Mix: read/write not in the generator (school-style extra).
    extra = []
    w = write_percent(60, 25)
    extra.append({"kind": "write", "prompt": "write 25% of 60", "got": w["got"], "want": 15, "ok": w["got"] == 15})
    r = read_meaning("turn left")
    extra.append(
        {
            "kind": "read_cmd",
            "prompt": "turn left",
            "got": r.get("splice_at") or r.get("kind"),
            "want": "DNg29",
            "ok": (r.get("splice_at") or r.get("kind")) == "DNg29",
        }
    )
    deny = read_meaning("court")
    extra.append({"kind": "deny", "prompt": "court", "got": deny.get("kind"), "want": "deny", "ok": deny.get("kind") == "deny"})

    n_ok = sum(1 for r in rows if r["ok"])
    n_ex = sum(1 for e in extra if e["ok"])
    n = len(rows)
    leftover_kinds = sorted({r["kind"] for r in rows if not r["ok"]})
    overall = n_ok == n and n_ex == len(extra)
    kind_tbl = {k: {"n": len(v), "n_ok": sum(v)} for k, v in by_kind.items()}
    doc = {
        "adventure": 1,
        "ted": "TED-21",
        "vs_bill": "Bill-20",
        "pin": "AEB2AD",
        "free_parameters": 0,
        "g_datasets": "zips empty/corrupt; DeepMind-style templates ingested instead",
        "n": n,
        "n_ok": n_ok,
        "extra_n_ok": n_ex,
        "extra_n": len(extra),
        "by_kind": kind_tbl,
        "leftover_kinds": leftover_kinds,
        "items": rows,
        "extra": extra,
        "overall_ok": overall,
        "promotes": overall,
        "promote_to": "Bill-21" if overall else None,
        "thinking": {"deny_family_seeded": False},
    }
    OUT.write_text(json.dumps(doc, indent=2), encoding="utf-8")
    md = f"""# Ingest TED-21 — DeepMind-style JSON

G:\\\\AI_Datasets archives are empty (0-byte zips). Ingest is **algorithmic templates** (DeepMind Mathematics Dataset method): plus/minus/times/divide/percent/times-as-many/equation/less-than.

The organism **works each prompt**. Not stored keys. Not LLM.

Arithmetic **{n_ok}/{n}**. Mix read/write/deny **{n_ex}/{len(extra)}**. Leftover kinds: {leftover_kinds or 'none'}.

Bank: `data/ingest_deepmind_style.json`.
"""
    DOC.write_text(md, encoding="utf-8")
    (ADV / "INGEST.md").write_text(md, encoding="utf-8")
    print(f"  TED-21 ingest {n_ok}/{n} extra {n_ex}/{len(extra)} leftover_kinds={leftover_kinds} overall={overall}")
    for k, v in kind_tbl.items():
        print(f"    {k:12s} {v['n_ok']}/{v['n']}")
    print(f"  wrote {OUT} {BANK}")
    return 0 if overall else 1


if __name__ == "__main__":
    raise SystemExit(main())
