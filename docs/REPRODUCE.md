# Reproduce this pack

Pin AEB2AD is the byte hash of `vendor/fsot_compute.py`. `.gitattributes` marks that file `-text`, so Git leaves the CRLF bytes alone. A fresh clone hashes to `AEB2ADAD6E80F487`. The LF rewrite hashes to `9EC3CF5CAB63E99E`.

From the repo root:

```bash
pip install -r requirements.txt
python scripts/fetch_data.py
python scripts/boot_pack.py
python scripts/boot_pack.py --check
python scripts/boot_pack.py --live
```

`fetch_data` reads `data_manifest.json` and saves public files under `data_external/` (`FLY_ROOT`, `CACHE_DIR`, `DATASETS_ROOT`). It exits non-zero when any downloadable non-token file fails. Without `--large`, multi-gigabyte dumps print SKIP, and that skip is not a failure. With `--large`, the Zenodo connection table and the BANC v888 feathers (Dataverse [doi:10.7910/DVN/7WTH1N](https://dataverse.harvard.edu/dataset.xhtml?persistentId=doi:10.7910/DVN/7WTH1N)) must download into `FLY_ROOT/banc/`. Larva is `Supplementary-Data-S1.zip` from [brain-networks/larval-drosophila-connectome](https://github.com/brain-networks/larval-drosophila-connectome), unzipped into `FLY_ROOT/larva/Supplementary-Data-S1/`. Walking CSVs from Dataverse [doi:10.7910/DVN/BBNPYX](https://dataverse.harvard.edu/dataset.xhtml?persistentId=doi:10.7910/DVN/BBNPYX) are saved as `Fly01_T001_BodyCoords3D.csv`, `Fly01_T002_BodyCoords3D.csv`, `Fly02_T002_BodyCoords3D.csv`, and `Fly01_T001_Coords3D.csv`. `FLY_ROOT/male_cns/fly_walking_proteins.fasta` is the UniProt FASTA for Gad1 P20228, nan Q9VUD5, iav Q9W3W0, and nompC Q7KIQ2. FlyWire Codex feathers are `requires_token`: place them in `FLY_ROOT/male_cns/`. Hemibrain has no static dump (neuPrint is live). Behavior videos are optional notes, not failed downloads.

`boot_pack.py` reads the committed JSON in `data/`. `--check` re-reads those headline fields and prints one line per file. It does not reload the Male CNS graph. `--live` reads the annotation TSV and, when the feathers are present, the Male CNS graph. If the feathers are absent it prints SKIP and names `FLY_ROOT/male_cns`.

A script rerun writes under `out/` and leaves `data/`, `docs/`, and the adventure notes in place. `--check` compares `overall_ok` and the integer score fields to the committed JSON. Scripts that do not define `--check` still accept it. Missing measured files exit 2 with `needs … from fetch_data` instead of a matching partial score. `FSOT_COMMIT_OUT=1` is how a promotion writes the tracked result. `python scripts/bill_ted.py` still writes the ledger. The feasibility PDF is built through that same write path, so a rerun lands in `out/` and `--check` does not replace the tracked PDF.

`--offline` replays the cached JSON and labels the line `replayed from cache, not recomputed`. It is not a fresh pass. Used by `adventure1_fold`, `fly_behavior`, `genetic_interactions`, `genetics_hook`, `hemibrain_connectome`, `kenyon_connectome`, and `live_verify`.

A full hemibrain or kenyon neuPrint fetch is well over 90 seconds (about 114 edge batches of 200 body ids; per-request timeouts are 180s and 240s). `genetic_interactions` live UniProt and Ensembl calls also exceed 90 seconds. Each of those requests times out at 45 seconds, so a dead host still fails. Use `--offline` to replay those caches.

`live_verify` counts GitHub HTTP 200 plus the repo name as ok. HTTP 404 fails. HTTP 429, or 403 with a rate-limit body or `X-RateLimit-Remaining: 0`, is `skipped (rate limit)` and is neither a pass nor a missing-repo failure. Set `GITHUB_TOKEN` (or `GH_TOKEN`) to raise the rate limit.

`fly_walking_proteins.py` calls `fsot_predict.py` from [FSOT-Genetics](https://github.com/dappalumbo91/FSOT-Genetics). Set `FSOT_GENETICS` to that checkout. The committed product table is `data/fly_walking_product.json`.

`bill30_adventure1_report.py` runs `lean` on `lean/Adventure1Thought.lean`. Install Lean 4 and put `lean` on `PATH`. Without it the script prints `needs Lean 4 on PATH` and exits 2.

Video scripts need `ffmpeg` and `ffprobe` on `PATH`. `torch` is optional. Without CUDA, residual hops run on NumPy.
