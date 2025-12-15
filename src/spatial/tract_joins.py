from __future__ import annotations
import geopandas as gpd
import pandas as pd

def points_to_gdf(df: pd.DataFrame, crs: str = "EPSG:4326") -> gpd.GeoDataFrame:
    return gpd.GeoDataFrame(
        df.copy(),
        geometry=gpd.points_from_xy(df["lon"], df["lat"]),
        crs=crs,
    )

def spatial_join_points_to_tracts(points_gdf: gpd.GeoDataFrame, tracts_gdf: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    if points_gdf.crs != tracts_gdf.crs:
        points_gdf = points_gdf.to_crs(tracts_gdf.crs)
    joined = gpd.sjoin(points_gdf, tracts_gdf[["GEOID", "geometry"]], how="left", predicate="within")
    if "index_right" in joined.columns:
        joined = joined.drop(columns=["index_right"])
    return joined
