#!/usr/bin/env python3
"""Download public measured files into the external data root.

  python scripts/fetch_data.py
  python scripts/fetch_data.py --large
  python scripts/fetch_data.py --dry-run

Token-gated FlyWire Codex files are listed and skipped. SHA-256 is checked
when the manifest has one. A report is written to out/fetch_report.json.
"""
from __future__ import annotations

import runio
runio.install()

import hashlib
import json
import sys
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from paths import CACHE_DIR, FLY_ROOT, ROOT as PACK  # noqa: E402

MANIFEST = PACK / "data_manifest.json"
UA = {"User-Agent": "FSOT-fly-pack"}


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def _dest(item: dict) -> Path:
    rel = Path(item["path"])
    if item.get("root") == "repo":
        # cache entries are "cache/..." under data_external, not the git tree.
        name = rel.name
        return CACHE_DIR / name
    return FLY_ROOT / rel


def _download(url: str, dest: Path) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    req = urllib.request.Request(url, headers=UA)
    tmp = dest.with_suffix(dest.suffix + ".part")
    print(f"  get {url}", flush=True)
    with urllib.request.urlopen(req, timeout=120) as resp, tmp.open("wb") as out:
        while True:
            chunk = resp.read(1 << 20)
            if not chunk:
                break
            out.write(chunk)
    tmp.replace(dest)
    print(f"  wrote {dest} ({dest.stat().st_size} bytes)", flush=True)


def _dataverse_csv(doi: str, names: list[str], folder: Path) -> list[dict]:
    url = (
        "https://dataverse.harvard.edu/api/datasets/:persistentId/?persistentId="
        + doi
    )
    req = urllib.request.Request(url, headers={**UA, "Accept": "application/json"})
    rows = []
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            doc = json.loads(resp.read().decode())
    except (urllib.error.URLError, TimeoutError, OSError, json.JSONDecodeError) as exc:
        print(f"  dataverse lookup failed ({exc})", flush=True)
        return [{"name": n, "ok": False, "error": str(exc)} for n in names]
    files = ((doc.get("data") or {}).get("latestVersion") or {}).get("files") or []
    by_name = {}
    for entry in files:
        data = entry.get("dataFile") or {}
        label = str(data.get("filename") or "")
        fid = data.get("id")
        if label and fid:
            by_name[label] = fid
    folder.mkdir(parents=True, exist_ok=True)
    for name in names:
        dest = folder / name
        if dest.is_file() and dest.stat().st_size > 1000:
            rows.append({"name": name, "ok": True, "path": str(dest), "cached": True})
            continue
        fid = by_name.get(name)
        if not fid:
            print(f"  dataverse has no file named {name}", flush=True)
            rows.append({"name": name, "ok": False, "error": "name not in dataset"})
            continue
        file_url = f"https://dataverse.harvard.edu/api/access/datafile/{fid}"
        try:
            _download(file_url, dest)
            rows.append({"name": name, "ok": True, "path": str(dest)})
        except (urllib.error.URLError, TimeoutError, OSError) as exc:
            rows.append({"name": name, "ok": False, "error": str(exc)})
    return rows


def _one(item: dict, large: bool, dry: bool) -> dict:
    rec = {"id": item["id"], "ok": True}
    if item.get("requires_token"):
        print(f"SKIP  {item['id']}: requires_token. {item.get('note')}", flush=True)
        rec.update({"skipped": "requires_token", "note": item.get("note")})
        return rec
    if item.get("large") and not large:
        print(f"SKIP  {item['id']}: large (pass --large)", flush=True)
        rec.update({"skipped": "large"})
        return rec
    if item.get("dataverse"):
        folder = FLY_ROOT / item["path"]
        print(f"DATA  {item['id']} {item['dataverse']}", flush=True)
        if dry:
            rec["dry_run"] = True
            return rec
        rec["files"] = _dataverse_csv(item["dataverse"], list(item.get("names") or []), folder)
        rec["ok"] = all(row.get("ok") for row in rec["files"]) if rec["files"] else False
        return rec
    url = item.get("url")
    if not url or item["id"] in {"hemibrain_cache", "behavior_videos", "banc_v888"}:
        print(f"NOTE  {item['id']}: {item.get('note') or url}", flush=True)
        rec.update({"skipped": "instructions", "note": item.get("note"), "url": url})
        return rec
    dest = _dest(item)
    if dry:
        print(f"DRY   {item['id']} -> {dest}", flush=True)
        rec.update({"dry_run": True, "path": str(dest)})
        return rec
    want = item.get("sha256")
    if dest.is_file() and dest.stat().st_size > 0:
        if want and _sha256(dest) != want:
            print(f"  sha mismatch, re-downloading {dest.name}", flush=True)
        else:
            print(f"HAVE  {item['id']} {dest}", flush=True)
            rec.update({"path": str(dest), "cached": True})
            return rec
    try:
        _download(url, dest)
    except (urllib.error.URLError, TimeoutError, OSError) as exc:
        print(f"FAIL  {item['id']}: {exc}", flush=True)
        if item.get("source"):
            print(f"      source {item['source']}", flush=True)
        rec.update({"ok": False, "error": str(exc)})
        return rec
    if want:
        got = _sha256(dest)
        rec["sha256"] = got
        if got != want:
            print(f"FAIL  {item['id']}: sha256 {got} != {want}", flush=True)
            rec["ok"] = False
            return rec
    rec["path"] = str(dest)
    return rec


def main(argv: list[str] | None = None) -> int:
    import argparse

    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--large", action="store_true", help="also download large dumps")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args(argv)
    doc = json.loads(MANIFEST.read_text(encoding="utf-8"))
    print(f"FLY_ROOT={FLY_ROOT}", flush=True)
    print(f"CACHE_DIR={CACHE_DIR}", flush=True)
    rows = [_one(item, args.large, args.dry_run) for item in doc.get("files") or []]
    report = {"fly_root": str(FLY_ROOT), "cache": str(CACHE_DIR), "files": rows}
    out = PACK / "out" / "fetch_report.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2), encoding="utf-8")
    required = {
        "flywire_annotations",
        "arc_easy_train",
        "arc_easy_validation",
        "arc_challenge_train",
        "arc_challenge_validation",
    }
    failed = [r["id"] for r in rows if r["id"] in required and not r.get("ok")]
    print(f"  wrote {out}  required_failed={failed}", flush=True)
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
