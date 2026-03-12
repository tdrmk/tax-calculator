"""
Core tax calculation functions.
All computation logic — no I/O or formatting.
"""

from constants import CAPITAL_LOSS_LIMIT


def calculate_progressive_tax(taxable_income, brackets):
    """
    Calculate tax using progressive (marginal) brackets.

    Args:
        taxable_income: The income to tax
        brackets: List of (upper_limit, rate) tuples

    Returns:
        (total_tax, bracket_details): total tax and list of
        (lower_limit, upper_limit, rate, taxed_amount, tax_in_bracket)
    """
    if taxable_income <= 0:
        return 0.0, []

    total_tax = 0.0
    details = []
    prev_limit = 0

    for upper_limit, rate in brackets:
        if taxable_income <= prev_limit:
            break

        taxable_in_bracket = min(taxable_income, upper_limit) - prev_limit
        if taxable_in_bracket <= 0:
            prev_limit = upper_limit
            continue

        tax_in_bracket = taxable_in_bracket * rate
        total_tax += tax_in_bracket

        details.append((prev_limit, upper_limit, rate, taxable_in_bracket, tax_in_bracket))
        prev_limit = upper_limit

    return total_tax, details


def calculate_ltcg_tax(ordinary_taxable_income, ltcg_income, brackets):
    """
    Calculate tax on long-term capital gains / qualified dividends.
    LTCG is stacked on top of ordinary income to determine the applicable rate.

    Args:
        ordinary_taxable_income: Ordinary taxable income (determines stacking start)
        ltcg_income: Total long-term capital gains + qualified dividends
        brackets: LTCG brackets for the filing status

    Returns:
        (total_tax, bracket_details): total tax and list of
        (lower_limit, upper_limit, rate, taxed_amount, tax_in_bracket)
    """
    if ltcg_income <= 0:
        return 0.0, []

    total_tax = 0.0
    details = []

    # LTCG is stacked on top of ordinary income
    stack_start = max(ordinary_taxable_income, 0)
    stack_end = stack_start + ltcg_income

    prev_limit = 0
    for upper_limit, rate in brackets:
        if stack_start >= upper_limit:
            prev_limit = upper_limit
            continue

        # The portion of LTCG in this bracket
        bracket_bottom = max(stack_start, prev_limit)
        bracket_top = min(stack_end, upper_limit)

        taxable_in_bracket = bracket_top - bracket_bottom
        if taxable_in_bracket <= 0:
            prev_limit = upper_limit
            continue

        tax_in_bracket = taxable_in_bracket * rate
        total_tax += tax_in_bracket

        details.append((prev_limit, upper_limit, rate, taxable_in_bracket, tax_in_bracket))

        if stack_end <= upper_limit:
            break

        prev_limit = upper_limit

    return total_tax, details


