# Customer Segmentation & Churn Pattern Analytics in European Banking

Segmentation-driven analysis of retail customer churn across **France, Spain, and Germany**, with a live Streamlit dashboard, research paper, and government-facing executive summary.

This work follows the Unified Mentor project brief and is framed against the public interest in a stable retail-banking franchise, as discussed in European Central Bank communications on the financial system: [ECB](https://www.ecb.europa.eu/home/html/index.en.html).

## Why it exists

Banks often know their headline churn rate and still cannot answer:

- which customer groups are most likely to leave
- how churn differs by country, age, and financial profile
- whether exits are concentrated among high-value or low-value customers

This repository turns a 10,000-customer extract into those answers.

## Headline results (unfiltered book)

| KPI | Result |
| --- | --- |
| Overall churn rate | **20.37%** (2,037 of 10,000) |
| Geographic risk index | Germany **1.59×**, Spain 0.82×, France 0.79× |
| Highest age-band churn | **51.1%** for ages 46–60 |
| High-balance share of churn | **59.5%** of exits |
| Engagement drop indicator | Inactive churn **1.88×** active churn |
| Balance of churned accounts | ≈ **€186 million** |

Full interpretation: [docs/research_paper.md](docs/research_paper.md).  
Policy-oriented briefing: [docs/executive_summary.md](docs/executive_summary.md).

## Dataset

File: [`data/churn_modelling.csv`](data/churn_modelling.csv)  
Source (project brief): [Google Drive extract](https://drive.google.com/file/d/1TpMEWG4De0sD_P7_VJ7HtjT_89jlJHpQ/view)

| Column | Role |
| --- | --- |
| CustomerId | Unique identifier (validated) |
| Surname | Dropped after validation (non-analytical) |
| CreditScore | Credit band: Low / Medium / High |
| Geography | France, Spain, Germany |
| Gender, Age, Tenure | Demographic and relationship length |
| Balance, EstimatedSalary | Financial profile and high-value flags |
| NumOfProducts, HasCrCard, IsActiveMember | Engagement and product holding |
| Exited | Churn label (1 = exited) |
| Year | Reference year (2025 in this extract) |

## Run the dashboard

```bash
python3 -m pip install -r requirements.txt
PYTHONPATH=src python3 -m streamlit run app/streamlit_app.py
```

The app provides:

- overall churn summary and profile comparison
- geography-wise rates, contribution, and country × age heatmaps
- age and tenure comparison
- high-value explorer (salary vs balance, premium balance at risk)
- segment filters with live KPI updates and a customer drill-down export

## Pipeline

Reusable logic lives in `src/churn_analytics/`:

1. **Ingestion and validation** — required columns, unique IDs, binary flags, geography and product ranges  
2. **Cleaning** — drop surname  
3. **Segmentation** — age, credit, tenure, balance, high-value flags  
4. **KPIs** — overall rate, segment rates, high-value churn ratio, geographic risk index, engagement drop  

## Tests

```bash
PYTHONPATH=src python3 -m pytest -q
```

## Segmentation design

- **Age:** <30, 30–45, 46–60, 60+  
- **Credit:** Low (<580), Medium (580–669), High (670+)  
- **Tenure:** New (0–2), Mid-term (3–6), Long-term (7–10)  
- **Balance:** Zero, Low (<€100k), High (≥€100k)  
- **High-value:** top-quartile balance **or** top-quartile salary  

## Project layout

```
app/streamlit_app.py          # interactive analytics
src/churn_analytics/          # validation, segments, KPIs
data/churn_modelling.csv
docs/research_paper.md
docs/executive_summary.md
tests/test_pipeline.py
```
