# Hypertension released-outcome audit (R05)

Investigator: Isaac Omoding · Research programme R05 · Stage: **CONDITIONAL — narrow released-data audit** (not a clinical prediction study; not submission-ready)

A September 2026 PLOS Medicine article (Gumede et al., doi:[10.1371/journal.pmed.1004957](https://doi.org/10.1371/journal.pmed.1004957)) reports how adults with and without HIV in nine Johannesburg clinics move along the hypertension care cascade, including "regression" from controlled to uncontrolled blood pressure. Its minimal dataset and Stata code are public. This repository asks what those released snapshot variables can and cannot establish: measured high BP, measured control, missing follow-up, and the article's longitudinal *any-transition* outcome.

## What was checked (17 Oct 2026)

- Downloaded the dictionary, Stata do-file (PDF) and released CSV (25,128 rows × 35 columns) from PLOS, plus the Table 2 and Table 4 image assets, which were read visually. SHA256 for all of them is in [`data/manifest.json`](data/manifest.json). Table 3 was not inspected.
- Re-expressed Stata's comparison rule (missing numeric > any number) and reproduced all four released control/transition flags **row for row, 0 disagreements**.
- Among 2,175 rows flagged controlled at baseline: **628** measured high at follow-up, **717** measured controlled, **830** with no classifiable follow-up BP. The released `Regressed_uncontrolled` codes those 830 as loss of control (1,458 = 628 + 830).

![Released flag vs recorded follow-up BP](results/figures/followup_reconciliation.png)

## What this does and does not show

- The released flag is the worst-case bound (67.0%); the measured-only lower bound is 28.9%; complete-case 46.7%. These describe the **released two-snapshot flag**, not the published estimand.
- **Table 4** (image read visually) is reconciled separately from the Fig 3 text.
  - Its "Diagnosed, not yet treated" column (N = 24) matches the released flags exactly on every stratum, using the comorbidity-checkbox HIV field.
  - "Regressed to uncontrolled" is N = 1,502, close to the released flag's 1,458. Of those 1,458 released rows, 830 have no classifiable follow-up BP.
  - Whether the published 1,502 has the same composition cannot be checked from the release. We do not re-estimate or judge the published risk ratios.
- **Fig 3 text** reports a different quantity (684 of 3,266). The release reproduces neither its numerator nor its denominator.
- **Sample and HIV fields:** the release has 22,973 rows with completed file review, against 23,855 published. Neither HIV field reproduces 18,720 / 5,135, and the two fields disagree for 2,065 rows.
- No participant, clinic or visit keys are released, so the any-transition outcome and cluster-robust adjusted risk ratios are **NOT REPRODUCIBLE FROM PUBLIC RELEASE**.
- **Age coding:**
  - Age 39 falls outside every `agecat_collapsed` category (912 rows). The published "missing age" counts in Tables 2 and 4 are consistent in size with this gap.
  - The released age-category text labels are mismatched because one Stata value label was overwritten.

Full matrix: [`docs/RECONCILIATION.md`](docs/RECONCILIATION.md) · limits: [`docs/LIMITATIONS.md`](docs/LIMITATIONS.md) · status: [`docs/STATUS.md`](docs/STATUS.md).

## Reproduce

```bash
pip install pandas numpy matplotlib openpyxl pytest
PYTHONPATH=src python -m htn_audit.acquire .
PYTHONPATH=src OMP_NUM_THREADS=2 python scripts/run_audit.py
python -m pytest -q   # 17 passed at this checkpoint
```

Raw files stay in git-ignored `data/raw/`; committed outputs are aggregate counts only. No dashboard is deployed.

## Next step

Investigator review of `docs/RECONCILIATION.md`. At most, it supports a brief, neutral reproducibility note asking for clarification of the release (sample filter, HIV field, follow-up missing-value handling). Authors have not been contacted, and nothing will be published externally without investigator approval.

Source data: Gumede SB et al., PLOS Medicine 2026, CC BY 4.0. AI assistance: analysis code and documentation drafted with Claude Code under investigator direction.
