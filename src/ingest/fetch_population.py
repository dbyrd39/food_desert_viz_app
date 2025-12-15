from __future__ import annotations
from pathlib import Path
import requests
import pandas as pd

ACS_URL = "https://api.census.gov/data/2022/acs/acs5"

def fetch_nc_tract_population() -> pd.DataFrame:
    """
    Fetch total population per census tract in North Carolina
    using ACS 5-year estimates.
    """
    params = {
        "get": "B01003_001E",
        "for": "tract:*",
        "in": "state:37",
    }

    r = requests.get(ACS_URL, params=params, timeout=60)
    r.raise_for_status()
    data = r.json()

    df = pd.DataFrame(data[1:], columns=data[0])
    df["GEOID"] = (
        df["state"]
        + df["county"]
        + df["tract"]
    )

    df["population"] = pd.to_numeric(df["B01003_001E"], errors="coerce").fillna(0).astype(int)

    return df[["GEOID", "population"]]
