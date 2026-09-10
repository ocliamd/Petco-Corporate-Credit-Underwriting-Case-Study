"""
recovery_waterfall.py

Estimates recovery for each part of Petco's capital structure assuming
default occurs at the FY2029 illustrative stress point identified in
stress_test.py (where gross secured leverage first exceeds this
analyst's illustrative 5.5x internal warning threshold -- NOT Petco's
actual covenant level, and not a claim that Petco would actually default
in FY2029).

STRUCTURAL NOTE -- CORRECTED FROM AN EARLIER DRAFT: this project
originally described the Term Loan B and Senior Secured Notes as simple
pari passu across all collateral. That's an oversimplification. Per
Petco's actual notes pricing press release, the Notes carry a SPLIT
LIEN: first-priority on fixed assets, second-priority on current assets
(subject to the company's ABL-style priority structure) -- likely the
mirror image of how the Term Loan B is secured. That means the two
tranches don't necessarily share every dollar of recovery pro rata; the
actual split would depend on how enterprise value breaks down between
fixed-asset value (real estate, fixtures) and current-asset value
(inventory, receivables) in a real distress scenario.

SIMPLIFICATION USED HERE: this model still allocates value pro rata
between the two secured tranches, because modeling the fixed/current
asset split explicitly would require asset-level detail (e.g., a
liquidation appraisal of owned real estate and fixtures vs. inventory
value) that isn't sourced for this case study. This is a real
limitation, not a rounding error -- a reader should not take the
tranche-level recovery split below as a precise estimate of how Petco's
actual split-lien structure would resolve.

WHAT THIS WATERFALL DOES NOT INCLUDE: a real Chapter 11 or out-of-court
restructuring would also involve DIP (debtor-in-possession) financing
that typically primes existing claims, administrative claims (which are
paid ahead of nearly everything), professional fees (legal, financial
advisory -- often tens of millions in a case this size), transaction
costs, and tax consequences of the reorganization. None of these are
modeled here. Real recoveries would likely be lower across the board
than what's shown below once these priority claims and costs are
layered in.

Methodology:
    1. Take the downside-case Adj. EBITDA at the FY2029 illustrative
       stress point (per stress_test.py: $255.0mm).
    2. Apply a range of DISTRESSED exit EV/EBITDA multiples (these are
       lower than a healthy-company multiple, reflecting a company
       already in distress -- illustrative, not sourced from a specific
       comparable transaction).
    3. Allocate that enterprise value by seniority:
       a. Secured debt (Term Loan B + Notes) FIRST, pro rata between them
          as a simplification (see structural note above).
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

STRESS_POINT_YEAR = 2029  # illustrative stress point, not a default date
DOWNSIDE_EBITDA_AT_STRESS_POINT = 255.0  # $mm, from stress_test.py FY2029 downside case
ESTIMATED_UNSECURED_CLAIMS_POOL = 400.0  # $mm, illustrative -- capped lease rejection claims + trade payables


def secured_balances_at_stress_point(year: int = STRESS_POINT_YEAR) -> dict:
    """Outstanding principal on each secured tranche entering the stress-point year."""
    schedule = debt_schedule(list(range(2026, year + 1)))
    row = schedule[schedule["year"] == year].iloc[0]
    return {"term_loan_b": row["tlb_balance"], "senior_secured_notes": row["notes_balance"]}


def recovery_at_multiple(ev_ebitda_multiple: float) -> dict:
    enterprise_value = DOWNSIDE_EBITDA_AT_STRESS_POINT * ev_ebitda_multiple

    secured = secured_balances_at_stress_point()
    total_secured = secured["term_loan_b"] + secured["senior_secured_notes"]

    # Secured claims paid first; PRO RATA SIMPLIFICATION between TLB and
    # Notes -- see structural note above on the actual split-lien structure
    # this simplifies away.
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
    secured = secured_balances_at_stress_point()
    print(f"Outstanding secured debt entering FY{STRESS_POINT_YEAR}: "
          f"TLB ${secured['term_loan_b']:.1f}mm + Notes ${secured['senior_secured_notes']:.1f}mm "
          f"= ${secured['term_loan_b'] + secured['senior_secured_notes']:.1f}mm\n")
    print(f"Downside-case Adj. EBITDA at illustrative stress point: ${DOWNSIDE_EBITDA_AT_STRESS_POINT:.1f}mm")
    print(f"Estimated unsecured claims pool (illustrative): ${ESTIMATED_UNSECURED_CLAIMS_POOL:.1f}mm")
    print("NOTE: excludes DIP financing, administrative claims, professional fees,")
    print("transaction costs, and taxes -- real recoveries would likely be lower.\n")

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
