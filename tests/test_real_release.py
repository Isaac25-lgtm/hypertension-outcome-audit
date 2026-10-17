"""Aggregate checks on the real released file. Skipped when data/raw is absent (e.g. CI)."""

import hashlib

import pytest

from htn_audit import audit, stata

pytestmark = pytest.mark.skipif(not audit.RAW_CSV.exists(), reason="released CSV not downloaded (run htn_audit.acquire)")

SHA = "e67bdf85676adfaef2916f3d602bbdaed3567206d4ff0c97c5ec42dd87511ec2"


@pytest.fixture(scope="module")
def data():
    df = audit.load()
    return df, audit.rederive(df)


def test_source_hash():
    assert hashlib.sha256(audit.RAW_CSV.read_bytes()).hexdigest() == SHA


def test_shape_and_no_keys(data):
    df, _ = data
    assert df.shape == (25128, 35)
    # Linkage/clustering fields used by the do-file are absent from the release.
    for key in ("recordid", "healthfacilityname", "clinicid", "dateofvisit", "v105", "eventname", "visit_type"):
        assert key not in df.columns


def test_rederived_flags_match_release_exactly(data):
    df, rd = data
    agree = audit.flag_agreement(df, rd)
    assert agree["row_disagreements"].sum() == 0


def test_followup_states_among_baseline_controlled(data):
    df, rd = data
    st = rd.loc[audit.flag(df["baseline_controlled"]) == 1, "followup_state"].value_counts()
    assert int((audit.flag(df["baseline_controlled"]) == 1).sum()) == 2175
    assert st[stata.MEASURED_HIGH] == 628
    assert st[stata.MEASURED_CONTROLLED] == 717
    assert st[stata.UNKNOWN_BOTH_MISSING] + st.get(stata.UNKNOWN_PARTIAL, 0) == 830
    assert int((audit.flag(df["Regressed_uncontrolled"]) == 1).sum()) == 628 + 830


def test_followup_controlled_has_no_missing(data):
    df, _ = data
    assert audit.flag(df["followup_controlled"]).isna().sum() == 0
    assert audit.num(df["followup_sbp"]).isna().sum() == 12092


def test_denominators_and_hiv_disagreement(data):
    df, _ = data
    assert df["filereviewdone"].eq("Yes").sum() == 22973
    disagree = (df["hivstatus"].eq("HIV positive") & df["HIVstatus2"].eq("HIV-")) | (df["hivstatus"].eq("HIV negative") & df["HIVstatus2"].eq("HIV+"))
    assert disagree.sum() == 2065


def test_age_39_gap(data):
    df, _ = data
    assert (audit.num(df["ageinyears"]) == 39).sum() == df["agecat_collapsed"].eq(".").sum() == 912
