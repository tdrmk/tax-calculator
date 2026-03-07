# Filing status constants
SINGLE = "single"
MFJ = "married_filing_jointly"
MFS = "married_filing_separately"
HOH = "head_of_household"

# Capital loss deduction limit (IRC §1211(b)) — not indexed for inflation.
# Net capital losses can offset up to this amount of ordinary income per year.
# Excess carries forward indefinitely.
CAPITAL_LOSS_LIMIT = {
    SINGLE: 3_000,
    MFJ: 3_000,
    MFS: 1_500,
    HOH: 3_000,
}
