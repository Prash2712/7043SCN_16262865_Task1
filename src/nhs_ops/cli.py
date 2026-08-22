from __future__ import annotations

import json
from pathlib import Path

import typer

from nhs_ops.forecast import forecast_metric
from nhs_ops.ingest import persist_raw, read_csv_source
from nhs_ops.kpis import executive_snapshot, provider_monthly_kpis
from nhs_ops.transform import canonicalise_ae

app = typer.Typer(help="NHS operational intelligence pipeline")


@app.command()
def build(
    source: str,
    output_dir: Path = Path("data/processed"),
) -> None:
    """Ingest, validate, transform and materialise provider-level KPI data."""
    raw, provenance = read_csv_source(source)
    output_dir.mkdir(parents=True, exist_ok=True)
    persist_raw(raw, output_dir / "raw_snapshot.parquet")

    canonical = canonicalise_ae(raw)
    kpis = provider_monthly_kpis(canonical)
    kpis.to_parquet(output_dir / "provider_monthly_kpis.parquet", index=False)
    (output_dir / "provenance.json").write_text(json.dumps(provenance, indent=2), encoding="utf-8")
    snapshot = executive_snapshot(kpis)
    (output_dir / "executive_snapshot.json").write_text(json.dumps(snapshot, indent=2), encoding="utf-8")
    typer.echo(json.dumps(snapshot, indent=2))


@app.command()
def forecast(
    provider_code: str,
    metric: str = "attendances",
    horizon: int = 3,
    input_path: Path = Path("data/processed/provider_monthly_kpis.parquet"),
) -> None:
    """Run a chronological hold-out evaluation and recursive monthly forecast."""
    import pandas as pd

    frame = pd.read_parquet(input_path)
    result = forecast_metric(frame, provider_code=provider_code, metric=metric, horizon=horizon)
    typer.echo(f"Hold-out MAE: {result.holdout_mae:.2f}")
    typer.echo(result.forecast.to_string(index=False))


if __name__ == "__main__":
    app()
