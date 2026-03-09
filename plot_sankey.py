"""
Sankey diagram visualization of tax calculation results.
Shows the flow of income → taxes → deductions → take-home pay.

Usage:
    from plot_sankey import generate_sankey
    results = calculate_taxes(inputs, tax_data)
    generate_sankey(results)
"""

import plotly.graph_objects as go
from constants import SINGLE, MFJ, MFS, HOH


FILING_STATUS_LABELS = {
    SINGLE: "Single",
    MFJ: "Married Filing Jointly",
    MFS: "Married Filing Separately",
    HOH: "Head of Household",
}

# ── Color Palette ──

# Income sources (greens)
CLR_WAGES_1 = "#2d8a4e"
CLR_WAGES_2 = "#52b788"
CLR_ORD_CAP = "#74c69d"
CLR_ORD_DIV = "#95d5b2"
CLR_INTEREST = "#b7e4c7"
CLR_OTHER_INC = "#8fbc8f"
CLR_PREF_CAP = "#1b4332"
CLR_QUAL_DIV = "#40916c"

# Aggregates
CLR_GROSS = "#14532d"
CLR_AGI = "#0077b6"

# Pre-tax deductions (purples)
CLR_PRETAX = "#7b2cbf"
CLR_RETIREMENT = "#9d4edd"
CLR_HEALTH = "#c77dff"
CLR_OTHER_PRETAX = "#e0aaff"

# Payroll taxes (reds/warm)
CLR_PAYROLL = "#d62828"
CLR_SS = "#ef476f"
CLR_MEDICARE = "#f4845f"
CLR_SDI = "#f4a261"

# Federal tax (blues)
CLR_FEDERAL = "#1d3557"
CLR_FED_ORD = "#264653"
CLR_FED_LTCG = "#2a9d8f"
CLR_NIIT = "#023e8a"

# CA tax (orange)
CLR_CA_TAX = "#e76f51"

# Net after tax / take-home
CLR_NET_AFTER_TAX = "#457b9d"
CLR_TAKE_HOME = "#06d6a0"

# Post-tax contributions (grays)
CLR_POSTTAX = "#6c757d"
CLR_IRA = "#adb5bd"
CLR_AFTER_401K = "#ced4da"
CLR_OTHER_POST = "#868e96"

# Final summary column
CLR_SUM_PRETAX = "#9d4edd"
CLR_SUM_TAXES = "#c1121f"
CLR_SUM_POSTTAX = "#495057"
CLR_SUM_TAKEHOME = "#06d6a0"


def _rgba(hex_color, alpha=0.35):
    """Convert hex color to rgba string for link colors."""
    h = hex_color.lstrip("#")
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    return f"rgba({r},{g},{b},{alpha})"


def _fmt(v):
    """Format a dollar amount for node labels."""
    return f"${v:,.0f}"


