# Data access and publication boundary

`python -m htn_audit.acquire .` downloads the PLOS Medicine supporting files into `data/raw/` (git-ignored) and writes `data/manifest.json` (URL, bytes, SHA256, retrieval time). The released CSV is de-identified and CC BY 4.0, but row-level records are still never committed or shown in a dashboard; outputs are aggregate only. See `docs/DATA_ACCESS.md`.
