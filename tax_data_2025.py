"""
Tax data constants — 2025 Tax Year
All year-specific brackets, rates, deductions, and thresholds.
"""

from constants import SINGLE, MFJ, MFS, HOH

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

# --- 401(k) / 403(b) / 457(b) Elective Deferral Limits (2025) ---
ELECTIVE_DEFERRAL_LIMIT = 23_500       # IRC §402(g)
TOTAL_ANNUAL_ADDITION_LIMIT = 70_000   # IRC §415(c) — employee + employer combined

# --- NIIT (Net Investment Income Tax) ---
NIIT_RATE = 0.038
NIIT_THRESHOLD = {
    SINGLE: 200_000,
    MFJ: 250_000,
    MFS: 125_000,
    HOH: 200_000,
}
