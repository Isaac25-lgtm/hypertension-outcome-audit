# Limitations and claim boundaries

- The release has no participant, clinic, visit or date fields. The published outcome (any progression/regression across all documented follow-up visits) and the cluster-robust adjusted risk ratios cannot be recomputed. We do not compute a replacement effect estimate.
- The bounds in `results/tables/regression_bounds.csv` describe the *released two-snapshot flag*, not the published estimand. They are not a corrected version of any published number.
- "Unknown follow-up BP" mixes three things the release cannot distinguish: no follow-up visit, a visit with no BP recorded, and control not documented. None of them is evidence of physiological loss of control.
- Published comparators are read from the article text. Tables 2–4 are images and were not machine-read; the prior figure of 1,502 (Table 4) is unverified here.
- Which HIV field (clinical `hivstatus` vs comorbidity checkbox `HIVstatus2`) is correct for each person is unknown. We report both and the 2,065 disagreements without choosing.
- The do-file was read from a PDF print-out (`pdftotext -layout`); line numbers refer to that print. We did not run Stata.
- Observations about code (age-39 gap, overwritten labels, adjacent-row carry) show what the code as printed does to *this* release; whether the authors' production run differed is unknown.
