from __future__ import annotations
import pandas as pd

def compute_food_swamp_index(healthy_points: pd.DataFrame, unhealthy_points: pd.DataFrame) -> pd.DataFrame:
    """Compute a per-tract food swamp index as unhealthy-to-healthy outlet ratio.

    Args:
        healthy_points: DataFrame of healthy outlets with a ``GEOID`` column
            identifying the census tract each point belongs to.
        unhealthy_points: DataFrame of unhealthy outlets with a ``GEOID`` column
            identifying the census tract each point belongs to.

    Returns:
        DataFrame with columns ``GEOID``, ``healthy_count`` (int),
        ``unhealthy_count`` (int), and ``swamp_index`` (float,
        ``unhealthy_count / (healthy_count + 1)``).
    """
    h = healthy_points.dropna(subset=["GEOID"]).groupby("GEOID").size().rename("healthy_count")
    u = unhealthy_points.dropna(subset=["GEOID"]).groupby("GEOID").size().rename("unhealthy_count")
    df = pd.concat([h, u], axis=1).fillna(0).reset_index()
    df["healthy_count"] = df["healthy_count"].astype(int)
    df["unhealthy_count"] = df["unhealthy_count"].astype(int)
    df["swamp_index"] = df["unhealthy_count"] / (df["healthy_count"] + 1.0)
    return df
