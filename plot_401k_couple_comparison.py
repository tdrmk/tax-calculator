#!/usr/bin/env python3
"""
Plot the impact of 401(k) contributions on federal tax, CA state tax,
and take-home pay for the 2026 tax year.

Three columns: Spouse 1 (Single), Spouse 2 (Single), Married Filing Jointly.
Four rows: All Taxes, Take-Home Pay, Take-Home Decrease, Take-Home % of Gross.

Usage: python3 plot_401k_impact.py
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker

import tax_data_2026 as tax_data
from calculator import calculate_taxes
from constants import SINGLE, MFJ

# ============================================================================
# CONFIGURATION
# ============================================================================

GROSS_WAGES_SPOUSE1 = 400_000
GROSS_WAGES_SPOUSE2 = 200_000

LIMIT_401K = tax_data.ELECTIVE_DEFERRAL_LIMIT

# ============================================================================
# SWEEP HELPER
# ============================================================================

def sweep_401k(filing_status, spouse1_wages, spouse2_wages, contributions):
    """Sweep 401(k) contributions and return tax result arrays."""
    results_dict = {
        k: [] for k in [
            "federal", "ca", "take_home", "fica", "ss", "medicare", "sdi",
        ]
    }

    for contrib in contributions:
        inputs = {
            "filing_status": filing_status,
            "wages": spouse1_wages + spouse2_wages,
            "spouse1_wages": spouse1_wages,
            "spouse2_wages": spouse2_wages,
            "s1_retirement": float(contrib),
            "s1_health": 0,
            "s1_other": 0,
            "s2_retirement": float(contrib) if spouse2_wages > 0 else 0.0,
            "s2_health": 0,
            "s2_other": 0,
            "st_cap_gains": 0,
            "lt_cap_gains": 0,
            "ordinary_dividends": 0,
            "qualified_dividends": 0,
            "interest_income": 0,
            "other_income": 0,
            "s1_vdi_enrolled": False,
            "s1_vdi_max": 0,
            "s2_vdi_enrolled": False,
            "s2_vdi_max": 0,
            "nondeduc_ira": 0,
            "after_tax_401k": 0,
            "other_posttax": 0,
        }

        r = calculate_taxes(inputs, tax_data)
        results_dict["federal"].append(r["total_federal_tax"])
        results_dict["ca"].append(r["total_ca_tax"])
        results_dict["take_home"].append(r["take_home"])
        results_dict["fica"].append(r["total_payroll"])
        results_dict["ss"].append(r["ss_tax"])
        results_dict["medicare"].append(r["total_medicare"])
        results_dict["sdi"].append(r["ca_sdi"])

    return {k: np.array(v) for k, v in results_dict.items()}


# ============================================================================
# RUN SWEEPS
# ============================================================================

contributions = np.linspace(0, LIMIT_401K, 100)

scenarios = [
    {
        "label": f"Spouse 1 (Single)\n${GROSS_WAGES_SPOUSE1:,} wages",
        "filing_status": SINGLE,
        "s1_wages": GROSS_WAGES_SPOUSE1,
        "s2_wages": 0,
        "gross": GROSS_WAGES_SPOUSE1,
        "num_spouses": 1,
    },
    {
        "label": f"Spouse 2 (Single)\n${GROSS_WAGES_SPOUSE2:,} wages",
        "filing_status": SINGLE,
        "s1_wages": GROSS_WAGES_SPOUSE2,
        "s2_wages": 0,
        "gross": GROSS_WAGES_SPOUSE2,
        "num_spouses": 1,
    },
    {
        "label": f"Married Filing Jointly\n${GROSS_WAGES_SPOUSE1 + GROSS_WAGES_SPOUSE2:,} wages",
        "filing_status": MFJ,
        "s1_wages": GROSS_WAGES_SPOUSE1,
        "s2_wages": GROSS_WAGES_SPOUSE2,
        "gross": GROSS_WAGES_SPOUSE1 + GROSS_WAGES_SPOUSE2,
        "num_spouses": 2,
    },
]

all_results = []
for sc in scenarios:
    res = sweep_401k(sc["filing_status"], sc["s1_wages"], sc["s2_wages"], contributions)
    all_results.append(res)

# ============================================================================
# PRINT SUMMARIES
# ============================================================================

for sc, res in zip(scenarios, all_results):
    fed_savings = res["federal"][0] - res["federal"][-1]
    ca_savings = res["ca"][0] - res["ca"][-1]
    total_savings = fed_savings + ca_savings
    thp_change = res["take_home"][-1] - res["take_home"][0]
    deferred = LIMIT_401K * sc["num_spouses"]

    print(f"\n=== {sc['label'].replace(chr(10), ' — ')} ({sc['filing_status']}) ===")
    print(f"  401(k) range: $0 → ${LIMIT_401K:,}/person (${deferred:,} total)")
    print(f"  Federal savings: ${fed_savings:>10,.2f}")
    print(f"  CA savings:      ${ca_savings:>10,.2f}")
    print(f"  Total savings:   ${total_savings:>10,.2f}")
    print(f"  Take-home Δ:     ${thp_change:>+10,.2f}")
    if deferred > 0:
        print(f"  Cost per $1 deferred: ${abs(thp_change) / deferred:.4f}")

# ============================================================================
# PLOT — 4 rows × 3 columns
# ============================================================================

dollar_fmt = mticker.FuncFormatter(lambda x, _: f"${x:,.0f}")
pct_fmt = mticker.FuncFormatter(lambda x, _: f"{x:.1f}%")

fig, axes = plt.subplots(
    3, 3, figsize=(22, 14), sharex=True,
    gridspec_kw={"height_ratios": [3, 3, 2]},
)
fig.suptitle(
    "Impact of 401(k) Contributions on Taxes & Take-Home Pay — 2026 Tax Year",
    fontsize=15,
    fontweight="bold",
    y=0.98,
)


def annotate_endpoints(ax, x, y, color, fmt="dollar", offset_y=5):
    if fmt == "dollar":
        ax.annotate(f"${y[0]:,.0f}", xy=(x[0], y[0]), xytext=(5, offset_y),
                    textcoords="offset points", fontsize=8, fontweight="bold", color=color)
        ax.annotate(f"${y[-1]:,.0f}", xy=(x[-1], y[-1]), xytext=(-5, offset_y),
                    textcoords="offset points", fontsize=8, fontweight="bold", color=color,
                    ha="right")
    elif fmt == "pct":
        ax.annotate(f"{y[0]:.1f}%", xy=(x[0], y[0]), xytext=(5, offset_y),
                    textcoords="offset points", fontsize=8, fontweight="bold", color=color)
        ax.annotate(f"{y[-1]:.1f}%", xy=(x[-1], y[-1]), xytext=(-5, offset_y),
                    textcoords="offset points", fontsize=8, fontweight="bold", color=color,
                    ha="right")


for col, (sc, res) in enumerate(zip(scenarios, all_results)):
    total_gross = sc["gross"]

    # ── Row 0: All Taxes ──
    ax = axes[0][col]
    total_taxes = res["federal"] + res["ca"] + res["fica"]
    ax.plot(contributions, total_taxes, label="Total", color="#2ca02c", linewidth=2.5, linestyle="--")
    ax.plot(contributions, res["federal"], label="Federal", color="#1f77b4", linewidth=2)
    ax.plot(contributions, res["ca"], label="CA State", color="#ff7f0e", linewidth=2)
    ax.plot(contributions, res["fica"], label="FICA+SDI", color="#d62728", linewidth=2, linestyle="--")
    ax.plot(contributions, res["ss"], label="Soc. Sec.", color="#d62728", linewidth=1.5, alpha=0.7)
    ax.plot(contributions, res["medicare"], label="Medicare", color="#9467bd", linewidth=1.5, alpha=0.7)
    ax.plot(contributions, res["sdi"], label="CA SDI", color="#8c564b", linewidth=1.5, alpha=0.7)
    ax.grid(True, alpha=0.3)
    ax.yaxis.set_major_formatter(dollar_fmt)
    annotate_endpoints(ax, contributions, total_taxes, "#2ca02c")
    annotate_endpoints(ax, contributions, res["federal"], "#1f77b4")
    annotate_endpoints(ax, contributions, res["ca"], "#ff7f0e")

    if col == 0:
        ax.set_ylabel("Tax Amount ($)")
    ax.set_title(sc["label"], fontsize=11, fontweight="bold", pad=10)
    ax.legend(loc="right", fontsize=7)

    # Right y-axis: per paycheck
    axr = ax.twinx()
    axr.set_ylim(ax.get_ylim()[0] / 24, ax.get_ylim()[1] / 24)
    if col == 2:
        axr.set_ylabel("Per Paycheck (÷24)")
    axr.yaxis.set_major_formatter(dollar_fmt)

    # Top x-axis: % of gross
    ax_top = ax.twiny()
    ax_top.set_xlim(ax.get_xlim())
    pct_ticks = np.arange(0, LIMIT_401K + 1, 5000)
    if pct_ticks[-1] != LIMIT_401K:
        pct_ticks = np.append(pct_ticks, LIMIT_401K)
    ax_top.set_xticks(pct_ticks)
    ax_top.set_xticklabels([f"{c / total_gross * 100:.1f}%" for c in pct_ticks], fontsize=7)
    ax_top.set_xlabel("401(k) as % of Gross Pay", fontsize=8)

    # ── Row 1: Take-Home Pay ──
    ax = axes[1][col]
    ax.plot(contributions, res["take_home"], color="#2ca02c", linewidth=2)
    ax.grid(True, alpha=0.3)
    ax.yaxis.set_major_formatter(dollar_fmt)
    ax.set_ylim(bottom=res["take_home"][-1], top=res["take_home"][0])
    left_auto = ax.get_yticks()
    left_ticks = [t for t in left_auto if res["take_home"][-1] < t < res["take_home"][0]]
    left_ticks.insert(0, res["take_home"][-1])
    left_ticks.append(res["take_home"][0])
    ax.set_yticks(left_ticks)
    annotate_endpoints(ax, contributions, res["take_home"], "#2ca02c")
    if col == 0:
        ax.set_ylabel("Take-Home Pay ($)")

    baseline_pp = res["take_home"][0] / 24
    axr = ax.twinx()
    bottom_pp = res["take_home"][-1] / 24
    axr.set_ylim(bottom_pp, baseline_pp)
    if col == 2:
        axr.set_ylabel("Per Paycheck (÷24)")

    auto_ticks = axr.get_yticks()
    ticks = [t for t in auto_ticks if bottom_pp < t < baseline_pp]
    ticks.insert(0, bottom_pp)
    ticks.append(baseline_pp)
    axr.set_yticks(ticks)
    axr.yaxis.set_major_formatter(dollar_fmt)

    axr2 = ax.twinx()
    axr2.spines["right"].set_position(("outward", 52))
    axr2.set_ylim(axr.get_ylim())
    axr2.set_yticks(ticks)
    axr2.yaxis.set_major_formatter(mticker.FuncFormatter(
        lambda v, _, b=baseline_pp: f"(−\\${b - v:,.0f})" if v < b - 0.5 else "(\\$0)"
    ))
    axr2.tick_params(axis="y", length=0)
    axr2.spines["right"].set_visible(False)
    if col == 2:
        axr2.set_ylabel("Per Paycheck Decrease (÷24)", color="#d62728")
    fig.canvas.draw()
    for lbl in axr2.get_yticklabels():
        if "−" in lbl.get_text():
            lbl.set_color("#d62728")

    ax.set_xlabel("401(k) Contribution per Spouse ($)")
    ax.xaxis.set_major_formatter(dollar_fmt)

    # ── Row 2: Summary Table ──
    ax = axes[2][col]
    ax.axis("off")

    total_taxes_arr = res["federal"] + res["ca"] + res["fica"]
    deferred = LIMIT_401K * sc["num_spouses"]
    rows = [
        ("Federal Tax",  res["federal"][0],  res["federal"][-1]),
        ("CA State Tax", res["ca"][0],       res["ca"][-1]),
        ("FICA + SDI",   res["fica"][0],     res["fica"][-1]),
        ("Total Tax",    total_taxes_arr[0], total_taxes_arr[-1]),
        ("Take-Home",    res["take_home"][0], res["take_home"][-1]),
        ("Per Paycheck",  res["take_home"][0] / 24, res["take_home"][-1] / 24),
        ("% of Gross",    res["take_home"][0] / total_gross * 100, res["take_home"][-1] / total_gross * 100),
        ("401(k) Deferred", 0,               deferred),
    ]

    cell_text = []
    row_labels = []
    for label, v0, vmax in rows:
        delta = vmax - v0
        if label == "% of Gross":
            sign = "+" if delta >= 0 else "−"
            cell_text.append([
                f"{v0:.1f}%",
                f"{vmax:.1f}%",
                f"{sign}{abs(delta):.1f}%",
            ])
        else:
            sign = "+" if delta >= 0 else "−"
            cell_text.append([
                f"${v0:,.0f}",
                f"${vmax:,.0f}",
                f"{sign}${abs(delta):,.0f}",
            ])
        row_labels.append(label)

    table = ax.table(
        cellText=cell_text,
        rowLabels=row_labels,
        colLabels=["$0 contrib", f"${LIMIT_401K:,} each", "Δ Change"],
        loc="center",
        cellLoc="right",
    )
    table.auto_set_font_size(False)
    table.set_fontsize(9)
    table.scale(1.0, 1.4)

    for (r, c), cell in table.get_celld().items():
        if r == 0:
            cell.set_facecolor("#d9e2f3")
            cell.set_text_props(fontweight="bold")
        elif row_labels[r - 1] in ("Total Tax", "Take-Home", "Per Paycheck", "% of Gross"):
            cell.set_facecolor("#fff2cc")
            cell.set_text_props(fontweight="bold")
        if c == -1:
            cell.set_text_props(ha="left", fontweight="bold")
        if c == 2 and r > 0:
            label = row_labels[r - 1]
            if label in ("Take-Home", "Per Paycheck", "% of Gross"):
                cell.set_text_props(color="#d62728")
            else:
                cell.set_text_props(color="#2ca02c")

# Shared x-axis limits
x_ticks = np.arange(0, LIMIT_401K + 1, 5000)
if x_ticks[-1] != LIMIT_401K:
    x_ticks = np.append(x_ticks, LIMIT_401K)
for ax in axes[1]:
    ax.set_xlim(0, LIMIT_401K)
    ax.set_xticks(x_ticks)

plt.tight_layout(rect=[0, 0, 1, 0.965])
plt.savefig("local/401k_impact_2026.png", dpi=150, bbox_inches="tight")
plt.close(fig)
print(f"\nPlot saved to local/401k_impact_2026.png")
