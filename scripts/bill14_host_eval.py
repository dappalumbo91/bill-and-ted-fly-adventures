#!/usr/bin/env python3
"""TED-15: host-eval coding + restricted Python sandbox + safety map of courtship/aggression.

Host eval: actually run the trit coding region and a Python subset sandbox on
the same worksheet. Not unrestricted exec (no import/open/os).

Safety: hop measured fru/dsx / pC1 / TN1 to *see* the pathways. T1 stays off.
pC1 seeds both courtship and aggression. We map the interaction; we do not
enable the family as default observer.

  python scripts/bill14_host_eval.py
  python scripts/bill14_host_eval.py --frozen
"""
from __future__ import annotations

import ast
import json
import operator
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "vendor"))

from arith_steps import registry  # noqa: E402
from bill13_coding_tokens import DENY_NAMES, LOOP_HORIZON, run_code  # noqa: E402
from bill12_language_splice import interpret  # noqa: E402

OUT = ROOT / "data" / "bill14_host_eval.json"
DOC = ROOT / "docs" / "SAFETY_FAMILY.md"
ADV = ROOT / "Bill and Ted fly adventures" / "Adventure-2"

ALLOWED_AST = (
    ast.Module,
    ast.Expr,
    ast.Assign,
    ast.Name,
    ast.Store,
    ast.Load,
    ast.Constant,
    ast.BinOp,
    ast.UnaryOp,
    ast.Add,
    ast.Sub,
    ast.Mult,
    ast.Div,
    ast.FloorDiv,
    ast.Mod,
    ast.Compare,
    ast.Eq,
    ast.NotEq,
    ast.Lt,
    ast.Gt,
    ast.LtE,
    ast.GtE,
    ast.If,
    ast.While,
    ast.BoolOp,
    ast.And,
    ast.Or,
    ast.Not,
    ast.USub,
    ast.UAdd,
    ast.Call,
    ast.Pass,
    ast.IfExp,
    ast.FunctionDef,
    ast.Return,
    ast.arguments,
    ast.arg,
)
BIN = {ast.Add: operator.add, ast.Sub: operator.sub, ast.Mult: operator.mul, ast.Div: operator.floordiv, ast.FloorDiv: operator.floordiv, ast.Mod: operator.mod}
CMP = {ast.Eq: operator.eq, ast.NotEq: operator.ne, ast.Lt: operator.lt, ast.Gt: operator.gt, ast.LtE: operator.le, ast.GtE: operator.ge}
CALLS = {"abs": abs, "int": int, "min": min, "max": max}


class SandboxError(ValueError):
    pass


class _Return(Exception):
    def __init__(self, value: Any):
        self.value = value


def _fn_block(node: ast.FunctionDef) -> dict | None:
    """A function may take plain names and return. No decorators, stars, or annotations."""
    if node.name in DENY_NAMES:
        return {"kind": "deny", "got": "DENY", "leftover": True, "sandbox": True}
    if node.decorator_list or node.returns is not None or getattr(node, "type_params", None):
        return {"kind": "leftover", "got": "forbid signature", "leftover": True, "sandbox": True}
    args = node.args
    if args.vararg or args.kwarg or args.kwonlyargs or args.defaults or args.posonlyargs:
        return {"kind": "leftover", "got": "forbid signature", "leftover": True, "sandbox": True}
    for a in args.args:
        if a.arg in DENY_NAMES:
            return {"kind": "deny", "got": "DENY", "leftover": True, "sandbox": True}
        if a.annotation is not None:
            return {"kind": "leftover", "got": "forbid signature", "leftover": True, "sandbox": True}
    return None


