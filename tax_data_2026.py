"""
Tax data constants — 2026 Tax Year
All year-specific brackets, rates, deductions, and thresholds.

NOTE: Many values below are carried forward from 2025 as placeholders.
      Official 2026 IRS and CA FTB figures should be verified and updated
      when published. Items marked "# TODO: verify" need confirmation.
"""

from constants import SINGLE, MFJ, MFS, HOH

# --- Federal Ordinary Income Tax Brackets (2026) ---
# Format: list of (upper_limit, rate) — progressive/marginal brackets
FEDERAL_BRACKETS = {
    SINGLE: [
        (12_400, 0.10),
        (50_400, 0.12),
        (105_700, 0.22),
        (201_775, 0.24),
        (256_225, 0.32),
        (640_600, 0.35),
        (float("inf"), 0.37),
    ],
    MFJ: [
        (24_800, 0.10),
        (100_800, 0.12),
        (211_400, 0.22),
        (403_550, 0.24),
        (512_450, 0.32),
        (768_700, 0.35),
        (float("inf"), 0.37),
    ],
    MFS: [
        (12_400, 0.10),
        (50_400, 0.12),
        (105_700, 0.22),
        (201_775, 0.24),
        (256_225, 0.32),
        (384_350, 0.35),
        (float("inf"), 0.37),
    ],
    HOH: [
        (17_700, 0.10),
        (67_450, 0.12),
        (105_700, 0.22),
        (201_775, 0.24),
        (256_200, 0.32),
        (640_600, 0.35),
        (float("inf"), 0.37),
    ],
}

# --- Federal Long-Term Capital Gains / Qualified Dividends Brackets (2026) ---
# Source: IRS Revenue Procedure 2025-32
FEDERAL_LTCG_BRACKETS = {
    SINGLE: [
        (49_450, 0.00),
        (545_500, 0.15),
        (float("inf"), 0.20),
    ],
    MFJ: [
        (98_900, 0.00),
        (613_700, 0.15),
        (float("inf"), 0.20),
    ],
    MFS: [
        (49_450, 0.00),
        (306_850, 0.15),
        (float("inf"), 0.20),
    ],
    HOH: [
        (66_200, 0.00),
        (579_600, 0.15),
        (float("inf"), 0.20),
    ],
}

# --- Federal Standard Deduction (2026) ---
FEDERAL_STANDARD_DEDUCTION = {
    SINGLE: 16_100,
    MFJ: 32_200,
    MFS: 16_100,
    HOH: 24_150,
}

# --- California Income Tax Brackets (2026) ---
# Single and MFS use the same brackets (Schedule X)
# MFJ uses Schedule Y, HOH uses Schedule Z (each has unique thresholds)
# TODO: approximate — 3% CCPI increase applied to 2025 values; update when CA FTB publishes actual 2026 figures
CA_BRACKETS = {
    SINGLE: [
        (11_411, 0.01),
        (27_052, 0.02),
        (42_696, 0.04),
        (59_268, 0.06),
        (74_906, 0.08),
        (382_623, 0.093),
        (459_144, 0.103),
        (765_242, 0.113),
        (float("inf"), 0.123),
    ],
    MFJ: [
        (22_823, 0.01),
        (54_104, 0.02),
        (85_391, 0.04),
        (118_537, 0.06),
        (149_811, 0.08),
        (765_247, 0.093),
        (918_288, 0.103),
        (1_530_483, 0.113),
        (float("inf"), 0.123),
    ],
    MFS: [
        (11_411, 0.01),
        (27_052, 0.02),
        (42_696, 0.04),
        (59_268, 0.06),
        (74_906, 0.08),
        (382_623, 0.093),
        (459_144, 0.103),
        (765_242, 0.113),
        (float("inf"), 0.123),
    ],
    HOH: [
        (22_838, 0.01),
        (54_106, 0.02),
        (69_747, 0.04),
        (86_319, 0.06),
        (101_960, 0.08),
        (520_364, 0.093),
        (624_439, 0.103),
        (1_040_729, 0.113),
        (float("inf"), 0.123),
    ],
}

# --- California Standard Deduction (2026) ---
# TODO: approximate — 3% CCPI increase applied to 2025 values; update when CA FTB publishes actual 2026 figures
CA_STANDARD_DEDUCTION = {
    SINGLE: 5_877,
    MFJ: 11_754,
    MFS: 5_877,
    HOH: 11_754,
}

# --- FICA (2026) ---
SS_RATE = 0.062
SS_WAGE_BASE = 184_500 
MEDICARE_RATE = 0.0145
ADDITIONAL_MEDICARE_RATE = 0.009
ADDITIONAL_MEDICARE_THRESHOLD = {  # Statutory — NOT indexed for inflation
    SINGLE: 200_000,
    MFJ: 250_000,
    MFS: 125_000,
    HOH: 200_000,
}

# --- CA SDI (2026) — no wage limit (SB 951, uncapped since 2024) ---
CA_SDI_RATE = 0.013  # 1.3% for 2026 (up from 1.2% in 2025)

# --- 401(k) / 403(b) / 457(b) Elective Deferral Limits (2026) ---
ELECTIVE_DEFERRAL_LIMIT = 24_500       # IRC §402(g)
TOTAL_ANNUAL_ADDITION_LIMIT = 72_000   # IRC §415(c) — employee + employer combined

# --- NIIT (Net Investment Income Tax) — Statutory, NOT indexed for inflation ---
NIIT_RATE = 0.038
NIIT_THRESHOLD = {
    SINGLE: 200_000,
    MFJ: 250_000,
    MFS: 125_000,
    HOH: 200_000,
}
