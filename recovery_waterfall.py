"""
recovery_waterfall.py

Estimates recovery for each part of Petco's capital structure assuming
default occurs at the FY2029 covenant breach identified in
stress_test.py.

STRUCTURAL NOTE (the key difference from the MBS project's CMO waterfall):
The Term Loan B and Senior Secured Notes are PARI PASSU -- same first
lien, same collateral, equal ranking. That means they do NOT get paid
sequentially like the MBS CMO's A/B/Z tranches did. Instead, if there
isn't enough value to repay both in full, they share the shortfall
PRO RATA, in proportion to their outstanding principal. This is a
different (and equally important) waterfall mechanic to understand:
sequential subordination (MBS project) vs. pro-rata pari passu sharing
(here).

Methodology:
    1. Take the downside-case Adj. EBITDA in the year of covenant breach
       (FY2029, per stress_test.py: $255.0mm).
    2. Apply a range of DISTRESSED exit EV/EBITDA multiples (these are
       lower than a healthy-company multiple, reflecting a company
       already in distress -- illustrative, not sourced from a specific
       comparable transaction).
    3. Allocate that enterprise value by seniority:
       a. Secured debt (Term Loan B + Notes) FIRST, pro rata between them
          if there's a shortfall.
       b. Unsecured claims SECOND -- here approximated as a single pool
          combining trade payables and CAPPED lease rejection claims
          (bankruptcy code caps landlord rejection damages; the full
          $1.34bn lease PV would significantly overstate the allowed
          unsecured claim, so a smaller illustrative pool is used
          instead -- explicitly a simplification).
       c. Equity LAST, and only if (a) and (b) are covered in full.
"""

import pandas as pd
from capital_structure import CAPITAL_STRUCTURE, debt_schedule

DEFAULT_YEAR = 2029
DOWNSIDE_EBITDA_AT_DEFAULT = 255.0  # $mm, from stress_test.py FY2029 downside case
ESTIMATED_UNSECURED_CLAIMS_POOL = 400.0  # $mm, illustrative -- capped lease rejection claims + trade payables


def secured_balances_at_default(year: int = DEFAULT_YEAR) -> dict:
    """Outstanding principal on each secured tranche entering the default year."""
    schedule = debt_schedule(list(range(2026, year + 1)))
    row = schedule[schedule["year"] == year].iloc[0]
    return {"term_loan_b": row["tlb_balance"], "senior_secured_notes": row["notes_balance"]}


def recovery_at_multiple(ev_ebitda_multiple: float) -> dict:
    enterprise_value = DOWNSIDE_EBITDA_AT_DEFAULT * ev_ebitda_multiple

    secured = secured_balances_at_default()
    total_secured = secured["term_loan_b"] + secured["senior_secured_notes"]

    # Secured claims paid first, pro rata between TLB and Notes if short
    secured_recovery_value = min(enterprise_value, total_secured)
    secured_recovery_pct = secured_recovery_value / total_secured
    tlb_recovery = secured["term_loan_b"] * secured_recovery_pct
    notes_recovery = secured["senior_secured_notes"] * secured_recovery_pct

    remaining_value = max(enterprise_value - total_secured, 0.0)

    # Unsecured claims paid second
    unsecured_recovery_value = min(remaining_value, ESTIMATED_UNSECURED_CLAIMS_POOL)
    unsecured_recovery_pct = unsecured_recovery_value / ESTIMATED_UNSECURED_CLAIMS_POOL

    remaining_value = max(remaining_value - ESTIMATED_UNSECURED_CLAIMS_POOL, 0.0)

    # Equity gets whatever's left, if anything
    equity_recovery_value = remaining_value

    return {
        "ev_ebitda_multiple": ev_ebitda_multiple,
        "enterprise_value": enterprise_value,
        "tlb_recovery_pct": secured_recovery_pct,
        "tlb_recovery_value": tlb_recovery,
        "notes_recovery_pct": secured_recovery_pct,
        "notes_recovery_value": notes_recovery,
        "unsecured_recovery_pct": unsecured_recovery_pct,
        "unsecured_recovery_value": unsecured_recovery_value,
        "equity_recovery_value": equity_recovery_value,
    }


if __name__ == "__main__":
    secured = secured_balances_at_default()
    print(f"Outstanding secured debt entering FY{DEFAULT_YEAR}: "
          f"TLB ${secured['term_loan_b']:.1f}mm + Notes ${secured['senior_secured_notes']:.1f}mm "
          f"= ${secured['term_loan_b'] + secured['senior_secured_notes']:.1f}mm\n")
    print(f"Downside-case Adj. EBITDA at default: ${DOWNSIDE_EBITDA_AT_DEFAULT:.1f}mm")
    print(f"Estimated unsecured claims pool (illustrative): ${ESTIMATED_UNSECURED_CLAIMS_POOL:.1f}mm\n")

    multiples = [4.5, 5.5, 6.5, 7.5]
    rows = [recovery_at_multiple(m) for m in multiples]
    df = pd.DataFrame(rows)

    print(df.to_string(index=False, formatters={
        "ev_ebitda_multiple": "{:.1f}x".format,
        "enterprise_value": "${:.0f}mm".format,
        "tlb_recovery_pct": "{:.1%}".format,
        "tlb_recovery_value": "${:.0f}mm".format,
        "notes_recovery_pct": "{:.1%}".format,
        "notes_recovery_value": "${:.0f}mm".format,
        "unsecured_recovery_pct": "{:.1%}".format,
        "unsecured_recovery_value": "${:.0f}mm".format,
        "equity_recovery_value": "${:.0f}mm".format,
    }))