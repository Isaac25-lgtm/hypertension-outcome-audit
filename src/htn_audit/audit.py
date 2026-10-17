"""Load the released CSV, re-derive its flags independently, and build public-safe aggregate tables."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

from . import stata

RAW_CSV = Path("data/raw/journal.pmed.1004957.s007.csv")

# Published counts quoted in the article text (Results and Fig 3 narrative). Tables 2-4 are
# images on the article page and were not machine-read in this checkpoint.
PUBLISHED = {
    "participants_analysed": 23855,
    "eligible_consented_denominator": 25120,
    "plhiv": 18720,
    "pnlhiv": 5135,
    "female": 16296,
    "female_plhiv": 12940,
    "female_pnlhiv": 3356,
    "south_african": 16097,
    "more_than_one_visit": 15553,
    "baseline_controlled_plhiv": 1125,
    "baseline_controlled_pnlhiv": 2141,
    "controlled_to_uncontrolled_plhiv": 242,
    "controlled_to_uncontrolled_pnlhiv": 442,
    "controlled_to_untreated_plhiv": 243,
    "controlled_to_untreated_pnlhiv": 235,
    "uncontrolled_to_untreated_plhiv": 392,
    "uncontrolled_treated_plhiv": 1524,
    "uncontrolled_to_untreated_pnlhiv": 522,
    "uncontrolled_treated_pnlhiv": 1932,
}

SMALL_CELL = 5  # suppress 1..4 in any public cross-tab


def load(path: Path = RAW_CSV) -> pd.DataFrame:
    """Read every column as text so released blanks and Stata '.' stay distinguishable."""
    return pd.read_csv(path, dtype=str, keep_default_na=False)


def num(s: pd.Series) -> pd.Series:
    return pd.to_numeric(s.replace({"": np.nan, ".": np.nan}), errors="coerce")


def flag(s: pd.Series) -> pd.Series:
    """Released 0/1 flag column -> float with NaN for blank/'.'."""
    return num(s)


def suppress(n: int) -> int | str:
    return "<5" if 0 < n < SMALL_CELL else int(n)


def schema(df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for c in df.columns:
        s = df[c]
        n_blank = int((s == "").sum())
        n_dot = int((s == ".").sum())
        numeric = num(s)
        is_num = numeric.notna().sum() == (len(s) - n_blank - n_dot)
        rows.append({
            "column": c,
            "n_rows": len(s),
            "n_blank": n_blank,
            "n_stata_dot": n_dot,
            "n_distinct_nonmissing": int(s[(s != "") & (s != ".")].nunique()),
            "type": "numeric" if is_num else "text",
            "min": float(numeric.min()) if is_num and numeric.notna().any() else None,
            "max": float(numeric.max()) if is_num and numeric.notna().any() else None,
        })
    return pd.DataFrame(rows)


def rederive(df: pd.DataFrame) -> pd.DataFrame:
    """Independent re-derivation of the released control flags under Stata and missing-aware semantics."""
    out = pd.DataFrame(index=df.index)
    treated = df["baseline_treated"].eq("Yes")
    out["baseline_controlled_stata"] = stata.stata_control_flag(
        df["systolicbpmeasurementatinitialvi"], df["diastolicbpmeasurementatinitialv"], treated)
    out["followup_controlled_stata"] = stata.stata_control_flag(df["followup_sbp"], df["followup_dbp"])
    out["treatedandcontrolled2_stata"] = stata.stata_control_flag(df["followup_sbp"], df["followup_dbp"], treated)
    bc = out["baseline_controlled_stata"]
    fc = out["followup_controlled_stata"]
    reg = pd.Series(np.nan, index=df.index)
    reg[(bc == 1) & (fc == 0)] = 1.0
    reg[(bc == 1) & (fc == 1)] = 0.0
    out["regressed_uncontrolled_stata"] = reg
    out["baseline_state"] = stata.measured_state(df["systolicbpmeasurementatinitialvi"], df["diastolicbpmeasurementatinitialv"])
    out["followup_state"] = stata.measured_state(df["followup_sbp"], df["followup_dbp"])
    return out


def flag_agreement(df: pd.DataFrame, rd: pd.DataFrame) -> pd.DataFrame:
    pairs = [
        ("baseline_controlled", "baseline_controlled_stata"),
        ("followup_controlled", "followup_controlled_stata"),
        ("Treatedandcontrolled2", "treatedandcontrolled2_stata"),
        ("Regressed_uncontrolled", "regressed_uncontrolled_stata"),
    ]
    rows = []
    for rel, ours in pairs:
        a, b = flag(df[rel]), rd[ours]
        same = (a == b) | (a.isna() & b.isna())
        rows.append({
            "released_flag": rel,
            "released_1": int((a == 1).sum()), "released_0": int((a == 0).sum()), "released_missing": int(a.isna().sum()),
            "rederived_1": int((b == 1).sum()), "rederived_0": int((b == 0).sum()), "rederived_missing": int(b.isna().sum()),
            "row_disagreements": int((~same).sum()),
        })
    return pd.DataFrame(rows)


def followup_reconciliation(df: pd.DataFrame, rd: pd.DataFrame) -> pd.DataFrame:
    """Released followup_controlled / Regressed_uncontrolled vs missing-aware follow-up BP state."""
    rows = []
    for name, mask in [
        ("all_released_rows", pd.Series(True, index=df.index)),
        ("baseline_treated_yes", df["baseline_treated"].eq("Yes")),
        ("baseline_controlled_eq_1", flag(df["baseline_controlled"]) == 1),
    ]:
        sub_state = rd.loc[mask, "followup_state"]
        rel_fc = flag(df.loc[mask, "followup_controlled"])
        for st in stata.STATES:
            m = sub_state == st
            rows.append({
                "population": name,
                "followup_state": st,
                "n": int(m.sum()),
                "released_followup_controlled_1": int((rel_fc[m] == 1).sum()),
                "released_followup_controlled_0": int((rel_fc[m] == 0).sum()),
                "released_followup_controlled_missing": int(rel_fc[m].isna().sum()),
            })
    return pd.DataFrame(rows)


def regression_bounds(df: pd.DataFrame, rd: pd.DataFrame) -> pd.DataFrame:
    """Snapshot 'controlled -> uncontrolled' among released baseline_controlled==1 under explicit assumptions."""
    base = flag(df["baseline_controlled"]) == 1
    st = rd.loc[base, "followup_state"]
    n = int(base.sum())
    high = int((st == stata.MEASURED_HIGH).sum())
    ctrl = int((st == stata.MEASURED_CONTROLLED).sum())
    unk = n - high - ctrl
    rel = int((flag(df.loc[base, "Regressed_uncontrolled"]) == 1).sum())
    return pd.DataFrame([
        {"quantity": "baseline_controlled_rows", "numerator": n, "denominator": n, "proportion": 1.0,
         "interpretation": "released baseline_controlled==1"},
        {"quantity": "released_Regressed_uncontrolled_eq_1", "numerator": rel, "denominator": n, "proportion": rel / n,
         "interpretation": "released flag; equals measured-high + unknown under unguarded Stata >= with missing"},
        {"quantity": "lower_bound_all_unknown_controlled", "numerator": high, "denominator": n, "proportion": high / n,
         "interpretation": "measured high only; every unknown follow-up assumed still controlled"},
        {"quantity": "upper_bound_all_unknown_uncontrolled", "numerator": high + unk, "denominator": n, "proportion": (high + unk) / n,
         "interpretation": "every unknown follow-up assumed uncontrolled (coincides with the released flag)"},
        {"quantity": "complete_case_measured_only", "numerator": high, "denominator": high + ctrl, "proportion": high / (high + ctrl),
         "interpretation": "restricted to rows with a classifiable follow-up snapshot; assumes ignorable missingness"},
        {"quantity": "unknown_followup", "numerator": unk, "denominator": n, "proportion": unk / n,
         "interpretation": "no classifiable follow-up BP in the released snapshot (missing follow-up OR undocumented control)"},
    ])


def denominator_reconciliation(df: pd.DataFrame) -> pd.DataFrame:
    """Published counts vs what the released file can produce, with the filter used."""
    fr = df["filereviewdone"].eq("Yes")
    hiv_clin = df["hivstatus"]
    hiv_cmb = df["HIVstatus2"]
    bc = flag(df["baseline_controlled"]) == 1
    reg = flag(df["Regressed_uncontrolled"]) == 1
    rows = [
        ("released_rows", None, len(df), "all rows in S2 Data"),
        ("participants_analysed", PUBLISHED["participants_analysed"], int(fr.sum()), "filereviewdone=='Yes' (do-file eligibility filter)"),
        ("eligible_consented_denominator", PUBLISHED["eligible_consented_denominator"], len(df), "all released rows (consent=='Yes' for all)"),
        ("plhiv (hivstatus, clinical)", PUBLISHED["plhiv"], int((fr & hiv_clin.eq("HIV positive")).sum()), "filereviewdone & hivstatus=='HIV positive'"),
        ("plhiv (HIVstatus2, comorbidity checkbox)", PUBLISHED["plhiv"], int((fr & hiv_cmb.eq("HIV+")).sum()), "filereviewdone & HIVstatus2=='HIV+' (regression exposure)"),
        ("pnlhiv (hivstatus, clinical)", PUBLISHED["pnlhiv"], int((fr & hiv_clin.eq("HIV negative")).sum()), "filereviewdone & hivstatus=='HIV negative'"),
        ("pnlhiv (HIVstatus2, comorbidity checkbox)", PUBLISHED["pnlhiv"], int((fr & hiv_cmb.eq("HIV-")).sum()), "filereviewdone & HIVstatus2=='HIV-'"),
        ("female", PUBLISHED["female"], int((fr & df["sex"].eq("Female")).sum()), "filereviewdone & sex=='Female'"),
        ("south_african", PUBLISHED["south_african"], int((fr & df["nationality2"].eq("South Africa")).sum()), "filereviewdone & nationality2=='South Africa'"),
        ("more_than_one_visit", PUBLISHED["more_than_one_visit"], None, "NOT DERIVABLE: no visit count / record id / visit dates released"),
        ("baseline_controlled (PLHIV+PNLHIV, Fig 3 text)", PUBLISHED["baseline_controlled_plhiv"] + PUBLISHED["baseline_controlled_pnlhiv"], int(bc.sum()), "released baseline_controlled==1"),
        ("baseline_controlled PLHIV (HIVstatus2)", PUBLISHED["baseline_controlled_plhiv"], int((bc & hiv_cmb.eq("HIV+")).sum()), "baseline_controlled==1 & HIVstatus2=='HIV+'"),
        ("baseline_controlled PNLHIV (HIVstatus2)", PUBLISHED["baseline_controlled_pnlhiv"], int((bc & hiv_cmb.eq("HIV-")).sum()), "baseline_controlled==1 & HIVstatus2=='HIV-'"),
        ("controlled_to_uncontrolled (Fig 3 text)", PUBLISHED["controlled_to_uncontrolled_plhiv"] + PUBLISHED["controlled_to_uncontrolled_pnlhiv"], int(reg.sum()), "released Regressed_uncontrolled==1"),
        ("controlled_to_uncontrolled PLHIV (HIVstatus2)", PUBLISHED["controlled_to_uncontrolled_plhiv"], int((reg & hiv_cmb.eq("HIV+")).sum()), "Regressed_uncontrolled==1 & HIVstatus2=='HIV+'"),
        ("controlled_to_uncontrolled PNLHIV (HIVstatus2)", PUBLISHED["controlled_to_uncontrolled_pnlhiv"], int((reg & hiv_cmb.eq("HIV-")).sum()), "Regressed_uncontrolled==1 & HIVstatus2=='HIV-'"),
    ]
    out = pd.DataFrame(rows, columns=["quantity", "published", "released_reconstruction", "filter_or_reason"])
    pub, rec = out["published"].astype("Int64"), out["released_reconstruction"].astype("Int64")
    out["published"], out["released_reconstruction"] = pub, rec
    out["difference"] = rec - pub
    out["status"] = [
        "NOT_DERIVABLE" if pd.isna(r) else ("NO_PUBLISHED_VALUE" if pd.isna(p) else ("MATCH" if r == p else "MISMATCH"))
        for p, r in zip(pub, rec)
    ]
    return out


def hiv_crosstab(df: pd.DataFrame) -> pd.DataFrame:
    fr = df["filereviewdone"].eq("Yes")
    rows = []
    for scope, m in [("all_released_rows", pd.Series(True, index=df.index)), ("filereviewdone_yes", fr)]:
        ct = pd.crosstab(df.loc[m, "hivstatus"], df.loc[m, "HIVstatus2"])
        for a in ct.index:
            for b in ct.columns:
                rows.append({"scope": scope, "hivstatus_clinical": a, "HIVstatus2_comorbidity_checkbox": b, "n": suppress(int(ct.loc[a, b]))})
    return pd.DataFrame(rows)


def age_label_audit(df: pd.DataFrame) -> pd.DataFrame:
    """Released age-category labels vs categories recomputed from ageinyears (do-file lines 4-35)."""
    age = num(df["ageinyears"])
    rows = []
    for col in ["agecat", "agecat4", "agecat_collapsed"]:
        g = pd.DataFrame({"label": df[col], "age": age}).groupby("label")["age"].agg(["count", "min", "max"]).reset_index()
        for _, r in g.iterrows():
            rows.append({"variable": col, "released_label": r["label"], "n": int(r["count"]), "age_min": r["min"], "age_max": r["max"]})
    return pd.DataFrame(rows)


def other_anomalies(df: pd.DataFrame) -> dict:
    age = num(df["ageinyears"])
    tc = flag(df["Treatedandcontrolled"])
    return {
        "age_exactly_39": int((age == 39).sum()),
        "agecat_collapsed_dot": int(df["agecat_collapsed"].eq(".").sum()),
        "Treatedandcontrolled_eq_1": int((tc == 1).sum()),
        "Treatedandcontrolled_eq_0": int((tc == 0).sum()),
        "hivstatuscode_nonblank": int(df["hivstatuscode"].ne("").sum()),
        "hivstatuscode_U": int(df["hivstatuscode"].eq("U").sum()),
        "followup_sbp_missing": int(num(df["followup_sbp"]).isna().sum()),
        "followup_dbp_missing": int(num(df["followup_dbp"]).isna().sum()),
        "followup_controlled_missing": int(flag(df["followup_controlled"]).isna().sum()),
        "baseline_treated_yes_baseline_bp_missing": int((df["baseline_treated"].eq("Yes") & (num(df["systolicbpmeasurementatinitialvi"]).isna() | num(df["diastolicbpmeasurementatinitialv"]).isna())).sum()),
        "columns_identifying_participant_clinic_or_visit": [],
    }


def run(raw: Path = RAW_CSV, out_dir: Path = Path("results/tables")) -> dict:
    df = load(raw)
    rd = rederive(df)
    out_dir.mkdir(parents=True, exist_ok=True)
    tables = {
        "schema": schema(df),
        "flag_agreement": flag_agreement(df, rd),
        "followup_reconciliation": followup_reconciliation(df, rd),
        "regression_bounds": regression_bounds(df, rd),
        "denominator_reconciliation": denominator_reconciliation(df),
        "hiv_crosstab": hiv_crosstab(df),
        "age_label_audit": age_label_audit(df),
    }
    for k, t in tables.items():
        t.to_csv(out_dir / f"{k}.csv", index=False)
    anomalies = other_anomalies(df)
    anomalies["n_rows"] = len(df)
    anomalies["n_columns"] = df.shape[1]
    (out_dir / "anomalies.json").write_text(json.dumps(anomalies, indent=2) + "\n")
    return {"tables": tables, "anomalies": anomalies}
