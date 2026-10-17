"""Publication-grade aggregate figure (counts only; no row-level data)."""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import pandas as pd  # noqa: E402

SURFACE = "#fcfcfb"
TEXT = "#0b0b0b"
TEXT2 = "#52514e"
GRID = "#e4e3df"
HIGH = "#eb6834"  # categorical slot 2 (validated pair with slot 1)
CTRL = "#2a78d6"  # categorical slot 1
UNK = "#b9b8b2"  # neutral: missing is not a category of physiology


def reconciliation_figure(recon: pd.DataFrame, bounds: pd.DataFrame, out: Path = Path("results/figures/followup_reconciliation.png")) -> Path:
    sub = recon[recon["population"] == "baseline_controlled_eq_1"].set_index("followup_state")["n"]
    high, ctrl = int(sub["measured_high"]), int(sub["measured_controlled"])
    unk = int(sub["unknown_partial_bp"] + sub["unknown_no_bp"])
    n = high + ctrl + unk
    b = bounds.set_index("quantity")

    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 10})
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(8.6, 5.4), gridspec_kw={"height_ratios": [1.5, 1]}, facecolor=SURFACE)
    for ax in (ax1, ax2):
        ax.set_facecolor(SURFACE)
        for s in ("top", "right", "left"):
            ax.spines[s].set_visible(False)
        ax.spines["bottom"].set_color(GRID)
        ax.tick_params(colors=TEXT2, length=0)

    gap = 0.004 * n
    # Bar A: released Stata flag. Bar B: missing-aware snapshot state.
    rows = [
        ("Released flag\n(Regressed_uncontrolled)", [(n - ctrl, HIGH, None, f"coded 1 = {n - ctrl:,}"), (ctrl, CTRL, None, f"coded 0 = {ctrl:,}")]),
        ("Recorded follow-up BP\n(missing-aware)", [(high, HIGH, None, f"high {high:,}"), (unk, UNK, "////", f"no classifiable BP {unk:,}"), (ctrl, CTRL, None, f"controlled {ctrl:,}")]),
    ]
    for y, (label, segs) in zip([1, 0], rows):
        left = 0
        for w, c, hatch, txt in segs:
            ax1.barh(y, w - gap, left=left, color=c, hatch=hatch, edgecolor=SURFACE if hatch is None else "#8f8e88", linewidth=0, height=0.56)
            ax1.text(left + w / 2, y, txt, ha="center", va="center", color=TEXT if c == UNK else "white", fontsize=9, fontweight="bold")
            left += w
    ax1.set_yticks([1, 0], [r[0] for r in rows], color=TEXT)
    ax1.set_xlim(0, n)
    ax1.set_xlabel(f"Released rows with baseline_controlled = 1 (n = {n:,})", color=TEXT2)
    ax1.set_title("Missing follow-up BP is coded as loss of control in the released flag", loc="left", color=TEXT, fontsize=11.5, fontweight="bold")

    pts = [
        ("Lower bound: unknown assumed controlled", b.loc["lower_bound_all_unknown_controlled", "proportion"]),
        ("Complete case: classifiable rows only", b.loc["complete_case_measured_only", "proportion"]),
        ("Upper bound = released flag", b.loc["upper_bound_all_unknown_uncontrolled", "proportion"]),
    ]
    lo, hi = pts[0][1], pts[2][1]
    ax2.plot([lo, hi], [0, 0], color=UNK, linewidth=6, solid_capstyle="round", zorder=1)
    for i, (lab, p) in enumerate(pts):
        ax2.scatter([p], [0], s=90, color=HIGH if i != 1 else TEXT, edgecolor=SURFACE, linewidth=2, zorder=3)
        ax2.annotate(f"{lab}\n{p:.1%}", (p, 0), xytext=(0, 14 if i != 1 else -30), textcoords="offset points", ha="center", color=TEXT, fontsize=8.5)
    ax2.set_xlim(0, 1)
    ax2.set_ylim(-1, 1)
    ax2.set_yticks([])
    ax2.xaxis.set_major_formatter(matplotlib.ticker.PercentFormatter(1.0))
    ax2.grid(axis="x", color=GRID, linewidth=0.8)
    ax2.set_xlabel("Snapshot 'controlled -> uncontrolled' proportion by assumption (not the published any-transition estimand)", color=TEXT2, fontsize=8)

    fig.text(0.01, 0.005, "Source: PLOS Med 2026 iHEART-SA S2 Data (journal.pmed.1004957.s007). Aggregate counts only. Threshold 140/90 mmHg.", color=TEXT2, fontsize=7.5)
    fig.tight_layout(rect=(0, 0.03, 1, 1))
    out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out, dpi=200, facecolor=SURFACE)
    fig.savefig(out.with_suffix(".svg"), facecolor=SURFACE)
    plt.close(fig)
    return out
