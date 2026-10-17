# Reproducibility

```bash
pip install pandas numpy matplotlib openpyxl pytest
PYTHONPATH=src python -m htn_audit.acquire .     # downloads 3 files to data/raw/, writes data/manifest.json
PYTHONPATH=src OMP_NUM_THREADS=2 python scripts/run_audit.py   # results/tables/*.csv, results/figures/*
python -m pytest -q                              # 15 tests; 7 skip without data/raw
```

Checkpoint run (17 Oct 2026): `scripts/run_audit.py` < 5 s; `pytest -q` → 15 passed in 0.84 s. Expected source SHA256 is asserted in `tests/test_real_release.py`.
