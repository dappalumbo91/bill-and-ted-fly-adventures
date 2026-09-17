#!/usr/bin/env python3
"""Trit expression parser + thought-stress watch.

Type FSOT arithmetic, e.g.  JO_L + JO_R - JO_h1
Functions: abs(x) trit(x) cons(a, b) overlay(x) leftover(x)
Compare: == != < > <= >=

Stress is leftover / bottleneck / consensus 0 — not a new synapse.
Expansion = residual on the *measured* type at the bottleneck
(DNg29, APL, Giant Fiber). Do not invent connective tissue.

  python scripts/trit_expr.py
"""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
import sys

sys.path.insert(0, str(ROOT / "scripts"))

from arith_steps import registry  # noqa: E402
from trit_alu import (  # noqa: E402
    abs_bt,
    add_bt,
    cmp_bt,
    consensus,
    divmod_bt,
    from_bt,
    mul_bt,
    sub_bt,
    to_bt,
    trit,
)

OUT = ROOT / "data" / "trit_expr.json"
STRESS = ROOT / "data" / "stress_map.json"
PHI = 1.618033988749895
INV_PHI = 1.0 / PHI

TOKEN = re.compile(
    r"\s*(?:(?P<num>\d+)|(?P<name>[A-Za-z_][A-Za-z0-9_]*)|"
    r"(?P<op>==|!=|<=|>=|[+\-*/(),<>]))"
)


class ParseError(ValueError):
    pass


def tokenize(s: str) -> list[tuple[str, str]]:
    out: list[tuple[str, str]] = []
    i = 0
    while i < len(s):
        m = TOKEN.match(s, i)
        if not m:
            raise ParseError(f"bad token at {i}: {s[i:]!r}")
        i = m.end()
        kind = m.lastgroup or "op"
        val = m.group(kind)
        if kind == "num":
            out.append(("num", val))
        elif kind == "name":
            out.append(("name", val))
        else:
            out.append(("op", val))
    out.append(("eof", ""))
    return out


class Parser:
    def __init__(self, src: str, env: dict[str, int]):
        self.toks = tokenize(src)
        self.i = 0
        self.env = env

    def peek(self) -> tuple[str, str]:
        return self.toks[self.i]

    def eat(self, kind: str | None = None, val: str | None = None) -> tuple[str, str]:
        k, v = self.peek()
        if kind and k != kind:
            raise ParseError(f"expected {kind} got {k} {v}")
        if val is not None and v != val:
            raise ParseError(f"expected {val} got {v}")
        self.i += 1
        return k, v

    def parse(self) -> int:
        n = self.cmp()
        if self.peek()[0] != "eof":
            raise ParseError(f"trailing {self.peek()}")
        return n

    def cmp(self) -> int:
        a = self.add()
        k, v = self.peek()
        if k == "op" and v in ("==", "!=", "<", ">", "<=", ">="):
            self.eat()
            b = self.add()
            c = cmp_bt(to_bt(a), to_bt(b))
            return {
                "==": 1 if c == 0 else 0,
                "!=": 1 if c != 0 else 0,
                "<": 1 if c < 0 else 0,
                ">": 1 if c > 0 else 0,
                "<=": 1 if c <= 0 else 0,
                ">=": 1 if c >= 0 else 0,
            }[v]
        return a

    def add(self) -> int:
        a = self.mul()
        while True:
            k, v = self.peek()
            if k == "op" and v in ("+", "-"):
                self.eat()
                b = self.mul()
                a = from_bt(
                    add_bt(to_bt(a), to_bt(b)) if v == "+" else sub_bt(to_bt(a), to_bt(b))
                )
            else:
                return a

    def mul(self) -> int:
        a = self.unary()
        while True:
            k, v = self.peek()
            if k == "op" and v in ("*", "/"):
                self.eat()
                b = self.unary()
                if v == "*":
                    a = from_bt(mul_bt(to_bt(a), to_bt(b)))
                else:
                    q, _r = divmod_bt(to_bt(a), to_bt(b))
                    a = from_bt(q)
            else:
                return a

    def unary(self) -> int:
        k, v = self.peek()
        if k == "op" and v == "-":
            self.eat()
            return from_bt(sub_bt(to_bt(0), to_bt(self.unary())))
        if k == "op" and v == "+":
            self.eat()
            return self.unary()
        return self.primary()

    def primary(self) -> int:
        k, v = self.peek()
        if k == "num":
            self.eat()
            return int(v)
        if k == "name":
            self.eat()
            if self.peek() == ("op", "("):
                return self.call(v)
            if v not in self.env:
                raise ParseError(f"unknown name {v}")
            return int(self.env[v])
        if k == "op" and v == "(":
            self.eat()
            n = self.cmp()
            self.eat("op", ")")
            return n
        raise ParseError(f"bad primary {k} {v}")

    def call(self, fn: str) -> int:
        self.eat("op", "(")
        args = [self.cmp()]
        while self.peek() == ("op", ","):
            self.eat()
            args.append(self.cmp())
        self.eat("op", ")")
        return self.apply(fn, args)

    def apply(self, fn: str, args: list[int]) -> int:
        fn = fn.lower()
        if fn == "abs":
            return from_bt(abs_bt(to_bt(args[0])))
        if fn == "trit":
            return trit(args[0])
        if fn == "overlay":
            return 1 if abs(float(args[0])) > INV_PHI else 0
        if fn == "leftover":
            return 1 if abs(float(args[0])) <= INV_PHI else 0
        if fn == "cons":
            if len(args) < 2:
                raise ParseError("cons(a, b)")
            return consensus(trit(args[0]), trit(args[1]))
        raise ParseError(f"unknown func {fn}")


