#!/usr/bin/env python3
"""
Generate a combined marginal tax rate table (Markdown) for both
Single and Married Filing Jointly in a single output file.

Usage: python3 gen_tax_table.py
"""

import math

import tax_data_2026 as td
from constants import SINGLE, MFJ

# ─── Configuration ───────────────────────────────────────────────
TAX_YEAR = td.TAX_YEAR

STATUSES = [
    {"fs": MFJ, "label": "Married Filing Jointly", "ss_multiplier": 2, "examples": [400_000, 500_000, 600_000]},
    {"fs": SINGLE, "label": "Single", "ss_multiplier": 1, "examples": [100_000, 200_000, 400_000]},
]

OUTPUT_FILE = f"tax_table_{TAX_YEAR}.md"


# ─── Helpers ─────────────────────────────────────────────────────

def calc_progressive_tax(income, brackets):
    tax = 0.0
    prev = 0
    for upper, rate in brackets:
        if income <= prev:
            break
        taxable = min(income, upper) - prev
        tax += taxable * rate
        prev = upper
    return tax


def fmt_dollar(val):
    return f"${val:,.0f}"


def fmt_rate(val):
    if val == 0:
        return "0%"
    pct = val * 100
    if pct == int(pct):
        return f"{int(pct)}%"
    s = f"{pct:.2f}".rstrip("0").rstrip(".")
    return f"{s}%"


def collect_breakpoints(fed_brackets, ca_brackets, fed_std_ded, ca_std_ded, ss_cap, add_med_threshold):
    points = {0}
    points.add(fed_std_ded)
    for upper, _ in fed_brackets:
        if not math.isinf(upper):
            points.add(upper + fed_std_ded)
    points.add(ca_std_ded)
    for upper, _ in ca_brackets:
        if not math.isinf(upper):
            points.add(upper + ca_std_ded)
    points.add(ss_cap)
    points.add(add_med_threshold)
    return sorted(points)


def marginal_rate(agi, brackets, std_ded):
    taxable = max(agi - std_ded, 0)
    if taxable == 0:
        return 0.0
    for upper, rate in brackets:
        if taxable <= upper:
            return rate
    return brackets[-1][1]


def build_rows(fs, ss_multiplier):
    fed_std_ded = td.FEDERAL_STANDARD_DEDUCTION[fs]
    ca_std_ded = td.CA_STANDARD_DEDUCTION[fs]
    fed_brackets = td.FEDERAL_BRACKETS[fs]
    ca_brackets = td.CA_BRACKETS[fs]
    ss_cap = td.SS_WAGE_BASE * ss_multiplier
    add_med_threshold = td.ADDITIONAL_MEDICARE_THRESHOLD[fs]

    breakpoints = collect_breakpoints(
        fed_brackets, ca_brackets, fed_std_ded, ca_std_ded, ss_cap, add_med_threshold
    )
    rows = []
    for i, start in enumerate(breakpoints):
        end = breakpoints[i + 1] if i + 1 < len(breakpoints) else None
        test = start + 1 if start > 0 else 1

        fr = marginal_rate(test, fed_brackets, fed_std_ded)
        cr = marginal_rate(test, ca_brackets, ca_std_ded)
        sr = td.SS_RATE if test < ss_cap else 0.0
        mr = td.MEDICARE_RATE if test < add_med_threshold else td.MEDICARE_RATE + td.ADDITIONAL_MEDICARE_RATE
        dr = td.CA_SDI_RATE
        combined = fr + cr + sr + mr + dr

        cf = calc_progressive_tax(max(start - fed_std_ded, 0), fed_brackets)
        cc = calc_progressive_tax(max(start - ca_std_ded, 0), ca_brackets)
        cs = min(start, ss_cap) * td.SS_RATE
        cm = start * td.MEDICARE_RATE + max(0, start - add_med_threshold) * td.ADDITIONAL_MEDICARE_RATE
        cd = start * td.CA_SDI_RATE
        ct = cf + cc + cs + cm + cd

        rows.append({
            "start": start, "end": end,
            "end_str": fmt_dollar(end) if end else "∞",
            "fed_rate": fr, "ca_rate": cr, "ss_rate": sr,
            "med_rate": mr, "sdi_rate": dr, "combined": combined,
            "cum_fed": cf, "cum_ca": cc, "cum_ss": cs,
            "cum_med": cm, "cum_sdi": cd, "cum_total": ct,
        })
    return rows


def find_example_bracket(rows, agi):
    for i, r in enumerate(rows):
        if r["end"] is None or agi < r["end"]:
            return i
    return len(rows) - 1


