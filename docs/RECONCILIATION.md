# Reconciliation matrix — published article vs public release

Source: Gumede SB et al. *The longitudinal care cascade for hypertension in people with and without HIV in South Africa.* PLOS Medicine, 11 Sep 2026, doi:10.1371/journal.pmed.1004957. Released file: S2 Data (`journal.pmed.1004957.s007.csv`, SHA256 `e67bdf85…11ec2`, 25,128 rows × 35 columns). Code: S1 Data (Stata do-file printed to PDF, 19 pages, `ee96bb73…a0f7`). All numbers below were computed in this repository on 17 Oct 2026 (`scripts/run_audit.py`; tables in `results/tables/`). Published numbers come from three places, which are kept apart:
- **Table 2 and Table 4.** These are image assets: [t002](https://journals.plos.org/plosmedicine/article/figure/image?id=10.1371%2Fjournal.pmed.1004957.t002&size=large), SHA256 `8bd68c07…f828`, and [t004](https://journals.plos.org/plosmedicine/article/figure/image?id=10.1371%2Fjournal.pmed.1004957.t004&size=large), SHA256 `2cf5db81…e016`. Both were downloaded on 17 Oct 2026 and transcribed by visual reading. They are not committed.
- **Fig 3 narrative text.**
- **Table 3 (unadjusted).** This table is **UNINSPECTED**.

Status key: **MATCH** · **MISMATCH (unexplained by release)** · **NOT DERIVABLE** (required fields absent) · **CODE-READING** (inferred from the do-file, not testable on the release).

## 1. Sample and descriptive denominators (Table 2 image, inspected)

| Quantity | Published (Table 2) | Release reconstruction | Filter | Status |
|---|---:|---:|---|---|
| Participants with records reviewed | 23,855 | 22,973 | `filereviewdone=="Yes"` (the do-file eligibility filter) | MISMATCH (−882) |
| Consented / eligible denominator (text) | 25,120 | 25,128 | all rows (`consentedtoaccessingclinicalinfo=="Yes"` everywhere) | MISMATCH (+8) |
| PLHIV | 18,720 | 18,609 / 18,153 | file-reviewed & `hivstatus` (clinical) / `HIVstatus2` (comorbidity checkbox) | MISMATCH (both) |
| PNLHIV | 5,135 | 4,364 / 4,820 | same two definitions | MISMATCH (both) |
| Female / Male | 16,296 / 7,559 | 15,688 / 7,285 | file-reviewed & `sex` | MISMATCH |
| South African / Zimbabwean / Other | 16,097 / 5,825 / 1,933 | 15,477 / 5,674 / 1,822 | file-reviewed & `nationality2` | MISMATCH |
| Had ≥1 follow-up visit | 15,553 (65.2%) | — (12,529 file-reviewed rows have a follow-up SBP, which is a different quantity) | needs visit rows | NOT DERIVABLE |
| Follow-up duration, visits per person | median 337 d; median 2 visits | — | needs dates / visit rows | NOT DERIVABLE |
| Age 18–39 / 40–49 / 50–59 / 60+ | 7,225 / 8,587 / 4,946 / 2,240 (sum **22,998**) | 7,573 / 8,375 / 4,849 / 2,176 | file-reviewed, binned from `ageinyears` | MISMATCH |
| Age not in any category | 23,855 − 22,998 = **857** | 831 aged exactly 39 (`agecat_collapsed=="."`) | file-reviewed | CONSISTENT IN SIZE, not proven |

The release has **no blank `ageinyears`**. The 857 participants missing from Table 2's age distribution are similar in number to the release's 831 file-reviewed rows aged exactly 39. Those rows fall outside every do-file bin (`<39`, then `>=40`). Table 2 still labels its first bin "18–39". This pattern fits, but does not prove, the age-39 coding gap explaining the "missing age" in the published tables.

The released rows also carry `filereviewdone=="."` for 2,155 rows, i.e. the release is not restricted to the analysed sample. No filter on the 35 released columns found here reproduces 23,855; the article's sample may have been built from the person-visit file before collapsing, which the release does not contain.

## 2. HIV exposure — two fields, explicitly unmapped

| `hivstatus` (clinical) × `HIVstatus2` (comorbidity checkbox, regression exposure in the do-file) | All rows | File-reviewed rows |
|---|---:|---:|
| HIV positive × HIV+ | 18,184 | 18,145 |
| HIV positive × HIV− | 2,057 | 464 |
| HIV negative × HIV+ | 8 | 8 |
| HIV negative × HIV− | 4,879 | 4,356 |
| **Disagreeing rows** | **2,065** | **472** |

The do-file uses `hivstatus` in descriptive tables and `i.HIVstatus2` in the Poisson models. Which field (or which person-level rule, e.g. the do-file's late "ever positive" `max()` example) produced the published 18,720 / 5,135 is **not identifiable** from the release. A separate `hivstatuscode` column is non-blank in 137 rows, including 9 coded `U`. We make no assumption that either field is the clinically correct one.

## 3. Follow-up control flag — Stata missing-value semantics

Do-file lines 379–385:

```stata
gen byte followup_controlled = .
replace followup_controlled = 1 if followup_sbp < 140 & followup_dbp < 90
replace followup_controlled = 0 if followup_sbp >= 140 | followup_dbp >= 90
```

In Stata a missing numeric value is larger than any finite number, so `. >= 140` is true. Rows with no follow-up BP therefore receive `followup_controlled = 0`. Our independent re-expression (`src/htn_audit/stata.py`) reproduces all four released flags **row for row with zero disagreements** (`results/tables/flag_agreement.csv`).

| Released rows with `baseline_controlled==1` (n = 2,175) | n | Released `Regressed_uncontrolled` |
|---|---:|---|
| Follow-up BP recorded, ≥140 and/or ≥90 (measured high) | 628 | 1 |
| Follow-up BP recorded, <140 and <90 (measured controlled) | 717 | 0 |
| No follow-up SBP or DBP | 829 | 1 |
| One component missing, other below threshold | 1 | 1 |
| **Total coded 1 / 0** | 1,458 / 717 | |

Released `followup_controlled` has **0** missing values although `followup_sbp` is missing in 12,092 rows. The same mechanism makes `Treatedandcontrolled2 = 0` for 2,322 treated rows without follow-up BP, and `baseline_controlled = 0` for 44 treated rows lacking a baseline BP component.

Snapshot bounds for "controlled → uncontrolled" among the 2,175 (`results/tables/regression_bounds.csv`): 28.9% if every unknown stayed controlled; 46.7% among the 1,345 classifiable rows (assumes ignorable missingness); 67.0% if every unknown lost control — which is exactly the released flag. "Unknown" combines no follow-up visit, a visit without a recorded BP, and failure to document control; the release cannot separate these.

## 4a. Table 4 outcome groups vs released flags (Table 4 image, inspected)

In Table 4, *N* is the number of participants **classified with** each outcome. The n/N cells give the composition of that outcome group, not risks. Below, the released counts are the rows with flag == 1. HIV strata use `HIVstatus2`, the do-file's regression exposure. "Age missing" is the published N minus the legend's age-complete N. Full stratum table: `results/tables/table4_reconciliation.csv`.

| Table 4 column | Released flag | Published N | Released N | PNLHIV / PLHIV published | PNLHIV / PLHIV released | Age missing published / released (aged 39) |
|---|---|---:|---:|---|---|---|
| Remained undiagnosed | `Undiagnosed` | 3,950 | 3,723 | 494 / 3,456 | 302 / 3,421 | 139 / 135 |
| Diagnosed, not yet treated | `Diagnosedbutuntreated` | **24** | **24** | **14 / 10** | **14 / 10** | 0 / 0 |
| Progressed to treatment | `Diagnosedandtreated` | 6,868 | 6,737 | 4,050 / 2,818 | 3,943 / 2,794 | 146 / 143 |
| Achieved BP control | `Treatedandcontrolled2` | 1,592 | 1,571 | 1,015 / 577 | 983 / 588 | 32 / 36 |
| Regressed to untreated | `Regressed_untreated` | 1,021 | 999 | 504 / 517 | 489 / 510 | 16 / 16 |
| Regressed to uncontrolled | `Regressed_uncontrolled` | **1,502** | **1,458** | 884 / 618 | 865 / 593 | 32 / 32 |

- **One exact match.** "Diagnosed, not yet treated" matches on all seven strata: N, both HIV groups using `HIVstatus2`, female, South African, Zimbabwean, and age-missing. With the clinical `hivstatus` field instead, the PLHIV count is 12, not 10. This is direct evidence that at least this Table 4 column was produced by the released flag logic with `HIVstatus2` as the exposure.
- **The other five columns differ by 0.3–6%.** Most released strata are smaller than published, but some are larger (achieved control: PLHIV 588 vs 577, female 1,115 vs 1,108, Zimbabwean 278 vs 272). So the release is **not** simply a row-subset of the Table 4 analysis sample with identical values. The difference cannot be explained from the release.
- **Regressed to uncontrolled: 1,502 published vs 1,458 released.** The published count is close in size to the released flag, which counts missing follow-up as uncontrolled. It is far from the 628 measured-high rows. In the release, 830 of the 1,458 flagged rows (56.9%) have no classifiable follow-up BP. **Whether Table 4's 1,502 has the same composition cannot be verified** without the analysis-sample rows. This is a statement about counts. It is not a re-estimate of, or a judgement on, the published aRR (1.10, 95% CI 1.02–1.18).
- **Age missing:** the published "missing age" exclusions per outcome (139, 146, 32, 16, 32) are close to the released counts of age-39 rows (135, 143, 36, 16, 32), and match exactly for two outcomes. This fits the age-39 gap, but does not prove it.

## 4b. Fig 3 narrative vs released flags (a separate published quantity)

| Quantity | Published Fig 3 text (PLHIV + PNLHIV) | Released flag | Status |
|---|---:|---:|---|
| Baseline controlled | 1,125 + 2,141 = 3,266 | 2,175 | MISMATCH |
| Controlled → uncontrolled | 242 + 442 = 684 | 1,458 | MISMATCH |
| Uncontrolled → untreated | 392/1,524 and 522/1,932 | not attempted | — |

Table 4 and the Fig 3 narrative do not report the same thing. Table 4 gives 1,502 (884 PNLHIV / 618 PLHIV) for "regressed to uncontrolled". The Fig 3 narrative gives 684 (442 PNLHIV / 242 PLHIV), with a denominator of 3,266 that does not appear in Table 4. We do **not** substitute one for the other. The release reproduces neither the Fig 3 numerators nor its denominators, and the estimand behind the Fig 3 narrative is not identifiable from the public materials.

## 5. Other release/code observations

| Observation | Evidence | Consequence |
|---|---|---|
| Age 39 falls in no `agecat_collapsed` category | `<39` then `>=40` (lines 27–28); 912 released rows aged 39 are `.` | Rows aged 39 would drop from the adjusted models as written. Table 2/4 "missing age" counts are consistent in size (§1, §4a). Effect on the published estimates is unknown and was not estimated |
| One value label reused and overwritten | `label define ageinyears …, replace` for three variables (lines 11, 21, 32) | Released text labels for `agecat`/`agecat4` mislabel ages (e.g. `agecat` "Between 50-59 years" holds ages 40–49; code 5 shows as "5"). Numeric regression coding unaffected; labels in the CSV must not be trusted (`results/tables/age_label_audit.csv`) |
| `Treatedandcontrolled` has 6,738 zeros and no ones | released column | Superseded in code by `Treatedandcontrolled2`; not used for estimates |
| Follow-up BP carried from the adjacent row only | `bysort recordid (visit_type): replace followup_sbp = followup_sbp[_n+1] if missing(...)` (lines 322–326) | CODE-READING: with several follow-up visits, which one becomes "follow-up" depends on within-`recordid` row order, which `visit_type` alone does not fix. Untestable without `recordid` |
| Cluster variable | `clinicid` from `healthfacilityname` (lines 567–577), used in `vce(cluster clinicid)` | NOT DERIVABLE: facility not released |

## 6. What the public release cannot reconstruct

Participant/record id, clinic, visit dates and visit order, number of visits, the person-visit panel, follow-up duration, and therefore the published *any-transition* outcomes and the adjusted cluster-robust risk ratios. Result: **NOT REPRODUCIBLE FROM PUBLIC RELEASE** for the longitudinal estimand and Tables 3–4. This is a statement about the release, not about the validity of the published estimates.
