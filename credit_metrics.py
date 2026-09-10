"""
credit_metrics.py

Combines financials.py (revenue/EBITDA projection) and
capital_structure.py (debt schedule) into the actual ratios a credit
committee tracks year over year:

    - Total Secured Debt / Adj. EBITDA      (leverage)
    - Lease-Adjusted Debt / Adj. EBITDA     (leverage, retailer-relevant)
    - Adj. EBITDA / Cash Interest           (interest coverage)
    - (Adj. EBITDA - Capex) / Debt Service  (fixed-charge-style coverage:
      debt service = cash interest + mandatory amortization)

Covenant headroom is assessed against a maintenance covenant assumption
of 5.5x Net Leverage (a level roughly consistent with the max leverage
covenants typically seen on B/B- rated leveraged loans of this size --
NOTE: this is an ANALYST ASSUMPTION for illustration, not Petco's actual
disclosed covenant level, which is not being sourced here).
"""

import pandas as pd
from financials import HISTORICAL, project_base_case, BASE_CASE_ASSUMPTIONS
from capital_structure import debt_schedule, OPERATING_LEASE_PV

MAINTENANCE_COVENANT_LEVERAGE = 5.5  # analyst assumption, see docstring


def compute_credit_metrics(financials_df: pd.DataFrame, debt_df: pd.DataFrame) -> pd.DataFrame:
    merged = financials_df.merge(debt_df, on="year")

    merged["net_leverage"] = merged["total_secured_debt"] / merged["adj_ebitda"]
    merged["lease_adjusted_leverage"] = (
        (merged["total_secured_debt"] + OPERATING_LEASE_PV) / merged["adj_ebitda"]
    )
    merged["interest_coverage"] = merged["adj_ebitda"] / merged["total_cash_interest"]

    debt_service = merged["total_cash_interest"] + merged["total_mandatory_amort"]
    merged["fixed_charge_coverage"] = (merged["adj_ebitda"] - merged["capex"]) / debt_service

    merged["covenant_headroom"] = MAINTENANCE_COVENANT_LEVERAGE - merged["net_leverage"]

    return merged[["year", "net_sales", "adj_ebitda", "total_secured_debt",
                    "net_leverage", "lease_adjusted_leverage", "interest_coverage",
                    "fixed_charge_coverage", "covenant_headroom"]]


if __name__ == "__main__":
    projected = project_base_case()
    years = BASE_CASE_ASSUMPTIONS["projection_years"]
    debt = debt_schedule(years)

    metrics = compute_credit_metrics(projected, debt)

    print("FY2025 actual (reference point):")
    fy25 = HISTORICAL[2025]
    fy25_leverage = 1500.0 / fy25["adj_ebitda"]  # $1.5bn secured debt at close vs FY25 EBITDA
    print(f"  Net Leverage (secured debt / EBITDA): {fy25_leverage:.2f}x "
          f"(Petco's own reported leverage ratio, net-debt basis: {fy25['leverage_ratio']:.1f}x)")

    print("\nBase case projection:")
    print(metrics.to_string(index=False, formatters={
        "net_sales": "{:.0f}".format,
        "adj_ebitda": "{:.1f}".format,
        "total_secured_debt": "{:.0f}".format,
        "net_leverage": "{:.2f}x".format,
        "lease_adjusted_leverage": "{:.2f}x".format,
        "interest_coverage": "{:.2f}x".format,
        "fixed_charge_coverage": "{:.2f}x".format,
        "covenant_headroom": "{:.2f}x".format,
    }))