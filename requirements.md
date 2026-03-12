# Tax Calculator — Requirements

## 1. Core Inputs

### 1.1 Filing Status
- Single
- Married Filing Jointly (MFJ)
- Married Filing Separately (MFS)
- Head of Household (HoH)

### 1.2 Gross Annual Income (Wages/Salary)
- For **MFJ**: Spouse 1 wages and Spouse 2 wages entered separately (required for per-spouse Social Security wage base)
- For all other statuses: a single gross wages/salary amount

---

## 2. Additional Income Inputs

Income from taxable brokerage accounts and savings, split into two tax buckets:

### 2.1 Ordinary Income Bucket (taxed at ordinary federal & CA rates)

| # | Income Type | Source |
|---|------------|--------|
| 1 | **Short-term capital gains/losses** | Assets held ≤ 1 year (negative values allowed) |
| 2 | **Ordinary (non-qualified) dividends** | Dividends not meeting qualified holding period |
| 3 | **Interest income** | Bond coupons, savings accounts, money market interest, etc. |
| 4 | **Other income** | Any other ordinary income not covered above |

### 2.2 Preferential Income Bucket (preferential federal rates; CA taxes as ordinary)

| # | Income Type | Source |
|---|------------|--------|
| 5 | **Long-term capital gains/losses** | Assets held > 1 year (negative values allowed) |
| 6 | **Qualified dividends** | Dividends meeting holding period requirements |

### 2.3 Capital Gains Netting (Schedule D)

When ST and/or LT capital gains are negative (losses), Schedule D netting applies:

1. **Net ST and LT separately**, then combine into a single net capital gain/loss
2. **Net gain** — determine character of the result:
   - Both positive: ST flows to ordinary income, LT flows to preferential income
   - ST loss absorbed by LT gain: net remainder flows as preferential
   - LT loss absorbed by ST gain: net remainder flows as ordinary
3. **Net loss** — capital loss deduction is capped per year (IRC §1211(b)):
   - **$3,000** for Single, MFJ, HoH
   - **$1,500** for MFS
   - Capped loss deducts against ordinary income
   - Excess carries forward to future tax years (tracked but informational only)

---

## 3. Pre-Tax Deductions (reduce AGI)

Pre-tax deductions are collected in **three categories**. For MFJ, each category is collected **per spouse**.

### 3.1 Categories

| # | Category | Typical Items | FICA Treatment |
|---|----------|---------------|----------------|
| 1 | **Retirement** | 401(k), 403(b), 457(b) | Reduces federal/state wages only — **still subject to FICA** |
| 2 | **Health** | Health insurance premiums, HSA, FSA, dental/vision, dependent care FSA | Reduces **all** wages including FICA (Section 125) |
| 3 | **Other** | Commuter/transit, group-term life insurance | Reduces **all** wages including FICA (Section 132(f) / Section 125) |

### 3.2 Per-Spouse Collection (MFJ)
- Spouse 1: Retirement, Health, Other
- Spouse 2: Retirement, Health, Other
- All other filing statuses: a single set of Retirement, Health, Other

---

## 4. Post-Tax Contributions (informational only — do NOT reduce AGI)

| # | Contribution | Notes |
|---|-------------|-------|
| 1 | **Non-deductible Traditional IRA** | Contributed with after-tax dollars; no deduction at higher income levels |
| 2 | **After-tax 401(k)** | Post-tax contributions (commonly used for mega backdoor Roth) |
| 3 | **Other post-tax contributions** | Any other after-tax contributions not covered above |

---

## 5. Deductions & AGI

### 5.1 Adjusted Gross Income (AGI)
- `AGI = gross income + all additional income − total pre-tax deductions`

### 5.2 Standard Deduction (only — no itemized deductions)
- **Federal** standard deduction — applied automatically based on filing status (2025 values)
- **California** standard deduction — applied automatically based on filing status (2025 values)

---

## 6. Taxable Wages (W-2 Perspective)

Different taxes apply to different "wage" definitions. These correspond to W-2 box values:

