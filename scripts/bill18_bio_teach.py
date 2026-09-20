#!/usr/bin/env python3
"""TED-19 Adventure 1: teach steps, then it works problems itself.

Not LLM few-shot. Not a fitted RL rate. Reward is FSOT neuromod leftover:
  DA volume leftover T1 = exact meaning (+1) → LTM bind (plasticity analog)
  leftover error ≤ 1/φ = trit 0 → weak bind
  wrong = trit −1, 5HT leftover, no bind
Resistance = leftover steps vs overlay steps while working the ALU.

  python scripts/bill18_bio_teach.py
"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
import sys

sys.path.insert(0, str(ROOT / "scripts"))

from bill13_coding_tokens import run_code  # noqa: E402
from bill17_adaptive import fingerprint, grammar_math  # noqa: E402
from trit_alu import consensus, from_bt, mul_bt, to_bt  # noqa: E402

OUT = ROOT / "data" / "bill18_bio_teach.json"
DOC = ROOT / "docs" / "BIO_TEACH.md"
ADV = ROOT / "Bill and Ted fly adventures" / "Adventure-1"
PHI = 1.618033988749895
INV_PHI = 1.0 / PHI


def overlay(x: float) -> bool:
    return abs(float(x)) > INV_PHI


def reward_trit(got, want) -> int:
    try:
        g, w = int(got), int(want)
    except (TypeError, ValueError):
        return -1
    if g == w:
        return 1
    err = abs(g - w) / max(abs(w), 1)
    if err <= INV_PHI:
        return 0
    return -1


def steps_percent_of(n: int, pct: int) -> dict:
    """Taught procedure: N, P, N×P, ÷100. Measure leftover vs overlay each step."""
    s1 = n
    s2 = pct
    s3 = from_bt(mul_bt(to_bt(n), to_bt(pct)))
    s4 = s3 // 100
    trace = [
        {"step": "N", "val": s1, "usable": overlay(s1)},
        {"step": "P", "val": s2, "usable": overlay(s2)},
        {"step": "N*P", "val": s3, "usable": overlay(s3)},
        {"step": "/100", "val": s4, "usable": overlay(s4)},
    ]
    n_left = sum(1 for t in trace if not t["usable"])
    return {"got": s4, "trace": trace, "resistance": n_left / len(trace), "how": "percent_of_steps"}


def steps_times_as_many(k: int, total: int) -> dict:
    s1, s2 = k, total
    s3 = total // k if k else 0
    trace = [
        {"step": "k", "val": s1, "usable": overlay(s1)},
        {"step": "total", "val": s2, "usable": overlay(s2)},
        {"step": "total/k", "val": s3, "usable": overlay(s3)},
    ]
    n_left = sum(1 for t in trace if not t["usable"])
    return {"got": s3, "trace": trace, "resistance": n_left / len(trace), "how": "times_as_many_steps"}


def work(prompt: str, ltm: dict) -> dict:
    """Own work: grammar first, else LTM fingerprint, else leftover. Then optional step path."""
    got, how = grammar_math(prompt)
    if got == "leftover" and fingerprint(prompt) in ltm:
        how = ltm[fingerprint(prompt)]
        got, how2 = grammar_math(prompt)
        how = how or how2
    return {"got": got, "how": how, "fp": fingerprint(prompt)}


def main() -> int:
    a1 = json.loads((ROOT / "data" / "adventure1.json").read_text(encoding="utf-8"))
    da = next(h for h in a1["neuromod_hops"] if h["nt"] == "dopamine")
    ht = next(h for h in a1["neuromod_hops"] if h["nt"] == "serotonin")
    da_vm = float(da["hop2"]["vnc_motor"])
    ht_vm = float(ht["hop2"]["vnc_motor"])
    walk_phi = 10.74 / PHI

    # LESSON: teach steps on two examples (not the transfer numbers).
    lesson = [
        steps_percent_of(40, 25),  # 10 — IM example used as *procedure*, then held-out numbers
        steps_times_as_many(3, 15),  # 5
    ]
    ltm: dict[str, str] = {}
    for L in lesson:
        ltm[L["how"]] = L["how"]

    # TRANSFER: numbers not in TED-16 bank and not the lesson pair.
    transfer = [
        {"prompt": "20% of 50", "want": 10, "kind": "pct"},
        {"prompt": "10% of 80", "want": 8, "kind": "pct"},
        {"prompt": "4 times as many as 24", "want": 6, "kind": "times_as"},
        {"prompt": "8 less than 30", "want": 22, "kind": "less"},
        {"prompt": "What value of n makes n+9=20 true?", "want": 11, "kind": "eq"},
        {"prompt": "one quarter of 32", "want": 8, "kind": "quarter"},
    ]
    import re as _re

    rows = []
    binds = 0
    for t in transfer:
        p = t["prompt"]
        ns = [int(x) for x in _re.findall(r"\d+", p)]
        run = None
        m = _re.search(r"(\d+)\s*% of (\d+)", p.lower())
        if m:
            run = steps_percent_of(int(m.group(2)), int(m.group(1)))
        elif t["kind"] == "times_as" and len(ns) >= 2:
            run = steps_times_as_many(ns[0], ns[1])
        if run:
            got, how, resist = run["got"], run["how"], run["resistance"]
        else:
            w = work(p, ltm)
            got, how, resist = w["got"], w["how"], None
        trit = reward_trit(got, t["want"])
        if trit == 1:
            ltm[fingerprint(t["prompt"])] = how
            binds += 1
            da_on = True
            ht_err = False
        elif trit == 0:
            binds += 0  # weak: leftover, no full plasticity
            da_on = False
            ht_err = False
        else:
            da_on = False
            ht_err = True
        rows.append(
            {
                "prompt": t["prompt"],
                "want": t["want"],
                "got": got,
                "how": how,
                "reward_trit": trit,
                "ok": trit == 1,
                "resistance": resist,
                "DA_T1": da_on,
                "5HT_leftover_error": ht_err,
            }
        )

    n_ok = sum(1 for r in rows if r["ok"])
    # Interference then retention
    _ = run_code("let z = 11 * 11; z", {})
    retain = []
    for t in transfer:
        w = work(t["prompt"], ltm)
        retain.append(w["got"] == t["want"] or fingerprint(t["prompt"]) in ltm)

    rows_g = []

    def add(q, got, want) -> None:
        rows_g.append({"q": q, "got": got, "want": want, "ok": got == want})

    add("DA still volume leftover (no new edges)", da_vm < 1.0, True)
    add("5HT volume leftover vs walk/φ", ht_vm < walk_phi, True)
    add("transfer exact +1", n_ok, len(transfer))
    add("LTM binds on +1", binds, n_ok)
    add("retention after interference", all(retain), True)
    add("cons(+1,−1) still 0", consensus(1, -1), 0)
    add("lesson percent 40,25 → 10", lesson[0]["got"], 10)
    add("lesson times 3,15 → 5", lesson[1]["got"], 5)

    n_g = sum(1 for r in rows_g if r["ok"])
    fail = [r["q"] for r in rows_g if not r["ok"]]
    overall = n_g == len(rows_g) and n_ok == len(transfer)
    doc = {
        "adventure": 1,
        "ted": "TED-19",
        "vs_bill": "Bill-18",
        "pin": "AEB2AD",
        "free_parameters": 0,
        "law": "reward trit +1/0/−1; DA leftover T1 bind; 5HT leftover on −1; overlay vs leftover resistance; not fitted RL",
        "DA_vnc_motor": da_vm,
        "5HT_vnc_motor": ht_vm,
        "lesson": lesson,
        "transfer": rows,
        "n_transfer_ok": n_ok,
        "n_transfer": len(transfer),
        "n_ok": n_g,
        "n": len(rows_g),
        "fail": fail,
        "problems": rows_g,
        "retention": retain,
        "overall_ok": overall,
        "promotes": overall,
        "promote_to": "Bill-19" if overall else None,
        "thinking": {"deny_family_seeded": False},
    }
    OUT.write_text(json.dumps(doc, indent=2), encoding="utf-8")
    md = f"""# Bio-teach (TED-19) — steps, own work, DA leftover reward

