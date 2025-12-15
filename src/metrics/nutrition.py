from __future__ import annotations
import pandas as pd

def compute_nutrition_scores_stub(healthy_points: pd.DataFrame):
    stores = healthy_points.copy()
    stores["nutrition_score"] = 0.0
    tract = (
        stores.dropna(subset=["GEOID"])
        .groupby("GEOID")["nutrition_score"]
        .mean()
        .rename("nutrition_score")
        .reset_index()
    )
    return stores[["name", "lat", "lon", "GEOID", "nutrition_score"]], tract
