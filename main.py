#!/usr/bin/env python3
"""
Tax Calculator — 2025 Tax Year
Federal + California + FICA + CA SDI

Calculates taxes based on wages, investment income, pre-tax deductions,
and post-tax contributions for all filing statuses.
"""

# ============================================================================
# TAX DATA — 2025 TAX YEAR
# ============================================================================

# Filing status constants
SINGLE = "single"
MFJ = "married_filing_jointly"
MFS = "married_filing_separately"
HOH = "head_of_household"

FILING_STATUS_LABELS = {
    SINGLE: "Single",
    MFJ: "Married Filing Jointly",
    MFS: "Married Filing Separately",
    HOH: "Head of Household",
}

# --- Federal Ordinary Income Tax Brackets (2025) ---
# Format: list of (upper_limit, rate) — progressive/marginal brackets
FEDERAL_BRACKETS = {
    SINGLE: [
        (11_925, 0.10),
        (48_475, 0.12),
        (103_350, 0.22),
        (197_300, 0.24),
        (250_525, 0.32),
        (626_350, 0.35),
        (float("inf"), 0.37),
    ],
    MFJ: [
        (23_850, 0.10),
        (96_950, 0.12),
        (206_700, 0.22),
        (394_600, 0.24),
        (501_050, 0.32),
        (751_600, 0.35),
        (float("inf"), 0.37),
    ],
    MFS: [
        (11_925, 0.10),
        (48_475, 0.12),
        (103_350, 0.22),
        (197_300, 0.24),
        (250_525, 0.32),
        (375_800, 0.35),
        (float("inf"), 0.37),
    ],
    HOH: [
        (17_000, 0.10),
        (64_850, 0.12),
        (103_350, 0.22),
        (197_300, 0.24),
        (250_500, 0.32),
        (626_350, 0.35),
        (float("inf"), 0.37),
    ],
}

# --- Federal Long-Term Capital Gains / Qualified Dividends Brackets (2025) ---
FEDERAL_LTCG_BRACKETS = {
    SINGLE: [
        (48_350, 0.00),
        (533_400, 0.15),
        (float("inf"), 0.20),
    ],
    MFJ: [
        (96_700, 0.00),
        (600_050, 0.15),
        (float("inf"), 0.20),
    ],
    MFS: [
        (48_350, 0.00),
        (300_000, 0.15),
        (float("inf"), 0.20),
    ],
    HOH: [
        (64_750, 0.00),
        (566_700, 0.15),
        (float("inf"), 0.20),
    ],
}

# --- Federal Standard Deduction (2025) ---
FEDERAL_STANDARD_DEDUCTION = {
    SINGLE: 15_750,
    MFJ: 31_500,
    MFS: 15_750,
    HOH: 23_625,
}

# --- California Income Tax Brackets (2025) ---
# Single and MFS use the same brackets (Schedule X)
# MFJ uses Schedule Y, HOH uses Schedule Z (each has unique thresholds)
CA_BRACKETS = {
    SINGLE: [
        (11_079, 0.01),
        (26_264, 0.02),
        (41_452, 0.04),
        (57_542, 0.06),
        (72_724, 0.08),
        (371_479, 0.093),
        (445_771, 0.103),
        (742_953, 0.113),
        (float("inf"), 0.123),
    ],
    MFJ: [
        (22_158, 0.01),
        (52_528, 0.02),
        (82_904, 0.04),
        (115_084, 0.06),
        (145_448, 0.08),
        (742_958, 0.093),
        (891_542, 0.103),
        (1_485_906, 0.113),
        (float("inf"), 0.123),
    ],
    MFS: [
        (11_079, 0.01),
        (26_264, 0.02),
        (41_452, 0.04),
        (57_542, 0.06),
        (72_724, 0.08),
        (371_479, 0.093),
        (445_771, 0.103),
        (742_953, 0.113),
        (float("inf"), 0.123),
    ],
    HOH: [
        (22_173, 0.01),
        (52_530, 0.02),
        (67_716, 0.04),
        (83_805, 0.06),
        (98_990, 0.08),
        (505_208, 0.093),
        (606_251, 0.103),
        (1_010_417, 0.113),
        (float("inf"), 0.123),
    ],
}

# --- California Standard Deduction (2025) ---
CA_STANDARD_DEDUCTION = {
    SINGLE: 5_706,
    MFJ: 11_412,
    MFS: 5_706,
    HOH: 11_412,
}

# --- FICA (2025) ---
SS_RATE = 0.062
SS_WAGE_BASE = 176_100
MEDICARE_RATE = 0.0145
ADDITIONAL_MEDICARE_RATE = 0.009
ADDITIONAL_MEDICARE_THRESHOLD = {
    SINGLE: 200_000,
    MFJ: 250_000,
    MFS: 125_000,
    HOH: 200_000,
}

