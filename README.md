# NHS Operations Intelligence

I built this around a simple problem: monthly A&E releases contain useful operational signals, but the raw files are not a management view. Before looking at a forecast, I want to know whether the source changed, whether the KPI is calculated consistently, and whether an apparent outlier is actually unusual relative to other providers in the same month.

The pipeline turns NHS England A&E activity files into a provider-month dataset with four-hour performance measures, demand trends, peer flags and short-horizon forecasts.

## The data

The intended source is the NHS England **A&E Attendances and Emergency Admissions** monthly collection. Source files are not copied into this repository; the CLI accepts either a downloaded CSV or a direct CSV URL.

Official releases: https://www.england.nhs.uk/statistics/statistical-work-areas/ae-waiting-times-and-activity/ae-attendances-and-emergency-admissions-2026-27/

Every ingestion records a SHA-256 hash and source metadata. That sounds slightly excessive for a small project, but it makes later questions such as “why did this number change?” much easier to answer when a public dataset is revised.

## Flow

```text
NHS CSV
  -> raw parquet snapshot + provenance
  -> column/schema normalisation
  -> provider-month aggregation
  -> operational KPIs
       |-> peer anomaly flags
       |-> lag-only forecasting features
  -> parquet / SQL outputs for BI
```

The code lives under `src/nhs_ops/`; notebooks are not part of the execution path.

## Measures

The current provider-month model calculates:

- total attendances
- admitted/emergency activity where available
- number and rate within four hours
- four-hour breaches
- month-on-month movement
- peer-relative anomaly flags using median absolute deviation

The anomaly flag is deliberately an investigation signal, not a league table. A provider can look unusual for reasons that have nothing to do with poor performance: reporting differences, service mix, local demand shocks or a genuine operational change.

## Forecasting

Forecasting is kept separate from descriptive reporting. A provider needs at least 18 monthly observations before the function will run.

```bash
nhs-ops forecast R01 --metric attendances --horizon 3
```

The model uses lagged history and rolling features. Evaluation holds out the most recent observations chronologically and reports MAE before the model is refit for the forward forecast. Future target values are never used as features.

I would not use the resulting forecast for staffing decisions without a longer backtest and local context. It is here to show the forecasting workflow and its boundaries, not to imply that national public data is enough for operational deployment.

## Run it

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e '.[dev]'

nhs-ops build sample_data/ae_sample.csv
```

The sample file is synthetic and only exercises the data contract. With a real NHS release, the same command writes:

```text
data/processed/raw_snapshot.parquet
data/processed/provider_monthly_kpis.parquet
data/processed/provenance.json
data/processed/executive_snapshot.json
```

The SQL model in `sql/provider_monthly_kpis.sql` uses the same provider/month grain and is intended to be the hand-off point for Power BI or another BI tool.

## Checks

```bash
ruff check src tests
pytest -q
```

CI runs both on pushes and pull requests.

## Things I would add next

The most useful extension is not a more complex forecaster. I would first bring in RTT waiting-list data, define a small cross-domain set of pressure measures and test whether provider-level movement is stable after accounting for reporting/revision effects. I would also keep the newest reporting periods visibly marked when source completeness is uncertain.

## Repository map

```text
src/nhs_ops/       ingestion, transforms, KPIs and forecasting
sql/               BI-oriented model
sample_data/       synthetic contract fixture
tests/             unit tests
docs/              architecture notes
.github/workflows/ CI
```

**Prasanth Balisetty**