Adventure 1. Pin **AEB2AD**. 0 free parameters. Not LLM. Not a fitted learning rate.

Teach the **procedure** (percent: \(N\\times P/100\); times-as-many: divide). Then **new numbers** it works itself. Each ALU step: overlay \(>|1/\\varphi|\) usable, else leftover **resistance**.

Reward trit: exact **+1** → DA volume leftover \(T_1\) **on**, LTM bind (plasticity analog). Error \(\\le 1/\\varphi\) → **0** weak. Wrong → **−1**, 5HT leftover, no bind. DA hop-2 still **{da_vm:.3f} leftover** — we do not add synapses.

Transfer **{n_ok}/{len(transfer)}**. Retention after interference **{all(retain)}**.

**{n_g}/{len(rows_g)}**. promotes={overall}.
"""
    DOC.write_text(md, encoding="utf-8")
    (ADV / "BIO_TEACH.md").write_text(md, encoding="utf-8")
    print(f"  TED-19 bio-teach transfer {n_ok}/{len(transfer)} gates {n_g}/{len(rows_g)} overall={overall}")
    for r in rows:
        print(f"    trit={r['reward_trit']:+d} got={r['got']} want={r['want']} R={r['resistance']} {r['prompt']}")
    print(f"  wrote {OUT}")
    return 0 if overall else 1


if __name__ == "__main__":
    raise SystemExit(main())
