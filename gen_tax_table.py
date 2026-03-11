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
    {"fs": MFJ, "label": "Married Filing Jointly", "ss_multiplier": 2, "examples": [400_000, 500_000, 600_000],
     "inv_example": {"wages": 400_000, "ordinary": 50_000, "preferential": 50_000},
     "k401_examples": [600_000]},
    {"fs": SINGLE, "label": "Single", "ss_multiplier": 1, "examples": [100_000, 200_000, 400_000],
     "inv_example": {"wages": 200_000, "ordinary": 25_000, "preferential": 25_000},
     "k401_examples": [400_000, 200_000]},
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


def collect_investment_breakpoints(fed_brackets, ca_brackets, fed_std_ded, ca_std_ded, niit_threshold):
    points = {0}
    points.add(fed_std_ded)
    for upper, _ in fed_brackets:
        if not math.isinf(upper):
            points.add(upper + fed_std_ded)
    points.add(ca_std_ded)
    for upper, _ in ca_brackets:
        if not math.isinf(upper):
            points.add(upper + ca_std_ded)
    points.add(niit_threshold)
    return sorted(points)


def build_investment_rows(fs, use_ltcg=False):
    fed_std_ded = td.FEDERAL_STANDARD_DEDUCTION[fs]
    ca_std_ded = td.CA_STANDARD_DEDUCTION[fs]
    fed_brackets = td.FEDERAL_LTCG_BRACKETS[fs] if use_ltcg else td.FEDERAL_BRACKETS[fs]
    ca_brackets = td.CA_BRACKETS[fs]
    niit_threshold = td.NIIT_THRESHOLD[fs]

    breakpoints = collect_investment_breakpoints(
        fed_brackets, ca_brackets, fed_std_ded, ca_std_ded, niit_threshold
    )
    rows = []
    for i, start in enumerate(breakpoints):
        end = breakpoints[i + 1] if i + 1 < len(breakpoints) else None
        test = start + 1 if start > 0 else 1

        fr = marginal_rate(test, fed_brackets, fed_std_ded)
        cr = marginal_rate(test, ca_brackets, ca_std_ded)
        nr = td.NIIT_RATE if test > niit_threshold else 0.0
        combined = fr + cr + nr

        rows.append({
            "start": start, "end": end,
            "end_str": fmt_dollar(end) if end else "∞",
            "fed_rate": fr, "ca_rate": cr, "niit_rate": nr,
            "combined": combined,
        })
    return rows


def calc_stacked_tax(inv_rows, start_agi, end_agi):
    """Tax on income stacked from start_agi to end_agi using investment rate rows."""
    details = []
    for r in inv_rows:
        row_end = r["end"] if r["end"] else float("inf")
        lo = max(start_agi, r["start"])
        hi = min(end_agi, row_end)
        if hi <= lo:
            continue
        chunk = hi - lo
        fed = chunk * r["fed_rate"]
        ca = chunk * r["ca_rate"]
        niit = chunk * r["niit_rate"]
        details.append({
            "lo": lo, "hi": hi, "chunk": chunk,
            "bracket_start": r["start"],
            "bracket_end_str": r["end_str"],
            "fed_rate": r["fed_rate"], "ca_rate": r["ca_rate"],
            "niit_rate": r["niit_rate"],
            "fed": fed, "ca": ca, "niit": niit, "total": fed + ca + niit,
        })
    return details


