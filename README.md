# Petco Corporate Credit Underwriting & Recovery Case Study

A corporate credit underwriting case study on Petco Health & Wellness
Company, Inc. (Nasdaq: WOOF), built on the company's actual reported
financials and capital structure — projecting a base case and a
downside stress case, then modeling recovery across the capital
structure in a default scenario.

## Why this project

Private credit and leveraged finance underwriting is fundamentally
about answering one question: can this company service its debt, and
if it can't, who gets paid back and how much? This project works
through that question end to end on a real, leveraged, publicly-traded
retailer — reading actual SEC filings and earnings releases, building
a forward financial model, stress-testing it against a plausible
downside, and modeling recovery across a real (pari passu) capital
structure. It's built to complement a separate MBS prepayment/cash-flow
model project: that one demonstrates structured/consumer credit and
quantitative modeling; this one demonstrates fundamental corporate
credit analysis and underwriting judgment.

## What it does

| Module | Purpose |
|---|---|
| `financials.py` | Petco's actual FY2024/FY2025 historical financials, plus an illustrative 5-year base-case projection built off management's stated expectation of a return to positive comps. |
| `capital_structure.py` | Petco's actual post-refinancing capital structure ($900mm Term Loan B + $600mm 8.250% Senior Secured Notes, both pari passu) and its debt service schedule. |
| `credit_metrics.py` | Leverage (gross and lease-adjusted), interest coverage, fixed-charge coverage, and covenant headroom against an illustrative maintenance covenant. |
| `stress_test.py` | A downside case assuming the recent sales decline resumes instead of reversing — finds the year covenant headroom runs out and free cash flow turns negative. |
| `recovery_waterfall.py` | Enterprise-value-based recovery analysis at the point of default, allocating value by seniority (secured pro rata, then unsecured, then equity) across a range of distressed exit multiples. |
| `credit_memo.md` | The document that ties it all together — the actual artifact a credit committee would read. |

## Key results

**FY2025 was a real inflection point** for Petco: Adjusted EBITDA grew
21% to $408.2mm, free cash flow nearly quadrupled to $187.0mm, and
leverage fell from 4.2x to 3.0x (company-reported, net-debt basis) —
even as net sales continued to decline slightly. A February 2026
refinancing extended the maturity wall from 2028 to 2031.

**Base case:** if that improvement continues, leverage falls further to
2.9x and interest coverage rises to 4.1x by FY2030.

**Downside case:** if the sales decline resumes instead (-3%/year, with
margin compression), leverage instead climbs to **6.6x by FY2030**,
tripping an illustrative 5.5x maintenance covenant in **FY2029** — a
four-year runway before real trouble, not an immediate risk, but a real
one.

**Recovery analysis:** at the FY2029 breach point, even the senior
secured Term Loan B and Notes (pari passu, same collateral) are **not**
guaranteed full recovery — at exit multiples below ~6.5x EBITDA, both
tranches take a proportional haircut (e.g. 77.9% recovery at a 4.5x
multiple). Unsecured claims and equity recover nothing below a 6.0x
multiple.

## Important caveats

- Every figure in `financials.py`'s `HISTORICAL` dict and
  `capital_structure.py`'s `CAPITAL_STRUCTURE` is either Petco's actual
  reported number, or algebraically implied from a reported percentage
  change (documented inline). Everything in `BASE_CASE_ASSUMPTIONS`,
  `DOWNSIDE_ASSUMPTIONS`, the 5.5x covenant level, and the $400mm
  unsecured claims pool is this analyst's own illustrative assumption,
  **not** a Petco disclosure — kept clearly separated throughout.
- Leverage is presented on a **gross** secured-debt basis, which is
  more conservative than (and differs numerically from) Petco's own
  reported ratio, which nets against cash on hand.
- SOFR is held static at 4.3% for the Term Loan B's floating rate.
- This is a resume case study, not an actual investment recommendation
  or a substitute for full diligence.

## Running it

Requires Python 3 with `pandas`:

```bash
pip install pandas
```

Then, from the repo root:

```bash
python3 financials.py           # historical actuals + base case projection
python3 capital_structure.py    # actual capital structure + debt schedule
python3 credit_metrics.py       # leverage/coverage ratios, base case
python3 stress_test.py          # downside case + covenant breach analysis
python3 recovery_waterfall.py   # recovery by tranche across exit multiples
```

`credit_memo.md` synthesizes all of the above into the final written
analysis.

## Data sources

- Petco Health & Wellness Company, Inc., Form 10-K, fiscal year ended
  February 1, 2025 (SEC EDGAR)
- Petco Reports Fourth Quarter and Full Year 2025 Results, press
  release, March 11, 2026
- Petco debt refinancing press releases and Q1 FY2026 10-Q disclosures,
  January-June 2026
