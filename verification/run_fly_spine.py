#!/usr/bin/env python3
"""Run the fly obligation spine through the prover list.

  python verification/export_fly_spine.py
  python verification/run_fly_spine.py

Layers: Python obligations, decision rule, Z3, Lean, Coq, Isabelle, F*, Rust, TLA+.
A missing tool fails the run. This spine does not inherit the genetics D1D38A report.
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import runio  # noqa: E402

runio.install()

FLY = ROOT / "verification" / "fly"
OBL = FLY / "obligations.json"
REPORT = ROOT / "data" / "fly_spine_report.json"
ISA_HOME = Path(r"C:\Users\damia\Desktop\Isabelle2025-2")
FSTAR_CANDIDATES = [
    Path(os.environ.get("FSTAR_HOME") or ""),
    Path(r"C:\Users\damia\tools\fstar-v2026.07.05"),
    Path(r"I:\FSOT-Physical-Archive\07_Portable-Toolchain\fstar"),
]
TLA_CANDIDATES = [
    Path(r"C:\Users\damia\tools\tla\tla2tools.jar"),
    Path(r"C:\Users\damia\Desktop\FSOT-Genetics\verification\tla\tla2tools.jar"),
    Path(r"C:\Users\damia\Desktop\FSOT-2.1-Lean\tools\tla\tla2tools.jar"),
]


def run(cmd: list[str], cwd: Path | None = None, timeout: int = 180, env: dict | None = None) -> tuple[int, str]:
    try:
        proc = subprocess.run(
            cmd,
            cwd=str(cwd or ROOT),
            capture_output=True,
            text=True,
            timeout=timeout,
            env=env,
        )
        out = (proc.stdout or "") + (proc.stderr or "")
        return proc.returncode, out
    except FileNotFoundError as exc:
        return 127, str(exc)
    except subprocess.TimeoutExpired:
        return 124, "timeout"


def which(names: tuple[str, ...], extra: list[Path] | None = None) -> str | None:
    for name in names:
        found = shutil.which(name)
        if found:
            return found
    for path in extra or []:
        if path.is_file():
            return str(path)
    return None


def cygpath(win: Path) -> str:
    resolved = win.resolve()
    drive = resolved.drive.rstrip(":").lower()
    tail = resolved.as_posix().split(":", 1)[-1]
    return f"/cygdrive/{drive}{tail}"


def resolve_isabelle() -> dict | None:
    tool = shutil.which("isabelle")
    if tool:
        return {"mode": "posix", "tool": tool}
    bash = ISA_HOME / "contrib" / "cygwin" / "bin" / "bash.exe"
    sh = ISA_HOME / "bin" / "isabelle"
    if bash.is_file() and sh.is_file():
        return {"mode": "cygwin", "tool": str(sh), "bash": str(bash), "home": str(ISA_HOME)}
    return None


def fstar_home() -> Path | None:
    for cand in FSTAR_CANDIDATES:
        if cand and (cand / "bin" / "fstar.exe").is_file():
            return cand
    return None


def tla_jar() -> Path | None:
    for cand in TLA_CANDIDATES:
        if cand.is_file():
            return cand
    return None


def check_obligations(doc: dict) -> tuple[int, str]:
    failed = []
    for row in doc.get("obligations") or []:
        lhs, rhs, kind = int(row["lhs"]), int(row["rhs"]), row["kind"]
        ok = (
            (kind == "nat_eq" and lhs == rhs)
            or (kind == "nat_lt" and lhs < rhs)
            or (kind == "nat_le" and lhs <= rhs)
            or (kind == "nat_gt" and lhs > rhs)
        )
        if not ok:
            failed.append(row["id"])
    for pred in doc.get("predictions") or []:
        if pred.get("filled") or pred.get("status") != "absent":
            failed.append(pred["id"])
        holds = pred.get("holds_now") or {}
        if "frame_count" in holds and holds["frame_count"] is not None:
            failed.append(pred["id"] + "_frames")
        if "body_id_count" in holds and holds["body_id_count"] is not None:
            failed.append(pred["id"] + "_ids")
    text = f"obligations={len(doc.get('obligations') or [])} predictions={len(doc.get('predictions') or [])} fail={len(failed)}"
    if failed:
        return 1, text + " " + " ".join(failed)
    return 0, text


def check_decision() -> tuple[int, str]:
    def commit(votes: list[str]) -> str | None:
        uniq: list[str] = []
        for vote in votes:
            if vote not in uniq:
                uniq.append(vote)
        return uniq[0] if len(uniq) == 1 else None

    cases = [
        (["reflect"], "reflect"),
        ([], None),
        (["rain", "drought"], None),
        (["gas", "gas"], "gas"),
    ]
    bad = [votes for votes, want in cases if commit(votes) != want]
    if bad:
        return 1, f"decision fail {bad}"
    return 0, "one label overlays; disagreement or silence is trit 0; a repeated label overlays"


def main() -> int:
    if not OBL.is_file():
        print("needs verification/fly/obligations.json from export_fly_spine.py", file=sys.stderr)
        return 2
    doc = json.loads(OBL.read_text(encoding="utf-8"))
    layers: list[dict] = []

    def record(name: str, rc: int, detail: str) -> None:
        status = "PASS" if rc == 0 else "FAIL"
        layers.append(
            {
                "name": name,
                "required": True,
                "ok": rc == 0,
                "status": status,
                "returncode": rc,
                "detail": detail[-1500:],
            }
        )
        print(f"[{status}] {name}")
        if status == "FAIL" and detail:
            print(detail[-1200:])

    rc, out = check_obligations(doc)
    record("python_obligations", rc, out)
    rc, out = check_decision()
    record("decision_rule", rc, out)

    z3 = which(("z3", "z3.exe"), [Path(r"C:\Users\damia\tools\bin\z3.exe")])
    if not z3:
        record("smt_z3", 127, "z3 not found")
    else:
        rc, out = run([z3, str(FLY / "smt" / "fly_spine.smt2")])
        first = (out.strip().splitlines() or [""])[-1].strip()
        ok = rc == 0 and first == "sat"
        record("smt_z3", 0 if ok else 1, out)

    lean = which(("lean", "lean.exe"))
    if not lean:
        record("lean", 127, "lean not found")
    else:
        rc, out = run([lean, str(FLY / "lean" / "FlySpine.lean")], timeout=180)
        record("lean", rc, out)

    coqc = which(("coqc", "coqc.exe", "rocqc", "rocqc.exe"))
    if not coqc:
        record("coq", 127, "coqc not found")
    else:
        with tempfile.TemporaryDirectory(prefix="fsot_fly_coq_") as tmp:
            src = Path(tmp) / "FlySpine.v"
            src.write_text((FLY / "coq" / "FlySpine.v").read_text(encoding="utf-8"), encoding="utf-8")
            rc, out = run([coqc, "-q", "FlySpine.v"], cwd=Path(tmp), timeout=180)
        record("coq", rc, out)

    isa = resolve_isabelle()
    if not isa:
        record("isabelle", 127, "isabelle not found")
    else:
        thy = FLY / "isabelle"
        if isa["mode"] == "cygwin":
            cmd = f"cd '{cygpath(Path(isa['home']))}' && bin/isabelle build -D '{cygpath(thy)}' FlySpine"
            rc, out = run([isa["bash"], "--login", "-c", cmd], timeout=900)
        else:
            rc, out = run([isa["tool"], "build", "-D", str(thy), "FlySpine"], timeout=900)
        record("isabelle", rc, out)

    home = fstar_home()
    fstar = str(home / "bin" / "fstar.exe") if home else which(("fstar", "fstar.exe"))
    if not fstar:
        record("fstar", 127, "fstar not found")
    else:
        env = os.environ.copy()
        if home:
            env["FSTAR_HOME"] = str(home)
        fstar_z3 = None
        if home:
            for cand in (home / "bin" / "z3-4.13.3.exe", home / "bin" / "z3.exe"):
                if cand.is_file():
                    fstar_z3 = str(cand)
                    break
        cmd = [fstar]
        if fstar_z3:
            cmd += ["--smt", fstar_z3]
        elif z3:
            cmd += ["--smt", z3, "--z3version", "4.15.4"]
        cmd.append("FlySpine.fst")
        rc, out = run(cmd, cwd=FLY / "fstar", timeout=300, env=env)
        record("fstar", rc, out)

    cargo = which(("cargo", "cargo.exe"))
    if not cargo:
        record("rust", 127, "cargo not found")
    else:
        env = os.environ.copy()
        env["CARGO_TARGET_DIR"] = str(Path(tempfile.gettempdir()) / "fsot_fly_spine_target")
        rc, out = run(
            [cargo, "run", "--quiet", "--release"],
            cwd=FLY / "rust",
            timeout=300,
            env=env,
        )
        ok = rc == 0 and "FSOT_FLY_SPINE_RUST_OK" in out
        record("rust", 0 if ok else rc or 1, out)

    jar = tla_jar()
    java = which(("java", "java.exe"))
    if not java or not jar:
        record("tla", 127, "java or tla2tools.jar missing")
    else:
        with tempfile.TemporaryDirectory(prefix="fsot_fly_tla_") as tmp:
            dest = Path(tmp)
            for name in ("FlySpine.tla", "FlySpine.cfg"):
                (dest / name).write_text((FLY / "tla" / name).read_text(encoding="utf-8"), encoding="utf-8")
            rc, out = run(
                [java, "-cp", str(jar), "tlc2.TLC", "-config", "FlySpine.cfg", "FlySpine.tla"],
                cwd=dest,
                timeout=180,
            )
        ok = rc == 0 and "No error has been found" in out
        if ok:
            kept = [
                line.strip()
                for line in out.splitlines()
                if "No error has been found" in line
                or "distinct states found" in line
                or line.startswith("Finished computing initial states")
            ]
            out = "\n".join(kept) if kept else "No error has been found"
        record("tla", 0 if ok else 1, out)

    failed = [layer["name"] for layer in layers if layer["status"] != "PASS"]
    report = {
        "application": "fly-obligation-spine",
        "inherits_hub_overall_ok": False,
        "inherits_genetics_report": False,
        "pin": "AEB2AD",
        "free_parameters": 0,
        "current_bill": doc.get("current_bill"),
        "law": doc.get("law"),
        "n_obligations": doc.get("n_obligations"),
        "n_predictions": doc.get("n_predictions"),
        "predictions": doc.get("predictions"),
        "overall_ok": not failed,
        "layers": layers,
        "frameworks_passed": [layer["name"] for layer in layers if layer["status"] == "PASS"],
        "frameworks_failed": failed,
    }
    REPORT.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(
        f"fly spine obligations={report['n_obligations']} predictions={report['n_predictions']} "
        f"overall_ok={report['overall_ok']}"
    )
    return 0 if report["overall_ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
