# Limitations and claim boundaries

- The release has no participant, clinic, visit or date fields. The published outcome (any progression/regression across all documented follow-up visits) and the cluster-robust adjusted risk ratios cannot be recomputed. We do not compute a replacement effect estimate.
- The bounds in `results/tables/regression_bounds.csv` describe the *released two-snapshot flag*, not the published estimand. They are not a corrected version of any published number.
- "Unknown follow-up BP" mixes three things the release cannot distinguish: no follow-up visit, a visit with no BP recorded, and control not documented. None of them is evidence of physiological loss of control.
- Tables 2 and 4 were transcribed by visually reading the PLOS PNG assets, not by OCR. A transcription slip is possible; the source hashes allow re-checking. Table 3 (unadjusted RRs) is UNINSPECTED.
- Table 4's "Regressed to uncontrolled" count of 1,502 is close in size to the released flag, which counts missing follow-up as uncontrolled. Size and stratum composition are not row-level proof. The share of unknown follow-up inside the published 1,502 is unknown, and nothing here re-estimates or invalidates the published aRR.
- Table 4 and the Fig 3 narrative report different "regressed to uncontrolled" counts (1,502 vs 684). We do not say which one the authors intended as the primary quantity.
- Which HIV field (clinical `hivstatus` vs comorbidity checkbox `HIVstatus2`) is correct for each person is unknown. We report both and the 2,065 disagreements without choosing.
- The do-file was read from a PDF print-out (`pdftotext -layout`); line numbers refer to that print. We did not run Stata.
- Observations about code (age-39 gap, overwritten labels, adjacent-row carry) show what the code as printed does to *this* release; whether the authors' production run differed is unknown.