def eval_expr(src: str, env: dict[str, int]) -> int:
    return Parser(src, env).parse()


WORKSHEET = [
    ("JO_L + JO_R", 672),
    ("JO_L + JO_R - JO_h1", 669),
    ("(JO_L + JO_R) / 3 * 3", 672),
    ("JO_L + JO_R == JO", 1),
    ("VNC_L + VNC_R", 6351),
    ("VNC - (VNC_L + VNC_R)", 14),
    ("VNC_L > VNC_R", 1),
    ("DNg29_M + DNg29_B", 4),
    ("(DNg29_M + DNg29_B) / 2 - DNg29_H", 2),
    ("T001_L - T001_R", 1),
    ("T02_L - T02_R", -12),
    ("abs(T02_L - T02_R)", 12),
    ("abs(T02_L - T02_R) > HOPS", 1),
    ("trit(T001_L - T001_R)", 1),
    ("trit(T02_L - T02_R)", -1),
    ("cons(trit(T001_L - T001_R), trit(T002_L - T002_R))", 1),
    ("cons(trit(T001_L - T001_R), trit(T02_L - T02_R))", 0),
    ("leftover(0)", 1),
    ("overlay(1)", 1),
    ("NEURONS - GABA > GABA", 1),
    ("H_JO + KC > JO", 1),
]


def stress_from_hops() -> list[dict]:
    """Bottleneck = n_seed / n_active after hop-1. Top type is expansion candidate."""
    files = [
        ROOT / "data" / "male_cns_boot.json",
        ROOT / "data" / "banc_connectome_boot.json",
        ROOT / "data" / "hemibrain_connectome_boot.json",
        ROOT / "data" / "kenyon_connectome_boot.json",
        ROOT / "data" / "develop_cycle.json",
    ]
    rows = []
    for path in files:
        if not path.is_file():
            continue
        doc = json.loads(path.read_text(encoding="utf-8"))
        programs = doc.get("programs") or []
        if not programs and isinstance(doc.get("hops"), dict):
            programs = (doc.get("hops") or {}).get("programs") or []
        src = path.name
        for p in programs:
            n_seed = int(p.get("n_seed") or 0)
            flow = p.get("flow") or []
            by_h = {int(f.get("hop") or -1): f for f in flow if isinstance(f, dict)}
            h1 = by_h.get(1) or {}
            h2 = by_h.get(2) or {}
            n1 = int(h1.get("n_active") or 0)
            n2 = int(h2.get("n_active") or 0)
            top1 = (h1.get("top") or {})
            if isinstance(top1, dict):
                top_name = top1.get("cell_type") or top1.get("name") or ""
            else:
                top_name = str(top1 or "")
            collapse = (n_seed / n1) if n1 else (float("inf") if n_seed else 0.0)
            bottleneck = collapse >= PHI
            pname = str(p.get("name") or "")
            leftover_hub = any(
                x in pname.lower()
                for x in ("olfactory", "kenyon", "kc", "mbp", "ito_mb")
            )
            kind = "leftover_hub" if leftover_hub else "command_bottleneck"
            rows.append(
                {
                    "source": src,
                    "program": pname,
                    "n_seed": n_seed,
                    "n_active_h1": n1,
                    "n_active_h2": n2,
                    "collapse_h1": collapse if collapse != float("inf") else None,
                    "bottleneck": bottleneck,
                    "kind": kind,
                    "top_h1": top_name,
                    "expansion": (
                        None
                        if leftover_hub
                        else (
                            f"measured type {top_name} — residual seed, do not invent edges"
                            if bottleneck and top_name
                            else None
                        )
                    ),
                }
            )
    rows.sort(key=lambda r: -(r["collapse_h1"] or 0))
    return rows


