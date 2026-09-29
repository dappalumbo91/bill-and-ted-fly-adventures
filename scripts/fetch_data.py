#!/usr/bin/env python3
"""Download public measured files into the external data root.

  python scripts/fetch_data.py
  python scripts/fetch_data.py --large
  python scripts/fetch_data.py --dry-run

Token-gated FlyWire Codex files are listed and skipped. A multi-gigabyte
file is SKIP unless --large; that skip is not a failure. Hemibrain and
optional behavior videos are notes, not downloads. Every other entry with
a url or a Dataverse id must land on disk or this process exits non-zero.
SHA-256 is checked when the manifest has one. The report is out/fetch_report.json.
"""
from __future__ import annotations

import runio
runio.install()

import hashlib
import json
import sys
import urllib.error
import urllib.request
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from paths import CACHE_DIR, FLY_ROOT, ROOT as PACK  # noqa: E402

MANIFEST = PACK / "data_manifest.json"
UA = {"User-Agent": "FSOT-fly-pack"}
NOTE_IDS = {"hemibrain_cache", "behavior_videos"}
LARVA_MEMBERS = ("annotations.csv", "all-all_connectivity_matrix.csv")


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def _dest(item: dict) -> Path:
    rel = Path(item["path"])
    if item.get("root") == "repo":
        return CACHE_DIR / rel.name
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


def _matches(path: Path, sha: str | None, nbytes: int | None) -> bool:
    if not path.is_file() or path.stat().st_size <= 0:
        return False
    if nbytes is not None and path.stat().st_size != int(nbytes):
        return False
    if sha and _sha256(path) != sha:
        return False
    return True


def _unzip_larva(zip_path: Path, dest: Path, expect: list[dict] | None) -> str | None:
    dest.mkdir(parents=True, exist_ok=True)
    found: set[str] = set()
    with zipfile.ZipFile(zip_path) as zf:
        for info in zf.infolist():
            if info.is_dir() or info.filename.startswith("__MACOSX"):
                continue
            name = Path(info.filename).name
            if name not in LARVA_MEMBERS:
                continue
            target = dest / name
            with zf.open(info) as src, target.open("wb") as out:
                while True:
                    chunk = src.read(1 << 20)
                    if not chunk:
                        break
                    out.write(chunk)
            found.add(name)
            print(f"  unzipped {target} ({target.stat().st_size} bytes)", flush=True)
    missing = [name for name in LARVA_MEMBERS if name not in found]
    if missing:
        return f"zip missing {missing}"
    for spec in expect or []:
        target = dest / str(spec["name"])
        if not _matches(target, spec.get("sha256"), spec.get("bytes")):
            return f"unzipped {target.name} does not match the manifest"
    return None