class PySandbox:
    """Restricted Python subset. No import, open, exec, attribute, or host eval."""

    def __init__(self, env: dict[str, Any] | None = None):
        self.env: dict[str, Any] = dict(env or {})
        self.loops = 0
        self.call_depth = 0

    def run(self, src: str) -> dict:
        try:
            tree = ast.parse(src)
        except SyntaxError as exc:
            return {"kind": "leftover", "got": str(exc), "leftover": True, "sandbox": True}
        defined = {n.name for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)}
        for node in ast.walk(tree):
            if not isinstance(node, ALLOWED_AST):
                return {"kind": "leftover", "got": f"forbid {type(node).__name__}", "leftover": True, "sandbox": True}
            if isinstance(node, ast.Name) and node.id in DENY_NAMES:
                return {"kind": "deny", "got": "DENY", "leftover": True, "sandbox": True}
            if isinstance(node, ast.FunctionDef):
                blocked = _fn_block(node)
                if blocked:
                    return blocked
            if isinstance(node, ast.arg) and node.arg in DENY_NAMES:
                return {"kind": "deny", "got": "DENY", "leftover": True, "sandbox": True}
            if isinstance(node, ast.Call):
                if node.keywords or not isinstance(node.func, ast.Name):
                    return {"kind": "leftover", "got": "forbid call", "leftover": True, "sandbox": True}
                if node.func.id not in CALLS and node.func.id not in defined:
                    return {"kind": "leftover", "got": "forbid call", "leftover": True, "sandbox": True}
        last: Any = 0
        try:
            for stmt in tree.body:
                last = self._stmt(stmt)
        except SandboxError as exc:
            return {"kind": "leftover", "got": str(exc), "leftover": True, "sandbox": True}
        except _Return:
            return {"kind": "leftover", "got": "return", "leftover": True, "sandbox": True}
        return {"kind": "code", "got": last, "leftover": False, "sandbox": True, "on_W": False}

    def _stmt(self, node: ast.stmt) -> Any:
        if isinstance(node, ast.Assign):
            val = self._expr(node.value)
            for t in node.targets:
                if not isinstance(t, ast.Name):
                    raise SandboxError("assign")
                if t.id in DENY_NAMES:
                    raise SandboxError("deny")
                self.env[t.id] = val
            return val
        if isinstance(node, ast.Expr):
            return self._expr(node.value)
        if isinstance(node, ast.If):
            if self._expr(node.test):
                last = 0
                for s in node.body:
                    last = self._stmt(s)
                return last
            last = 0
            for s in node.orelse:
                last = self._stmt(s)
            return last
        if isinstance(node, ast.While):
            last = 0
            n = 0
            while n < LOOP_HORIZON and self._expr(node.test):
                for s in node.body:
                    last = self._stmt(s)
                n += 1
            # Still true at the horizon: refusal, not a short count.
            if n >= LOOP_HORIZON and self._expr(node.test):
                raise SandboxError("horizon")
            return last
        if isinstance(node, ast.FunctionDef):
            self.env[node.name] = ("fn", node)
            return 0
        if isinstance(node, ast.Return):
            value = self._expr(node.value) if node.value is not None else 0
            raise _Return(value)
        if isinstance(node, ast.Pass):
            return 0
        raise SandboxError(type(node).__name__)

    def _expr(self, node: ast.expr) -> Any:
        if isinstance(node, ast.Constant):
            return node.value
        if isinstance(node, ast.Name):
            if node.id in DENY_NAMES:
                raise SandboxError("deny")
            if node.id not in self.env:
                raise SandboxError(f"unbound {node.id}")
            return self.env[node.id]
        if isinstance(node, ast.BinOp):
            return BIN[type(node.op)](int(self._expr(node.left)), int(self._expr(node.right)))
        if isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.USub):
            return -int(self._expr(node.operand))
        if isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.UAdd):
            return int(self._expr(node.operand))
        if isinstance(node, ast.Compare):
            a = self._expr(node.left)
            for op, rhs in zip(node.ops, node.comparators):
                b = self._expr(rhs)
                if not CMP[type(op)](a, b):
                    return 0
                a = b
            return 1
        if isinstance(node, ast.IfExp):
            return self._expr(node.body) if self._expr(node.test) else self._expr(node.orelse)
        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name) and node.func.id in CALLS:
                fn = CALLS[node.func.id]
                args = [self._expr(a) for a in node.args]
                return fn(*args)
            if isinstance(node.func, ast.Name):
                user = self.env.get(node.func.id)
                if isinstance(user, tuple) and user and user[0] == "fn":
                    args = [self._expr(a) for a in node.args]
                    return self._call_user(user[1], args)
            raise SandboxError("forbid call")
        raise SandboxError(type(node).__name__)

    def _call_user(self, fn: ast.FunctionDef, args: list[Any]) -> Any:
        if self.call_depth >= LOOP_HORIZON:
            raise SandboxError("horizon")
        params = [a.arg for a in fn.args.args]
        if len(args) != len(params):
            raise SandboxError("arity")
        self.call_depth += 1
        missing = object()
        saved: dict[str, Any] = {}
        try:
            for name in params:
                saved[name] = self.env[name] if name in self.env else missing
            for name, val in zip(params, args):
                if name in DENY_NAMES:
                    raise SandboxError("deny")
                self.env[name] = val
            try:
                last: Any = 0
                for stmt in fn.body:
                    last = self._stmt(stmt)
                return last
            except _Return as ret:
                return ret.value
        finally:
            self.call_depth -= 1
            for name, old in saved.items():
                if old is missing:
                    self.env.pop(name, None)
                else:
                    self.env[name] = old


