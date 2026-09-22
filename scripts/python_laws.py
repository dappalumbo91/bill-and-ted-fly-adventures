#!/usr/bin/env python3
"""First-principle Python for the language sandbox.

A sentence composes from a few laws: a value, a fold (the same sum or
difference, one more term at a time), a binding, a choice, a counted
loop, and a function that is that fold with a hole. The sandbox runs
the program. A sentence that does not compose is a leftover. Courtship
names DENY. Measured W stays unchanged.

  python scripts/bill36_python_laws.py
"""
from __future__ import annotations

import ast
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from bill13_coding_tokens import DENY_NAMES, LOOP_HORIZON  # noqa: E402
from bill14_host_eval import CALLS, PySandbox  # noqa: E402

WORDS = {
    "zero": 0,
    "one": 1,
    "two": 2,
    "three": 3,
    "four": 4,
    "five": 5,
    "six": 6,
    "seven": 7,
    "eight": 8,
    "nine": 9,
    "ten": 10,
    "eleven": 11,
    "twelve": 12,
}
KEYWORDS = frozenset({
    "plus", "minus", "add", "and", "let", "be", "then", "the", "larger", "of",
    "count", "from", "to", "define", "as", "apply", "once", "twice", "times",
    "what", "is", "compute", "simplify", "work", "out",
})
RESERVED = frozenset(CALLS) | DENY_NAMES | KEYWORDS | frozenset(WORDS)


class _Fail(Exception):
    pass


def _done(kind: str, why: str) -> dict:
    return {
        "kind": kind,
        "source": None,
        "laws": [],
        "why": why,
        "leftover": True,
    }


def tokenize(text: str) -> list[list[str]]:
    if re.search(r"\d\.\d", text):
        return []
    parts = re.split(r"[.\n;]+", text.lower().replace("?", " ").replace("!", " ").replace(",", " ").replace(":", " "))
    clauses = []
    for part in parts:
        toks = re.findall(r"[a-z_]+|\d+", part)
        if toks:
            clauses.append(toks)
    return clauses


def strip_fluff(tokens: list[str]) -> list[str]:
    t = list(tokens)
    changed = True
    while changed and t:
        changed = False
        if len(t) >= 2 and t[0] == "what" and t[1] == "is":
            t = t[2:]
            changed = True
        elif t[0] in ("compute", "simplify"):
            t = t[1:]
            changed = True
        elif len(t) >= 2 and t[0] == "work" and t[1] == "out":
            t = t[2:]
            changed = True
    return t


def literal(token: str) -> int | None:
    if token in WORDS:
        return WORDS[token]
    if token.isdigit():
        return int(token)
    return None


def _bad_name(name: str) -> str | None:
    if name in DENY_NAMES:
        return "deny"
    if name in RESERVED or not re.fullmatch(r"[a-z_][a-z0-9_]*", name):
        return "refuse"
    return None


def parse_value(tokens: list[str], i: int, names: set[str]) -> tuple[dict | None, int]:
    if i >= len(tokens):
        return None, i
    t = tokens[i]
    lit = literal(t)
    if lit is not None:
        return {"law": "value", "n": lit}, i + 1
    if t in names:
        return {"law": "name", "id": t}, i + 1
    return None, i


def parse_expr(tokens: list[str], i: int, names: set[str], stop: set[str]) -> tuple[dict, int]:
    node, i = parse_value(tokens, i, names)
    if node is None:
        raise _Fail()
    ops: list[str] = []
    args = [node]
    while i < len(tokens) and tokens[i] not in stop and tokens[i] in ("plus", "minus"):
        ops.append("+" if tokens[i] == "plus" else "-")
        i += 1
        node, i = parse_value(tokens, i, names)
        if node is None:
            raise _Fail()
        args.append(node)
    if i < len(tokens) and tokens[i] not in stop:
        raise _Fail()
    if ops:
        node = {"law": "fold", "ops": ops, "args": args}
    return node, i


def _literals_only(node: dict) -> bool:
    if node["law"] == "value":
        return True
    if node["law"] == "fold":
        return all(_literals_only(arg) for arg in node["args"])
    return False


def parse_define(tokens: list[str]) -> dict:
    if len(tokens) < 5 or tokens[2] != "as" or tokens[3] not in ("add", "minus"):
        raise _Fail()
    name = tokens[1]
    bad = _bad_name(name)
    if bad == "deny":
        return {"law": "deny"}
    if bad:
        raise _Fail()
    op = "+" if tokens[3] == "add" else "-"
    expr, i = parse_expr(tokens, 4, set(), set())
    if i != len(tokens) or not _literals_only(expr):
        raise _Fail()
    return {"law": "define", "name": name, "op": op, "expr": expr}