def render_section(status_cfg):
    fs = status_cfg["fs"]
    label = status_cfg["label"]
    ss_mult = status_cfg["ss_multiplier"]

    fed_std_ded = td.FEDERAL_STANDARD_DEDUCTION[fs]
    ca_std_ded = td.CA_STANDARD_DEDUCTION[fs]
    ss_cap = td.SS_WAGE_BASE * ss_mult
    add_med_threshold = td.ADDITIONAL_MEDICARE_THRESHOLD[fs]

    lines = []
    lines.append(f"## {label}\n")
    lines.append("**Assumptions:**\n")
    lines.append(f"- Federal standard deduction: {fmt_dollar(fed_std_ded)}")
    lines.append(f"- CA standard deduction: {fmt_dollar(ca_std_ded)}")
    if ss_mult > 1:
        lines.append(
            f"- SS wage base: {fmt_dollar(td.SS_WAGE_BASE)} per person "
            f"(doubled to {fmt_dollar(ss_cap)} for MFJ)"
        )
        lines.append(
            f"\n> **Note:** SS tax depends on each spouse's individual wages, not combined AGI\n"
        )
    else:
        lines.append(f"- SS wage base: {fmt_dollar(ss_cap)}")
    lines.append(
        f"- Medicare: {fmt_rate(td.MEDICARE_RATE)} base + "
        f"{fmt_rate(td.ADDITIONAL_MEDICARE_RATE)} additional above {fmt_dollar(add_med_threshold)}"
    )
    lines.append(f"- CA SDI: {fmt_rate(td.CA_SDI_RATE)} (no cap)")
    lines.append("- All income is W-2 wages; no other income sources\n")

    # Table
    lines.append(
        "| AGI Range | Fed | CA | SS | Med | SDI "
        "| **Fed+CA** | **FICA** | **Combined** "
        "| Cum Fed | Cum CA | Cum SS | Cum Med | Cum SDI | **Cum Total** |"
    )
    lines.append("|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|")

    rows = build_rows(fs, ss_mult)
    for r in rows:
        fed_ca = r["fed_rate"] + r["ca_rate"]
        fica = r["ss_rate"] + r["med_rate"] + r["sdi_rate"]
        line = (
            f"| {fmt_dollar(r['start'])} – {r['end_str']} "
            f"| {fmt_rate(r['fed_rate'])} "
            f"| {fmt_rate(r['ca_rate'])} "
            f"| {fmt_rate(r['ss_rate'])} "
            f"| {fmt_rate(r['med_rate'])} "
            f"| {fmt_rate(r['sdi_rate'])} "
            f"| **{fmt_rate(fed_ca)}** "
            f"| **{fmt_rate(fica)}** "
            f"| **{fmt_rate(r['combined'])}** "
            f"| {fmt_dollar(round(r['cum_fed']))} "
            f"| {fmt_dollar(round(r['cum_ca']))} "
            f"| {fmt_dollar(round(r['cum_ss']))} "
            f"| {fmt_dollar(round(r['cum_med']))} "
            f"| {fmt_dollar(round(r['cum_sdi']))} "
            f"| **{fmt_dollar(round(r['cum_total']))}** |"
        )
        lines.append(line)

    # Examples
    for example_agi in status_cfg["examples"]:
        ex_idx = find_example_bracket(rows, example_agi)
        b = rows[ex_idx]
        delta = example_agi - b["start"]
        total_tax = b["cum_total"] + delta * b["combined"]

        lines.append(f"\n### Example — AGI {fmt_dollar(example_agi)}\n")
        lines.append(
            f"Falls in the **{fmt_dollar(b['start'])} – {b['end_str']}** bracket "
            f"({fmt_rate(b['combined'])} combined):\n"
        )
        lines.append("```")
        lines.append(
            f"Total tax = {fmt_dollar(round(b['cum_total']))} "
            f"+ ({fmt_dollar(example_agi)} − {fmt_dollar(b['start'])}) "
            f"× {fmt_rate(b['combined'])}"
        )
        lines.append(
            f"         = {fmt_dollar(round(b['cum_total']))} "
            f"+ {fmt_dollar(delta)} × {fmt_rate(b['combined'])}"
        )
        lines.append(f"         = {fmt_dollar(round(total_tax))}")
        lines.append("```\n")

        lines.append("**By component:**\n")
        lines.append("| Tax | Cumulative at bracket start | + Marginal on remainder | = Amount |")
        lines.append("|---|---|---|---|")

        components = [
            ("Federal", b["cum_fed"], b["fed_rate"]),
            ("CA State", b["cum_ca"], b["ca_rate"]),
            ("Social Security", b["cum_ss"], b["ss_rate"]),
            ("Medicare", b["cum_med"], b["med_rate"]),
            ("CA SDI", b["cum_sdi"], b["sdi_rate"]),
        ]
        grand_total = 0.0
        for name, cum, rate in components:
            marginal = delta * rate
            amt = cum + marginal
            grand_total += amt
            lines.append(
                f"| {name} "
                f"| {fmt_dollar(round(cum))} "
                f"| {fmt_dollar(delta)} × {fmt_rate(rate)} = {fmt_dollar(round(marginal))} "
                f"| **{fmt_dollar(round(amt))}** |"
            )
        lines.append(f"| **Total** | | | **{fmt_dollar(round(grand_total))}** |")

    return "\n".join(lines)


# ─── Main ────────────────────────────────────────────────────────

if __name__ == "__main__":
    parts = []
    parts.append(f"# Combined Marginal Tax Rate Tables — {TAX_YEAR}\n")

    for status_cfg in STATUSES:
        parts.append("---\n")
        parts.append(render_section(status_cfg))

    md = "\n".join(parts) + "\n"

    with open(OUTPUT_FILE, "w") as f:
        f.write(md)

    print(f"Written to {OUTPUT_FILE}")
    print()
    print(md)
