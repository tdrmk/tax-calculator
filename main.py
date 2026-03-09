#!/usr/bin/env python3
"""
Tax Calculator — 2025 Tax Year
Federal + California + FICA + CA SDI

Calculates taxes based on wages, investment income, pre-tax deductions,
and post-tax contributions for all filing statuses.
"""

from prompts import collect_inputs, display_results
from calculator import calculate_taxes
from plot_sankey import generate_sankey
import tax_data_2025 as tax_data


# ============================================================================
# ENTRY POINT
# ============================================================================


def main():
    try:
        inputs = collect_inputs()
        results = calculate_taxes(inputs, tax_data)
        display_results(results, tax_data)
        generate_sankey(results)
    except KeyboardInterrupt:
        print("\n\nCalculation cancelled.")
    except EOFError:
        print("\n\nNo input available. Exiting.")


if __name__ == "__main__":
    main()
