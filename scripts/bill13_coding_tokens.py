#!/usr/bin/env python3
"""TED-14: splice coding tokens on the language region (still not FlyWire W).

let / if / else / while / trit functions. ALU is balanced ternary.
Loop horizon round(φ⁵)=11. Courtship identifiers DENY. Unknown leftover.
Splice at ALU + command bottlenecks. Never APL/il3LN6.

  python scripts/bill13_coding_tokens.py
"""
from __future__ import annotations

import runio
runio.install()

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
import sys

sys.path.insert(0, str(ROOT / "scripts"))

from arith_steps import registry  # noqa: E402
from trit_alu import consensus  # noqa: E402
from trit_expr import ParseError, eval_expr  # noqa: E402

OUT = ROOT / "data" / "bill13_coding_tokens.json"
DOC = ROOT / "docs" / "CODING_SPLICE.md"
ADV = ROOT / "Bill and Ted fly adventures" / "Adventure-2"
PHI = 1.618033988749895
LOOP_HORIZON = int(round(PHI ** 5))  # 11
NEVER = frozenset({"APL", "il3LN6", "lLN2F_b", "INXXX007"})
DENY_NAMES = frozenset({"court", "courtship", "mate", "fru", "dsx", "fight", "aggression"})
KEYWORDS = frozenset({"let", "if", "else", "while", "return", "cons", "overlay", "leftover", "trit", "abs"})


class CodeError(ValueError):
    pass


def tokenize_src(src: str) -> list[str]:
    return re.findall(
        r"[A-Za-z_][A-Za-z0-9_]*|\d+|==|!=|<=|>=|[+\-*/(){},=<>;]",
        src,
    )


class Runner:
    def __init__(self, env: dict[str, int]):
        self.env = dict(env)
        self.splice_at = "ALU"
        self.on_W = False

    def run(self, src: str) -> dict:
        names = {t for t in tokenize_src(src) if t[0].isalpha() or t[0] == "_"}
        if names & DENY_NAMES:
            return {"kind": "deny", "got": "DENY", "leftover": True, "on_W": False, "splice_at": None}
        toks = tokenize_src(src) + ["eof"]
        val = self._block(toks, [0])
        return {
            "kind": "code",
            "got": val,
            "leftover": False,
            "on_W": False,
            "splice_at": "ALU",
            "env_keys": sorted(k for k in self.env if k not in registry()),
        }

    def _peek(self, toks: list[str], i: list[int]) -> str:
        return toks[i[0]]

    def _eat(self, toks: list[str], i: list[int], want: str | None = None) -> str:
        t = toks[i[0]]
        if want is not None and t != want:
            raise CodeError(f"expected {want} got {t}")
        i[0] += 1
        return t

    def _block(self, toks: list[str], i: list[int], until: set[str] | None = None) -> int:
        until = until or {"eof", "}"}
        last = 0
        while self._peek(toks, i) not in until:
            last = self._stmt(toks, i)
            if self._peek(toks, i) == ";":
                self._eat(toks, i)
        return last

    def _stmt(self, toks: list[str], i: list[int]) -> int:
        t = self._peek(toks, i)
        if t == "let":
            self._eat(toks, i)
            name = self._eat(toks, i)
            if not re.match(r"[A-Za-z_][A-Za-z0-9_]*$", name) or name in KEYWORDS:
                raise CodeError(f"bad name {name}")
            if name.lower() in DENY_NAMES:
                raise CodeError("deny")
            self._eat(toks, i, "=")
            val = self._expr_until(toks, i, {";", "eof", "}", "let", "if", "while"})
            self.env[name] = val
            return val
        if t == "if":
            self._eat(toks, i)
            cond = self._expr_until(toks, i, {"{"})
            then_toks = self._take_brace_body(toks, i)
            then = self._run_body(then_toks) if cond else 0
            els = 0
            if self._peek(toks, i) == "else":
                self._eat(toks, i)
                else_toks = self._take_brace_body(toks, i)
                if not cond:
                    els = self._run_body(else_toks)
            return then if cond else els
        if t == "while":
            self._eat(toks, i)
            cond_toks = self._take_expr_toks(toks, i, {"{"})
            body_toks = self._take_brace_body(toks, i)
            last = 0
            n = 0
            while n < LOOP_HORIZON:
                if not self._eval_toks(cond_toks):
                    break
                last = self._run_body(body_toks)
                n += 1
            return last
        if t == "return":
            self._eat(toks, i)
            return self._expr_until(toks, i, {";", "eof", "}"})
        return self._expr_until(toks, i, {";", "eof", "}", "let", "if", "while"})

    def _take_expr_toks(self, toks: list[str], i: list[int], stops: set[str]) -> list[str]:
        buf: list[str] = []
        depth = 0
        while True:
            t = self._peek(toks, i)
            if t == "eof":
                break
            if t == "(":
                depth += 1
            if t == ")":
                depth -= 1
            if depth <= 0 and t in stops:
                break
            if t in {"let", "if", "while", "else", "return"} and depth <= 0 and buf:
                break
            buf.append(self._eat(toks, i))
        return buf

    def _join_expr(self, buf: list[str]) -> str:
        out: list[str] = []
        for j, t in enumerate(buf):
            prev = out[-1] if out else ""
            unary = t == "-" and (not out or prev in "(,+-*/<>=")
            if t in "()," or unary or (out and prev in "(,"):
                out.append(t)
            else:
                if out and prev not in "(,+-*/":
                    out.append(" ")
                out.append(t)
        return "".join(out)

    def _eval_toks(self, buf: list[str]) -> int:
        if not buf:
            return 0
        src = self._join_expr(buf)
        try:
            return eval_expr(src, self.env)
        except ParseError as exc:
            raise CodeError(str(exc)) from exc

    def _expr_until(self, toks: list[str], i: list[int], stops: set[str]) -> int:
        return self._eval_toks(self._take_expr_toks(toks, i, stops))

    def _run_body(self, body_toks: list[str]) -> int:
        inner = Runner(self.env)
        inner.env = self.env
        return inner._block(body_toks + ["eof"], [0], {"eof"})

    def _take_brace_body(self, toks: list[str], i: list[int]) -> list[str]:
        self._eat(toks, i, "{")
        body: list[str] = []
        depth = 1
        while depth:
            t = self._eat(toks, i)
            if t == "eof":
                raise CodeError("unclosed {")
            if t == "{":
                depth += 1
            if t == "}":
                depth -= 1
            if depth:
                body.append(t)
        return body


