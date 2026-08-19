# Executive Summary
## Customer Segmentation and Churn in European Retail Banking

**Audience:** government and supervisory stakeholders concerned with household
financial services, deposit franchise stability, and fair treatment of retail
customers in the euro area  
**Context:** Unified Mentor applied analytics project, informed by the European
Central Bank’s public mandate for a stable financial system
(https://www.ecb.europa.eu/home/html/index.en.html)  
**Evidence base:** 10,000 retail customers in France, Spain, and Germany (2025 extract)

---

### Why this matters

Retail banks fund households and SMEs through sticky deposits. When customers leave,
institutions lose franchise value and must replace funding at higher cost. At scale,
poorly targeted retention also wastes consumer attention and can leave older, higher-balance
households without timely support. Aggregate churn statistics hide those distributional
facts. This summary reports **who leaves, where, and with what balances**.

### Headline results

- **Overall churn rate: 20.4%** (2,037 of 10,000 customers).
- **Germany is the intensity problem.** German customers churn at 32.4% — a geographic
  risk index of **1.59 times** the book average — while representing only a quarter of
  customers and **40% of all exits**.
- **France is the volume problem.** French churn (16.2%) is below average, but France is
  half the book and still accounts for about **40% of exits**.
- **Age 46–60 is the critical life-stage.** That band churns at **51.1%** and produces
  41% of exits despite being 16.5% of customers. In Germany the same age band churns at
  **67%**.
- **Churn is not a low-value phenomenon.** High-balance accounts (≥ €100,000) generate
  **60% of exits**. Churned balances total about **€186 million**. Youth and zero-balance
  customers are comparatively sticky.
- **Inactivity nearly doubles risk.** Inactive members churn at 26.9% versus 14.3% for
  active members (engagement drop **1.88×**).
- **Two-product households are the stability core** (7.6% churn). One-product customers
  produce 69% of exits. Very high product counts (3–4) are rare and almost fully churned,
  which warrants consumer-outcome review rather than a simple “more products is better”
  reading.

### Implications for public-interest oversight

1. **Concentration of household exits in late-career and high-balance segments** can
   amplify funding volatility at individual banks and, in stressed markets, reduce
   confidence among depositors who believed they were “core” customers.
2. **Cross-country divergence inside a three-market book** shows that a single EU-level
   narrative on “retail loyalty” is too coarse. National competitive and service
   conditions still dominate observed exit rates.
3. **Gender gaps** (female churn 25.1% vs male 16.5%) are large enough to justify
   questions about advice quality, complaint handling, and product suitability — without
   treating gender as a credit-risk substitute.
4. **Engagement and product structure are observable conduct metrics.** Supervisors and
   consumer bodies can ask institutions how they monitor inactivity and single-product
   dependence among older, high-balance customers.

### Recommended institutional actions (non-binding)

| Priority | Action | Rationale |
| --- | --- | --- |
| 1 | Targeted save capacity for German, age 46–60, inactive, high-balance relationships | Highest combined probability and balance at risk |
| 2 | Measure retention by **balance at risk**, not headcount of leavers | Prevents under-serving premium households |
| 3 | Audit 3–4 product churn for suitability and distress | Protects consumers from mis-sale while clarifying bank economics |
| 4 | Treat two-product activity as a stability indicator in management information | Strongest protective pattern in the extract |
| 5 | Keep country strategies distinct: intensity in Germany, industrialised process in France | Matches volume vs rate |

### What this document is not

It is not a stress test, not an ECB opinion, and not a prediction of system-wide
deposit flight. It is a transparent segmentation of one retail extract, intended to
replace generic churn commentary with **measurable segment rates, contribution shares,
and financial exposure**.

### Accompanying materials

- Full EDA and recommendations: `docs/research_paper.md`
- Live analytics application: `streamlit run app/streamlit_app.py`