| Wage Type | W-2 Box | Formula | Notes |
|-----------|---------|---------|-------|
| **Federal Taxable Wages** | Box 1 | Gross wages − all pre-tax deductions | Retirement, Health, and Other all reduce this |
| **State Taxable Wages** | Box 16 | Same as federal | CA conforms to all federal exclusions |
| **Social Security Wages** | Box 3 | Gross wages − Health − Other | Only retirement stays in FICA wages |
| **Medicare Wages** | Box 5 | Gross wages − Health − Other | Same as SS wages |

- For MFJ, all wage types are calculated **per spouse** (each spouse has their own W-2)
- Values are clamped to $0 minimum

---

## 7. Federal Tax Calculation — Ordinary Income

### 7.1 Federal Ordinary Taxable Income
- `Federal ordinary taxable income = AGI − federal standard deduction − long-term capital gains − qualified dividends`

### 7.2 Federal Ordinary Tax Brackets (2025)
- Progressive brackets: **10%, 12%, 22%, 24%, 32%, 35%, 37%**

### 7.3 Federal Ordinary Tax Owed
- Calculated by applying the progressive brackets to federal ordinary taxable income

---

## 8. Federal Tax Calculation — Preferential Income

### 8.1 Long-Term Capital Gains / Qualified Dividends
- Taxed at preferential federal rates: **0%, 15%, 20%**
- LTCG brackets are **stacked on top of ordinary income** to determine the applicable rate

### 8.2 Net Investment Income Tax (NIIT)
- **3.8%** on net investment income (capital gains, dividends, interest, etc.)
- Applies when AGI exceeds:
  - $200,000 (Single)
  - $250,000 (Married Filing Jointly)
  - $125,000 (Married Filing Separately)
  - $200,000 (Head of Household)
- Tax base = lesser of: total investment income OR (AGI − threshold)

### 8.3 Federal Preferential Tax Owed
- Calculated by applying LTCG/qualified dividend brackets stacked on top of ordinary income, plus NIIT if applicable

---

## 9. California State Tax Calculation

### 9.1 California Taxable Income
- `CA taxable income = AGI − CA standard deduction`
- **California taxes ALL income as ordinary** — no special rates for long-term capital gains or qualified dividends

### 9.2 California Tax Brackets (2025)
- Progressive brackets: **1%, 2%, 4%, 6%, 8%, 9.3%, 10.3%, 11.3%, 12.3%, 13.3%**
- Includes CA Mental Health Services Tax (Prop 63): additional **1%** on taxable income over **$1,000,000** (all filing statuses), making the effective top rate **13.3%**

### 9.3 California Tax Owed
- Calculated by applying CA progressive brackets to CA taxable income

---

## 10. FICA Taxes

FICA taxes are calculated on **FICA wages** (Gross wages − Health − Other deductions), NOT gross wages. Only retirement deductions remain subject to FICA.

### 10.1 Social Security Tax
- **6.2%** on FICA wages up to the wage base limit (**$176,100** per person for 2025)
- Does NOT apply to investment income (only wages)
- **Calculated per spouse** for MFJ (each spouse has their own $176,100 cap)

### 10.2 Medicare Tax
- **1.45%** on all FICA wages (combined for MFJ)
- Does NOT apply to investment income (only wages)

### 10.3 Additional Medicare Tax
- **0.9%** on FICA wages exceeding:
  - $200,000 (Single)
  - $250,000 (Married Filing Jointly)
  - $125,000 (Married Filing Separately)
  - $200,000 (Head of Household)

---

## 11. CA SDI (State Disability Insurance)

### 11.1 CA SDI Tax
- **1.2%** on **all FICA wages** (no wage limit)
- Does NOT apply to investment income (only wages)
- Follows FICA wage treatment (Health and Other deductions reduce SDI wages)
- For MFJ, SDI is calculated **per spouse** on their individual FICA wages

### 11.2 CA VDI (Voluntary Disability Insurance)
- Some employers offer VDI plans as an alternative to standard CA SDI
- If enrolled, the disability insurance cost is the **lesser of**: standard SDI (rate × FICA wages) or the VDI plan's max annual contribution
- VDI enrollment and max contribution are collected **per spouse** for MFJ
- If not enrolled, standard SDI applies