def generate_sankey(results, output_file="local/tax_sankey.png"):
    """
    Generate a Sankey diagram showing the flow of income through
    pre-tax deductions, taxes, post-tax contributions, and take-home pay.

    Args:
        results: Dictionary returned by calculate_taxes()
        output_file: Path for the output image file (PNG)
    """
    r = results
    inputs = r["inputs"]
    fs = r["filing_status"]

    # ── Dynamic node/link builder ──
    labels = []
    node_colors = []
    link_sources = []
    link_targets = []
    link_values = []
    link_colors = []
    node_map = {}

    def add_node(name, label, color):
        idx = len(labels)
        labels.append(label)
        node_colors.append(color)
        node_map[name] = idx
        return idx

    def add_link(src, tgt, value, color):
        if value <= 0:
            return
        link_sources.append(node_map[src])
        link_targets.append(node_map[tgt])
        link_values.append(value)
        link_colors.append(color)

    # ════════════════════════════════════════════════════════════════════
    # NODES
    # ════════════════════════════════════════════════════════════════════

    # ── Column 1: Income Sources ──
    if fs == MFJ and inputs["spouse2_wages"] > 0:
        add_node("s1_wages",
                 f"Spouse 1 Wages  {_fmt(inputs['spouse1_wages'])}",
                 CLR_WAGES_1)
        add_node("s2_wages",
                 f"Spouse 2 Wages  {_fmt(inputs['spouse2_wages'])}",
                 CLR_WAGES_2)
    elif r["wages"] > 0:
        add_node("wages", f"Wages  {_fmt(r['wages'])}", CLR_WAGES_1)

    if r["ordinary_cap_gains"] > 0:
        add_node("ord_cap",
                 f"ST Cap Gains  {_fmt(r['ordinary_cap_gains'])}",
                 CLR_ORD_CAP)
    if inputs["ordinary_dividends"] > 0:
        add_node("ord_div",
                 f"Ordinary Dividends  {_fmt(inputs['ordinary_dividends'])}",
                 CLR_ORD_DIV)
    if inputs["interest_income"] > 0:
        add_node("interest",
                 f"Interest Income  {_fmt(inputs['interest_income'])}",
                 CLR_INTEREST)
    if inputs["other_income"] > 0:
        add_node("other_inc",
                 f"Other Income  {_fmt(inputs['other_income'])}",
                 CLR_OTHER_INC)
    if r["preferential_cap_gains"] > 0:
        add_node("pref_cap",
                 f"LT Cap Gains  {_fmt(r['preferential_cap_gains'])}",
                 CLR_PREF_CAP)
    if inputs["qualified_dividends"] > 0:
        add_node("qual_div",
                 f"Qualified Dividends  {_fmt(inputs['qualified_dividends'])}",
                 CLR_QUAL_DIV)

    # ── Column 2: Total Gross Income ──
    add_node("gross",
             f"Total Gross Income  {_fmt(r['total_gross'])}",
             CLR_GROSS)

    # ── Column 3: Pre-Tax Deductions & AGI ──
    if r["total_pretax_deductions"] > 0:
        add_node("pretax",
                 f"Pre-Tax Deductions  {_fmt(r['total_pretax_deductions'])}",
                 CLR_PRETAX)
    add_node("agi", f"AGI  {_fmt(r['agi'])}", CLR_AGI)

    # ── Pre-Tax sub-breakdowns ──
    total_retirement = inputs["s1_retirement"] + inputs["s2_retirement"]
    total_health = inputs["s1_health"] + inputs["s2_health"]
    total_other_pretax = inputs["s1_other"] + inputs["s2_other"]

    if total_retirement > 0:
        add_node("retirement",
                 f"Retirement  {_fmt(total_retirement)}",
                 CLR_RETIREMENT)
    if total_health > 0:
        add_node("health", f"Health  {_fmt(total_health)}", CLR_HEALTH)
    if total_other_pretax > 0:
        add_node("other_pretax",
                 f"Other Pre-Tax  {_fmt(total_other_pretax)}",
                 CLR_OTHER_PRETAX)

    # ── Column 4: Tax Categories & Net After Tax ──
    if r["total_payroll"] > 0:
        add_node("payroll",
                 f"Payroll Taxes  {_fmt(r['total_payroll'])}",
                 CLR_PAYROLL)
    if r["total_federal_tax"] > 0:
        add_node("federal",
                 f"Federal Tax  {_fmt(r['total_federal_tax'])}",
                 CLR_FEDERAL)
    if r["total_ca_tax"] > 0:
        add_node("ca_tax",
                 f"CA State Tax  {_fmt(r['total_ca_tax'])}",
                 CLR_CA_TAX)

    net_after_tax = r["agi"] - r["total_all_taxes"]
    add_node("net_after_tax",
             f"Net After Tax  {_fmt(net_after_tax)}",
             CLR_NET_AFTER_TAX)

    # ── Payroll sub-breakdowns ──
    if r["ss_tax"] > 0:
        add_node("ss",
                 f"Social Security  {_fmt(r['ss_tax'])}",
                 CLR_SS)
    if r["total_medicare"] > 0:
        add_node("medicare",
                 f"Medicare  {_fmt(r['total_medicare'])}",
                 CLR_MEDICARE)
    if r["ca_sdi"] > 0:
        add_node("sdi", f"CA SDI  {_fmt(r['ca_sdi'])}", CLR_SDI)

    # ── Federal sub-breakdowns ──
    if r["fed_ordinary_tax"] > 0:
        add_node("fed_ordinary",
                 f"Ordinary Income Tax  {_fmt(r['fed_ordinary_tax'])}",
                 CLR_FED_ORD)
    if r["fed_ltcg_tax"] > 0:
        add_node("fed_ltcg",
                 f"LTCG Tax  {_fmt(r['fed_ltcg_tax'])}",
                 CLR_FED_LTCG)
    if r["niit"] > 0:
        add_node("niit", f"NIIT  {_fmt(r['niit'])}", CLR_NIIT)

    # ── Post-Tax & Take-Home ──
    if r["total_posttax"] > 0:
        add_node("posttax",
                 f"Post-Tax Contributions  {_fmt(r['total_posttax'])}",
                 CLR_POSTTAX)
    add_node("take_home",
             f"Take-Home Pay  {_fmt(r['take_home'])}",
             CLR_TAKE_HOME)

    # ── Post-Tax sub-breakdowns ──
    if inputs["nondeduc_ira"] > 0:
        add_node("ira",
                 f"Non-deductible IRA  {_fmt(inputs['nondeduc_ira'])}",
                 CLR_IRA)
    if inputs["after_tax_401k"] > 0:
        add_node("after_401k",
                 f"After-tax 401(k)  {_fmt(inputs['after_tax_401k'])}",
                 CLR_AFTER_401K)
    if inputs["other_posttax"] > 0:
        add_node("other_post",
                 f"Other Post-Tax  {_fmt(inputs['other_posttax'])}",
                 CLR_OTHER_POST)

    # ── Final Summary Column ──
    pct_pretax = r["total_pretax_deductions"] / r["total_gross"] * 100 if r["total_gross"] > 0 else 0
    pct_taxes = r["total_all_taxes"] / r["total_gross"] * 100 if r["total_gross"] > 0 else 0
    pct_posttax = r["total_posttax"] / r["total_gross"] * 100 if r["total_gross"] > 0 else 0
    pct_takehome = r["take_home"] / r["total_gross"] * 100 if r["total_gross"] > 0 else 0

    if r["total_pretax_deductions"] > 0:
        add_node("sum_pretax",
                 f"Pre-Tax  {_fmt(r['total_pretax_deductions'])}  ({pct_pretax:.1f}%)",
                 CLR_SUM_PRETAX)
    add_node("sum_taxes",
             f"All Taxes  {_fmt(r['total_all_taxes'])}  ({pct_taxes:.1f}%)",
             CLR_SUM_TAXES)
    if r["total_posttax"] > 0:
        add_node("sum_posttax",
                 f"Post-Tax  {_fmt(r['total_posttax'])}  ({pct_posttax:.1f}%)",
                 CLR_SUM_POSTTAX)
    add_node("sum_takehome",
             f"Take-Home  {_fmt(r['take_home'])}  ({pct_takehome:.1f}%)",
             CLR_SUM_TAKEHOME)

    # ════════════════════════════════════════════════════════════════════
    # LINKS
    # ════════════════════════════════════════════════════════════════════

    # ── Income Sources → Total Gross Income ──
    if "s1_wages" in node_map:
        add_link("s1_wages", "gross",
                 inputs["spouse1_wages"], _rgba(CLR_WAGES_1))
    if "s2_wages" in node_map:
        add_link("s2_wages", "gross",
                 inputs["spouse2_wages"], _rgba(CLR_WAGES_2))
    if "wages" in node_map:
        add_link("wages", "gross",
                 r["wages"], _rgba(CLR_WAGES_1))
    if "ord_cap" in node_map:
        add_link("ord_cap", "gross",
                 r["ordinary_cap_gains"], _rgba(CLR_ORD_CAP))
    if "ord_div" in node_map:
        add_link("ord_div", "gross",
                 inputs["ordinary_dividends"], _rgba(CLR_ORD_DIV))
    if "interest" in node_map:
        add_link("interest", "gross",
                 inputs["interest_income"], _rgba(CLR_INTEREST))
    if "other_inc" in node_map:
        add_link("other_inc", "gross",
                 inputs["other_income"], _rgba(CLR_OTHER_INC))
    if "pref_cap" in node_map:
        add_link("pref_cap", "gross",
                 r["preferential_cap_gains"], _rgba(CLR_PREF_CAP))
    if "qual_div" in node_map:
        add_link("qual_div", "gross",
                 inputs["qualified_dividends"], _rgba(CLR_QUAL_DIV))

    # ── Total Gross Income → Pre-Tax Deductions + AGI ──
    if "pretax" in node_map:
        add_link("gross", "pretax",
                 r["total_pretax_deductions"], _rgba(CLR_PRETAX))
    add_link("gross", "agi", r["agi"], _rgba(CLR_AGI))

    # ── Pre-Tax Deductions → sub-breakdowns ──
    if "retirement" in node_map:
        add_link("pretax", "retirement",
                 total_retirement, _rgba(CLR_RETIREMENT))
    if "health" in node_map:
        add_link("pretax", "health",
                 total_health, _rgba(CLR_HEALTH))
    if "other_pretax" in node_map:
        add_link("pretax", "other_pretax",
                 total_other_pretax, _rgba(CLR_OTHER_PRETAX))

    # ── AGI → Tax Categories + Net After Tax ──
    if "payroll" in node_map:
        add_link("agi", "payroll",
                 r["total_payroll"], _rgba(CLR_PAYROLL))
    if "federal" in node_map:
        add_link("agi", "federal",
                 r["total_federal_tax"], _rgba(CLR_FEDERAL))
    if "ca_tax" in node_map:
        add_link("agi", "ca_tax",
                 r["total_ca_tax"], _rgba(CLR_CA_TAX))
    add_link("agi", "net_after_tax",
             net_after_tax, _rgba(CLR_NET_AFTER_TAX))

    # ── Payroll → sub-breakdowns ──
    if "ss" in node_map:
        add_link("payroll", "ss",
                 r["ss_tax"], _rgba(CLR_SS))
    if "medicare" in node_map:
        add_link("payroll", "medicare",
                 r["total_medicare"], _rgba(CLR_MEDICARE))
    if "sdi" in node_map:
        add_link("payroll", "sdi",
                 r["ca_sdi"], _rgba(CLR_SDI))

    # ── Federal → sub-breakdowns ──
    if "fed_ordinary" in node_map:
        add_link("federal", "fed_ordinary",
                 r["fed_ordinary_tax"], _rgba(CLR_FED_ORD))
    if "fed_ltcg" in node_map:
        add_link("federal", "fed_ltcg",
                 r["fed_ltcg_tax"], _rgba(CLR_FED_LTCG))
    if "niit" in node_map:
        add_link("federal", "niit",
                 r["niit"], _rgba(CLR_NIIT))

    # ── Net After Tax → Post-Tax Contributions + Take-Home ──
    if "posttax" in node_map:
        add_link("net_after_tax", "posttax",
                 r["total_posttax"], _rgba(CLR_POSTTAX))
    add_link("net_after_tax", "take_home",
             r["take_home"], _rgba(CLR_TAKE_HOME, 0.45))

    # ── Post-Tax → sub-breakdowns ──
    if "ira" in node_map:
        add_link("posttax", "ira",
                 inputs["nondeduc_ira"], _rgba(CLR_IRA))
    if "after_401k" in node_map:
        add_link("posttax", "after_401k",
                 inputs["after_tax_401k"], _rgba(CLR_AFTER_401K))
    if "other_post" in node_map:
        add_link("posttax", "other_post",
                 inputs["other_posttax"], _rgba(CLR_OTHER_POST))

    # ── Sub-breakdowns → Final Summary ──

    # Pre-tax sub-breakdowns → Summary Pre-Tax
    if "sum_pretax" in node_map:
        if "retirement" in node_map:
            add_link("retirement", "sum_pretax",
                     total_retirement, _rgba(CLR_SUM_PRETAX))
        if "health" in node_map:
            add_link("health", "sum_pretax",
                     total_health, _rgba(CLR_SUM_PRETAX))
        if "other_pretax" in node_map:
            add_link("other_pretax", "sum_pretax",
                     total_other_pretax, _rgba(CLR_SUM_PRETAX))

    # Tax sub-breakdowns → Summary Taxes
    if "ss" in node_map:
        add_link("ss", "sum_taxes",
                 r["ss_tax"], _rgba(CLR_SUM_TAXES))
    if "medicare" in node_map:
        add_link("medicare", "sum_taxes",
                 r["total_medicare"], _rgba(CLR_SUM_TAXES))
    if "sdi" in node_map:
        add_link("sdi", "sum_taxes",
                 r["ca_sdi"], _rgba(CLR_SUM_TAXES))
    if "fed_ordinary" in node_map:
        add_link("fed_ordinary", "sum_taxes",
                 r["fed_ordinary_tax"], _rgba(CLR_SUM_TAXES))
    if "fed_ltcg" in node_map:
        add_link("fed_ltcg", "sum_taxes",
                 r["fed_ltcg_tax"], _rgba(CLR_SUM_TAXES))
    if "niit" in node_map:
        add_link("niit", "sum_taxes",
                 r["niit"], _rgba(CLR_SUM_TAXES))
    if "ca_tax" in node_map:
        add_link("ca_tax", "sum_taxes",
                 r["total_ca_tax"], _rgba(CLR_SUM_TAXES))

    # Post-tax sub-breakdowns → Summary Post-Tax
    if "sum_posttax" in node_map:
        if "ira" in node_map:
            add_link("ira", "sum_posttax",
                     inputs["nondeduc_ira"], _rgba(CLR_SUM_POSTTAX))
        if "after_401k" in node_map:
            add_link("after_401k", "sum_posttax",
                     inputs["after_tax_401k"], _rgba(CLR_SUM_POSTTAX))
        if "other_post" in node_map:
            add_link("other_post", "sum_posttax",
                     inputs["other_posttax"], _rgba(CLR_SUM_POSTTAX))

    # Take-Home → Summary Take-Home
    add_link("take_home", "sum_takehome",
             r["take_home"], _rgba(CLR_SUM_TAKEHOME, 0.45))

    # ════════════════════════════════════════════════════════════════════
    # BUILD FIGURE
    # ════════════════════════════════════════════════════════════════════

    fig = go.Figure(data=[go.Sankey(
        arrangement="snap",
        valueformat="$,.0f",
        node=dict(
            pad=20,
            thickness=25,
            line=dict(color="black", width=0.5),
            label=labels,
            color=node_colors,
        ),
        link=dict(
            source=link_sources,
            target=link_targets,
            value=link_values,
            color=link_colors,
        ),
    )])

    fs_label = FILING_STATUS_LABELS.get(fs, fs)

    def _fmt_title(v):
        """Format dollar amount without $ (Plotly treats $ as MathJax)."""
        return f"{v:,.0f}"

    subtitle = (
        f"Gross: {_fmt_title(r['total_gross'])}  ·  "
        f"Tax: {_fmt_title(r['total_all_taxes'])}  ·  "
        f"Effective: {r['effective_rate'] * 100:.1f}%  ·  "
        f"Take-Home: {_fmt_title(r['take_home'])}"
    )
    fig.update_layout(
        title=dict(
            text=f"Tax Flow — {fs_label}<br>{subtitle}",
            font=dict(size=15),
        ),
        font=dict(size=11, family="Arial"),
        width=1600,
        height=800,
        margin=dict(l=10, r=10, t=80, b=20),
    )

    fig.write_image(output_file, scale=2)
    print(f"\nSankey diagram saved to {output_file}")
