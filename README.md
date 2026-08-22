# NHS Operations Intelligence Platform

A production-style analytics project for turning NHS England monthly A&E activity data into **provider performance KPIs, data-quality controls, peer anomaly signals and leakage-aware forecasts**.

This repository is intentionally designed as an analytics-engineering system rather than a notebook exercise. The core pipeline is package-based, testable and reproducible; the output grain is suitable for SQL/Power BI consumption.

## Business questions

The project is structured around questions an operational performance team could actually ask:

- Which providers are experiencing rising A&E demand?
- Where is the four-hour performance rate deteriorating month on month?
- Which providers are unusual relative to peers in the same reporting month?
- What does the recent trajectory imply for short-horizon activity planning?
- Can every published KPI be traced back to a specific source snapshot?

## Data source

The target source is the official **NHS England A&E Attendances and Emergency Admissions** monthly collection. NHS England publishes provider-level activity, including attendances and the number discharged, admitted or transferred within four hours. July 2026 was published on 13 August 2026.

Official publication page:

https://www.england.nhs.uk/statistics/statistical-work-areas/ae-waiting-times-and-activity/ae-attendances-and-emergency-admissions-2026-27/

The repository does not redistribute NHS source files. Pass a downloaded CSV or direct CSV URL to the CLI.

## Architecture

```text
Official NHS CSV
      |
      v
Ingestion + SHA-256 provenance
      |
      v
Raw parquet snapshot
      |
      v
Schema contract / quality checks
      |
      v
Canonical provider-month model
      |
      +----------------------+-------------------+
      |                      |                   |
      v                      v                   v
Operational KPIs       Peer anomaly flags   Forecast features
      |                                          |
      +----------------------+-------------------+
                             v
                    BI-ready parquet / SQL
```

See [`docs/architecture.md`](docs/architecture.md) for design decisions and limitations.

## Engineering features

- HTTP or local-file ingestion
- SHA-256 source provenance
- Raw parquet snapshot materialisation
- Flexible column-alias resolution into a stable analytical contract
- Fail-fast required-field checks
- Four-hour rate and breach calculations
- Provider/month aggregation
- Month-on-month demand and breach-rate movement
- Median-absolute-deviation peer anomaly logic
- Lag-only forecasting features
- Chronological hold-out evaluation
- Recursive multi-month forecasts
- CLI entrypoint
- BI-oriented SQL model
- Unit tests and GitHub Actions CI

## Project layout

```text
.
├── src/nhs_ops/
│   ├── ingest.py
│   ├── transform.py
│   ├── kpis.py
│   ├── forecast.py
│   └── cli.py
├── sql/
│   └── provider_monthly_kpis.sql
├── tests/
├── sample_data/
├── docs/
├── .github/workflows/ci.yml
└── pyproject.toml
```

## Run locally

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e '.[dev]'

nhs-ops build sample_data/ae_sample.csv
```

The synthetic sample is only a contract fixture. For real analysis, replace it with an official NHS England monthly CSV.

Generated outputs:

```text
data/processed/raw_snapshot.parquet
data/processed/provider_monthly_kpis.parquet
data/processed/provenance.json
data/processed/executive_snapshot.json
```

## Forecasting

Forecasting is deliberately separated from descriptive performance reporting. A provider requires at least 18 monthly observations before the modelling function will run.

```bash
nhs-ops forecast R01 --metric attendances --horizon 3
```

The model uses lagged activity and rolling-history features, holds out the most recent observations for evaluation, reports **MAE**, then refits before recursively forecasting future months. Future target values are never used as input features.

## Power BI / analytics layer

`sql/provider_monthly_kpis.sql` defines the intended BI grain and measures. A Power BI implementation can sit directly on the provider/month output with pages for:

- executive overview
- provider benchmarking
- four-hour performance
- demand trends
- breach analysis
- anomaly investigation
- forecast and capacity planning
- data-quality/provenance checks

## What is not claimed

This project does **not** claim that statistical anomalies establish poor clinical performance, nor that a forecast is suitable for operational deployment without longer history, backtesting and local validation. The purpose of the anomaly layer is prioritisation for investigation.

## Quality controls

```bash
ruff check src tests
pytest -q
```

CI runs both checks on pushes and pull requests.

## Suggested repository name

The current GitHub shell contains an old university-style name. For a recruiter-facing portfolio, rename it to:

`nhs-operations-intelligence-platform`

The original coursework state is preserved on the `archive/original-coursework` branch.

## Author

**Prasanth Balisetty**  
Data Science · Analytics Engineering · Machine Learning
