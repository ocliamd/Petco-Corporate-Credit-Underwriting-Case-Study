"""
stress_test.py

Downside scenario: what happens to leverage, coverage, and headroom
against an illustrative internal warning threshold if Petco's "return to
growth" story DOESN'T materialize?

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

TERMINOLOGY NOTE: the 5.5x threshold used here is this analyst's own
ILLUSTRATIVE INTERNAL LEVERAGE WARNING THRESHOLD, not Petco's actual
disclosed maintenance covenant. Exceeding it is referred to as reaching
an "illustrative stress point," not a "covenant breach" or "default" --
this case study does not model Petco's real credit agreement terms.
The cash flow figure below is also a SIMPLIFIED PROXY: it nets Adj.
EBITDA against capex and debt service only. It does NOT include cash
taxes, working capital movements, restructuring costs, or other cash
uses, all of which would matter for an actual liquidity assessment.
"""

import pandas as pd
from capital_structure import debt_schedule, OPERATING_LEASE_PV
from credit_metrics import ILLUSTRATIVE_LEVERAGE_WARNING_THRESHOLD

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
    merged["gross_secured_leverage"] = merged["total_secured_debt"] / merged["adj_ebitda"]
    merged["lease_adjusted_leverage"] = (
        (merged["total_secured_debt"] + OPERATING_LEASE_PV) / merged["adj_ebitda"]
    )
    merged["interest_coverage"] = merged["adj_ebitda"] / merged["total_cash_interest"]

    debt_service = merged["total_cash_interest"] + merged["total_mandatory_amort"]
    merged["simplified_cash_flow_proxy"] = (
        merged["adj_ebitda"] - merged["capex"] - debt_service
    )
    merged["headroom_vs_warning_threshold"] = (
        ILLUSTRATIVE_LEVERAGE_WARNING_THRESHOLD - merged["gross_secured_leverage"]
    )
    merged["exceeds_warning_threshold"] = merged["headroom_vs_warning_threshold"] < 0

    return merged[["year", "net_sales", "adj_ebitda", "gross_secured_leverage",
                    "lease_adjusted_leverage", "interest_coverage",
                    "simplified_cash_flow_proxy", "headroom_vs_warning_threshold",
                    "exceeds_warning_threshold"]]


if __name__ == "__main__":
    downside = project_downside_case()
    years = DOWNSIDE_ASSUMPTIONS["projection_years"]
    debt = debt_schedule(years)

    metrics = stress_metrics(downside, debt)

    print("DOWNSIDE CASE: -3% revenue/year, -50bps EBITDA margin/year, flat capex\n")
    print(metrics.to_string(index=False, formatters={
        "net_sales": "{:.0f}".format,
        "adj_ebitda": "{:.1f}".format,
        "gross_secured_leverage": "{:.2f}x".format,
        "lease_adjusted_leverage": "{:.2f}x".format,
        "interest_coverage": "{:.2f}x".format,
        "simplified_cash_flow_proxy": "{:.1f}".format,
        "headroom_vs_warning_threshold": "{:.2f}x".format,
    }))

    first_exceed = metrics[metrics["exceeds_warning_threshold"]]
    if not first_exceed.empty:
        stress_year = first_exceed.iloc[0]["year"]
        print(f"\n>>> Illustrative stress point: gross secured leverage first exceeds the "
              f"{ILLUSTRATIVE_LEVERAGE_WARNING_THRESHOLD}x warning threshold in FY{int(stress_year)}. "
              f"This is an analyst-defined threshold, not Petco's actual covenant level.")
    else:
        print(f"\n>>> Leverage stays under the {ILLUSTRATIVE_LEVERAGE_WARNING_THRESHOLD}x "
              f"illustrative warning threshold throughout the projection window.")

    negative_cf = metrics[metrics["simplified_cash_flow_proxy"] < 0]
    if not negative_cf.empty:
        print(f">>> The simplified cash-flow proxy (after capex and debt service) turns NEGATIVE "
              f"starting FY{int(negative_cf.iloc[0]['year'])}.")
    else:
        print(">>> The simplified cash-flow proxy stays positive throughout the downside case.")