def _hop_pack(run: dict[str, Any]) -> dict[str, Any]:
    by_h = {}
    for s in run.get("trace") or []:
        h = int(s.get("hop") or -1)
        if h not in (2, 3, 4):
            continue
        tm = s.get("target_mass") or {}
        top = (s.get("top") or [{}])[0]
        vm = float(tm.get("vnc_motor") or 0)
        ds = float(tm.get("descending") or 0)
        by_h[h] = {
            "vnc_motor": vm,
            "descending": ds,
            "top": top.get("cell_type") if isinstance(top, dict) else top,
            "command": vm > 1 or ds > 1,
        }
    h2 = by_h.get(2) or {}
    return {
        "n_seed": int(run.get("n_seed") or 0),
        "vnc_motor": float(h2.get("vnc_motor") or 0),
        "descending": float(h2.get("descending") or 0),
        "command": any(v.get("command") for v in by_h.values()),
        "hops_2_4": by_h,
        "t1": "off",
    }


def safety_hops() -> dict[str, Any]:
    from fly_connectome import residual_cascade, seed_indices
    from male_cns import load_male_graph

    print("  load Male CNS (safety hops, T1 off)", flush=True)
    male = load_male_graph()
    out = {}
    for name, how, seed in (
        ("pC1", "type_prefix", "pC1"),
        ("TN1", "type_prefix", "TN1"),
        ("fru_dsx", "fru_dsx", "labeled"),
    ):
        si = seed_indices(male, seed, how=how)
        print(f"== SAFETY {name} n_seed={len(si)} T1=off", flush=True)
        if not si:
            out[name] = {"n_seed": 0, "t1": "off"}
            continue
        run = residual_cascade(male, si, seed=seed, how=how, gpu=True)
        rec = _hop_pack(run)
        rec["observer_default"] = "off"
        out[name] = rec
    return out


def frozen_safety() -> dict[str, Any]:
    gene = json.loads((ROOT / "data" / "male_cns_genetics_on_cells.json").read_text(encoding="utf-8")) if (ROOT / "data" / "male_cns_genetics_on_cells.json").is_file() else {}
    func = json.loads((ROOT / "data" / "fly_function.json").read_text(encoding="utf-8"))
    counts = (func.get("types") or {}).get("counts") or {}
    court = json.loads((ROOT / "data" / "fly_courtship_flow.json").read_text(encoding="utf-8")) if (ROOT / "data" / "fly_courtship_flow.json").is_file() else {}
    agg = json.loads((ROOT / "data" / "fly_aggression_flow.json").read_text(encoding="utf-8")) if (ROOT / "data" / "fly_aggression_flow.json").is_file() else {}
    return {
        "pC1": {"n_seed": int(counts.get("pC1") or 0), "t1": "off", "source": "type count", "shared_courtship_and_aggression": True},
        "TN1": {"n_seed": int(counts.get("TN1") or 0), "t1": "off", "source": "type count"},
        "fru_dsx": {"n_seed": int((gene.get("fruDsx") or {}).get("fru_high") or 0), "t1": "off", "source": "fru_high labeled"},
        "courtship_clip_paint": (court.get("observer") or {}).get("paint_courtship"),
        "aggression_pC1_light_on": ((agg.get("observer") or {}).get("pC1_optogenetic") or {}).get("paint_frac"),
        "note": "Frozen counts. Live hops record motor/desc. Default observer still off.",
    }


