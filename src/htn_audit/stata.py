"""Re-expression of Stata comparison semantics and the released control/transition flags.

In Stata, numeric missing (``.``, ``.a``-``.z``) sorts above every finite number, so
``x >= 140`` is TRUE and ``x < 140`` is FALSE when ``x`` is missing. Code written without
``& !missing(x)`` therefore assigns rows with no measurement to the ">= threshold" branch.
Here missing is ``NaN`` and each helper states which semantics it uses.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

SBP_T = 140
DBP_T = 90


def _num(x) -> pd.Series:
    return pd.to_numeric(pd.Series(x), errors="coerce").astype(float)


def stata_ge(x, t) -> pd.Series:
    """Stata ``x >= t``: missing counts as +infinity, so missing -> True."""
    x = _num(x)
    return x.isna() | (x >= t)


def stata_lt(x, t) -> pd.Series:
    """Stata ``x < t``: missing counts as +infinity, so missing -> False."""
    x = _num(x)
    return x.notna() & (x < t)


def stata_control_flag(sbp, dbp, eligible=None) -> pd.Series:
    """Replicate the do-file pattern (lines 369-375, 381-385 of S1 Data)::

        gen byte flag = .
        replace flag = 1 if [eligible &] sbp < 140 & dbp < 90
        replace flag = 0 if [eligible &] (sbp >= 140 | dbp >= 90)

    Returns 1.0 / 0.0 / NaN. With ``eligible=None`` there is no eligibility guard
    (as for ``followup_controlled``), so every row receives 0 or 1.
    """
    sbp, dbp = _num(sbp), _num(dbp)
    elig = pd.Series(True, index=sbp.index) if eligible is None else pd.Series(eligible, index=sbp.index).astype(bool)
    out = pd.Series(np.nan, index=sbp.index)
    out[elig & stata_lt(sbp, SBP_T) & stata_lt(dbp, DBP_T)] = 1.0
    out[elig & (stata_ge(sbp, SBP_T) | stata_ge(dbp, DBP_T))] = 0.0
    return out


MEASURED_HIGH = "measured_high"
MEASURED_CONTROLLED = "measured_controlled"
UNKNOWN_BOTH_MISSING = "unknown_no_bp"
UNKNOWN_PARTIAL = "unknown_partial_bp"
STATES = [MEASURED_HIGH, MEASURED_CONTROLLED, UNKNOWN_PARTIAL, UNKNOWN_BOTH_MISSING]


def measured_state(sbp, dbp) -> pd.Series:
    """Missing-aware BP state.

    * measured_high: any recorded component at/above threshold (one high reading suffices).
    * measured_controlled: both components recorded and both below threshold.
    * unknown_partial_bp: one component recorded below threshold, the other missing.
    * unknown_no_bp: neither component recorded.
    """
    sbp, dbp = _num(sbp), _num(dbp)
    high = (sbp >= SBP_T) | (dbp >= DBP_T)  # NaN comparisons are False in pandas
    ctrl = sbp.notna() & dbp.notna() & (sbp < SBP_T) & (dbp < DBP_T)
    none = sbp.isna() & dbp.isna()
    out = pd.Series(UNKNOWN_PARTIAL, index=sbp.index, dtype=object)
    out[none] = UNKNOWN_BOTH_MISSING
    out[ctrl] = MEASURED_CONTROLLED
    out[high] = MEASURED_HIGH
    return out
