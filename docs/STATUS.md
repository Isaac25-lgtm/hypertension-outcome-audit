# R05 evidence status

Checkpoint: 17 October 2026, Claude Code cloud session (Linux, Python 3.13, 4 vCPU visible, run with ≤2 threads).

- **Scientific decision: CONDITIONAL — narrow audit.** Possible output: a short reproducibility note/correspondence after investigator review. Not a standalone clinical article; not submission-ready. No contact with authors and no external publication without investigator approval.
- **Data access:** RETRIEVED. S1 Appendix (dictionary), S1 Data (Stata do-file PDF), S2 Data (CSV) downloaded from journals.plos.org, one attempt each; hashes in `data/manifest.json`. CC BY 4.0. Raw files are git-ignored.
- **Method validity (released-flag semantics):** VERIFIED. Independent re-expression reproduces `baseline_controlled`, `followup_controlled`, `Treatedandcontrolled2`, `Regressed_uncontrolled` with 0 row disagreements; missing follow-up BP is coded as "uncontrolled".
- **Prior exploratory results:** reproduced — 25,128 rows; 2,175 baseline-controlled = 628 measured high + 717 measured controlled + 830 unknown; 22,973 vs published 23,855; 2,065 HIV-field disagreements. Table 4 count 1,502 not checked (table is an image).
- **New this checkpoint:** published Fig 3 counts (684/3,266) do not derive from the released flags (1,458/2,175), so the release cannot show that the published estimates used the unguarded coding; age-39 gap in `agecat_collapsed` (912 rows); overwritten age value labels.
- **Longitudinal estimand / adjusted RRs:** NOT REPRODUCIBLE FROM PUBLIC RELEASE (no record, clinic or visit keys).
- **Scientific novelty:** narrow (reproducibility of one release). **AI incremental value:** none sought; no model trained.
- **Tests:** 15 passed (`python -m pytest -q`): 8 synthetic edge cases, 7 real-release aggregate checks (skipped in CI).
- **Dashboard:** not built. A static figure (`results/figures/followup_reconciliation.png`) carries the main result; an interactive explorer would add little at this stage.

See `docs/RECONCILIATION.md` for the full matrix and `docs/LIMITATIONS.md`.