def _dataverse(item: dict) -> dict:
    doi = str(item["dataverse"])
    folder = FLY_ROOT / item["path"]
    specs = list(item.get("files") or [])
    if not specs:
        specs = [{"name": name} for name in (item.get("names") or [])]
    url = "https://dataverse.harvard.edu/api/datasets/:persistentId/?persistentId=" + doi
    req = urllib.request.Request(url, headers={**UA, "Accept": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            doc = json.loads(resp.read().decode())
    except (urllib.error.URLError, TimeoutError, OSError, json.JSONDecodeError) as exc:
        print(f"  dataverse lookup failed ({exc})", flush=True)
        return {
            "ok": False,
            "error": str(exc),
            "files": [{"name": s.get("name"), "ok": False} for s in specs],
        }
    by_name = {}
    for entry in ((doc.get("data") or {}).get("latestVersion") or {}).get("files") or []:
        data = entry.get("dataFile") or {}
        label = str(data.get("filename") or "")
        fid = data.get("id")
        if label and fid:
            by_name[label] = fid
    folder.mkdir(parents=True, exist_ok=True)
    rows = []
    for spec in specs:
        name = str(spec["name"])
        save = str(spec.get("save_as") or name)
        dest = folder / save
        sha = spec.get("sha256")
        nbytes = spec.get("bytes")
        if _matches(dest, sha, nbytes):
            print(f"HAVE  {save}", flush=True)
            rows.append({"name": name, "save_as": save, "ok": True, "path": str(dest), "cached": True})
            continue
        fid = by_name.get(name)
        if not fid:
            print(f"FAIL  dataverse has no file named {name}", flush=True)
            rows.append({"name": name, "ok": False, "error": "name not in dataset"})
            continue
        file_url = f"https://dataverse.harvard.edu/api/access/datafile/{fid}"
        try:
            _download(file_url, dest)
        except (urllib.error.URLError, TimeoutError, OSError) as exc:
            print(f"FAIL  {save}: {exc}", flush=True)
            rows.append({"name": name, "ok": False, "error": str(exc)})
            continue
        if not _matches(dest, sha, nbytes):
            got = _sha256(dest) if sha else None
            print(f"FAIL  {save}: sha256/bytes mismatch got={got} size={dest.stat().st_size}", flush=True)
            rows.append({"name": name, "ok": False, "error": "sha256 or bytes mismatch", "sha256": got})
            continue
        rows.append({"name": name, "save_as": save, "ok": True, "path": str(dest)})
    return {"ok": bool(rows) and all(row.get("ok") for row in rows), "files": rows}


def _url_item(item: dict, dry: bool) -> dict:
    dest = _dest(item)
    rec = {"id": item["id"], "ok": True, "path": str(dest)}
    if dry:
        print(f"DRY   {item['id']} -> {dest}", flush=True)
        rec["dry_run"] = True
        return rec
    sha = item.get("sha256")
    nbytes = item.get("bytes")
    unzip_to = item.get("unzip_to")
    extracted_ok = True
    if unzip_to:
        folder = FLY_ROOT / unzip_to
        specs = list(item.get("extract") or [])
        if specs:
            extracted_ok = all(
                _matches(folder / str(spec["name"]), spec.get("sha256"), spec.get("bytes"))
                for spec in specs
            )
        else:
            extracted_ok = all((folder / name).is_file() for name in LARVA_MEMBERS)
    if _matches(dest, sha, nbytes) and extracted_ok:
        print(f"HAVE  {item['id']} {dest}", flush=True)
        rec["cached"] = True
        return rec
    if not _matches(dest, sha, nbytes):
        try:
            _download(str(item["url"]), dest)
        except (urllib.error.URLError, TimeoutError, OSError) as exc:
            print(f"FAIL  {item['id']}: {exc}", flush=True)
            if item.get("source"):
                print(f"      source {item['source']}", flush=True)
            rec.update({"ok": False, "error": str(exc)})
            return rec
        if not _matches(dest, sha, nbytes):
            got = _sha256(dest) if dest.is_file() else None
            print(f"FAIL  {item['id']}: sha256/bytes mismatch got={got}", flush=True)
            rec.update({"ok": False, "error": "sha256 or bytes mismatch", "sha256": got})
            return rec
    if unzip_to:
        err = _unzip_larva(dest, FLY_ROOT / unzip_to, list(item.get("extract") or []))
        if err:
            print(f"FAIL  {item['id']}: {err}", flush=True)
            rec.update({"ok": False, "error": err})
            return rec
    rec["sha256"] = sha
    return rec


def _one(item: dict, large: bool, dry: bool) -> dict:
    rec = {"id": item["id"], "ok": True}
    if item.get("requires_token"):
        print(f"SKIP  {item['id']}: requires_token. {item.get('note')}", flush=True)
        rec.update({"skipped": "requires_token", "note": item.get("note")})
        return rec
    if item.get("kind") == "note" or item["id"] in NOTE_IDS:
        print(f"NOTE  {item['id']}: {item.get('note')}", flush=True)
        rec.update({"skipped": "instructions", "note": item.get("note"), "url": item.get("url")})
        return rec
    if item.get("large") and not large:
        print(f"SKIP  {item['id']}: large (pass --large)", flush=True)
        rec.update({"skipped": "large"})
        return rec
    if item.get("dataverse"):
        print(f"DATA  {item['id']} {item['dataverse']}", flush=True)
        if dry:
            rec["dry_run"] = True
            return rec
        got = _dataverse(item)
        rec.update(got)
        return rec
    if item.get("url"):
        return _url_item(item, dry)
    print(f"FAIL  {item['id']}: no url", flush=True)
    rec.update({"ok": False, "error": "no url"})
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
    failed = [r["id"] for r in rows if not r.get("skipped") and not r.get("ok")]
    print(f"  wrote {out}  failed={failed}", flush=True)
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