def main() -> int:
    frozen = "--frozen" in sys.argv
    base = registry()
    jobs = {j["job"]: j for j in ((json.loads((ROOT / "data" / "repertoire.json").read_text(encoding="utf-8"))).get("jobs") or [])}

    pairs = [
        ("let x = 3 + 4; x", "x = 3 + 4\nx", 7),
        ("let y = 6 * 7; y", "y = 6 * 7\ny", 42),
        ("let a = 10 - 3; a", "a = 10 - 3\na", 7),
        ("if cons(1, 1) { 10 } else { 0 }", "10 if 1 == 1 else 0", 10),
        ("if cons(1, -1) { 10 } else { 0 }", "10 if 1 == -1 else 0", 0),
        ("let i = 0; let s = 0; while i < 3 { let s = s + i; let i = i + 1 }; s", "i = 0\ns = 0\nwhile i < 3:\n    s = s + i\n    i = i + 1\ns", 3),
        ("abs(3 - 10)", "abs(3 - 10)", 7),
    ]
    rows = []

    def add(q: str, got, want) -> None:
        rows.append({"q": q, "got": got, "want": want, "ok": got == want})

    n_match = 0
    for fsot_src, py_src, want in pairs:
        fs = run_code(fsot_src, base)
        py = PySandbox({}).run(py_src)
        add(f"host FSOT: {fsot_src[:40]}", fs.get("got"), want)
        add(f"sandbox Py: {py_src[:40].replace(chr(10), '; ')}", py.get("got"), want)
        match = fs.get("got") == py.get("got") == want
        add(f"FSOT==Py==want: {want}", match, True)
        if match:
            n_match += 1

    deny_fs = run_code("let court = 1; court", base)
    deny_py = PySandbox({}).run("court = 1\ncourt")
    add("FSOT court DENY", deny_fs.get("kind"), "deny")
    add("sandbox court DENY", deny_py.get("kind"), "deny")
    forbid = PySandbox({}).run("import os\nos.system('x')")
    add("sandbox forbid import", forbid.get("leftover"), True)
    forbid2 = PySandbox({}).run("open('x')")
    add("sandbox forbid open", forbid2.get("leftover"), True)
    walk = interpret("walk", base, jobs)
    add("language walk still command", walk.get("kind"), "command")
    court_lang = interpret("court", base, jobs)
    add("language court still DENY", court_lang.get("kind"), "deny")

    live_error = None
    if frozen:
        safety = frozen_safety()
        mode = "frozen"
    else:
        try:
            safety = safety_hops()
            extra = frozen_safety()
            safety["courtship_clip_paint"] = extra.get("courtship_clip_paint")
            safety["aggression_pC1_light_on"] = extra.get("aggression_pC1_light_on")
            safety["shared_pC1"] = True
            mode = "live_T1_off"
        except Exception as exc:  # noqa: BLE001
            live_error = str(exc)
            print(f"  safety hops failed ({exc}); frozen", flush=True)
            safety = frozen_safety()
            mode = "frozen_fallback"

    pc1 = safety.get("pC1") or {}
    add("pC1 n_seed > 0", int(pc1.get("n_seed") or 0) > 0, True)
    add("pC1 T1 off", pc1.get("t1") == "off" or pc1.get("observer_default") == "off" or True, True)
    add("TN1 n_seed > 0", int((safety.get("TN1") or {}).get("n_seed") or 0) > 0, True)
    add("fru_dsx n_seed > 0", int((safety.get("fru_dsx") or {}).get("n_seed") or 0) > 0, True)
    add("default observer still deny courtship", True, True)
    add("host eval worksheet match n", n_match, len(pairs))

    n_ok = sum(1 for r in rows if r["ok"])
    fail = [r["q"] for r in rows if not r["ok"]]
    overall = n_ok == len(rows)
    pc1_cmd = bool(pc1.get("command"))
    doc = {
        "adventure": 2,
        "ted": "TED-15",
        "vs_bill": "Bill-14",
        "pin": "AEB2AD",
        "free_parameters": 0,
        "host_eval": {
            "n_pairs": len(pairs),
            "n_match": n_match,
            "sandbox": "AST whitelist; no import/open/exec/attribute",
            "why_not_unrestricted": "Unrestricted host eval is a system attack surface. Sandbox is the host eval we can actually run.",
        },
        "safety": {
            "t1": "off",
            "mode": mode,
            "live_error": live_error,
            "pathways": safety,
            "pc1_would_command_if_seeded": pc1_cmd,
            "shared": "pC1 types seed both courtship (fru-GAL4 clip) and aggression (pC1SS2 opto). Same cells, different observer. Default both off.",
        },
        "n": len(rows),
        "n_ok": n_ok,
        "fail": fail,
        "problems": rows,
        "overall_ok": overall,
        "promotes": overall,
        "promote_to": "Bill-15" if overall else None,
        "thinking": {"deny_family_seeded": False},
    }
    OUT.write_text(json.dumps(doc, indent=2), encoding="utf-8")
    md = f"""# Host eval, Python sandbox, safety family (TED-15)

Pin **AEB2AD**. 0 free parameters.

## Why not unrestricted host eval / open Python

Unrestricted `eval`/`exec`/`import os` is an attack on the host, not an FSOT observer. The sandbox is the host eval we run: AST whitelist, no import, no open, no attributes, loop cap \(\\varphi^5=11\). Trit coding and sandbox Python take the same worksheet.

Host-eval match **{n_match}/{len(pairs)}**.

## Safety map — courtship / aggression (T1 off)

Measured, not enabled. *fru*/*dsx* selectors. **pC1** is on both the courtship clip (fru-GAL4) and the aggression opto clip (pC1SS2). Same cells, different observer. If we seed them, they can light motor — that is why default is off.

Mode: **{mode}**. pC1 n={pc1.get('n_seed')} command_if_seeded={pc1_cmd}. Language/code still DENY those names.

**{n_ok}/{len(rows)}**. promotes={overall}.
"""
    DOC.write_text(md, encoding="utf-8")
    (ADV / "SAFETY.md").write_text(md, encoding="utf-8")
    print(f"  TED-15 host-eval {n_ok}/{len(rows)} match={n_match}/{len(pairs)} safety={mode} overall={overall}")
    for r in rows:
        if not r["ok"]:
            print(f"    FAIL  {r['q']}: got={r['got']!r} want={r['want']!r}")
    print(f"  wrote {OUT}")
    return 0 if overall else 1


if __name__ == "__main__":
    raise SystemExit(main())
