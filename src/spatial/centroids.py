from __future__ import annotations
import geopandas as gpd
import pandas as pd

def tract_centroids(tracts: gpd.GeoDataFrame) -> pd.DataFrame:
    c = tracts.copy()
    c["centroid"] = c.geometry.centroid
    return pd.DataFrame({"GEOID": c["GEOID"], "lat": c["centroid"].y, "lon": c["centroid"].x})