---

## 12. Output / Summary

The calculator displays a detailed breakdown report with the following sections:

### 12.1 Income Section
- Filing status
- For MFJ: Spouse 1 wages, Spouse 2 wages, and combined wages
- For other statuses: gross wages/salary
- Capital gains / losses: ST gains/losses, LT gains/losses, net capital gain/loss
  - If net loss: capital loss limit applied, carryforward amount (if any)
  - If net gain with mixed signs: shows how net flows to ordinary vs. preferential
- Additional ordinary income breakdown (capital gains flowing as ordinary, ordinary dividends, interest income, other income, subtotal)
- Additional preferential income breakdown (capital gains flowing as preferential, qualified dividends, subtotal)
- **Total gross income** (highlighted)

### 12.2 Pre-Tax Deductions Section
- For MFJ: per-spouse breakdown with Retirement, Health, Other subtotals, then combined total
- For other statuses: Retirement, Health, Other, then total
- **Total pre-tax deductions**

### 12.3 Taxable Wages (W-2 Perspective)
- Federal Taxable Wages (Box 1) — per spouse for MFJ, then combined
- State Taxable Wages (Box 16) — same as federal (CA conforms)
- Social Security Wages (Box 3) — per spouse for MFJ, then combined
- Medicare Wages (Box 5) — per spouse for MFJ, then combined
- Note explaining the distinction between Fed/State wages and FICA wages

### 12.4 Adjusted Gross Income
- **AGI** = total gross income − total pre-tax deductions (highlighted)

### 12.5 Standard Deductions
- Federal standard deduction (based on filing status)
- California standard deduction (based on filing status)

### 12.6 Taxable Income
- Federal ordinary taxable income (with formula)
- Federal preferential income (with formula)
- Federal taxable income (ordinary + preferential combined)
- California taxable income (with formula)

### 12.7 Federal Tax Breakdown
- Federal ordinary tax (per-bracket breakdown showing amount taxed in each bracket)
- Federal LTCG / qualified dividend tax (per-bracket breakdown with stacking)
- NIIT (if applicable, showing base and rate; or "not applicable" with threshold)
- **Total federal tax** (highlighted)

### 12.8 California Tax Breakdown
- California income tax (per-bracket breakdown showing amount taxed in each bracket)
- **Total California tax** (highlighted)

### 12.9 Payroll Tax Breakdown
- Social Security tax — for MFJ: per-spouse FICA wages (capped), per-spouse tax, combined tax
- Medicare tax — FICA wages and tax
- Additional Medicare tax (if applicable) — excess wages and tax
- CA SDI / VDI tax — if VDI enrolled, shows standard SDI, VDI max, and applied (lesser of); per-spouse for MFJ
- Total FICA + CA SDI/VDI
- **Total payroll taxes** (highlighted)

### 12.10 Tax Summary
- Total federal tax
- Total California tax
- Total payroll taxes (FICA + CA SDI)
- **Total all taxes** (double-highlighted)
- **Effective tax rate** (total all taxes ÷ AGI)
- **Marginal tax rate — federal ordinary**
- **Marginal tax rate — California**

### 12.11 Post-Tax Contributions Section (informational)
- Non-deductible Traditional IRA contributions
- After-tax 401(k) contributions
- Other post-tax contributions
- **Total post-tax contributions**

### 12.12 Take-Home Pay
- **Take-home pay** = total gross income − all taxes − pre-tax deductions − post-tax contributions (double-highlighted)

---

## 13. UX / Usability

### 13.1 Interactive CLI Prompts
- Guide the user step-by-step through all inputs
- Group prompts logically (filing status → income → additional income → deductions → contributions)

### 13.2 Input Validation
- Handle non-numeric entries gracefully with clear error messages
- Reject negative numbers (except short-term and long-term capital gains, which allow losses)
- Allow `0` or empty input for optional fields (default to $0)
- Wages are required fields

### 13.3 Currency Formatting
- Display all dollar amounts with `$` sign and comma separators (e.g., `$52,300.00`)
- Show percentages to two decimal places (e.g., `24.35%`)
