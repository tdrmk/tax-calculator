"""
CLI display and input helper functions.
Formatting, input validation, and report output components.
"""

from constants import SINGLE, MFJ, MFS, HOH, CAPITAL_LOSS_LIMIT

W = 70  # report width

FILING_STATUS_LABELS = {
    SINGLE: "Single",
    MFJ: "Married Filing Jointly",
    MFS: "Married Filing Separately",
    HOH: "Head of Household",
}


def fmt(amount):
    """Format a number as currency: $1,234.56"""
    if amount < 0:
        return f"-${abs(amount):,.2f}"
    return f"${amount:,.2f}"


def pct(rate):
    """Format a decimal rate as percentage: 24.00%"""
    return f"{rate * 100:.2f}%"


def get_input(prompt, required=False, allow_negative=False):
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
            if value < 0 and not allow_negative:
                print("  ⚠  Negative values not allowed for this field.")
                continue
            return value
        except ValueError:
            print("  ⚠  Invalid input. Please enter a number.")


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
    for lower, upper, rate, amount, tax in details:
        if upper == float("inf"):
            bracket_label = f"{fmt(lower)}+"
        else:
            bracket_label = f"{fmt(lower)} - {fmt(upper)}"
        print(
            f"    {bracket_label:<30} {pct(rate):>7} {fmt(amount):>16} {fmt(tax):>14}"
        )


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
    st_cap_gains = get_input("  Short-term capital gains:       $", allow_negative=True)
    ordinary_dividends = get_input("  Ordinary (non-qualified) div:   $")
    interest_income = get_input("  Interest income:                $")
    other_income = get_input("  Other income:                   $")

    # --- Additional Income — Preferential ---
    print("\n  ADDITIONAL INCOME — Preferential (LTCG / Qualified Dividends)")
    print("  " + "-" * 40)
    print("  (Press Enter to skip any field, defaults to $0)\n")
    lt_cap_gains = get_input("  Long-term capital gains:        $", allow_negative=True)
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
    print("  is the lesser of the standard CA SDI or the VDI max contribution.")
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
        "interest_income": interest_income,
        "other_income": other_income,
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


def display_results(r, tax_data):
    """Display the full tax breakdown report."""
    inputs = r["inputs"]
    fs = r["filing_status"]

    # ── Extract tax data ──
    SS_RATE = tax_data.SS_RATE
    SS_WAGE_BASE = tax_data.SS_WAGE_BASE
    MEDICARE_RATE = tax_data.MEDICARE_RATE
    ADDITIONAL_MEDICARE_RATE = tax_data.ADDITIONAL_MEDICARE_RATE
    ADDITIONAL_MEDICARE_THRESHOLD = tax_data.ADDITIONAL_MEDICARE_THRESHOLD[fs]
    CA_SDI_RATE = tax_data.CA_SDI_RATE
    NIIT_RATE = tax_data.NIIT_RATE
    NIIT_THRESHOLD = tax_data.NIIT_THRESHOLD[fs]

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
    print(f"  Capital Gains / Losses:")
    print(f"    Short-term gains/losses:         {fmt(r['st_gains']):>16}")
    print(f"    Long-term gains/losses:          {fmt(r['lt_gains']):>16}")
    print(f"    Net capital gain/loss:           {fmt(r['net_capital']):>16}")

    if r["net_capital"] < 0:
        print(f"    Capital loss limit:              {fmt(-abs(r['capital_loss_applied'])):>16}")
        print(f"      (max {fmt(CAPITAL_LOSS_LIMIT[fs])} deductible per year)")
        if r["capital_loss_carryforward"] > 0:
            print(f"    Loss carryforward (future yrs):  {fmt(r['capital_loss_carryforward']):>16}")
    elif r["st_gains"] < 0 or r["lt_gains"] < 0:
        # Net is positive but one side had losses — show netting result
        if r["ordinary_cap_gains"] > 0:
            print(f"    → Net flows as ordinary:         {fmt(r['ordinary_cap_gains']):>16}")
        if r["preferential_cap_gains"] > 0:
            print(f"    → Net flows as preferential:     {fmt(r['preferential_cap_gains']):>16}")

    print()
    print(f"  Additional Ordinary Income:")
    print(f"    Capital gains (ordinary):        {fmt(r['ordinary_cap_gains'] + r['capital_loss_applied']):>16}")
    print(f"    Ordinary dividends:              {fmt(inputs['ordinary_dividends']):>16}")
    print(f"    Interest income:                 {fmt(inputs['interest_income']):>16}")
    print(f"    Other income:                    {fmt(inputs['other_income']):>16}")
    print(f"    Subtotal:                        {fmt(r['ordinary_additional']):>16}")
    print()
    print(f"  Additional Preferential Income:")
    print(f"    Capital gains (preferential):    {fmt(r['preferential_cap_gains']):>16}")
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
    print(f"  Federal Taxable Income:           {fmt(r['fed_ordinary_taxable'] + r['preferential_income']):>16}")
    print(f"    = Ordinary + Preferential")
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
            f"    Not applicable (AGI below {fmt(NIIT_THRESHOLD)} threshold)"
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
        print(
            f"\n  Additional Medicare "
            f"({pct(ADDITIONAL_MEDICARE_RATE)} on wages over {fmt(ADDITIONAL_MEDICARE_THRESHOLD)}):"
        )
        print(
            f"    Excess wages:  {fmt(r['total_fica_wages'] - ADDITIONAL_MEDICARE_THRESHOLD):>16}"
            f"   Tax: {fmt(r['addl_medicare_tax']):>14}"
        )
        print(f"\n  Total Medicare:                   {fmt(r['total_medicare']):>16}")
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
            print(f"      Applied (lesser of):               {fmt(r['s1_ca_sdi_or_vdi']):>14}")
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
            print(f"      Applied (lesser of):               {fmt(r['s2_ca_sdi_or_vdi']):>14}")
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
            print(f"      Applied (lesser of):               {fmt(r['ca_sdi']):>14}")
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
