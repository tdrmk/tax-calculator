"""
Tax data constants — 2024 Tax Year
All year-specific brackets, rates, deductions, and thresholds.
"""

from constants import SINGLE, MFJ, MFS, HOH

TAX_YEAR = 2024

# --- Federal Ordinary Income Tax Brackets (2024) ---
# Format: list of (upper_limit, rate) — progressive/marginal brackets
FEDERAL_BRACKETS = {
    SINGLE: [
        (11_600, 0.10),
        (47_150, 0.12),
        (100_525, 0.22),
        (191_950, 0.24),
        (243_725, 0.32),
        (609_350, 0.35),
        (float("inf"), 0.37),
    ],
    MFJ: [
        (23_200, 0.10),
        (94_300, 0.12),
        (201_050, 0.22),
        (383_900, 0.24),
        (487_450, 0.32),
        (731_200, 0.35),
        (float("inf"), 0.37),
    ],
    MFS: [
        (11_600, 0.10),
        (47_150, 0.12),
        (100_525, 0.22),
        (191_950, 0.24),
        (243_725, 0.32),
        (365_600, 0.35),
        (float("inf"), 0.37),
    ],
    HOH: [
        (16_550, 0.10),
        (63_100, 0.12),
        (100_500, 0.22),
        (191_950, 0.24),
        (243_700, 0.32),
        (609_350, 0.35),
        (float("inf"), 0.37),
    ],
}

# --- Federal Long-Term Capital Gains / Qualified Dividends Brackets (2024) ---
FEDERAL_LTCG_BRACKETS = {
    SINGLE: [
        (47_025, 0.00),
        (518_900, 0.15),
        (float("inf"), 0.20),
    ],
    MFJ: [
        (94_050, 0.00),
        (583_750, 0.15),
        (float("inf"), 0.20),
    ],
    MFS: [
        (47_025, 0.00),
        (291_850, 0.15),
        (float("inf"), 0.20),
    ],
    HOH: [
        (63_000, 0.00),
        (551_350, 0.15),
        (float("inf"), 0.20),
    ],
}

# --- Federal Standard Deduction (2024) ---
FEDERAL_STANDARD_DEDUCTION = {
    SINGLE: 14_600,
    MFJ: 29_200,
    MFS: 14_600,
    HOH: 21_900,
}

# --- California Income Tax Brackets (2024) ---
# Single and MFS use the same brackets (Schedule X)
# MFJ uses Schedule Y, HOH uses Schedule Z (each has unique thresholds)
# Includes 1% Mental Health Services Tax (Prop 63) on taxable income > $1M (all statuses)
CA_BRACKETS = {
    SINGLE: [
        (10_756, 0.01),
        (25_499, 0.02),
        (40_245, 0.04),
        (55_866, 0.06),
        (70_606, 0.08),
        (360_659, 0.093),
        (432_787, 0.103),
        (721_314, 0.113),
        (1_000_000, 0.123),
        (float("inf"), 0.133),
    ],
    MFJ: [
        (21_512, 0.01),
        (50_998, 0.02),
        (80_490, 0.04),
        (111_732, 0.06),
        (141_212, 0.08),
        (721_318, 0.093),
        (865_574, 0.103),
        (1_000_000, 0.113),
        (1_442_628, 0.123),
        (float("inf"), 0.133),
    ],
    MFS: [
        (10_756, 0.01),
        (25_499, 0.02),
        (40_245, 0.04),
        (55_866, 0.06),
        (70_606, 0.08),
        (360_659, 0.093),
        (432_787, 0.103),
        (721_314, 0.113),
        (1_000_000, 0.123),
        (float("inf"), 0.133),
    ],
    HOH: [
        (21_527, 0.01),
        (51_000, 0.02),
        (65_744, 0.04),
        (81_364, 0.06),
        (96_107, 0.08),
        (490_493, 0.093),
        (588_593, 0.103),
        (980_987, 0.113),
        (1_000_000, 0.123),
        (float("inf"), 0.133),
    ],
}

# --- California Standard Deduction (2024) ---
CA_STANDARD_DEDUCTION = {
    SINGLE: 5_540,
    MFJ: 11_080,
    MFS: 5_540,
    HOH: 11_080,
}

# --- FICA (2024) ---
SS_RATE = 0.062
SS_WAGE_BASE = 168_600
MEDICARE_RATE = 0.0145
ADDITIONAL_MEDICARE_RATE = 0.009
ADDITIONAL_MEDICARE_THRESHOLD = {
    SINGLE: 200_000,
    MFJ: 250_000,
    MFS: 125_000,
    HOH: 200_000,
}

# --- CA SDI (2024) — no wage limit (cap removed 1/1/2024) ---
CA_SDI_RATE = 0.011

# --- 401(k) / 403(b) / 457(b) Elective Deferral Limits (2024) ---
ELECTIVE_DEFERRAL_LIMIT = 23_000      # IRC §402(g)
TOTAL_ANNUAL_ADDITION_LIMIT = 69_000  # IRC §415(c) — employee + employer combined

# --- NIIT (Net Investment Income Tax) ---
NIIT_RATE = 0.038
NIIT_THRESHOLD = {
    SINGLE: 200_000,
    MFJ: 250_000,
    MFS: 125_000,
    HOH: 200_000,
}

# --- SALT (State and Local Tax) Deduction Limits (2024, TCJA flat cap) ---
# TCJA §11042 imposed a flat $10K cap ($5K MFS) on the combined SALT deduction
# for tax years 2018–2025. No income-based phase-out existed until the 2025 OBBBA.
# Set phase-out fields to None so calculator.py skips phase-out logic for this year.
SALT_CAP = {
    SINGLE: 10_000,
    MFJ: 10_000,
    MFS: 5_000,
    HOH: 10_000,
}
SALT_PHASEOUT_THRESHOLD = None  # no phase-out pre-2025
SALT_PHASEOUT_RATE = None
SALT_FLOOR = None