# --- CA SDI (2025) — no wage limit ---
CA_SDI_RATE = 0.012

# --- NIIT (Net Investment Income Tax) ---
NIIT_RATE = 0.038
NIIT_THRESHOLD = {
    SINGLE: 200_000,
    MFJ: 250_000,
    MFS: 125_000,
    HOH: 200_000,
}


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================


def fmt(amount):
    """Format a number as currency: $1,234.56"""
    if amount < 0:
        return f"-${abs(amount):,.2f}"
    return f"${amount:,.2f}"


def pct(rate):
    """Format a decimal rate as percentage: 24.00%"""
    return f"{rate * 100:.2f}%"


def get_input(prompt, required=False):
    """Get a numeric input from the user with validation."""
    while True:
        raw = input(prompt).strip().replace(",", "").replace("$", "")
        if not raw:
            if required:
                print("  ⚠  This field is required. Please enter a value.")
                continue
            return 0.0
        try:
            value = float(raw)
            if value < 0:
                print("  ⚠  Please enter a non-negative number.")
                continue
            return value
        except ValueError:
            print("  ⚠  Invalid input. Please enter a number.")


def calculate_progressive_tax(taxable_income, brackets):
    """
    Calculate tax using progressive (marginal) brackets.

    Args:
        taxable_income: The income to tax
        brackets: List of (upper_limit, rate) tuples

    Returns:
        (total_tax, bracket_details): total tax and list of
        (bracket_label, rate, taxed_amount, tax_in_bracket)
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

        if upper_limit == float("inf"):
            bracket_label = f"{fmt(prev_limit)}+"
        else:
            bracket_label = f"{fmt(prev_limit)} - {fmt(upper_limit)}"

        details.append((bracket_label, rate, taxable_in_bracket, tax_in_bracket))
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
        (total_tax, bracket_details)
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

        if upper_limit == float("inf"):
            bracket_label = f"{fmt(prev_limit)}+"
        else:
            bracket_label = f"{fmt(prev_limit)} - {fmt(upper_limit)}"

        details.append((bracket_label, rate, taxable_in_bracket, tax_in_bracket))

        if stack_end <= upper_limit:
            break

        prev_limit = upper_limit

    return total_tax, details


# ============================================================================
# INPUT COLLECTION
# ============================================================================


def collect_inputs():
    """Collect all user inputs via interactive CLI prompts."""
    print()
    print("=" * 70)
    print("           TAX CALCULATOR — 2025 TAX YEAR")
    print("           Federal + California + FICA + CA SDI")
    print("=" * 70)
    print()

    # --- Filing Status ---
    print("  FILING STATUS")
    print("  " + "-" * 40)
    print("  1. Single")
    print("  2. Married Filing Jointly")
    print("  3. Married Filing Separately")
    print("  4. Head of Household")
    while True:
        choice = input("\n  Select filing status (1-4): ").strip()
        if choice in ("1", "2", "3", "4"):
            filing_status = [SINGLE, MFJ, MFS, HOH][int(choice) - 1]
            break
        print("  ⚠  Please enter 1, 2, 3, or 4.")

    print(f"\n  ✓ Filing as: {FILING_STATUS_LABELS[filing_status]}")

    # --- Gross Income ---
    print("\n  GROSS ANNUAL INCOME (Wages/Salary)")
    print("  " + "-" * 40)
    if filing_status == MFJ:
        print("  (SS wage base applies per spouse — enter each separately)\n")
        spouse1_wages = get_input("  Spouse 1 wages/salary: $", required=True)
        spouse2_wages = get_input("  Spouse 2 wages/salary: $", required=True)
        wages = spouse1_wages + spouse2_wages
        print(f"\n  Combined wages: {fmt(wages)}")
    else:
        wages = get_input("  Gross annual wages/salary: $", required=True)
        spouse1_wages = wages
        spouse2_wages = 0.0

    # --- Additional Income — Ordinary ---
    print("\n  ADDITIONAL INCOME — Ordinary (taxed at ordinary rates)")
    print("  " + "-" * 40)
    print("  (Press Enter to skip any field, defaults to $0)\n")
    st_cap_gains = get_input("  Short-term capital gains:       $")
    ordinary_dividends = get_input("  Ordinary (non-qualified) div:   $")
    bond_interest = get_input("  Bond interest:                  $")
    savings_interest = get_input("  Savings account interest:       $")

    # --- Additional Income — Preferential ---
    print("\n  ADDITIONAL INCOME — Preferential (LTCG / Qualified Dividends)")
    print("  " + "-" * 40)
    print("  (Press Enter to skip any field, defaults to $0)\n")
    lt_cap_gains = get_input("  Long-term capital gains:        $")
    qualified_dividends = get_input("  Qualified dividends:            $")

    # --- Pre-Tax Deductions ---
    print("\n  PRE-TAX DEDUCTIONS (reduce AGI)")
    print("  " + "-" * 40)
    print("  Enter the total for each category.")
    print("  (Press Enter to skip any field, defaults to $0)")
    if filing_status == MFJ:
        print("\n  Spouse 1:")
        print("    Retirement (401k, 403b, 457b, etc.):")
        s1_retirement = get_input("      $")
        print("    Health (premiums, HSA, FSA, dental/vision, dep. care FSA):")
        s1_health = get_input("      $")
        print("    Other (commuter/transit, life insurance, etc.):")
        s1_other = get_input("      $")
        print("\n  Spouse 2:")
        print("    Retirement (401k, 403b, 457b, etc.):")
        s2_retirement = get_input("      $")
        print("    Health (premiums, HSA, FSA, dental/vision, dep. care FSA):")
        s2_health = get_input("      $")
        print("    Other (commuter/transit, life insurance, etc.):")
        s2_other = get_input("      $")
    else:
        print()
        print("  Retirement (401k, 403b, 457b, etc.):")
        s1_retirement = get_input("    $")
        print("  Health (premiums, HSA, FSA, dental/vision, dep. care FSA):")
        s1_health = get_input("    $")
        print("  Other (commuter/transit, life insurance, etc.):")
        s1_other = get_input("    $")
        s2_retirement = 0.0
        s2_health = 0.0
        s2_other = 0.0

    # --- CA VDI (Voluntary Disability Insurance) ---
    print("\n  CA VDI (Voluntary Disability Insurance)")
    print("  " + "-" * 40)
    print("  If enrolled in a CA VDI plan, the disability insurance cost")
    print("  is the greater of the standard CA SDI or the VDI max contribution.")
    if filing_status == MFJ:
        while True:
            s1_vdi_choice = input("\n  Is Spouse 1 enrolled in CA VDI? (y/n, default n): ").strip().lower()
            if s1_vdi_choice in ("y", "yes"):
                s1_vdi_enrolled = True
                s1_vdi_max = get_input("  Spouse 1 max annual VDI contribution: $", required=True)
                break
            elif s1_vdi_choice in ("n", "no", ""):
                s1_vdi_enrolled = False
                s1_vdi_max = 0.0
                break
            print("  ⚠  Please enter y or n.")
        while True:
            s2_vdi_choice = input("\n  Is Spouse 2 enrolled in CA VDI? (y/n, default n): ").strip().lower()
            if s2_vdi_choice in ("y", "yes"):
                s2_vdi_enrolled = True
                s2_vdi_max = get_input("  Spouse 2 max annual VDI contribution: $", required=True)
                break
            elif s2_vdi_choice in ("n", "no", ""):
                s2_vdi_enrolled = False
                s2_vdi_max = 0.0
                break
            print("  ⚠  Please enter y or n.")
    else:
        while True:
            vdi_choice = input("\n  Are you enrolled in CA VDI? (y/n, default n): ").strip().lower()
            if vdi_choice in ("y", "yes"):
                s1_vdi_enrolled = True
                s1_vdi_max = get_input("  Max annual VDI contribution: $", required=True)
                break
            elif vdi_choice in ("n", "no", ""):
                s1_vdi_enrolled = False
                s1_vdi_max = 0.0
                break
            print("  ⚠  Please enter y or n.")
        s2_vdi_enrolled = False
        s2_vdi_max = 0.0

    # --- Post-Tax Contributions ---
    print("\n  POST-TAX CONTRIBUTIONS (informational only)")
    print("  " + "-" * 40)
    print("  (Press Enter to skip any field, defaults to $0)\n")
    nondeduc_ira = get_input("  Non-deductible Traditional IRA:   $")
    after_tax_401k = get_input("  After-tax 401(k) contributions:   $")
    other_posttax = get_input("  Other post-tax contributions:     $")

    return {
        "filing_status": filing_status,
        "wages": wages,
        "spouse1_wages": spouse1_wages,
        "spouse2_wages": spouse2_wages,
        "st_cap_gains": st_cap_gains,
        "ordinary_dividends": ordinary_dividends,
        "bond_interest": bond_interest,
        "savings_interest": savings_interest,
        "lt_cap_gains": lt_cap_gains,
        "qualified_dividends": qualified_dividends,
        "s1_retirement": s1_retirement,
        "s1_health": s1_health,
        "s1_other": s1_other,
        "s2_retirement": s2_retirement,
        "s2_health": s2_health,
        "s2_other": s2_other,
        "s1_vdi_enrolled": s1_vdi_enrolled,
        "s1_vdi_max": s1_vdi_max,
        "s2_vdi_enrolled": s2_vdi_enrolled,
        "s2_vdi_max": s2_vdi_max,
        "nondeduc_ira": nondeduc_ira,
        "after_tax_401k": after_tax_401k,
        "other_posttax": other_posttax,
    }


# ============================================================================
# TAX CALCULATIONS
# ============================================================================


def calculate_taxes(inputs):
    """Perform all tax calculations and return a results dictionary."""
    fs = inputs["filing_status"]
    wages = inputs["wages"]
    spouse1_wages = inputs["spouse1_wages"]
    spouse2_wages = inputs["spouse2_wages"]

    # ── Income Aggregation ──
    ordinary_additional = (
        inputs["st_cap_gains"]
        + inputs["ordinary_dividends"]
        + inputs["bond_interest"]
        + inputs["savings_interest"]
    )
    preferential_income = inputs["lt_cap_gains"] + inputs["qualified_dividends"]
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
    fed_std_deduction = FEDERAL_STANDARD_DEDUCTION[fs]
    ca_std_deduction = CA_STANDARD_DEDUCTION[fs]

    # ── Federal Ordinary Taxable Income ──
    # Excludes LTCG and qualified dividends (they are taxed separately)
    fed_ordinary_taxable = max(agi - fed_std_deduction - preferential_income, 0)

    # ── Federal Ordinary Tax ──
    fed_ordinary_tax, fed_ordinary_details = calculate_progressive_tax(
        fed_ordinary_taxable, FEDERAL_BRACKETS[fs]
    )

    # ── Federal LTCG / Qualified Dividend Tax ──
    # Stacked on top of ordinary taxable income
    fed_ltcg_tax, fed_ltcg_details = calculate_ltcg_tax(
        fed_ordinary_taxable, preferential_income, FEDERAL_LTCG_BRACKETS[fs]
    )

    # ── NIIT (Net Investment Income Tax) ──
    net_investment_income = total_additional
    niit_threshold = NIIT_THRESHOLD[fs]
    if agi > niit_threshold and net_investment_income > 0:
        niit_base = min(net_investment_income, agi - niit_threshold)
        niit = niit_base * NIIT_RATE
    else:
        niit = 0.0
        niit_base = 0.0

    # ── Total Federal Tax ──
    total_federal_tax = fed_ordinary_tax + fed_ltcg_tax + niit

    # ── California Taxable Income ──
    # CA taxes ALL income as ordinary (no preferential LTCG rates)
    ca_taxable = max(agi - ca_std_deduction, 0)

    # ── California Tax ──
    ca_tax, ca_details = calculate_progressive_tax(ca_taxable, CA_BRACKETS[fs])
    # TODO: Add CA Mental Health Services Tax (Prop 63) — additional 1% on
    #       taxable income over $1,000,000 (all filing statuses), making the
    #       effective top CA rate 13.3% instead of 12.3%.
    total_ca_tax = ca_tax

    # ── FICA: Social Security (per-spouse wage base for MFJ) ──
    # SS wages = FICA wages (gross − Section 125 health deductions), capped per person
    spouse1_ss_wages = min(s1_fica_wages, SS_WAGE_BASE)
    spouse2_ss_wages = min(s2_fica_wages, SS_WAGE_BASE)
    spouse1_ss_tax = spouse1_ss_wages * SS_RATE
    spouse2_ss_tax = spouse2_ss_wages * SS_RATE
    ss_tax = spouse1_ss_tax + spouse2_ss_tax

    # ── FICA: Medicare (combined FICA wages for MFJ) ──
    medicare_tax = total_fica_wages * MEDICARE_RATE
    addl_medicare_threshold = ADDITIONAL_MEDICARE_THRESHOLD[fs]
    if total_fica_wages > addl_medicare_threshold:
        addl_medicare_tax = (total_fica_wages - addl_medicare_threshold) * ADDITIONAL_MEDICARE_RATE
    else:
        addl_medicare_tax = 0.0
    total_medicare = medicare_tax + addl_medicare_tax

    # ── CA SDI / VDI (per-spouse, FICA wages, no cap) ──
    # Standard SDI is calculated per spouse on their FICA wages.
    # If enrolled in CA VDI, use the greater of standard SDI or VDI max contribution.
    s1_ca_sdi = s1_fica_wages * CA_SDI_RATE
    s2_ca_sdi = s2_fica_wages * CA_SDI_RATE

    if inputs["s1_vdi_enrolled"]:
        s1_ca_sdi_or_vdi = max(s1_ca_sdi, inputs["s1_vdi_max"])
    else:
        s1_ca_sdi_or_vdi = s1_ca_sdi

    if inputs["s2_vdi_enrolled"]:
        s2_ca_sdi_or_vdi = max(s2_ca_sdi, inputs["s2_vdi_max"])
    else:
        s2_ca_sdi_or_vdi = s2_ca_sdi

    ca_sdi = s1_ca_sdi_or_vdi + s2_ca_sdi_or_vdi

    # ── Totals ──
    total_fica = ss_tax + total_medicare
    total_payroll = total_fica + ca_sdi
    total_all_taxes = total_federal_tax + total_ca_tax + total_payroll

    # ── Rates ──
    effective_rate = total_all_taxes / total_gross if total_gross > 0 else 0

    # Federal marginal rate (highest bracket ordinary income reaches)
    fed_marginal = 0.0
    prev = 0
    for upper, rate in FEDERAL_BRACKETS[fs]:
        if fed_ordinary_taxable > prev:
            fed_marginal = rate
        prev = upper

    # CA marginal rate
    ca_marginal = 0.0
    prev = 0
    for upper, rate in CA_BRACKETS[fs]:
        if ca_taxable > prev:
            ca_marginal = rate
        prev = upper

    # ── Take-Home Pay ──
    take_home = total_gross - total_all_taxes - total_pretax_deductions - total_posttax

    return {
        "filing_status": fs,
        "wages": wages,
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


# ============================================================================
# OUTPUT DISPLAY
# ============================================================================

W = 70  # report width


def section_header(title):
    """Print a section header."""
    print(f"\n{'-' * W}")
    print(f"  {title}")
    print(f"{'-' * W}")


def highlight_box(label, value):
    """Print a highlighted value in a box."""
    content = f"  {label}{value:>16}"
    padding = W - 4 - len(content) + 2
    print(f"  +{'-' * (W - 4)}+")
    print(f"  |{content}{' ' * padding}|")
    print(f"  +{'-' * (W - 4)}+")


def big_box(label, value):
    """Print an emphasized value in a double-line box."""
    content = f"  {label}{value:>16}"
    padding = W - 4 - len(content) + 2
    print(f"  {'=' * (W - 4)}")
    print(f"   {content}{' ' * padding}")
    print(f"  {'=' * (W - 4)}")


def print_bracket_table(details, label=""):
    """Print a bracket breakdown table."""
    if not details:
        print(f"    No {label} tax (taxable income is $0)")
        return

    print(f"    {'Bracket':<30} {'Rate':>7} {'Taxed Amount':>16} {'Tax':>14}")
    print(f"    {'-' * 30} {'-' * 7} {'-' * 16} {'-' * 14}")
    for bracket_label, rate, amount, tax in details:
        print(
            f"    {bracket_label:<30} {pct(rate):>7} {fmt(amount):>16} {fmt(tax):>14}"
        )


def display_results(r):
    """Display the full tax breakdown report."""
    inputs = r["inputs"]
    fs = r["filing_status"]

    print()
    print("=" * W)
    print("                      TAX CALCULATION RESULTS")
    print("                         2025 Tax Year")
    print("=" * W)

    # ── 1. Income ──
    section_header("INCOME")
    print(f"  Filing Status:                    {FILING_STATUS_LABELS[fs]}")
    if fs == MFJ:
        print(f"  Spouse 1 Wages/Salary:            {fmt(inputs['spouse1_wages']):>16}")
        print(f"  Spouse 2 Wages/Salary:            {fmt(inputs['spouse2_wages']):>16}")
        print(f"  Combined Wages/Salary:            {fmt(r['wages']):>16}")
    else:
        print(f"  Gross Wages/Salary:               {fmt(r['wages']):>16}")
    print()
    print(f"  Additional Ordinary Income:")
    print(f"    Short-term capital gains:        {fmt(inputs['st_cap_gains']):>16}")
    print(f"    Ordinary dividends:              {fmt(inputs['ordinary_dividends']):>16}")
    print(f"    Bond interest:                   {fmt(inputs['bond_interest']):>16}")
    print(f"    Savings account interest:        {fmt(inputs['savings_interest']):>16}")
    print(f"    Subtotal:                        {fmt(r['ordinary_additional']):>16}")
    print()
    print(f"  Additional Preferential Income:")
    print(f"    Long-term capital gains:         {fmt(inputs['lt_cap_gains']):>16}")
    print(f"    Qualified dividends:             {fmt(inputs['qualified_dividends']):>16}")
    print(f"    Subtotal:                        {fmt(r['preferential_income']):>16}")
    print()
    highlight_box("Total Gross Income:               ", fmt(r["total_gross"]))

    # ── 2. Pre-Tax Deductions ──
    section_header("PRE-TAX DEDUCTIONS")
    if fs == MFJ:
        print(f"  Spouse 1:")
        print(f"    Retirement:                      {fmt(inputs['s1_retirement']):>16}")
        print(f"    Health:                          {fmt(inputs['s1_health']):>16}")
        print(f"    Other:                           {fmt(inputs['s1_other']):>16}")
        print(f"    Subtotal:                        {fmt(r['s1_total_ded']):>16}")
        print(f"  Spouse 2:")
        print(f"    Retirement:                      {fmt(inputs['s2_retirement']):>16}")
        print(f"    Health:                          {fmt(inputs['s2_health']):>16}")
        print(f"    Other:                           {fmt(inputs['s2_other']):>16}")
        print(f"    Subtotal:                        {fmt(r['s2_total_ded']):>16}")
        print(f"                                    {'-' * 16}")
        print(f"  Combined Pre-Tax Deductions:      {fmt(r['total_pretax_deductions']):>16}")
    else:
        print(f"  Retirement:                       {fmt(inputs['s1_retirement']):>16}")
        print(f"  Health:                           {fmt(inputs['s1_health']):>16}")
        print(f"  Other:                            {fmt(inputs['s1_other']):>16}")
        print(f"                                    {'-' * 16}")
        print(f"  Total Pre-Tax Deductions:         {fmt(r['total_pretax_deductions']):>16}")

    # ── 3. Taxable Wages (W-2 Perspective) ──
    section_header("TAXABLE WAGES (W-2 Perspective)")
    if fs == MFJ:
        print(f"  Federal Taxable Wages (Box 1):")
        print(f"    Spouse 1:                        {fmt(r['s1_fed_taxable_wages']):>16}")
        print(f"    Spouse 2:                        {fmt(r['s2_fed_taxable_wages']):>16}")
        print(f"    Combined:                        {fmt(r['fed_taxable_wages']):>16}")
        print(f"  State Taxable Wages (Box 16):      {fmt(r['state_taxable_wages']):>16}")
        print(f"    (Same as federal — CA conforms)")
        print(f"  Social Security Wages (Box 3):")
        print(f"    Spouse 1:                        {fmt(r['s1_fica_wages']):>16}")
        print(f"    Spouse 2:                        {fmt(r['s2_fica_wages']):>16}")
        print(f"    Combined:                        {fmt(r['total_fica_wages']):>16}")
        print(f"  Medicare Wages (Box 5):")
        print(f"    Spouse 1:                        {fmt(r['s1_fica_wages']):>16}")
        print(f"    Spouse 2:                        {fmt(r['s2_fica_wages']):>16}")
        print(f"    Combined:                        {fmt(r['total_fica_wages']):>16}")
    else:
        print(f"  Federal Taxable Wages (Box 1):     {fmt(r['fed_taxable_wages']):>16}")
        print(f"  State Taxable Wages (Box 16):      {fmt(r['state_taxable_wages']):>16}")
        print(f"    (Same as federal — CA conforms)")
        print(f"  Social Security Wages (Box 3):     {fmt(r['total_fica_wages']):>16}")
        print(f"  Medicare Wages (Box 5):            {fmt(r['total_fica_wages']):>16}")
    print()
    print(f"  Note: Fed/State wages = Gross − all pre-tax deductions")
    print(f"        SS/Medicare     = Gross − health & other (FICA-exempt)")
    print(f"        Only 401(k)/retirement deductions stay in FICA wages")

    # ── 4. AGI ──
    section_header("ADJUSTED GROSS INCOME (AGI)")
    print(f"  Total Gross Income:               {fmt(r['total_gross']):>16}")
    print(f"  - Pre-Tax Deductions:             {fmt(r['total_pretax_deductions']):>16}")
    print()
    highlight_box("AGI:                              ", fmt(r["agi"]))

    # ── 5. Standard Deductions ──
    section_header("STANDARD DEDUCTIONS")
    print(f"  Federal Standard Deduction:       {fmt(r['fed_std_deduction']):>16}")
    print(f"  California Standard Deduction:    {fmt(r['ca_std_deduction']):>16}")

    # ── 6. Taxable Income ──
    section_header("TAXABLE INCOME")
    print(f"  Federal Ordinary Taxable Income:  {fmt(r['fed_ordinary_taxable']):>16}")
    print(f"    = AGI - Fed Std Deduction - Preferential Income")
    print(f"  Federal Preferential Income:      {fmt(r['preferential_income']):>16}")
    print(f"    = LTCG + Qualified Dividends (stacked on ordinary)")
    print(f"  California Taxable Income:        {fmt(r['ca_taxable']):>16}")
    print(f"    = AGI - CA Std Deduction (CA taxes all as ordinary)")

    # ── 7. Federal Tax ──
    section_header("FEDERAL TAX BREAKDOWN")

    print(f"\n  Federal Ordinary Income Tax:")
    print_bracket_table(r["fed_ordinary_details"], "ordinary")
    if r["fed_ordinary_details"]:
        print(
            f"    {'':30} {'':7} {'Subtotal:':>16} {fmt(r['fed_ordinary_tax']):>14}"
        )

    print(f"\n  Federal LTCG / Qualified Dividend Tax:")
    print_bracket_table(r["fed_ltcg_details"], "LTCG")
    if r["fed_ltcg_details"]:
        print(f"    {'':30} {'':7} {'Subtotal:':>16} {fmt(r['fed_ltcg_tax']):>14}")

    print(f"\n  Net Investment Income Tax (NIIT):")
    if r["niit"] > 0:
        print(
            f"    {pct(NIIT_RATE)} on {fmt(r['niit_base'])} "
            f"of investment income:          {fmt(r['niit']):>14}"
        )
    else:
        print(
            f"    Not applicable (AGI below {fmt(NIIT_THRESHOLD[fs])} threshold)"
        )

    print()
    highlight_box("Total Federal Tax:                ", fmt(r["total_federal_tax"]))

    # ── 8. California Tax ──
    section_header("CALIFORNIA TAX BREAKDOWN")

    print(f"\n  California Income Tax:")
    print_bracket_table(r["ca_details"], "CA")
    if r["ca_details"]:
        print(f"    {'':30} {'':7} {'Subtotal:':>16} {fmt(r['ca_tax']):>14}")

    print()
    highlight_box("Total California Tax:             ", fmt(r["total_ca_tax"]))

    # ── 9. Payroll Taxes ──
    section_header("PAYROLL TAXES (FICA + CA SDI)")

    print(
        f"\n  Social Security ({pct(SS_RATE)} on wages up to {fmt(SS_WAGE_BASE)} per person):"
    )
    if fs == MFJ:
        print(
            f"    Spouse 1:      {fmt(r['spouse1_ss_wages']):>16}"
            f"   Tax: {fmt(r['spouse1_ss_tax']):>14}"
        )
        print(
            f"    Spouse 2:      {fmt(r['spouse2_ss_wages']):>16}"
            f"   Tax: {fmt(r['spouse2_ss_tax']):>14}"
        )
        print(
            f"    Combined:      {'':>16}"
            f"   Tax: {fmt(r['ss_tax']):>14}"
        )
    else:
        print(
            f"    Taxable wages: {fmt(r['spouse1_ss_wages']):>16}"
            f"   Tax: {fmt(r['ss_tax']):>14}"
        )
    print(f"\n  Medicare ({pct(MEDICARE_RATE)} on all FICA wages):")
    print(
        f"    FICA wages:    {fmt(r['total_fica_wages']):>16}"
        f"   Tax: {fmt(r['medicare_tax']):>14}"
    )
    if r["addl_medicare_tax"] > 0:
        threshold = ADDITIONAL_MEDICARE_THRESHOLD[fs]
        print(
            f"\n  Additional Medicare "
            f"({pct(ADDITIONAL_MEDICARE_RATE)} on wages over {fmt(threshold)}):"
        )
        print(
            f"    Excess wages:  {fmt(r['total_fica_wages'] - threshold):>16}"
            f"   Tax: {fmt(r['addl_medicare_tax']):>14}"
        )
    s1_vdi = inputs["s1_vdi_enrolled"]
    s2_vdi = inputs["s2_vdi_enrolled"]
    any_vdi = s1_vdi or s2_vdi

    if any_vdi:
        print(f"\n  CA SDI / VDI:")
    else:
        print(f"\n  CA SDI ({pct(CA_SDI_RATE)} on all FICA wages, no wage limit):")

    if fs == MFJ:
        # Spouse 1
        if s1_vdi:
            print(f"    Spouse 1 (VDI enrolled):")
            print(f"      Standard SDI ({pct(CA_SDI_RATE)} × {fmt(r['s1_fica_wages'])}): {fmt(r['s1_ca_sdi']):>14}")
            print(f"      VDI max annual contribution:       {fmt(inputs['s1_vdi_max']):>14}")
            print(f"      Applied (greater of):              {fmt(r['s1_ca_sdi_or_vdi']):>14}")
        else:
            print(
                f"    Spouse 1:      {fmt(r['s1_fica_wages']):>16}"
                f"   SDI: {fmt(r['s1_ca_sdi_or_vdi']):>14}"
            )
        # Spouse 2
        if s2_vdi:
            print(f"    Spouse 2 (VDI enrolled):")
            print(f"      Standard SDI ({pct(CA_SDI_RATE)} × {fmt(r['s2_fica_wages'])}): {fmt(r['s2_ca_sdi']):>14}")
            print(f"      VDI max annual contribution:       {fmt(inputs['s2_vdi_max']):>14}")
            print(f"      Applied (greater of):              {fmt(r['s2_ca_sdi_or_vdi']):>14}")
        else:
            print(
                f"    Spouse 2:      {fmt(r['s2_fica_wages']):>16}"
                f"   SDI: {fmt(r['s2_ca_sdi_or_vdi']):>14}"
            )
        print(
            f"    Combined:      {'':>16}"
            f"   {'VDI/SDI' if any_vdi else 'SDI'}: {fmt(r['ca_sdi']):>14}"
        )
    else:
        if s1_vdi:
            print(f"      Standard SDI ({pct(CA_SDI_RATE)} × {fmt(r['total_fica_wages'])}): {fmt(r['s1_ca_sdi']):>14}")
            print(f"      VDI max annual contribution:       {fmt(inputs['s1_vdi_max']):>14}")
            print(f"      Applied (greater of):              {fmt(r['ca_sdi']):>14}")
        else:
            print(
                f"    FICA wages:    {fmt(r['total_fica_wages']):>16}"
                f"   Tax: {fmt(r['ca_sdi']):>14}"
            )

    print()
    print(f"  Total FICA:                       {fmt(r['total_fica']):>16}")
    print(f"  CA {'SDI/VDI' if any_vdi else 'SDI'}:{'':>{25 - (2 if any_vdi else 0)}}{fmt(r['ca_sdi']):>16}")
    highlight_box("Total Payroll Taxes:              ", fmt(r["total_payroll"]))

    # ── 10. Tax Summary ──
    print()
    print("=" * W)
    print("  TAX SUMMARY")
    print("=" * W)
    print(f"  Total Federal Tax:                {fmt(r['total_federal_tax']):>16}")
    print(f"  Total California Tax:             {fmt(r['total_ca_tax']):>16}")
    print(f"  Total Payroll Taxes:              {fmt(r['total_payroll']):>16}")
    any_vdi = inputs["s1_vdi_enrolled"] or inputs["s2_vdi_enrolled"]
    sdi_label = "CA SDI/VDI" if any_vdi else "CA SDI"
    print(f"    (FICA: {fmt(r['total_fica'])}  +  {sdi_label}: {fmt(r['ca_sdi'])})")
    print()
    big_box("TOTAL ALL TAXES:                  ", fmt(r["total_all_taxes"]))
    print()
    print(f"  Effective Tax Rate:               {pct(r['effective_rate']):>16}")
    print(f"  Federal Marginal Rate:            {pct(r['fed_marginal']):>16}")
    print(f"  California Marginal Rate:         {pct(r['ca_marginal']):>16}")

    # ── 11. Post-Tax Contributions ──
    section_header("POST-TAX CONTRIBUTIONS (informational)")
    print(f"  Non-deductible Traditional IRA:   {fmt(inputs['nondeduc_ira']):>16}")
    print(f"  After-tax 401(k):                 {fmt(inputs['after_tax_401k']):>16}")
    print(f"  Other:                            {fmt(inputs['other_posttax']):>16}")
    print(f"                                    {'-' * 16}")
    print(f"  Total Post-Tax Contributions:     {fmt(r['total_posttax']):>16}")

    # ── 12. Take-Home Pay ──
    print()
    print("=" * W)
    print("  TAKE-HOME PAY")
    print("=" * W)
    print(f"  Total Gross Income:               {fmt(r['total_gross']):>16}")
    print(f"  - Total All Taxes:                {fmt(r['total_all_taxes']):>16}")
    print(f"  - Pre-Tax Deductions:             {fmt(r['total_pretax_deductions']):>16}")
    print(f"  - Post-Tax Contributions:         {fmt(r['total_posttax']):>16}")
    print()
    big_box("TAKE-HOME PAY:                    ", fmt(r["take_home"]))
    print()


# ============================================================================
# ENTRY POINT
# ============================================================================


def main():
    try:
        inputs = collect_inputs()
        results = calculate_taxes(inputs)
        display_results(results)
    except KeyboardInterrupt:
        print("\n\nCalculation cancelled.")
    except EOFError:
        print("\n\nNo input available. Exiting.")


if __name__ == "__main__":
    main()
