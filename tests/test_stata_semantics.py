"""Synthetic edge cases for the Stata comparison re-expression (no real records)."""

import numpy as np
import pandas as pd

from htn_audit import stata


def test_missing_ranks_above_threshold():
    x = [np.nan, 139, 140, 200]
    assert stata.stata_ge(x, 140).tolist() == [True, False, True, True]
    assert stata.stata_lt(x, 140).tolist() == [False, True, False, False]


def test_unguarded_flag_codes_missing_as_uncontrolled():
    sbp = [120, 150, np.nan, 120, np.nan, 139, 120]
    dbp = [80, 80, np.nan, np.nan, 95, 89, 90]
    got = stata.stata_control_flag(sbp, dbp).tolist()
    # both missing -> 0 and one missing (other controlled) -> 0: the documented hazard
    assert got == [1.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0]


def test_eligibility_guard_leaves_ineligible_missing():
    got = stata.stata_control_flag([120, np.nan], [80, np.nan], eligible=[False, True])
    assert np.isnan(got[0]) and got[1] == 0.0


def test_measured_state_separates_unknown_from_high():
    sbp = [120, 150, np.nan, 120, np.nan, 140, np.nan]
    dbp = [80, 80, np.nan, np.nan, 95, np.nan, 89]
    assert stata.measured_state(sbp, dbp).tolist() == [
        stata.MEASURED_CONTROLLED,
        stata.MEASURED_HIGH,
        stata.UNKNOWN_BOTH_MISSING,
        stata.UNKNOWN_PARTIAL,
        stata.MEASURED_HIGH,  # one recorded high component is sufficient evidence
        stata.MEASURED_HIGH,
        stata.UNKNOWN_PARTIAL,
    ]


def test_stata_zero_equals_high_plus_unknown():
    rng = np.random.default_rng(5)
    sbp = pd.Series(rng.normal(135, 15, 500)).mask(rng.random(500) < 0.3)
    dbp = pd.Series(rng.normal(85, 10, 500)).mask(rng.random(500) < 0.3)
    flag = stata.stata_control_flag(sbp, dbp)
    st = stata.measured_state(sbp, dbp)
    assert ((flag == 1) == (st == stata.MEASURED_CONTROLLED)).all()
    assert ((flag == 0) == (st != stata.MEASURED_CONTROLLED)).all()


def test_string_and_blank_inputs_coerce_to_missing():
    assert stata.measured_state(["", "130"], ["85", "."]).tolist() == [stata.UNKNOWN_PARTIAL, stata.UNKNOWN_PARTIAL]