def calculate_taxes(inputs, tax_data):
    """
    Perform all tax calculations and return a results dictionary.

    Args:
        inputs: Dictionary of user inputs from collect_inputs()
        tax_data: Tax data module (e.g. tax_data_2025) with all
                  brackets, rates, deductions, and thresholds.
    """
    fs = inputs["filing_status"]
    wages = inputs["wages"]
    spouse1_wages = inputs["spouse1_wages"]
    spouse2_wages = inputs["spouse2_wages"]

    # ── Extract tax data ──
    FEDERAL_BRACKETS = tax_data.FEDERAL_BRACKETS[fs]
    FEDERAL_LTCG_BRACKETS = tax_data.FEDERAL_LTCG_BRACKETS[fs]
    FEDERAL_STANDARD_DEDUCTION = tax_data.FEDERAL_STANDARD_DEDUCTION[fs]
    CA_BRACKETS = tax_data.CA_BRACKETS[fs]
    CA_STANDARD_DEDUCTION = tax_data.CA_STANDARD_DEDUCTION[fs]
    SS_RATE = tax_data.SS_RATE
    SS_WAGE_BASE = tax_data.SS_WAGE_BASE
    MEDICARE_RATE = tax_data.MEDICARE_RATE
    ADDITIONAL_MEDICARE_RATE = tax_data.ADDITIONAL_MEDICARE_RATE
    ADDITIONAL_MEDICARE_THRESHOLD = tax_data.ADDITIONAL_MEDICARE_THRESHOLD[fs]
    CA_SDI_RATE = tax_data.CA_SDI_RATE
    NIIT_RATE = tax_data.NIIT_RATE
    NIIT_THRESHOLD = tax_data.NIIT_THRESHOLD[fs]
    CAP_LOSS_LIMIT = CAPITAL_LOSS_LIMIT[fs]

    # ── Capital Gains Netting (Schedule D logic) ──
    # Net ST and LT separately, then combine.
    # If net is negative, cap the deduction against ordinary income.
    st_gains = inputs["st_cap_gains"]
    lt_gains = inputs["lt_cap_gains"]
    qualified_dividends = inputs["qualified_dividends"]
    net_capital = st_gains + lt_gains

    if net_capital >= 0:
        # Net gain — determine character of the gain
        if st_gains >= 0 and lt_gains >= 0:
            # Both positive: ST is ordinary, LT is preferential
            ordinary_cap_gains = st_gains
            preferential_cap_gains = lt_gains
        elif st_gains < 0:
            # ST loss absorbed by LT gain; remainder is preferential
            ordinary_cap_gains = 0
            preferential_cap_gains = net_capital
        else:
            # LT loss absorbed by ST gain; remainder is ordinary
            ordinary_cap_gains = net_capital
            preferential_cap_gains = 0
        capital_loss_applied = 0
        capital_loss_carryforward = 0
    else:
        # Net loss — cap deduction at $3,000 ($1,500 MFS) against ordinary income
        ordinary_cap_gains = 0
        preferential_cap_gains = 0
        capital_loss_applied = max(net_capital, -CAP_LOSS_LIMIT)  # e.g., max(-20000, -3000) = -3000
        capital_loss_carryforward = abs(net_capital) - abs(capital_loss_applied)

    # ── Income Aggregation ──
    ordinary_additional = (
        ordinary_cap_gains
        + capital_loss_applied  # 0 or negative (capped deduction)
        + inputs["ordinary_dividends"]
        + inputs["interest_income"]
        + inputs["other_income"]
    )
    preferential_income = preferential_cap_gains + qualified_dividends
    total_additional = ordinary_additional + preferential_income
    total_gross = wages + total_additional

    # ── Pre-Tax Deductions ──
    s1_total_ded = inputs["s1_retirement"] + inputs["s1_health"] + inputs["s1_other"]
    s2_total_ded = inputs["s2_retirement"] + inputs["s2_health"] + inputs["s2_other"]
    total_pretax_deductions = s1_total_ded + s2_total_ded

    # ── Taxable Wages by Category (W-2 perspective) ──
    # Federal/State taxable wages (W-2 Box 1 / Box 16):
    #   = Gross wages − all pre-tax deductions (retirement + health + other)
    #   CA conforms to all federal exclusions, so Box 16 = Box 1.
    #
    # Social Security / Medicare wages (W-2 Box 3 / Box 5):
    #   = Gross wages − Section 125 (health) − Section 132(f) (other) deductions
    #   Only 401(k)/403(b)/457(b) elective deferrals remain subject to FICA.
    #   Health (Sec 125) and Other (commuter/transit, life ins) are FICA-exempt.
    s1_fed_taxable_wages = max(spouse1_wages - s1_total_ded, 0)
    s2_fed_taxable_wages = max(spouse2_wages - s2_total_ded, 0)
    fed_taxable_wages = s1_fed_taxable_wages + s2_fed_taxable_wages
    state_taxable_wages = fed_taxable_wages  # CA conforms

    s1_fica_wages = max(spouse1_wages - inputs["s1_health"] - inputs["s1_other"], 0)
    s2_fica_wages = max(spouse2_wages - inputs["s2_health"] - inputs["s2_other"], 0)
    total_fica_wages = s1_fica_wages + s2_fica_wages

    # ── Post-Tax Contributions ──
    total_posttax = inputs["nondeduc_ira"] + inputs["after_tax_401k"] + inputs["other_posttax"]

    # ── AGI ──
    agi = total_gross - total_pretax_deductions

    # ── Standard Deductions ──
    fed_std_deduction = FEDERAL_STANDARD_DEDUCTION
    ca_std_deduction = CA_STANDARD_DEDUCTION

    # ── California Taxable Income (computed first — needed for SALT) ──
    # CA taxes ALL income as ordinary (no preferential LTCG rates)
    ca_taxable = max(agi - ca_std_deduction, 0)

    # ── California Tax ──
    ca_tax, ca_details = calculate_progressive_tax(ca_taxable, CA_BRACKETS)
    total_ca_tax = ca_tax

    # ── SALT Deduction (Itemized) ──
    # For now, SALT = CA state income tax only (no property tax, local tax, etc.)
    # The SALT cap is $40K (2025 OBBBA), with income-based phase-out.
    SALT_CAP = tax_data.SALT_CAP[fs]
    SALT_PHASEOUT_THRESHOLD = tax_data.SALT_PHASEOUT_THRESHOLD[fs]
    SALT_PHASEOUT_RATE = tax_data.SALT_PHASEOUT_RATE
    SALT_FLOOR = tax_data.SALT_FLOOR[fs]

    salt_taxes_paid = total_ca_tax  # only CA income tax for now
    salt_excess = max(agi - SALT_PHASEOUT_THRESHOLD, 0)
    salt_cap_effective = max(SALT_CAP - SALT_PHASEOUT_RATE * salt_excess, SALT_FLOOR)
    salt_capped = min(salt_taxes_paid, salt_cap_effective)

    # Itemized deduction = SALT (could add mortgage interest, charitable, etc. later)
    itemized_deduction = salt_capped

    # ── Choose: Standard vs. Itemized ──
    if itemized_deduction > fed_std_deduction:
        fed_deduction_used = itemized_deduction
        fed_deduction_method = "itemized"
    else:
        fed_deduction_used = fed_std_deduction
        fed_deduction_method = "standard"

    # ── Federal Ordinary Taxable Income ──
    # Excludes LTCG and qualified dividends (they are taxed separately)
    fed_ordinary_taxable = max(agi - fed_deduction_used - preferential_income, 0)

    # ── Federal Ordinary Tax ──
    fed_ordinary_tax, fed_ordinary_details = calculate_progressive_tax(
        fed_ordinary_taxable, FEDERAL_BRACKETS
    )

    # ── Federal LTCG / Qualified Dividend Tax ──
    # Stacked on top of ordinary taxable income
    fed_ltcg_tax, fed_ltcg_details = calculate_ltcg_tax(
        fed_ordinary_taxable, preferential_income, FEDERAL_LTCG_BRACKETS
    )

    # ── NIIT (Net Investment Income Tax) ──
    net_investment_income = total_additional
    if agi > NIIT_THRESHOLD and net_investment_income > 0:
        niit_base = min(net_investment_income, agi - NIIT_THRESHOLD)
        niit = niit_base * NIIT_RATE
    else:
        niit = 0.0
        niit_base = 0.0

    # ── Total Federal Tax ──
    total_federal_tax = fed_ordinary_tax + fed_ltcg_tax + niit

    # ── FICA: Social Security (per-spouse wage base for MFJ) ──
    # SS wages = FICA wages (gross − Section 125 health deductions), capped per person
    spouse1_ss_wages = min(s1_fica_wages, SS_WAGE_BASE)
    spouse2_ss_wages = min(s2_fica_wages, SS_WAGE_BASE)
    spouse1_ss_tax = spouse1_ss_wages * SS_RATE
    spouse2_ss_tax = spouse2_ss_wages * SS_RATE
    ss_tax = spouse1_ss_tax + spouse2_ss_tax

    # ── FICA: Medicare (combined FICA wages for MFJ) ──
    medicare_tax = total_fica_wages * MEDICARE_RATE
    if total_fica_wages > ADDITIONAL_MEDICARE_THRESHOLD:
        addl_medicare_tax = (total_fica_wages - ADDITIONAL_MEDICARE_THRESHOLD) * ADDITIONAL_MEDICARE_RATE
    else:
        addl_medicare_tax = 0.0
    total_medicare = medicare_tax + addl_medicare_tax

    # ── CA SDI / VDI (per-spouse, FICA wages, no cap) ──
    # Standard SDI is calculated per spouse on their FICA wages.
    # If enrolled in CA VDI, use the lesser of standard SDI or VDI max contribution.
    s1_ca_sdi = s1_fica_wages * CA_SDI_RATE
    s2_ca_sdi = s2_fica_wages * CA_SDI_RATE

    if inputs["s1_vdi_enrolled"]:
        s1_ca_sdi_or_vdi = min(s1_ca_sdi, inputs["s1_vdi_max"])
    else:
        s1_ca_sdi_or_vdi = s1_ca_sdi

    if inputs["s2_vdi_enrolled"]:
        s2_ca_sdi_or_vdi = min(s2_ca_sdi, inputs["s2_vdi_max"])
    else:
        s2_ca_sdi_or_vdi = s2_ca_sdi

    ca_sdi = s1_ca_sdi_or_vdi + s2_ca_sdi_or_vdi

    # ── Totals ──
    total_fica = ss_tax + total_medicare
    total_payroll = total_fica + ca_sdi
    total_all_taxes = total_federal_tax + total_ca_tax + total_payroll

    # ── Rates ──
    effective_rate = total_all_taxes / agi if agi > 0 else 0

    # Federal marginal rate (highest bracket ordinary income reaches)
    fed_marginal = 0.0
    prev = 0
    for upper, rate in FEDERAL_BRACKETS:
        if fed_ordinary_taxable > prev:
            fed_marginal = rate
        prev = upper

    # CA marginal rate
    ca_marginal = 0.0
    prev = 0
    for upper, rate in CA_BRACKETS:
        if ca_taxable > prev:
            ca_marginal = rate
        prev = upper

    # ── Take-Home Pay ──
    take_home = total_gross - total_all_taxes - total_pretax_deductions - total_posttax

    return {
        "filing_status": fs,
        "wages": wages,
        "st_gains": st_gains,
        "lt_gains": lt_gains,
        "net_capital": net_capital,
        "ordinary_cap_gains": ordinary_cap_gains,
        "preferential_cap_gains": preferential_cap_gains,
        "capital_loss_applied": capital_loss_applied,
        "capital_loss_carryforward": capital_loss_carryforward,
        "ordinary_additional": ordinary_additional,
        "preferential_income": preferential_income,
        "total_additional": total_additional,
        "total_gross": total_gross,
        "total_pretax_deductions": total_pretax_deductions,
        "s1_total_ded": s1_total_ded,
        "s2_total_ded": s2_total_ded,
        "s1_fed_taxable_wages": s1_fed_taxable_wages,
        "s2_fed_taxable_wages": s2_fed_taxable_wages,
        "fed_taxable_wages": fed_taxable_wages,
        "state_taxable_wages": state_taxable_wages,
        "s1_fica_wages": s1_fica_wages,
        "s2_fica_wages": s2_fica_wages,
        "total_fica_wages": total_fica_wages,
        "total_posttax": total_posttax,
        "agi": agi,
        "fed_std_deduction": fed_std_deduction,
        "ca_std_deduction": ca_std_deduction,
        "salt_taxes_paid": salt_taxes_paid,
        "salt_cap_effective": salt_cap_effective,
        "salt_capped": salt_capped,
        "itemized_deduction": itemized_deduction,
        "fed_deduction_used": fed_deduction_used,
        "fed_deduction_method": fed_deduction_method,
        "fed_ordinary_taxable": fed_ordinary_taxable,
        "ca_taxable": ca_taxable,
        "fed_ordinary_tax": fed_ordinary_tax,
        "fed_ordinary_details": fed_ordinary_details,
        "fed_ltcg_tax": fed_ltcg_tax,
        "fed_ltcg_details": fed_ltcg_details,
        "niit": niit,
        "niit_base": niit_base,
        "total_federal_tax": total_federal_tax,
        "ca_tax": ca_tax,
        "ca_details": ca_details,
        "total_ca_tax": total_ca_tax,
        "spouse1_wages": spouse1_wages,
        "spouse2_wages": spouse2_wages,
        "spouse1_ss_wages": spouse1_ss_wages,
        "spouse2_ss_wages": spouse2_ss_wages,
        "spouse1_ss_tax": spouse1_ss_tax,
        "spouse2_ss_tax": spouse2_ss_tax,
        "ss_tax": ss_tax,
        "medicare_tax": medicare_tax,
        "addl_medicare_tax": addl_medicare_tax,
        "total_medicare": total_medicare,
        "s1_ca_sdi": s1_ca_sdi,
        "s2_ca_sdi": s2_ca_sdi,
        "s1_ca_sdi_or_vdi": s1_ca_sdi_or_vdi,
        "s2_ca_sdi_or_vdi": s2_ca_sdi_or_vdi,
        "ca_sdi": ca_sdi,
        "total_fica": total_fica,
        "total_payroll": total_payroll,
        "total_all_taxes": total_all_taxes,
        "effective_rate": effective_rate,
        "fed_marginal": fed_marginal,
        "ca_marginal": ca_marginal,
        "take_home": take_home,
        "inputs": inputs,
    }
