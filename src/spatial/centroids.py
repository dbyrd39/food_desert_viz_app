from __future__ import annotations
import geopandas as gpd
import pandas as pd

def tract_centroids(tracts: gpd.GeoDataFrame) -> pd.DataFrame:
    """Compute the geographic centroid of each census tract polygon.

    Args:
        tracts: GeoDataFrame with ``GEOID`` and ``geometry`` columns, projected
            to a CRS that yields meaningful centroid coordinates (e.g., EPSG:4326).

    Returns:
        DataFrame with columns ``GEOID``, ``lat`` (centroid latitude), and
        ``lon`` (centroid longitude).
    """
    c = tracts.copy()
    c["centroid"] = c.geometry.centroid
    return pd.DataFrame({"GEOID": c["GEOID"], "lat": c["centroid"].y, "lon": c["centroid"].x})
