#!/usr/bin/env python3
"""
Runner script — feeds predefined inputs into the tax calculator.
Edit the values below, then run: python3 run.py
"""

import os
import pty
import select
import sys
import time

# ============================================================================
# EDIT YOUR INPUTS HERE
# ============================================================================

# Set to 0 for instant mode, or e.g. 0.5 for half-second delay between inputs
DELAY_SECONDS = 0

# Filing status: "1" = Single, "2" = MFJ, "3" = MFS, "4" = HoH
FILING_STATUS = "2"

# Wages/Salary
# For MFJ: set both spouse wages; for all others only SPOUSE_1_WAGES is used
SPOUSE_1_WAGES = "200000"
SPOUSE_2_WAGES = "0"  # only used when FILING_STATUS = "2" (MFJ)

# Additional Income — Ordinary (taxed at ordinary rates)
SHORT_TERM_CAP_GAINS = "5000"
ORDINARY_DIVIDENDS = "1000"
BOND_INTEREST = "500"
SAVINGS_INTEREST = "2000"

# Additional Income — Preferential (LTCG / Qualified Dividends)
LONG_TERM_CAP_GAINS = "10000"
QUALIFIED_DIVIDENDS = "3000"

# Pre-Tax Deductions — Spouse 1 (used for all filing statuses)
# Retirement: 401k, 403b, 457b, etc.
# Health: premiums, HSA, FSA, dental/vision, dependent care FSA
# Other: commuter/transit, life insurance, etc.
S1_RETIREMENT = "23500"
S1_HEALTH = "4500"
S1_OTHER = "0"

# Pre-Tax Deductions — Spouse 2 (only used when FILING_STATUS = "2" / MFJ)
S2_RETIREMENT = "23500"
S2_HEALTH = "2500"
S2_OTHER = "0"

# CA VDI (Voluntary Disability Insurance)
# Set to "y" if enrolled, "n" if not. If "y", set the max annual contribution.
S1_VDI_ENROLLED = "n"  # "y" or "n"
S1_VDI_MAX = "0"       # only used if S1_VDI_ENROLLED = "y"
S2_VDI_ENROLLED = "n"  # "y" or "n" (only used for MFJ)
S2_VDI_MAX = "0"       # only used if S2_VDI_ENROLLED = "y"

# Post-Tax Contributions (informational only)
NONDEDUCTIBLE_IRA = "7000"
AFTER_TAX_401K = "15000"
OTHER_POSTTAX = "0"

# ============================================================================
# BUILD INPUT SEQUENCE & RUN
# ============================================================================

if FILING_STATUS == "2":
    # MFJ: filing status, spouse1 wages, spouse2 wages, then the rest
    inputs = [
        FILING_STATUS,
        SPOUSE_1_WAGES,
        SPOUSE_2_WAGES,
    ]
else:
    # Single / MFS / HoH: filing status, wages, then the rest
    inputs = [
        FILING_STATUS,
        SPOUSE_1_WAGES,
    ]

# Additional income (same order for all filing statuses)
inputs += [
    SHORT_TERM_CAP_GAINS,
    ORDINARY_DIVIDENDS,
    BOND_INTEREST,
    SAVINGS_INTEREST,
    LONG_TERM_CAP_GAINS,
    QUALIFIED_DIVIDENDS,
]

# Pre-tax deductions (per-spouse for MFJ)
if FILING_STATUS == "2":
    inputs += [
        S1_RETIREMENT,
        S1_HEALTH,
        S1_OTHER,
        S2_RETIREMENT,
        S2_HEALTH,
        S2_OTHER,
    ]
else:
    inputs += [
        S1_RETIREMENT,
        S1_HEALTH,
        S1_OTHER,
    ]

# CA VDI (per-spouse for MFJ)
if FILING_STATUS == "2":
    inputs.append(S1_VDI_ENROLLED)
    if S1_VDI_ENROLLED.lower() in ("y", "yes"):
        inputs.append(S1_VDI_MAX)
    inputs.append(S2_VDI_ENROLLED)
    if S2_VDI_ENROLLED.lower() in ("y", "yes"):
        inputs.append(S2_VDI_MAX)
else:
    inputs.append(S1_VDI_ENROLLED)
    if S1_VDI_ENROLLED.lower() in ("y", "yes"):
        inputs.append(S1_VDI_MAX)

# Post-tax contributions
inputs += [
    NONDEDUCTIBLE_IRA,
    AFTER_TAX_401K,
    OTHER_POSTTAX,
]

# Run main.py inside a pseudo-terminal so input is echoed automatically
master_fd, slave_fd = pty.openpty()

pid = os.fork()
if pid == 0:
    # Child process: run main.py with the pty as its terminal
    os.close(master_fd)
    os.setsid()
    os.dup2(slave_fd, 0)  # stdin
    os.dup2(slave_fd, 1)  # stdout
    os.dup2(slave_fd, 2)  # stderr
    if slave_fd > 2:
        os.close(slave_fd)
    os.execvp(sys.executable, [sys.executable, "-u", "main.py"])
else:
    # Parent process: feed inputs and read output
    os.close(slave_fd)
    input_idx = 0

    try:
        while True:
            # Wait for output or until we can write
            rlist, _, _ = select.select([master_fd], [], [], 0.1)

            if rlist:
                try:
                    data = os.read(master_fd, 4096)
                except OSError:
                    break
                if not data:
                    break
                sys.stdout.write(data.decode("utf-8", errors="replace"))
                sys.stdout.flush()

            # Send next input when the child is waiting (after a small delay)
            if input_idx < len(inputs):
                # Check if there's more output pending before sending input
                rcheck, _, _ = select.select([master_fd], [], [], DELAY_SECONDS if DELAY_SECONDS > 0 else 0.05)
                if rcheck:
                    try:
                        data = os.read(master_fd, 4096)
                    except OSError:
                        break
                    if data:
                        sys.stdout.write(data.decode("utf-8", errors="replace"))
                        sys.stdout.flush()

                os.write(master_fd, (inputs[input_idx] + "\n").encode())
                input_idx += 1
    except OSError:
        pass

    # Drain any remaining output
    while True:
        rlist, _, _ = select.select([master_fd], [], [], 0.1)
        if not rlist:
            break
        try:
            data = os.read(master_fd, 4096)
        except OSError:
            break
        if not data:
            break
        sys.stdout.write(data.decode("utf-8", errors="replace"))
        sys.stdout.flush()

    os.close(master_fd)
    _, status = os.waitpid(pid, 0)
    sys.exit(os.WEXITSTATUS(status))