def parse_apply(tokens: list[str], defined: set[str], bound: set[str]) -> dict:
    if len(tokens) < 4:
        raise _Fail()
    name = tokens[1]
    if name in DENY_NAMES:
        return {"law": "deny"}
    if _bad_name(name) == "refuse" or name not in defined:
        if name not in defined and name not in DENY_NAMES:
            return {"law": "refuse", "why": "unbound"}
        raise _Fail()
    idx = 2
    if tokens[idx] == "once":
        times = 1
        idx += 1
    elif tokens[idx] == "twice":
        times = 2
        idx += 1
    elif tokens[idx] == "to":
        times = 1
    elif literal(tokens[idx]) is not None and idx + 1 < len(tokens) and tokens[idx + 1] == "times":
        times = literal(tokens[idx])
        idx += 2
    else:
        raise _Fail()
    if times is None or times < 1:
        raise _Fail()
    if idx >= len(tokens) or tokens[idx] != "to":
        raise _Fail()
    arg, j = parse_expr(tokens, idx + 1, bound, set())
    if j != len(tokens):
        raise _Fail()
    if times > LOOP_HORIZON:
        return {"law": "refuse", "why": "horizon"}
    return {"law": "apply", "name": name, "times": times, "arg": arg}


def parse_let(tokens: list[str], bound: set[str]) -> dict:
    if len(tokens) < 6 or tokens[2] != "be":
        raise _Fail()
    name = tokens[1]
    bad = _bad_name(name)
    if bad == "deny":
        return {"law": "deny"}
    if bad:
        raise _Fail()
    expr, i = parse_expr(tokens, 3, set(bound), {"then"})
    if i >= len(tokens) or tokens[i] != "then":
        raise _Fail()
    rest = tokens[i + 1 :]
    names = set(bound)
    names.add(name)
    if rest and rest[0] == "add":
        vals = []
        j = 1
        while True:
            val, j2 = parse_value(rest, j, names)
            if val is None:
                raise _Fail()
            vals.append(val)
            j = j2
            if j < len(rest) and rest[j] == "and":
                j += 1
                continue
            break
        if j != len(rest) or not vals:
            raise _Fail()
        then = {"law": "fold", "ops": ["+"] * len(vals), "args": [{"law": "name", "id": name}, *vals]}
    else:
        then, j = parse_expr(rest, 0, names, set())
        if j != len(rest):
            raise _Fail()
    return {"law": "bind", "name": name, "expr": expr, "then": then}


def parse_larger(tokens: list[str], bound: set[str]) -> dict:
    i = 1 if tokens and tokens[0] == "the" else 0
    if i + 1 >= len(tokens) or tokens[i] != "larger" or tokens[i + 1] != "of":
        raise _Fail()
    a, i = parse_expr(tokens, i + 2, set(bound), {"and"})
    if i >= len(tokens) or tokens[i] != "and":
        raise _Fail()
    b, i = parse_expr(tokens, i + 1, set(bound), set())
    if i != len(tokens):
        raise _Fail()
    return {"law": "larger", "a": a, "b": b}


def parse_count(tokens: list[str]) -> dict:
    if len(tokens) != 5 or tokens[1] != "from" or tokens[3] != "to":
        raise _Fail()
    start = literal(tokens[2])
    stop = literal(tokens[4])
    if start is None or stop is None:
        raise _Fail()
    steps = stop - start
    if steps < 0:
        raise _Fail()
    if steps > LOOP_HORIZON:
        return {"law": "refuse", "why": "horizon"}
    return {"law": "count", "start": start, "stop": stop}


def parse_add(tokens: list[str], bound: set[str]) -> dict:
    vals = []
    i = 1
    while True:
        val, j = parse_value(tokens, i, bound)
        if val is None:
            raise _Fail()
        vals.append(val)
        i = j
        if i < len(tokens) and tokens[i] == "and":
            i += 1
            continue
        break
    if i != len(tokens) or len(vals) < 2:
        raise _Fail()
    return {"law": "fold", "ops": ["+"] * (len(vals) - 1), "args": vals}