def main() -> int:
    env = registry()
    rows = []
    n_cons0 = 0
    for src, want in WORKSHEET:
        try:
            got = eval_expr(src, env)
            err = None
        except Exception as e:
            got = None
            err = str(e)
        ok = got == want and err is None
        leftover_flag = False
        if "cons(" in src and got == 0:
            n_cons0 += 1
            leftover_flag = True
        rows.append(
            {
                "expr": src,
                "want": want,
                "got": got,
                "ok": ok,
                "error": err,
                "thought_stress": leftover_flag,
            }
        )
        mark = "OK" if ok else "FAIL"
        print(f"{mark}  {src}  → {got}")
    hop_stress = stress_from_hops()
    bottlenecks = [h for h in hop_stress if h.get("bottleneck")]
    fail = [r["expr"] for r in rows if not r["ok"]]
    doc = {
        "pin": "AEB2AD",
        "free_parameters": 0,
        "n": len(rows),
        "n_ok": len(rows) - len(fail),
        "fail": fail,
        "overall_ok": not fail,
        "consensus_zero_stress": n_cons0,
        "expressions": rows,
        "note": "Parser evaluates on trit ALU. cons=0 is thought leftover, not a new axon.",
    }
    stress_doc = {
        "pin": "AEB2AD",
        "free_parameters": 0,
        "rule": (
            "Stress = hop-1 collapse ≥ φ, or consensus trit 0. "
            "Expansion = residual on the measured top type. Do not invent synapses."
        ),
        "thought_consensus_zero": n_cons0,
        "n_bottlenecks": len(bottlenecks),
        "top_bottlenecks": bottlenecks[:12],
        "all": hop_stress,
        "connective_candidates": [
            {
                "type": b.get("top_h1"),
                "program": b.get("program"),
                "source": b.get("source"),
                "collapse": b.get("collapse_h1"),
                "do": "seed this measured class; do not add edges",
            }
            for b in bottlenecks
            if b.get("top_h1") and b.get("kind") != "leftover_hub"
        ][:8],
        "do_not_expand": [
            {
                "type": b.get("top_h1"),
                "program": b.get("program"),
                "why": "leftover hub (olfactory LN / Kenyon APL) is not a thought",
            }
            for b in bottlenecks
            if b.get("kind") == "leftover_hub" and b.get("top_h1")
        ][:6],
    }
    OUT.write_text(json.dumps(doc, indent=2), encoding="utf-8")
    STRESS.write_text(json.dumps(stress_doc, indent=2), encoding="utf-8")
    print(f"  trit_expr {doc['n_ok']}/{doc['n']}  cons0_stress={n_cons0}")
    print(f"  bottlenecks {len(bottlenecks)}  wrote {OUT} and {STRESS}")
    if bottlenecks:
        b0 = bottlenecks[0]
        print(
            f"  top stress {b0.get('program')} {b0.get('source')} "
            f"collapse={b0.get('collapse_h1')} top={b0.get('top_h1')}"
        )
    return 0 if doc["overall_ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
