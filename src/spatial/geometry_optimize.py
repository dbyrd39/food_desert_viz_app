from __future__ import annotations
import geopandas as gpd

def simplify_polygons(gdf: gpd.GeoDataFrame, tolerance: float = 0.001) -> gpd.GeoDataFrame:
    out = gdf.copy()
    out["geometry"] = out["geometry"].simplify(tolerance=tolerance, preserve_topology=True)
    out["geometry"] = out["geometry"].buffer(0)  # fix invalids
    return out

def drop_large_columns(gdf: gpd.GeoDataFrame, keep: list[str]) -> gpd.GeoDataFrame:
    cols = [c for c in keep if c in gdf.columns]
    if "geometry" not in cols:
        cols.append("geometry")
    return gdf[cols]
