# R05 evidence status

Checkpoint: 17 October 2026 (updated after Table 2/4 source verification), Claude Code cloud session (Linux, Python 3.13, 4 vCPU visible, run with ≤2 threads).

- **Scientific decision: CONDITIONAL — narrow audit.** Possible output: a short reproducibility note/correspondence after investigator review. Not a standalone clinical article; not submission-ready. No contact with authors and no external publication without investigator approval.
- **Data access:** RETRIEVED. S1 Appendix (dictionary), S1 Data (Stata do-file PDF), S2 Data (CSV) downloaded from journals.plos.org, one attempt each; hashes in `data/manifest.json`. CC BY 4.0. Raw files are git-ignored.
- **Method validity (released-flag semantics):** VERIFIED. Independent re-expression reproduces `baseline_controlled`, `followup_controlled`, `Treatedandcontrolled2`, `Regressed_uncontrolled` with 0 row disagreements; missing follow-up BP is coded as "uncontrolled".
- **Prior exploratory results reproduced:**
  - 25,128 rows.
  - 2,175 baseline-controlled rows = 628 measured high + 717 measured controlled + 830 unknown.
  - 22,973 released vs 23,855 published.
  - 2,065 rows where the two HIV fields disagree.
  - Table 4 count of 1,502 confirmed against the image (released 1,458).
- **Tables 2 and 4 inspected:** both image assets were downloaded and read visually (hashes in `data/manifest.json`). Table 3 is UNINSPECTED.
  - Table 4 "Diagnosed, not yet treated" matches the released flags on all 7 strata, using `HIVstatus2`.
  - The other Table 4 columns differ by 0.3–6%, some in each direction.
  - "Regressed to uncontrolled" is 1,502 published vs 1,458 released. The released flag counts 830 rows without a classifiable follow-up BP as uncontrolled. Whether the published 1,502 has the same composition is not verifiable.
- **Table 4 vs Fig 3 narrative:** these report different "regressed to uncontrolled" quantities (1,502 vs 684 of 3,266). They are reconciled separately; the release reproduces neither the Fig 3 numerator nor its denominator.
- **Age-39 gap:** 912 released rows aged exactly 39 fall outside every `agecat_collapsed` category. Table 2/4 "missing age" counts are consistent in size with this gap (e.g. 857 vs 831; 32 vs 32). Not proven.
- **Age labels:** the released age-category text labels are wrong because one Stata value label was overwritten.
- **Longitudinal estimand / adjusted RRs:** NOT REPRODUCIBLE FROM PUBLIC RELEASE (no record, clinic or visit keys).
- **Scientific novelty:** narrow (reproducibility of one release). **AI incremental value:** none sought; no model trained.
- **Tests:** 17 passed (`python -m pytest -q`): 8 synthetic edge cases and 9 real-release aggregate checks. The real-release checks are skipped in CI.
- **Dashboard:** not built. A static figure (`results/figures/followup_reconciliation.png`) carries the main result; an interactive explorer would add little at this stage.

See `docs/RECONCILIATION.md` for the full matrix and `docs/LIMITATIONS.md`.
