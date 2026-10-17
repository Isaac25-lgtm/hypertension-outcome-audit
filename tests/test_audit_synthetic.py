"""Audit functions on a small synthetic frame shaped like the release (values invented)."""

import pandas as pd

from htn_audit import audit


def synthetic():
    rows = [
        # treated, baseline controlled, follow-up high
        dict(baseline_treated="Yes", systolicbpmeasurementatinitialvi="120", diastolicbpmeasurementatinitialv="80", followup_sbp="150", followup_dbp="85"),
        # treated, baseline controlled, follow-up controlled
        dict(baseline_treated="Yes", systolicbpmeasurementatinitialvi="125", diastolicbpmeasurementatinitialv="70", followup_sbp="130", followup_dbp="80"),
        # treated, baseline controlled, follow-up missing
        dict(baseline_treated="Yes", systolicbpmeasurementatinitialvi="110", diastolicbpmeasurementatinitialv="70", followup_sbp="", followup_dbp=""),
        # treated, baseline BP missing -> Stata codes baseline_controlled 0
        dict(baseline_treated="Yes", systolicbpmeasurementatinitialvi="", diastolicbpmeasurementatinitialv="", followup_sbp="", followup_dbp=""),
        # untreated
        dict(baseline_treated="No", systolicbpmeasurementatinitialvi="160", diastolicbpmeasurementatinitialv="95", followup_sbp="", followup_dbp=""),
    ]
    df = pd.DataFrame(rows)
    return df


def test_rederive_and_bounds():
    df = synthetic()
    rd = audit.rederive(df)
    assert rd["baseline_controlled_stata"].tolist()[:4] == [1.0, 1.0, 1.0, 0.0]
    assert pd.isna(rd["baseline_controlled_stata"].iloc[4])
    assert rd["followup_controlled_stata"].tolist() == [0.0, 1.0, 0.0, 0.0, 0.0]
    assert rd["regressed_uncontrolled_stata"].tolist()[:3] == [1.0, 0.0, 1.0]

    df["baseline_controlled"] = rd["baseline_controlled_stata"].map({1.0: "1", 0.0: "0"}).fillna("")
    df["Regressed_uncontrolled"] = rd["regressed_uncontrolled_stata"].map({1.0: "1", 0.0: "0"}).fillna("")
    b = audit.regression_bounds(df, rd).set_index("quantity")
    assert b.loc["released_Regressed_uncontrolled_eq_1", "numerator"] == 2
    assert b.loc["lower_bound_all_unknown_controlled", "numerator"] == 1
    assert b.loc["upper_bound_all_unknown_uncontrolled", "numerator"] == 2
    assert b.loc["complete_case_measured_only", "denominator"] == 2


def test_small_cell_suppression():
    assert audit.suppress(0) == 0
    assert audit.suppress(3) == "<5"
    assert audit.suppress(5) == 5