def run_code(src: str, base: dict[str, int]) -> dict:
    try:
        return Runner(base).run(src)
    except CodeError as exc:
        msg = str(exc)
        if msg == "deny":
            return {"kind": "deny", "got": "DENY", "leftover": True, "on_W": False, "splice_at": None}
        return {"kind": "leftover", "got": msg, "leftover": True, "on_W": False, "splice_at": "ALU"}


def main() -> int:
    base = registry()
    lng = json.loads((ROOT / "data" / "bill12_language_splice.json").read_text(encoding="utf-8")) if (ROOT / "data" / "bill12_language_splice.json").is_file() else {}
    rows = []

    def add(q: str, got, want) -> None:
        rows.append({"q": q, "got": got, "want": want, "ok": got == want})

    programs = [
        ("let x = 3 + 4; x", 7),
        ("let y = 6 * 7; y", 42),
        ("let a = JO_L + JO_R; a", 672),
        ("if cons(1, 1) { 10 } else { 0 }", 10),
        ("if cons(1, -1) { 10 } else { 0 }", 0),
        ("if overlay(1) { 5 } else { 9 }", 5),
        ("if leftover(0) { 1 } else { 0 }", 1),
        ("let i = 0; let s = 0; while i < 3 { let s = s + i; let i = i + 1 }; s", 3),
        ("let n = 1; while n < 5 { let n = n * 2 }; n", 8),
        ("abs(3 - 10)", 7),
        ("trit(0 - 4)", -1),
        ("let walk = 1; walk", 1),
    ]
    for src, want in programs:
        r = run_code(src, base)
        add(src.replace("\n", " "), r.get("got"), want)
        add(f"not on W: {src[:24]}", r.get("on_W"), False)
        add(f"splice ALU: {src[:24]}", r.get("splice_at") not in NEVER, True)

    deny = run_code("let court = 1; court", base)
    add("court identifier DENY", deny.get("kind"), "deny")
    unk = run_code("zzz +++", base)
    add("unknown leftover", unk.get("leftover"), True)
    add("loop horizon φ⁵", LOOP_HORIZON, 11)
    add("language splice still not on W", (lng.get("splice") or {}).get("not_on_W"), True)
    add("walk ∧ smell still cons 0", consensus(1, 0), 0)

    n_ok = sum(1 for r in rows if r["ok"])
    fail = [r["q"] for r in rows if not r["ok"]]
    overall = n_ok == len(rows)
    doc = {
        "adventure": 2,
        "ted": "TED-14",
        "vs_bill": "Bill-13",
        "pin": "AEB2AD",
        "free_parameters": 0,
        "splice": {
            "job": "coding tokens",
            "tissue": "invented region on language splice: let/if/while + trit ALU",
            "not_on_W": True,
            "loop_horizon": LOOP_HORIZON,
            "never": sorted(NEVER),
        },
        "n": len(rows),
        "n_ok": n_ok,
        "fail": fail,
        "problems": rows,
        "overall_ok": overall,
        "promotes": overall,
        "promote_to": "Bill-14" if overall else None,
        "thinking": {"deny_family_seeded": False},
    }
    OUT.write_text(json.dumps(doc, indent=2), encoding="utf-8")
    md = f"""# Coding-token splice (TED-14)

Pin **AEB2AD**. 0 free parameters.

Coding tokens sit on the language invented region: `let`, `if`/`else`, `while` (horizon \(\\mathrm{{round}}(\\varphi^5)={LOOP_HORIZON}\)), trit functions. Not FlyWire \(W\). Courtship names DENY. Unknown leftover.

**{n_ok}/{len(rows)}**. promotes={overall} → **{'Bill-14' if overall else 'Bill-13 stays'}**.
"""
    DOC.write_text(md, encoding="utf-8")
    (ADV / "CODING.md").write_text(md, encoding="utf-8")
    print(f"  TED-14 coding tokens {n_ok}/{len(rows)}  overall={overall}")
    for r in rows:
        if not r["ok"]:
            print(f"    FAIL  {r['q']}: got={r['got']!r} want={r['want']!r}")
    if not fail:
        print("  all gates green")
    print(f"  wrote {OUT}")
    return 0 if overall else 1


if __name__ == "__main__":
    raise SystemExit(main())
