"""Fetch the PLOS Medicine supporting files (dictionary, Stata code PDF, minimal CSV) and write a manifest.

Raw files go to ``data/raw/`` (git-ignored). Only the manifest (URL, bytes, SHA256, time) is committed.
At most ``MAX_ATTEMPTS`` ordinary attempts per file, short timeout, no retries after a block.
"""

from __future__ import annotations

import hashlib
import json
import sys
import time
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ARTICLE_DOI = "10.1371/journal.pmed.1004957"
ARTICLE_URL = "https://journals.plos.org/plosmedicine/article?id=" + ARTICLE_DOI
SUPP_URL = "https://journals.plos.org/plosmedicine/article/file?type=supplementary&id=" + ARTICLE_DOI + ".{sid}"
LICENSE = "CC BY 4.0 (article copyright statement: Creative Commons Attribution License)"

# Supporting-information items actually used by this audit.
FILES = {
    "s002": ("journal.pmed.1004957.s002.xlsx", "S1 Appendix: REDCap medical-record abstraction dictionary"),
    "s005": ("journal.pmed.1004957.s005.pdf", "S1 Data: Stata do-file (printed to PDF)"),
    "s007": ("journal.pmed.1004957.s007.csv", "S2 Data: minimal de-identified released dataset"),
}
MAX_ATTEMPTS = 3
TIMEOUT_S = 60


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def fetch(url: str, dest: Path) -> int:
    last = None
    for attempt in range(1, MAX_ATTEMPTS + 1):
        try:
            with urllib.request.urlopen(url, timeout=TIMEOUT_S) as r:
                data = r.read()
            dest.write_bytes(data)
            return attempt
        except Exception as e:  # network/HTTP failure: record and back off briefly
            last = e
            time.sleep(2 * attempt)
    raise RuntimeError(f"{url}: failed after {MAX_ATTEMPTS} attempts: {last}")


def build_manifest(raw_dir: Path, retrieved_utc: str | None = None) -> dict:
    entries = []
    for sid, (name, desc) in FILES.items():
        p = raw_dir / name
        if not p.exists():
            entries.append({"id": sid, "file": name, "description": desc, "status": "MISSING"})
            continue
        entries.append({
            "id": sid,
            "file": name,
            "description": desc,
            "url": SUPP_URL.format(sid=sid),
            "doi": f"https://doi.org/{ARTICLE_DOI}.{sid}",
            "bytes": p.stat().st_size,
            "sha256": sha256_file(p),
            "status": "RETRIEVED",
        })
    return {
        "article": ARTICLE_URL,
        "article_published": "2026-09-11 (citation_date meta tag)",
        "license": LICENSE,
        "retrieved_utc": retrieved_utc,
        "files": entries,
    }


def main(argv: list[str]) -> int:
    root = Path(argv[1]) if len(argv) > 1 else Path(".")
    raw = root / "data" / "raw"
    raw.mkdir(parents=True, exist_ok=True)
    for sid, (name, _) in FILES.items():
        dest = raw / name
        if dest.exists():
            print(f"{name}: present, not re-downloaded")
            continue
        n = fetch(SUPP_URL.format(sid=sid), dest)
        print(f"{name}: downloaded in {n} attempt(s)")
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    manifest = build_manifest(raw, now)
    (root / "data" / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    print(json.dumps(manifest, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
