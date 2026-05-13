from __future__ import annotations
import geopandas as gpd
import pandas as pd

def points_to_gdf(df: pd.DataFrame, crs: str = "EPSG:4326") -> gpd.GeoDataFrame:
    """Convert a DataFrame with ``lat``/``lon`` columns to a GeoDataFrame.

    Args:
        df: DataFrame containing ``lat`` and ``lon`` columns of point coordinates.
        crs: Coordinate reference system string for the resulting GeoDataFrame;
            defaults to EPSG:4326 (WGS 84).

    Returns:
        GeoDataFrame with all original columns plus a ``geometry`` column of
        Point objects in the specified CRS.
    """
    return gpd.GeoDataFrame(
        df.copy(),
        geometry=gpd.points_from_xy(df["lon"], df["lat"]),
        crs=crs,
    )

def spatial_join_points_to_tracts(points_gdf: gpd.GeoDataFrame, tracts_gdf: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    """Spatially join outlet points to census tract polygons, adding a ``GEOID`` column.

    Args:
        points_gdf: GeoDataFrame of outlet points to join. Reprojected
            automatically if its CRS differs from ``tracts_gdf``.
        tracts_gdf: GeoDataFrame of census tract polygons with a ``GEOID``
            column.

    Returns:
        GeoDataFrame with all columns from ``points_gdf`` plus ``GEOID`` from
        the containing tract. Points that fall outside every tract receive a
        null ``GEOID``.
    """
    if points_gdf.crs != tracts_gdf.crs:
        points_gdf = points_gdf.to_crs(tracts_gdf.crs)
    joined = gpd.sjoin(points_gdf, tracts_gdf[["GEOID", "geometry"]], how="left", predicate="within")
    if "index_right" in joined.columns:
        joined = joined.drop(columns=["index_right"])
    return joined
