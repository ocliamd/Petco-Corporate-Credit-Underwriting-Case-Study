"""
financials.py

Historical and projected income statement / free cash flow model for
Petco Health & Wellness Company, Inc. (Nasdaq: WOOF).

HISTORICAL figures (FY2024, FY2025) are Petco's actual reported results,
sourced from:
    - Petco Q4 & Full Year 2025 Results press release (March 11, 2026)
    - Petco 10-K, fiscal year ended February 1, 2025

FY2025 here refers to Petco's fiscal year ended January 31, 2026 (Petco's
fiscal year runs roughly Feb-Jan, so "FY2025" is what they reported in
March 2026 covering that period).

PROJECTED figures (FY2026 onward) are ILLUSTRATIVE, built by this analyst
(not Petco) off of two real anchors: (1) FY2025 actuals as the starting
base, and (2) Petco management's own qualitative guidance that they
expect "a return to positive comps in 2026" after two years of declining
sales. The specific growth/margin assumptions beyond that qualitative
signal are mine, not Petco's -- exactly as a credit analyst would build
a working model off a company's public disclosures without insider
guidance on every future model input.
"""

import pandas as pd

# ---- Actual historical figures (in $ millions) ----
HISTORICAL = {
    2024: {
        "net_sales": 6154.0,          # implied: 6000 / (1 - 0.025)
        "gross_margin": 0.3804,       # implied: 38.7% - 66bps
        "adj_ebitda": 336.5,          # implied: 408.2 / 1.213
        "operating_income": 7.1,      # actual, reported
        "net_income": -101.8,         # actual, reported
        "cash_from_ops": 177.7,       # implied: 314.1 / 1.768
        "free_cash_flow": 49.7,       # implied: 187.0 / 3.763
        "cash_balance": 165.7,        # implied: 256.7 - 91.0
        "leverage_ratio": 4.2,        # actual, reported (start of FY2025)
    },
    2025: {
        "net_sales": 6000.0,          # actual, reported ("$6.0 billion")
        "gross_margin": 0.387,        # actual, reported
        "adj_ebitda": 408.2,          # actual, reported
        "operating_income": 120.4,    # actual, reported
        "net_income": 9.1,            # actual, reported
        "cash_from_ops": 314.1,       # actual, reported
        "free_cash_flow": 187.0,      # actual, reported
        "cash_balance": 256.7,        # actual, reported
        "leverage_ratio": 3.0,        # actual, reported (end of FY2025)
    },
}

# ---- Illustrative base-case projection assumptions (analyst's own) ----
BASE_CASE_ASSUMPTIONS = {
    "revenue_growth": 0.015,          # modest return-to-growth, per mgmt tone
    "ebitda_margin_start": 0.068,     # FY2025 actual: 408.2 / 6000.0
    "ebitda_margin_annual_improvement": 0.002,  # continued cost discipline
    "capex_pct_of_sales": 0.020,      # typical mature retailer maintenance capex
    "cash_interest_rate_blended": 0.079,  # blended coupon on the $1.5B secured stack (see capital_structure.py)
    "tax_rate": 0.25,
    "projection_years": [2026, 2027, 2028, 2029, 2030],
}


def project_base_case(assumptions: dict = None) -> pd.DataFrame:
    """Builds a 5-year forward projection (FY2026-FY2030) off FY2025 actuals."""
    a = assumptions or BASE_CASE_ASSUMPTIONS
    rows = []

    # Seed with FY2025 actual as the jump-off point
    prior_sales = HISTORICAL[2025]["net_sales"]
    ebitda_margin = a["ebitda_margin_start"]

    for year in a["projection_years"]:
        net_sales = prior_sales * (1 + a["revenue_growth"])
        ebitda_margin = min(ebitda_margin + a["ebitda_margin_annual_improvement"], 0.09)
        adj_ebitda = net_sales * ebitda_margin
        capex = net_sales * a["capex_pct_of_sales"]

        rows.append({
            "year": year,
            "net_sales": net_sales,
            "adj_ebitda": adj_ebitda,
            "ebitda_margin": ebitda_margin,
            "capex": capex,
        })

        prior_sales = net_sales

    return pd.DataFrame(rows)


if __name__ == "__main__":
    print("HISTORICAL (actual, per Petco public filings/press releases):\n")
    hist_df = pd.DataFrame(HISTORICAL).T
    print(hist_df.to_string())

    print("\n\nPROJECTED BASE CASE (illustrative, analyst assumptions):\n")
    proj = project_base_case()
    print(proj.to_string(index=False))