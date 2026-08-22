from __future__ import annotations

import hashlib
from io import BytesIO
from pathlib import Path
from urllib.parse import urlparse

import pandas as pd
import requests


def _sha256(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def read_csv_source(source: str | Path, timeout: int = 30) -> tuple[pd.DataFrame, dict[str, str]]:
    """Read a CSV from a local path or HTTPS URL and return provenance metadata."""
    source_text = str(source)
    parsed = urlparse(source_text)

    if parsed.scheme in {"http", "https"}:
        response = requests.get(source_text, timeout=timeout)
        response.raise_for_status()
        payload = response.content
        frame = pd.read_csv(BytesIO(payload))
        metadata = {
            "source": source_text,
            "sha256": _sha256(payload),
            "content_type": response.headers.get("content-type", ""),
        }
        return frame, metadata

    path = Path(source_text).expanduser().resolve()
    payload = path.read_bytes()
    return pd.read_csv(BytesIO(payload)), {
        "source": str(path),
        "sha256": _sha256(payload),
        "content_type": "text/csv",
    }


def persist_raw(frame: pd.DataFrame, output_path: str | Path) -> Path:
    """Persist an immutable-ish raw snapshot as parquet for downstream processing."""
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    frame.to_parquet(path, index=False)
    return path
