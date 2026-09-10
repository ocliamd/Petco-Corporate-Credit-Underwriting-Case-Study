"""
stress_test.py

Downside scenario: what happens to leverage, coverage, and covenant
headroom if Petco's "return to growth" story DOESN'T materialize?

This is the actual underwriting question a credit committee asks. The
base case (financials.py) assumes modest positive comps starting in
FY2026, consistent with management's stated expectation. The downside
case instead assumes:

    - Revenue DECLINES 3% per year (a continuation, not reversal, of the
      FY2024/FY2025 comp trend -- i.e. management's turnaround doesn't
      take hold), pressured by continued competition from Chewy,
      PetSmart, Amazon, and Walmart in a low-margin category.
    - EBITDA margin COMPRESSES 50bps per year rather than expanding, as
      the company defends volume with promotional pricing.
    - Capex is held constant in dollar terms (maintenance capex doesn't
      scale down just because sales are falling) rather than as a fixed
      % of a shrinking sales base.

All three assumptions are the analyst's own illustrative stress, not a
company disclosure -- exactly like the base case assumptions, but
designed to pressure-test the credit rather than extend its recent
improvement.
"""

import pandas as pd
from capital_structure import debt_schedule, OPERATING_LEASE_PV
from credit_metrics import MAINTENANCE_COVENANT_LEVERAGE

DOWNSIDE_ASSUMPTIONS = {
    "revenue_decline": -0.03,
    "ebitda_margin_start": 0.068,       # same FY2025 actual starting point
    "ebitda_margin_annual_change": -0.005,  # compression, not expansion
    "capex_fixed": 120.0,               # held flat in $ terms
    "projection_years": [2026, 2027, 2028, 2029, 2030],
}


def project_downside_case(assumptions: dict = None) -> pd.DataFrame:
    a = assumptions or DOWNSIDE_ASSUMPTIONS
    rows = []

    prior_sales = 6000.0  # FY2025 actual net sales
    ebitda_margin = a["ebitda_margin_start"]

    for year in a["projection_years"]:
        net_sales = prior_sales * (1 + a["revenue_decline"])
        ebitda_margin = max(ebitda_margin + a["ebitda_margin_annual_change"], 0.02)
        adj_ebitda = net_sales * ebitda_margin

        rows.append({
            "year": year,
            "net_sales": net_sales,
            "adj_ebitda": adj_ebitda,
            "ebitda_margin": ebitda_margin,
            "capex": a["capex_fixed"],
        })

        prior_sales = net_sales

    return pd.DataFrame(rows)


def stress_metrics(downside_df: pd.DataFrame, debt_df: pd.DataFrame) -> pd.DataFrame:
    merged = downside_df.merge(debt_df, on="year")
    merged["net_leverage"] = merged["total_secured_debt"] / merged["adj_ebitda"]
    merged["lease_adjusted_leverage"] = (
        (merged["total_secured_debt"] + OPERATING_LEASE_PV) / merged["adj_ebitda"]
    )
    merged["interest_coverage"] = merged["adj_ebitda"] / merged["total_cash_interest"]

    debt_service = merged["total_cash_interest"] + merged["total_mandatory_amort"]
    merged["free_cash_flow_after_debt_service"] = (
        merged["adj_ebitda"] - merged["capex"] - debt_service
    )
    merged["covenant_headroom"] = MAINTENANCE_COVENANT_LEVERAGE - merged["net_leverage"]
    merged["covenant_breach"] = merged["covenant_headroom"] < 0

    return merged[["year", "net_sales", "adj_ebitda", "net_leverage",
                    "lease_adjusted_leverage", "interest_coverage",
                    "free_cash_flow_after_debt_service", "covenant_headroom",
                    "covenant_breach"]]


if __name__ == "__main__":
    downside = project_downside_case()
    years = DOWNSIDE_ASSUMPTIONS["projection_years"]
    debt = debt_schedule(years)

    metrics = stress_metrics(downside, debt)

    print("DOWNSIDE CASE: -3% revenue/year, -50bps EBITDA margin/year, flat capex\n")
    print(metrics.to_string(index=False, formatters={
        "net_sales": "{:.0f}".format,
        "adj_ebitda": "{:.1f}".format,
        "net_leverage": "{:.2f}x".format,
        "lease_adjusted_leverage": "{:.2f}x".format,
        "interest_coverage": "{:.2f}x".format,
        "free_cash_flow_after_debt_service": "{:.1f}".format,
        "covenant_headroom": "{:.2f}x".format,
    }))

    first_breach = metrics[metrics["covenant_breach"]]
    if not first_breach.empty:
        breach_year = first_breach.iloc[0]["year"]
        print(f"\n>>> Covenant breach (5.5x maintenance leverage) first occurs in FY{int(breach_year)}.")
    else:
        print(f"\n>>> No covenant breach within the projection window "
              f"-- leverage stays under {MAINTENANCE_COVENANT_LEVERAGE}x throughout.")

    negative_fcf = metrics[metrics["free_cash_flow_after_debt_service"] < 0]
    if not negative_fcf.empty:
        print(f">>> Free cash flow after debt service turns NEGATIVE starting FY{int(negative_fcf.iloc[0]['year'])}.")
    else:
        print(">>> Free cash flow after debt service stays positive throughout the downside case.")