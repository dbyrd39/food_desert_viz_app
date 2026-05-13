from __future__ import annotations
import geopandas as gpd

def simplify_polygons(gdf: gpd.GeoDataFrame, tolerance: float = 0.001) -> gpd.GeoDataFrame:
    """Simplify polygon geometries to reduce file size while preserving topology.

    Args:
        gdf: GeoDataFrame whose geometries are simplified in place on a copy.
        tolerance: Simplification tolerance in the CRS units (degrees for
            EPSG:4326). Larger values produce coarser polygons.

    Returns:
        New GeoDataFrame with simplified, topologically valid geometries.
    """
    out = gdf.copy()
    out["geometry"] = out["geometry"].simplify(tolerance=tolerance, preserve_topology=True)
    out["geometry"] = out["geometry"].buffer(0)  # fix invalids
    return out

def drop_large_columns(gdf: gpd.GeoDataFrame, keep: list[str]) -> gpd.GeoDataFrame:
    """Return a GeoDataFrame containing only the specified columns plus geometry.

    Args:
        gdf: Source GeoDataFrame to subset.
        keep: Column names to retain. ``geometry`` is always included even if
            omitted from this list. Columns absent from ``gdf`` are silently
            ignored.

    Returns:
        New GeoDataFrame with only the kept columns and ``geometry``.
    """
    cols = [c for c in keep if c in gdf.columns]
    if "geometry" not in cols:
        cols.append("geometry")
    return gdf[cols]
