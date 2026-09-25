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

`fetch_data` reads `data_manifest.json` and saves public files under `data_external/` (`FLY_ROOT`, `CACHE_DIR`, `DATASETS_ROOT`). `--large` also fetches the Zenodo connection table and the larva matrix. FlyWire Codex feathers are `requires_token`: place them in `FLY_ROOT/male_cns/`. BANC feathers go in `FLY_ROOT/banc/`. The manifest names each file and its source.

`boot_pack.py` reads the committed JSON in `data/`. `--check` is that same frozen comparison. `--live` reads the annotation TSV and, when the feathers are present, the Male CNS graph.

A script rerun writes under `out/` and leaves `data/`, `docs/`, and the adventure notes in place. `--check` on a script compares `overall_ok` and the integer score fields to the committed JSON. `FSOT_COMMIT_OUT=1` is how a promotion writes the tracked result. `python scripts/bill_ted.py` still writes the ledger.

`--offline` on the live-API scripts (`adventure1_fold`, `fly_behavior`, `genetic_interactions`, `genetics_hook`, `hemibrain_connectome`, `kenyon_connectome`, `live_verify`) uses the cached JSON and does not call the network.

Video scripts need `ffmpeg` and `ffprobe` on `PATH`. `torch` is optional. Without CUDA, residual hops run on NumPy.

`fly_walking_proteins.py` calls `fsot_predict.py` from [FSOT-Genetics](https://github.com/dappalumbo91/FSOT-Genetics). Set `FSOT_GENETICS` to that checkout. The committed product table is `data/fly_walking_product.json`.

Missing measured files exit with `needs … from fetch_data` instead of a wrong score.
