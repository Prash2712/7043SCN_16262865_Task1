# Architecture

## Flow

```text
NHS England monthly A&E CSV
        |
        v
Provenance-aware ingestion
(source URL/path + SHA-256)
        |
        v
Raw parquet snapshot
        |
        v
Schema contract + data-quality rules
        |
        v
Canonical provider/month records
        |
        +-------------------+
        |                   |
        v                   v
KPI / anomaly layer     Forecasting layer
        |                   |
        +---------+---------+
                  v
        BI-ready parquet / SQL
```

## Engineering decisions

1. **Raw data is not silently mutated.** The ingestion layer captures a SHA-256 hash and materialises a raw snapshot.
2. **Source schemas are treated as external contracts.** Column aliases are normalised into a small canonical model; missing required fields fail fast.
3. **Resampling and model evaluation are chronological.** Forecast features are lagged and the hold-out is the most recent block of observations.
4. **No forecast is presented without an error measure.** The CLI exposes hold-out MAE before future predictions.
5. **Synthetic fixtures are clearly separated from source data.** `sample_data/` exists only to exercise the pipeline.

## Intended BI model

The principal analytical grain is **provider x month**. Recommended dimensions are provider, calendar month, region/system and organisational hierarchy. Measures include attendances, emergency admissions, four-hour completions, breaches, rates and month-on-month change.

## Limitations

The repository does not claim clinical causality. A&E operational measures are affected by coding, provider configuration, demand mix and reporting changes. Anomaly flags identify records for investigation rather than proving under-performance.