def parse_clause(tokens: list[str], defined: set[str], bound: set[str]) -> dict:
    tokens = strip_fluff(tokens)
    if not tokens:
        raise _Fail()
    head = tokens[0]
    if head == "define":
        return parse_define(tokens)
    if head == "apply":
        return parse_apply(tokens, defined, bound)
    if head == "let":
        return parse_let(tokens, bound)
    if head in ("the", "larger"):
        return parse_larger(tokens, bound)
    if head == "count":
        return parse_count(tokens)
    if head == "add":
        return parse_add(tokens, bound)
    node, i = parse_expr(tokens, 0, set(bound), set())
    if i != len(tokens):
        raise _Fail()
    return node


def emit_expr(node: dict) -> str:
    law = node["law"]
    if law == "value":
        return str(int(node["n"]))
    if law == "name":
        return str(node["id"])
    if law == "fold":
        expr = emit_expr(node["args"][0])
        for op, arg in zip(node["ops"], node["args"][1:]):
            expr = f"({expr} {op} {emit_expr(arg)})"
        return expr
    if law == "larger":
        a = emit_expr(node["a"])
        b = emit_expr(node["b"])
        return f"({a} if {a} > {b} else {b})"
    raise _Fail()


def emit(nodes: list[dict]) -> str:
    lines: list[str] = []
    for node in nodes:
        law = node["law"]
        if law == "define":
            lines.append(f"def {node['name']}(n):")
            lines.append(f"    return n {node['op']} {emit_expr(node['expr'])}")
        elif law == "bind":
            lines.append(f"{node['name']} = {emit_expr(node['expr'])}")
            lines.append(emit_expr(node["then"]))
        elif law == "count":
            lines.append(f"k = {int(node['start'])}")
            lines.append(f"while k < {int(node['stop'])}:")
            lines.append("    k = k + 1")
            lines.append("k")
        elif law == "apply":
            expr = emit_expr(node["arg"])
            for _ in range(int(node["times"])):
                expr = f"{node['name']}({expr})"
            lines.append(expr)
        else:
            lines.append(emit_expr(node))
    return "\n".join(lines)


def compose(prompt: str) -> dict:
    """Build a program from the laws. The wanted number is not an input."""
    clauses = tokenize(prompt)
    if not clauses:
        return _done("leftover", "does not compose")
    nodes: list[dict] = []
    laws: list[str] = []
    defined: set[str] = set()
    bound: set[str] = set()
    try:
        for clause in clauses:
            node = parse_clause(clause, defined, bound)
            if node["law"] == "deny":
                return _done("deny", "DENY")
            if node["law"] == "refuse":
                return _done("leftover", str(node.get("why") or "leftover"))
            nodes.append(node)
            laws.append(str(node["law"]))
            if node["law"] == "define":
                defined.add(str(node["name"]))
            elif node["law"] == "bind":
                bound.add(str(node["name"]))
        source = emit(nodes)
    except _Fail:
        return _done("leftover", "does not compose")
    return {"kind": "code", "source": source, "laws": laws, "why": "", "leftover": False}


def _host_python(prompt: str) -> bool:
    """Import, open, and assignment are sandbox sentences. Other leftovers stay leftovers."""
    try:
        ast.parse(prompt)
    except SyntaxError:
        return False
    text = prompt.strip()
    return text.startswith("import ") or text.startswith("from ") or "open(" in text or "=" in text


def run_prompt(prompt: str) -> dict:
    """Compose from the laws, then run that source in the sandbox."""
    made = compose(prompt)
    base = {
        "source": made.get("source"),
        "laws": list(made.get("laws") or []),
        "why": made.get("why") or "",
        "on_W": False,
    }
    if made["kind"] == "deny":
        return {**base, "kind": "deny", "got": "DENY", "leftover": True}
    if made["kind"] == "leftover" and made.get("why") != "does not compose":
        return {**base, "kind": "leftover", "got": None, "leftover": True}
    if made.get("source"):
        py = PySandbox({}).run(str(made["source"]))
        return {
            **base,
            "kind": py["kind"],
            "got": py.get("got"),
            "leftover": bool(py.get("leftover")),
            "why": base["why"] or (str(py.get("got")) if py.get("leftover") else ""),
        }
    if not _host_python(prompt):
        return {**base, "kind": "leftover", "got": None, "leftover": True, "why": "does not compose"}
    py = PySandbox({}).run(prompt)
    return {
        "source": None,
        "laws": [],
        "why": str(py.get("got") or "does not compose"),
        "on_W": False,
        "kind": py["kind"],
        "got": py.get("got"),
        "leftover": bool(py.get("leftover")),
    }