def calc_tax_components(gross_wages, agi, fs, ss_multiplier):
    """Individual tax components; FICA based on gross_wages, income tax on agi."""
    fed_std_ded = td.FEDERAL_STANDARD_DEDUCTION[fs]
    ca_std_ded = td.CA_STANDARD_DEDUCTION[fs]
    ss_cap = td.SS_WAGE_BASE * ss_multiplier
    add_med_thr = td.ADDITIONAL_MEDICARE_THRESHOLD[fs]

    fed = calc_progressive_tax(max(agi - fed_std_ded, 0), td.FEDERAL_BRACKETS[fs])
    ca = calc_progressive_tax(max(agi - ca_std_ded, 0), td.CA_BRACKETS[fs])
    ss = min(gross_wages, ss_cap) * td.SS_RATE
    med = (gross_wages * td.MEDICARE_RATE
           + max(0, gross_wages - add_med_thr) * td.ADDITIONAL_MEDICARE_RATE)
    sdi = gross_wages * td.CA_SDI_RATE
    total = fed + ca + ss + med + sdi
    return {"fed": fed, "ca": ca, "ss": ss, "med": med, "sdi": sdi, "total": total}


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

    # ── Investment Income Tables ──────────────────────────────────
    niit_threshold = td.NIIT_THRESHOLD[fs]

    lines.append(f"\n### Ordinary Investment Income")
    lines.append("*(interest, non-qualified dividends, short-term capital gains)*\n")
    lines.append(
        f"> Stack on top of wage income — find your **total AGI** to determine the starting bracket.  "
    )
    lines.append(f"> No FICA (SS, Medicare) or SDI. NIIT of {fmt_rate(td.NIIT_RATE)} "
                 f"applies above {fmt_dollar(niit_threshold)}.\n")

    lines.append("| AGI Range | Fed | CA | NIIT | **Combined** |")
    lines.append("|---|---|---|---|---|")

    for r in build_investment_rows(fs, use_ltcg=False):
        lines.append(
            f"| {fmt_dollar(r['start'])} – {r['end_str']} "
            f"| {fmt_rate(r['fed_rate'])} "
            f"| {fmt_rate(r['ca_rate'])} "
            f"| {fmt_rate(r['niit_rate'])} "
            f"| **{fmt_rate(r['combined'])}** |"
        )

    lines.append(f"\n### Preferential Investment Income")
    lines.append("*(long-term capital gains, qualified dividends)*\n")
    lines.append(
        "> Stack on top of **all ordinary taxable income** (wages + ordinary investment) "
        "to find the starting bracket.  "
    )
    lines.append(
        "> Federal uses 0%/15%/20% LTCG brackets. CA taxes capital gains as ordinary income "
        f"(no preferential rate). NIIT of {fmt_rate(td.NIIT_RATE)} applies above "
        f"{fmt_dollar(niit_threshold)}.\n"
    )

    lines.append("| AGI Range | Fed (LTCG) | CA | NIIT | **Combined** |")
    lines.append("|---|---|---|---|---|")

    for r in build_investment_rows(fs, use_ltcg=True):
        lines.append(
            f"| {fmt_dollar(r['start'])} – {r['end_str']} "
            f"| {fmt_rate(r['fed_rate'])} "
            f"| {fmt_rate(r['ca_rate'])} "
            f"| {fmt_rate(r['niit_rate'])} "
            f"| **{fmt_rate(r['combined'])}** |"
        )

    # ── Investment Example ────────────────────────────────────────
    inv_ex = status_cfg.get("inv_example")
    if inv_ex:
        wages = inv_ex["wages"]
        ordinary = inv_ex["ordinary"]
        preferential = inv_ex["preferential"]
        total_agi = wages + ordinary + preferential

        lines.append(f"\n### Example — Combined Income\n")
        lines.append(
            f"**Scenario:** {fmt_dollar(wages)} wages "
            f"+ {fmt_dollar(ordinary)} ordinary investment income "
            f"+ {fmt_dollar(preferential)} LTCG/qualified dividends  "
        )
        lines.append(f"**Total AGI:** {fmt_dollar(total_agi)}\n")

        # Step 1: Wages
        wage_rows = build_rows(fs, status_cfg["ss_multiplier"])
        wi = find_example_bracket(wage_rows, wages)
        wb = wage_rows[wi]
        w_delta = wages - wb["start"]
        wage_tax = wb["cum_total"] + w_delta * wb["combined"]

        lines.append(f"**Step 1 — Wages** ({fmt_dollar(wages)}, from wage table):\n")
        lines.append("```")
        lines.append(
            f"Wage taxes = {fmt_dollar(round(wb['cum_total']))} "
            f"+ ({fmt_dollar(wages)} − {fmt_dollar(wb['start'])}) "
            f"× {fmt_rate(wb['combined'])}"
        )
        lines.append(f"           = {fmt_dollar(round(wage_tax))}")
        lines.append("```\n")

        # Step 2: Ordinary investment income
        ord_rows = build_investment_rows(fs, use_ltcg=False)
        ord_details = calc_stacked_tax(ord_rows, wages, wages + ordinary)
        ord_total = sum(d["total"] for d in ord_details)

        lines.append(
            f"**Step 2 — Ordinary investment income** "
            f"(stacks {fmt_dollar(wages)} → {fmt_dollar(wages + ordinary)}):\n"
        )
        lines.append("| Bracket | Amount | Combined | Tax |")
        lines.append("|---|---|---|---|")
        for d in ord_details:
            combined = d["fed_rate"] + d["ca_rate"] + d["niit_rate"]
            lines.append(
                f"| {fmt_dollar(d['bracket_start'])} – {d['bracket_end_str']} "
                f"| {fmt_dollar(d['chunk'])} "
                f"| {fmt_rate(combined)} "
                f"| {fmt_dollar(round(d['total']))} |"
            )
        if len(ord_details) > 1:
            lines.append(
                f"| **Total** | **{fmt_dollar(ordinary)}** "
                f"| | **{fmt_dollar(round(ord_total))}** |"
            )
        lines.append("")

        # Step 3: Preferential income
        pref_start = wages + ordinary
        pref_end = total_agi
        ltcg_rows = build_investment_rows(fs, use_ltcg=True)
        pref_details = calc_stacked_tax(ltcg_rows, pref_start, pref_end)
        pref_total = sum(d["total"] for d in pref_details)

        lines.append(
            f"**Step 3 — Preferential income (LTCG/qualified dividends)** "
            f"(stacks {fmt_dollar(pref_start)} → {fmt_dollar(pref_end)}):\n"
        )
        lines.append("| Bracket | Amount | Combined | Tax |")
        lines.append("|---|---|---|---|")
        for d in pref_details:
            combined = d["fed_rate"] + d["ca_rate"] + d["niit_rate"]
            lines.append(
                f"| {fmt_dollar(d['bracket_start'])} – {d['bracket_end_str']} "
                f"| {fmt_dollar(d['chunk'])} "
                f"| {fmt_rate(combined)} "
                f"| {fmt_dollar(round(d['total']))} |"
            )
        if len(pref_details) > 1:
            lines.append(
                f"| **Total** | **{fmt_dollar(preferential)}** "
                f"| | **{fmt_dollar(round(pref_total))}** |"
            )
        lines.append("")

        # Grand total
        grand_total = wage_tax + ord_total + pref_total
        eff_rate = grand_total / total_agi

        lines.append("**Grand total:**\n")
        lines.append("| Category | Tax |")
        lines.append("|---|---|")
        lines.append(f"| Wages | {fmt_dollar(round(wage_tax))} |")
        lines.append(f"| Ordinary investment | {fmt_dollar(round(ord_total))} |")
        lines.append(f"| Preferential (LTCG) | {fmt_dollar(round(pref_total))} |")
        lines.append(f"| **Total** | **{fmt_dollar(round(grand_total))}** |")
        lines.append(f"| Effective rate on {fmt_dollar(total_agi)} | **{fmt_rate(eff_rate)}** |")

    # ── 401(k) Examples ──────────────────────────────────────────
    k401_list = status_cfg.get("k401_examples", [])
    if k401_list:
        ss_mult = status_cfg["ss_multiplier"]
        contrib = td.ELECTIVE_DEFERRAL_LIMIT * ss_mult

        def fmt_delta(val):
            if val == 0:
                return "$0"
            return f"−{fmt_dollar(round(abs(val)))}" if val < 0 else f"+{fmt_dollar(round(val))}"

        for k401_wages in k401_list:
            agi_before = k401_wages
            agi_after = k401_wages - contrib

            before = calc_tax_components(k401_wages, agi_before, fs, ss_mult)
            after = calc_tax_components(k401_wages, agi_after, fs, ss_mult)

            take_home_before = agi_before - before["total"]
            take_home_after = agi_after - after["total"]
            th_delta = take_home_after - take_home_before
            th_pct = th_delta / take_home_before

            contrib_label = fmt_dollar(contrib)
            if ss_mult > 1:
                contrib_label += f" ({ss_mult} × {fmt_dollar(td.ELECTIVE_DEFERRAL_LIMIT)})"

            lines.append(f"\n### Example — 401(k) Max Contribution ({fmt_dollar(k401_wages)} wages)\n")
            lines.append(
                f"**Scenario:** {fmt_dollar(k401_wages)} wages, "
                f"{contrib_label} pre-tax 401(k) contribution  "
            )
            lines.append(
                f"> 401(k) reduces AGI for federal and CA income tax, "
                f"but FICA (SS, Medicare) and SDI are based on gross wages.\n"
            )

            lines.append("| | Without 401(k) | With 401(k) | Δ |")
            lines.append("|---|---|---|---|")

            components = [
                ("AGI", agi_before, agi_after),
                ("Federal", before["fed"], after["fed"]),
                ("CA State", before["ca"], after["ca"]),
                ("Social Security", before["ss"], after["ss"]),
                ("Medicare", before["med"], after["med"]),
                ("CA SDI", before["sdi"], after["sdi"]),
            ]
            for name, bv, av in components:
                delta = av - bv
                lines.append(
                    f"| {name} "
                    f"| {fmt_dollar(round(bv))} "
                    f"| {fmt_dollar(round(av))} "
                    f"| {fmt_delta(delta)} |"
                )

            total_delta = after["total"] - before["total"]
            lines.append(
                f"| **Total tax** "
                f"| **{fmt_dollar(round(before['total']))}** "
                f"| **{fmt_dollar(round(after['total']))}** "
                f"| **{fmt_delta(total_delta)}** |"
            )
            lines.append(
                f"| **Take-home** "
                f"| **{fmt_dollar(round(take_home_before))}** "
                f"| **{fmt_dollar(round(take_home_after))}** "
                f"| **{fmt_delta(th_delta)} ({th_pct:+.1%})** |"
            )

            tax_saved = abs(total_delta)
            th_cost = abs(th_delta)
            th_cost_pct = round(th_cost / contrib * 100)
            tax_saved_pct = round(tax_saved / contrib * 100)
            leverage = contrib / th_cost

            lines.append(
                f"\n> {fmt_dollar(contrib)} contributed "
                f"= {fmt_dollar(round(th_cost))} from take-home ({th_cost_pct}%) "
                f"+ {fmt_dollar(round(tax_saved))} from tax savings ({tax_saved_pct}%)  "
            )
            lines.append(
                f"> → Every $1 less in take-home puts **${leverage:.2f}** into your 401(k)."
            )

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
