"""
Customer Segmentation and Churn Pattern Analytics in European Banking
Research Paper (EDA, Insights, and Recommendations)

Programme context: Unified Mentor applied analytics project  
Policy context: retail-banking stability and customer-outcome monitoring consistent with
European Central Bank (ECB) interest in resilient deposit franchises
https://www.ecb.europa.eu/home/html/index.en.html

Dataset: 10,000 retail customers across France, Spain, and Germany (reference year 2025)
"""

# 1. Introduction

Customer churn is one of the largest hidden costs in retail banking. When an existing
customer exits, the bank loses remaining lifetime value, must replace the relationship
at a higher acquisition cost, and absorbs greater revenue volatility. Institutions
typically report an aggregate churn rate. That number is not enough. Without
segmentation, leadership cannot answer which groups are most likely to leave, how
risk differs by country, age, and financial profile, or whether exits are concentrated
among high-value or low-value customers.

This paper analyses a customer-level European retail book and produces a
segmentation-driven view of churn. The work is descriptive and diagnostic: it measures
incidence, contribution, and financial exposure. It does not claim causal identification
or a production scoring model, though the patterns below are the natural foundation
for both.

# 2. Problem Statement

Despite rich customer-level data, banks still struggle to:

- identify high-risk segments rather than average customers
- explain geographic and demographic differences in exit rates
- quantify the financial profile of churned customers, especially high-balance holders

Without that structure, retention programmes stay generic, reactive, and inefficient:
the same offer is sent to a young, low-balance, multi-product customer in France and
to an inactive, high-balance, single-product customer in Germany.

# 3. Objectives

Primary:

- measure the overall churn rate
- identify churn distribution across designed customer segments
- compare churn behaviour across France, Spain, and Germany

Secondary:

- understand churn among high-value customers
- evaluate engagement and tenure patterns
- support strategic planning and marketing decisions with quantified KPIs

# 4. Data, Validation, and Preparation

The source file contains 10,000 unique customers and 14 fields, including a constant
reference year (2025). Required analytical columns are CustomerId, CreditScore,
Geography, Gender, Age, Tenure, Balance, NumOfProducts, HasCrCard, IsActiveMember,
EstimatedSalary, and Exited.

Validation checks applied before analysis:

- uniqueness of CustomerId (10,000 distinct identifiers, no duplicates)
- no missing cells
- binary consistency of HasCrCard, IsActiveMember, and Exited (strictly {0, 1})
- Geography restricted to France, Spain, Germany
- NumOfProducts in the expected 1–4 range
- churn label accuracy via the same binary constraint (1 = exited)

Non-analytical surname is dropped after validation. Derived segmentation fields are:

| Dimension | Bands |
| --- | --- |
| Geography | France, Spain, Germany |
| Age | <30, 30–45, 46–60, 60+ |
| Credit score | Low (<580), Medium (580–669), High (670+) |
| Tenure | New (0–2 years), Mid-term (3–6), Long-term (7–10) |
| Balance | Zero-balance, Low-balance (<€100,000), High-balance (≥€100,000) |

High-value customers are defined as those in the top quartile of account balance
(€127,644) or estimated salary (€149,388). This dual rule captures both deposit-heavy
and income-heavy relationships.

# 5. Exploratory Findings

## 5.1 Overall churn

Of 10,000 customers, 2,037 have exited. The overall churn rate is **20.37%**.
Retained customers are the remaining 7,963 (79.63%).

Mean profile comparison:

| Metric | Retained | Churned |
| --- | ---: | ---: |
| Credit score | 651.9 | 645.4 |
| Age (years) | 37.4 | 44.8 |
| Tenure (years) | 5.03 | 4.93 |
| Balance (€) | 72,745 | 91,109 |
| Products | 1.54 | 1.48 |
| Estimated salary (€) | 99,738 | 101,466 |

Churned customers are substantially older and hold **higher** balances. Salary and
credit-score gaps are modest. Churn is therefore not a low-value, low-credit phenomenon.
It is concentrated in economically meaningful relationships.

Aggregate balance of churned accounts is approximately **€185.6 million**, versus
€579.3 million among retained accounts. That is the revenue-risk stock associated
with observed exits, before any multiple for interest margin or cross-sell.

## 5.2 Geographic segmentation

| Country | Customers | Churn rate | Share of customers | Share of churn | Geographic risk index |
| --- | ---: | ---: | ---: | ---: | ---: |
| Germany | 2,509 | 32.44% | 25.1% | 40.0% | 1.59× |
| Spain | 2,477 | 16.67% | 24.8% | 20.3% | 0.82× |
| France | 5,014 | 16.15% | 50.1% | 39.8% | 0.79× |

Germany is 25% of the book but 40% of exits. The geographic risk index (country churn
rate divided by the book-wide rate) is 1.59 in Germany and below 1.0 in France and
Spain. France still contributes almost as many churners as Germany in absolute terms
because it is twice as large; volume and intensity are different management problems.

Female churn is higher in every country, and the German female rate (37.6%) is the
most severe cell in the geography–gender grid.

## 5.3 Age and tenure

| Age band | Customers | Churn rate | Share of churn |
| --- | ---: | ---: | ---: |
| <30 | 1,641 | 7.6% | 6.1% |
| 30–45 | 6,248 | 15.3% | 46.9% |
| 46–60 | 1,647 | **51.1%** | 41.3% |
| 60+ | 464 | 24.8% | 5.6% |

