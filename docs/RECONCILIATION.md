# Reconciliation matrix — published article vs public release

Source: Gumede SB et al. *The longitudinal care cascade for hypertension in people with and without HIV in South Africa.* PLOS Medicine, 11 Sep 2026, doi:10.1371/journal.pmed.1004957. Released file: S2 Data (`journal.pmed.1004957.s007.csv`, SHA256 `e67bdf85…11ec2`, 25,128 rows × 35 columns). Code: S1 Data (Stata do-file printed to PDF, 19 pages, `ee96bb73…a0f7`). All numbers below were computed in this repository on 17 Oct 2026 (`scripts/run_audit.py`; tables in `results/tables/`). Published numbers are taken from the article **text** (Results, Fig 3 narrative); Tables 2–4 are images on the article page and were not machine-read in this checkpoint.

Status key: **MATCH** · **MISMATCH (unexplained by release)** · **NOT DERIVABLE** (required fields absent) · **CODE-READING** (inferred from the do-file, not testable on the release).

## 1. Sample and descriptive denominators (Table 2 text)

| Quantity | Published | Release reconstruction | Filter | Status |
|---|---:|---:|---|---|
| Analysed participants | 23,855 | 22,973 | `filereviewdone=="Yes"` (the do-file eligibility filter) | MISMATCH (−882) |
| Consented / eligible denominator | 25,120 | 25,128 | all rows (`consentedtoaccessingclinicalinfo=="Yes"` everywhere) | MISMATCH (+8) |
| PLHIV | 18,720 | 18,609 / 18,153 | file-reviewed & `hivstatus` (clinical) / `HIVstatus2` (comorbidity checkbox) | MISMATCH (both) |
| PNLHIV | 5,135 | 4,364 / 4,820 | same two definitions | MISMATCH (both) |
| Female | 16,296 | 15,688 | file-reviewed & `sex=="Female"` | MISMATCH |
| South African | 16,097 | 15,477 | file-reviewed & `nationality2` | MISMATCH |
| >1 visit | 15,553 | — | needs record id / visit rows | NOT DERIVABLE |

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

## 4. Published regression counts vs released flags (Fig 3 text)

| Quantity | Published (PLHIV + PNLHIV) | Released flag | Status |
|---|---:|---:|---|
| Baseline controlled | 1,125 + 2,141 = 3,266 | 2,175 (840 HIV+ / 1,335 HIV− by `HIVstatus2`) | MISMATCH |
| Controlled → uncontrolled | 242 + 442 = 684 (≈21%) | 1,458 (67%) | MISMATCH |
| Uncontrolled → untreated | 392/1,524 and 522/1,932 | not attempted (different denominator definition) | — |
| Table 4 outcome count 1,502 (prior handoff) | — | image table not read this checkpoint | UNVERIFIED HERE |

**Interpretation.** The published Fig 3 counts are *not* the released two-snapshot flags: both numerator and denominator differ, and the published proportion (~21%) lies below even our lower bound (28.9%) for the released snapshot. This is consistent with the article's stated outcome — *any* transition across *all* documented follow-up visits — being computed from person-visit data that are not in the release. We therefore **cannot** conclude that the missing-value coding affected the published estimates. What we can state is narrower: the released variables named `followup_controlled`/`Regressed_uncontrolled` encode missing follow-up as loss of control, and anyone re-analysing S2 Data with those flags would obtain a different quantity from the published one.

## 5. Other release/code observations

| Observation | Evidence | Consequence |
|---|---|---|
| Age 39 falls in no `agecat_collapsed` category | `<39` then `>=40` (lines 27–28); 912 released rows aged 39 are `.` | Rows aged 39 would drop from the adjusted models as written; effect on published estimates unknown |
| One value label reused and overwritten | `label define ageinyears …, replace` for three variables (lines 11, 21, 32) | Released text labels for `agecat`/`agecat4` mislabel ages (e.g. `agecat` "Between 50-59 years" holds ages 40–49; code 5 shows as "5"). Numeric regression coding unaffected; labels in the CSV must not be trusted (`results/tables/age_label_audit.csv`) |
| `Treatedandcontrolled` has 6,738 zeros and no ones | released column | Superseded in code by `Treatedandcontrolled2`; not used for estimates |
| Follow-up BP carried from the adjacent row only | `bysort recordid (visit_type): replace followup_sbp = followup_sbp[_n+1] if missing(...)` (lines 322–326) | CODE-READING: with several follow-up visits, which one becomes "follow-up" depends on within-`recordid` row order, which `visit_type` alone does not fix. Untestable without `recordid` |
| Cluster variable | `clinicid` from `healthfacilityname` (lines 567–577), used in `vce(cluster clinicid)` | NOT DERIVABLE: facility not released |

## 6. What the public release cannot reconstruct

Participant/record id, clinic, visit dates and visit order, number of visits, the person-visit panel, follow-up duration, and therefore the published *any-transition* outcomes and the adjusted cluster-robust risk ratios. Result: **NOT REPRODUCIBLE FROM PUBLIC RELEASE** for the longitudinal estimand and Tables 3–4. This is a statement about the release, not about the validity of the published estimates.
