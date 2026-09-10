"""
credit_metrics.py

Combines financials.py (revenue/EBITDA projection) and
capital_structure.py (debt schedule) into the actual ratios a credit
committee tracks year over year:

    - Total Secured Debt / Adj. EBITDA      (GROSS secured leverage --
      not net of cash; see naming note below)
    - Lease-Adjusted Debt / Adj. EBITDA     (leverage, retailer-relevant)
    - Adj. EBITDA / Cash Interest           (interest coverage)
    - (Adj. EBITDA - Capex) / Debt Service  (fixed-charge-style coverage:
      debt service = cash interest + mandatory amortization)

NAMING NOTE: this is deliberately called GROSS secured leverage, not "net
leverage" -- it does not subtract cash on hand. Petco's own reported
leverage ratio IS net-debt-based, which is why the FY2025 reference
figure below differs from Petco's disclosed number. Gross leverage is
used here as the more conservative measure for a downside/stress
analysis, since cash can be depleted quickly in a deteriorating
scenario -- netting against a cash balance you might not still have
next year would understate real leverage risk.

THRESHOLD NOTE: the 5.5x level used below is an ILLUSTRATIVE INTERNAL
LEVERAGE WARNING THRESHOLD set by this analyst for the purpose of this
case study -- it is NOT Petco's actual disclosed maintenance covenant
level, and exceeding it should not be read as modeling an actual
covenant default under Petco's real credit agreement.
"""

import pandas as pd
from financials import HISTORICAL, project_base_case, BASE_CASE_ASSUMPTIONS
from capital_structure import debt_schedule, OPERATING_LEASE_PV

ILLUSTRATIVE_LEVERAGE_WARNING_THRESHOLD = 5.5  # analyst assumption, see docstring


def compute_credit_metrics(financials_df: pd.DataFrame, debt_df: pd.DataFrame) -> pd.DataFrame:
    merged = financials_df.merge(debt_df, on="year")

    merged["gross_secured_leverage"] = merged["total_secured_debt"] / merged["adj_ebitda"]
    merged["lease_adjusted_leverage"] = (
        (merged["total_secured_debt"] + OPERATING_LEASE_PV) / merged["adj_ebitda"]
    )
    merged["interest_coverage"] = merged["adj_ebitda"] / merged["total_cash_interest"]

    debt_service = merged["total_cash_interest"] + merged["total_mandatory_amort"]
    merged["fixed_charge_coverage"] = (merged["adj_ebitda"] - merged["capex"]) / debt_service

    merged["headroom_vs_warning_threshold"] = (
        ILLUSTRATIVE_LEVERAGE_WARNING_THRESHOLD - merged["gross_secured_leverage"]
    )

    return merged[["year", "net_sales", "adj_ebitda", "total_secured_debt",
                    "gross_secured_leverage", "lease_adjusted_leverage", "interest_coverage",
                    "fixed_charge_coverage", "headroom_vs_warning_threshold"]]


if __name__ == "__main__":
    projected = project_base_case()
    years = BASE_CASE_ASSUMPTIONS["projection_years"]
    debt = debt_schedule(years)

    metrics = compute_credit_metrics(projected, debt)

    print("FY2025 actual (reference point):")
    fy25 = HISTORICAL[2025]
    fy25_gross_leverage = 1500.0 / fy25["adj_ebitda"]  # $1.5bn secured debt at close vs FY25 EBITDA
    print(f"  Gross Secured Leverage (secured debt / EBITDA): {fy25_gross_leverage:.2f}x "
          f"(Petco's own reported leverage ratio, NET-DEBT basis: {fy25['leverage_ratio']:.1f}x -- "
          f"these are different measures, not a discrepancy)")

    print("\nBase case projection:")
    print(metrics.to_string(index=False, formatters={
        "net_sales": "{:.0f}".format,
        "adj_ebitda": "{:.1f}".format,
        "total_secured_debt": "{:.0f}".format,
        "gross_secured_leverage": "{:.2f}x".format,
        "lease_adjusted_leverage": "{:.2f}x".format,
        "interest_coverage": "{:.2f}x".format,
        "fixed_charge_coverage": "{:.2f}x".format,
        "headroom_vs_warning_threshold": "{:.2f}x".format,
    }))
