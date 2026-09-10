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
| `capital_structure.py` | Petco's actual post-refinancing capital structure ($900mm Term Loan B + $600mm 8.250% Senior Secured Notes, the latter with a split lien — first-priority fixed assets, second-priority current assets) and its debt service schedule. |
| `credit_metrics.py` | Gross secured leverage (not net of cash), lease-adjusted leverage, interest coverage, fixed-charge coverage, and headroom against an illustrative internal warning threshold. |
| `stress_test.py` | A downside case assuming the recent sales decline resumes instead of reversing — finds the year gross secured leverage crosses the illustrative threshold and a simplified cash-flow proxy turns negative. |
| `recovery_waterfall.py` | Enterprise-value-based recovery analysis at an illustrative stress point, allocating value by seniority (secured pro rata as a simplification, then unsecured, then equity) across a range of distressed exit multiples. |
| `credit_memo.md` | The document that ties it all together — the actual artifact a credit committee would read. |

## Key results

**FY2025 was a real inflection point** for Petco: Adjusted EBITDA grew
21% to $408.2mm, free cash flow nearly quadrupled to $187.0mm, and
leverage fell from 4.2x to 3.0x (company-reported, net-debt basis) —
even as net sales continued to decline slightly. A February 2026
refinancing extended the maturity wall from 2028 to 2031. Petco returned
to public markets via a traditional IPO in January 2021, following its
2016 leveraged buyout — not a de-SPAC, as an earlier draft of this
project incorrectly stated.

**Base case:** if that improvement continues, gross secured leverage
falls further to 2.9x and interest coverage rises to 4.1x by FY2030.

**Downside case:** if the sales decline resumes instead (-3%/year, with
margin compression), gross secured leverage instead climbs to **6.6x by
FY2030**, crossing an illustrative 5.5x internal warning threshold (this
analyst's own assumption, not Petco's actual covenant level) in
**FY2029** — a four-year runway before real trouble, not an immediate
risk, but a real one.

**Recovery analysis:** at the FY2029 illustrative stress point, even the
senior secured Term Loan B and Notes are **not** guaranteed full
recovery — at exit multiples below ~6.5x EBITDA, both tranches take a
proportional haircut in this model (e.g. 77.9% recovery at a 4.5x
multiple). Unsecured claims and equity recover nothing below a 6.0x
multiple. Note: the Notes actually carry a split lien (first-priority
fixed assets, second-priority current assets) rather than plain pari
passu with the Term Loan B — this project simplifies that into a pro
rata split; see the memo's limitations section.

## Important caveats

- Every figure in `financials.py`'s `HISTORICAL` dict and
  `capital_structure.py`'s `CAPITAL_STRUCTURE` is either Petco's actual
  reported number, or algebraically implied from a reported percentage
  change (documented inline). Everything in `BASE_CASE_ASSUMPTIONS`,
  `DOWNSIDE_ASSUMPTIONS`, the 5.5x threshold, and the $400mm unsecured
  claims pool is this analyst's own illustrative assumption, **not** a
  Petco disclosure — kept clearly separated throughout.
- Leverage is presented on a **gross secured-debt basis** (not net of
  cash), which is more conservative than — and differs numerically
  from — Petco's own reported ratio, which nets against cash on hand.
  It is labeled `gross_secured_leverage` throughout the code, not "net
  leverage."
- The 5.5x threshold is called an **illustrative internal leverage
  warning threshold** throughout, not a "covenant" — it is not sourced
  from Petco's actual credit agreement, and crossing it is called an
  "illustrative stress point," not a "covenant breach" or "default."
- The Term Loan B and Senior Secured Notes are **not** simple pari passu
  across all collateral. Per Petco's actual disclosures, the Notes carry
  a split lien (first-priority on fixed assets, second-priority on
  current assets). `recovery_waterfall.py` simplifies this into a pro
  rata split between the two tranches — a real limitation, documented
  in both the code and the memo.
- The recovery waterfall excludes DIP financing, administrative claims,
  professional fees, transaction costs, and taxes — all of which would
  likely reduce real-world recoveries below what's modeled here.
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