Customers aged 46–60 are 16.5% of the book and 41% of churn. The 30–45 band supplies
the largest count of exits because it is the largest segment, but its rate is below
the book average. Youth is protective; late-career customers are not.

Geography–age interaction is extreme in Germany: churn among German customers aged
46–60 is **67.3%**, versus 45.8% in France and 40.7% in Spain for the same age band.
German customers under 30 still churn at 12.6%, more than twice the French youth rate.

Tenure differences are small relative to age and geography. New customers churn at
21.2%, mid-term at 20.6%, and long-term at 19.5%. Longevity alone is not a retention
strategy.

## 5.4 Credit, products, cards, and engagement

Credit-score bands move churn only modestly: Low 22.0%, Medium 20.6%, High 19.3%.
Creditworthiness is a weak discriminator compared with age, country, activity, and
product holding.

Product holding is not weak:

| Products | Customers | Churn rate | Share of churn |
| ---: | ---: | ---: | ---: |
| 1 | 5,084 | 27.7% | 69.2% |
| 2 | 4,590 | 7.6% | 17.1% |
| 3 | 266 | 82.7% | 10.8% |
| 4 | 60 | 100% | 2.9% |

Two-product relationships are the sticky core. Single-product customers generate
more than two-thirds of exits. Three- and four-product cells are small but almost
entirely churned — a pattern consistent with distress, product mismatch, or
last-resort stacking rather than healthy deepening. Credit-card ownership is almost
irrelevant (20.2% with a card vs 20.8% without).

Engagement is decisive. Inactive members churn at **26.9%**; active members at
**14.3%**. The engagement drop indicator (inactive rate / active rate) is **1.88×**,
a gap of 12.6 percentage points. In Germany the inactive rate reaches 41.1%.

## 5.5 Balance and high-value churn

| Balance segment | Customers | Churn rate | Share of churn |
| --- | ---: | ---: | ---: |
| Zero-balance | 3,617 | 13.8% | 24.5% |
| Low-balance | 1,584 | 20.6% | 16.0% |
| High-balance | 4,799 | **25.2%** | **59.5%** |

Zero-balance customers are safer, not riskier. High-balance customers are 48% of the
book and 60% of churn. Among the top-quartile balance cohort (2,500 customers),
churn is 23.7% and associated balance of those exits is about **€88.7 million**.

Salary versus balance:

- neither high salary nor high balance: 18.9% churn
- high salary only: 20.4%
- high balance only: 23.2%
- both high salary and high balance: **25.0%**

Deposit size is a stronger churn correlate than salary. Premium relationships are
not self-retaining.

# 6. Key Performance Indicators

| KPI | Unfiltered result | Interpretation |
| --- | --- | --- |
| Overall churn rate | 20.37% | One in five customers has exited |
| Segment churn rate | See sections 5.2–5.5 | 46–60, Germany, inactive, 1/3/4 products |
| High-value churn ratio | 22.3% among dual-quartile premium flag (4,351 customers) | Premium exits exceed a “low-value only” story |
| Geographic risk index | Germany 1.59×, Spain 0.82×, France 0.79× | Intensity vs volume |
| Engagement drop indicator | 1.88× (26.9% / 14.3%) | Inactivity is a leading observable |

# 7. Recommendations

1. **Treat Germany 46–60 inactive single-product holders as a priority cell.**
   This intersection combines the three strongest rate effects. A dedicated
   relationship review (rate, service, and product fit) is more efficient than a
   book-wide campaign.

2. **Protect two-product relationships and diagnose 3–4 product churn.**
   Deepening from one product to two is the highest-leverage structural change in
   the data. Three- and four-product exits should be audited as possible distress
   or mis-sale, not celebrated as “engaged.”

3. **Do not starve high-balance retention.**
   More than half of churn events sit in high-balance accounts. Win-back and
   save-desk capacity should be allocated by balance at risk, not by headcount
   of complaints.

4. **Re-activate before discounting.**
   The engagement gap is larger than the credit-score gap. Activity flags are
   cheaper to observe than new credit data. Trigger outreach when a previously
   active customer goes dark.

5. **Separate French volume from German intensity.**
   France needs process-scale retention because of book size. Germany needs
   intensity (pricing, competitive response, and late-career offers) because of rate.

6. **Gender-aware service design, not a single message.**
   Female churn is higher in every country. Investigate product mix, complaint
   handling, and advice quality rather than assuming a uniform “retail” journey.

# 8. Limitations

The file is a cross-section, not a panel. Exited is an outcome label, not a
hazard over time. There is no competitor offer, branch, digital-usage, or complaint
history. High 3–4 product churn may reflect selection (customers already leaving
take additional products) rather than a causal product effect. Results should not
be generalised beyond France, Spain, and Germany or beyond this retail extract.

# 9. Conclusion

Churn in this European retail book is **high-intensity in Germany, age-concentrated
in 46–60, engagement-sensitive, and financially heavy**. It is not primarily a
youth, zero-balance, or poor-credit problem. Segmentation therefore changes the
retention map: the bank should fund save actions where both probability and
balance coincide, and should treat two-product active relationships as the
stability core of the franchise.

Supporting artefacts: interactive Streamlit dashboard (`app/streamlit_app.py`)
and government-facing executive summary (`docs/executive_summary.md`).
