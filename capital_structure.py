"""
capital_structure.py

Petco's ACTUAL capital structure following its February 2, 2026
refinancing, which extended the maturity wall from 2028 to 2031.
Sourced from Petco's Q1 FY2026 10-Q disclosures and the refinancing
press releases (Jan-Feb 2026).

LIEN STRUCTURE (corrected from an earlier draft of this project that
oversimplified this as plain pari passu -- worth getting right, since
it changes how a real recovery would work):

Per Petco's notes pricing press release (January 22, 2026), the new
Senior Secured Notes are secured on a SPLIT-LIEN basis: first-priority
lien on fixed assets, second-priority lien on current assets (subject
to the company's ABL-style priority structure). This is NOT the same
as being pari passu with the Term Loan B across all collateral -- the
two tranches likely have first-priority claims on DIFFERENT pools of
collateral (a common structure sometimes called "crossing liens"),
meaning actual recovery could differ meaningfully between them
depending on how enterprise value splits between fixed and current
assets in a distress scenario.

This project's recovery_waterfall.py SIMPLIFIES this by treating the
two tranches as sharing enterprise value pro rata rather than modeling
the fixed-asset/current-asset split explicitly -- that simplification
is called out again there. A full analysis would require asset-level
detail (real estate/fixtures value vs. inventory/receivables value)
that isn't being sourced for this case study.

Structure:

    1. Amended First Lien Term Loan ("Term Loan B")
       - Principal: $900.0 million
       - Rate: SOFR + 4.25% (floating)
       - Amortization: 1% per year (mandatory), quarterly
       - Maturity: February 2031 (5-year tenor from the Feb 2026 refi)

    2. Senior Secured Notes due 2031
       - Principal: $600.0 million
       - Rate: 8.250% (fixed)
       - No mandatory amortization (bullet at maturity, typical of notes)
       - Maturity: 2031
       - First-priority lien on fixed assets, second-priority lien on
         current assets

    Combined secured debt: $1.5 billion (matches Petco's reported total
    secured debt figure).

    3. Operating lease liabilities (present value): ~$1.34 billion
       Not funded debt, but a real fixed obligation ahead of unsecured
       creditors in a bankruptcy (landlords get paid or the store
       closes) -- material for a retailer and worth carrying as
       "lease-adjusted" leverage alongside the funded-debt view.

A SOFR assumption is needed to project the Term Loan B's floating cash
interest; this model uses a static 4.3% SOFR assumption (roughly in
line with the observed short-end SOFR environment as of this analysis)
-- flagged explicitly since actual floating-rate interest expense will
vary with the real rate path.
"""

import pandas as pd

SOFR_ASSUMPTION = 0.043  # static assumption, see docstring

CAPITAL_STRUCTURE = {
    "term_loan_b": {
        "principal": 900.0,
        "rate_type": "floating",
        "spread_over_sofr": 0.0425,
        "annual_amortization_pct": 0.01,
        "maturity_year": 2031,
    },
    "senior_secured_notes": {
        "principal": 600.0,
        "rate_type": "fixed",
        "fixed_rate": 0.0825,
        "annual_amortization_pct": 0.0,  # bullet
        "maturity_year": 2031,
    },
}

OPERATING_LEASE_PV = 1343.6  # $mm, present value of lease liabilities


def debt_schedule(years: list) -> pd.DataFrame:
    """Projects beginning/ending balances and cash interest for both
    tranches, plus the blended total, over the given projection years."""
    tlb = CAPITAL_STRUCTURE["term_loan_b"]
    notes = CAPITAL_STRUCTURE["senior_secured_notes"]

    tlb_balance = tlb["principal"]
    notes_balance = notes["principal"]
    tlb_rate = SOFR_ASSUMPTION + tlb["spread_over_sofr"]

    rows = []
    for year in years:
        tlb_interest = tlb_balance * tlb_rate
        tlb_amort = tlb["principal"] * tlb["annual_amortization_pct"]
        tlb_amort = min(tlb_amort, tlb_balance)

        notes_interest = notes_balance * notes["fixed_rate"]
        notes_amort = 0.0  # bullet, no scheduled amortization

        total_beginning = tlb_balance + notes_balance
        total_interest = tlb_interest + notes_interest
        total_amort = tlb_amort + notes_amort

        rows.append({
            "year": year,
            "tlb_balance": tlb_balance,
            "tlb_rate": tlb_rate,
            "tlb_interest": tlb_interest,
            "tlb_amort": tlb_amort,
            "notes_balance": notes_balance,
            "notes_interest": notes_interest,
            "total_secured_debt": total_beginning,
            "total_cash_interest": total_interest,
            "total_mandatory_amort": total_amort,
        })

        tlb_balance -= tlb_amort
        notes_balance -= notes_amort

    return pd.DataFrame(rows)


if __name__ == "__main__":
    print(f"Combined secured debt at close: "
          f"${CAPITAL_STRUCTURE['term_loan_b']['principal'] + CAPITAL_STRUCTURE['senior_secured_notes']['principal']:.0f}mm")
    print(f"Blended cash coupon at SOFR={SOFR_ASSUMPTION:.2%}: "
          f"Term Loan B {SOFR_ASSUMPTION + CAPITAL_STRUCTURE['term_loan_b']['spread_over_sofr']:.2%}, "
          f"Notes {CAPITAL_STRUCTURE['senior_secured_notes']['fixed_rate']:.2%}\n")

    schedule = debt_schedule([2026, 2027, 2028, 2029, 2030])
    print(schedule.to_string(index=False))

    print(f"\nOperating lease liabilities (PV): ${OPERATING_LEASE_PV:.1f}mm")
    print(f"Lease-adjusted total obligations at close: "
          f"${900.0 + 600.0 + OPERATING_LEASE_PV:.1f}mm")
