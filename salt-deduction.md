# SALT Deduction (State and Local Tax)

How the SALT deduction works for the **2025 tax year**, including changes under the One Big Beautiful Bill Act (OBBBA).

---

## What Is SALT?

SALT stands for **State and Local Taxes**. It allows you to deduct certain taxes paid to state or local governments from your **federal** taxable income — but only if you **itemize** deductions instead of taking the standard deduction.

### Eligible Taxes

| Tax Type | Examples |
|---|---|
| **State & local income tax** | California income tax, New York state tax, etc. |
| **State & local sales tax** | Alternative to income tax — pick whichever is larger |
| **Property tax** | Real estate taxes on your home |
| **Personal property tax** | Vehicle registration taxes (in some states) |

> **Choose one:** You can deduct either state/local **income tax** or **sales tax**, not both.

---

## 2025 SALT Cap — OBBBA Changes

The SALT deduction has a **cap** — a maximum amount you can deduct regardless of how much you actually paid.

### Cap Amounts

| Filing Status | SALT Cap | Phase-out Threshold |
|---|---|---|
| Single | $40,000 | $500,000 MAGI |
| Married Filing Jointly | $40,000 | $500,000 MAGI |
| Married Filing Separately | $20,000 | $250,000 MAGI |
| Head of Household | $40,000 | $500,000 MAGI |

This is a significant increase from the **$10,000 cap** that was in place from 2018–2024 under the TCJA.

### Income Phase-Out

The $40,000 cap is reduced for higher earners:

1. If your **MAGI** (Modified Adjusted Gross Income) exceeds the threshold, the cap shrinks
2. **Reduction** = 30% × (MAGI − threshold)
3. **Floor** = $10,000 ($5,000 MFS) — the cap cannot go below this

> **Effective Cap** = max($40,000 − 30% × excess, $10,000)

### Phase-Out Example (MFJ)

| MAGI | Excess Over $500K | 30% Reduction | Effective Cap |
|---|---|---|---|
| $450,000 | $0 | $0 | **$40,000** |
| $500,000 | $0 | $0 | **$40,000** |
| $550,000 | $50,000 | $15,000 | **$25,000** |
| $600,000 | $100,000 | $30,000 | **$10,000** (floor) |
| $700,000 | $200,000 | $60,000 | **$10,000** (floor) |

At ~$600,000 MAGI (MFJ), the cap effectively reverts to the old $10,000 limit.

---

## Standard vs. Itemized — How the Choice Works

You get **one federal deduction** — either the standard deduction or itemized deductions, whichever benefits you more:

| Deduction Type | 2025 Amount (MFJ) | What's Included |
|---|---|---|
| **Standard** | $31,500 | Flat amount, no receipts needed |
| **Itemized** | Varies | SALT + mortgage interest + charitable + medical (if applicable) |

> **Use whichever is larger.** Most filers take the standard deduction.

### When Does SALT Make Itemizing Worth It?

For itemizing to beat the standard deduction, your **total itemized deductions** must exceed the standard deduction. With only SALT (no mortgage, charitable, etc.):

- **Single/MFS:** SALT alone must exceed $15,750 — possible with high state taxes
- **MFJ:** SALT alone must exceed $31,500 — very unlikely with only state income tax; typically needs property tax + state tax combined

In practice, SALT alone rarely exceeds the MFJ standard deduction. It usually takes SALT **plus** mortgage interest and/or charitable contributions to make itemizing worthwhile.

---

## What This Calculator Currently Handles

| Feature | Status |
|---|---|
| SALT from CA state income tax | ✅ Implemented |
| SALT cap ($40K with phase-out) | ✅ Implemented |
| Standard vs. itemized comparison | ✅ Implemented |
| Property tax as SALT | ❌ Not yet (could add as input) |
| Mortgage interest deduction | ❌ Not yet |
| Charitable contributions | ❌ Not yet |
| Medical expense deduction | ❌ Not yet |

Currently, the calculator computes your CA income tax, applies the SALT cap (with phase-out if applicable), and compares the resulting itemized deduction against the standard deduction. It automatically uses whichever is larger.

---

## How It Fits in the Tax Calculation Flow

```
Total Income
  − Pre-tax deductions (401k, HSA, etc.)
  = AGI

AGI
  − CA standard deduction
  = CA taxable income → CA tax (this becomes your SALT amount)

SALT amount
  → Apply $40K cap (with phase-out if MAGI > $500K)
  = Capped SALT

Compare:
  Standard deduction ($31,500 MFJ)  vs.  Itemized (capped SALT)
  → Use the LARGER one

AGI
  − Chosen federal deduction (standard or itemized)
  − Preferential income (LTCG + qualified dividends)
  = Federal ordinary taxable income → Federal tax
```

---

## Timeline

| Period | SALT Cap |
|---|---|
| Before 2018 | No cap (fully deductible) |
| 2018–2024 | $10,000 ($5,000 MFS) — TCJA |
| **2025–2029** | **$40,000 ($20,000 MFS) — OBBBA** |
| 2030+ | Reverts to $10,000 unless Congress acts |

---

## Key Takeaways

1. **SALT only matters if you itemize** — and only for federal taxes (CA ignores it)
2. **The $40K cap is a big improvement** over $10K, but still limits high-tax-state filers
3. **Phase-out penalizes high earners** — above ~$600K MAGI (MFJ), you're back to the old $10K cap
4. **SALT alone rarely beats the MFJ standard deduction** — you typically need property tax and/or other itemized deductions to make it worthwhile
5. **This is temporary** — the $40K cap expires after 2029
