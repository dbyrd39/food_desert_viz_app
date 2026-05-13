from __future__ import annotations
from pathlib import Path
import pandas as pd
import requests
from src.utils.cache import ensure_dir

DEFAULT_LOCAL_NAME = "usda_food_access.csv"

def get_usda_food_access(cache_dir: Path, url: str | None = None) -> Path:
    """Return the path to the USDA Food Access Research Atlas CSV, downloading if needed.

    Args:
        cache_dir: Directory where the CSV is cached after download.
        url: Optional HTTPS URL to download the CSV from if it is not already
            cached. Raises ``FileNotFoundError`` if omitted and the file is absent.

    Returns:
        Path to the local CSV file.
    """
    ensure_dir(cache_dir)
    out = cache_dir / DEFAULT_LOCAL_NAME
    if out.exists():
        return out
    if not url:
        raise FileNotFoundError(
            f"USDA food access CSV not found at {out}. "
            "Place it there or pass a download URL via url=..."
        )
    r = requests.get(url, stream=True, timeout=120)
    r.raise_for_status()
    with out.open("wb") as f:
        for chunk in r.iter_content(chunk_size=1024 * 1024):
            if chunk:
                f.write(chunk)
    return out

def load_usda_food_access(cache_dir: Path, url: str | None = None) -> pd.DataFrame:
    """Load the USDA Food Access Research Atlas CSV into a DataFrame.

    Args:
        cache_dir: Directory where the CSV is cached after download.
        url: Optional HTTPS URL to download the CSV from if it is not already
            cached. Passed through to ``get_usda_food_access``.

    Returns:
        DataFrame containing all columns from the USDA food access CSV.
    """
    return pd.read_csv(get_usda_food_access(cache_dir, url=url), low_memory=False)
