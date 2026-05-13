from __future__ import annotations

from pathlib import Path
import zipfile
import requests
import geopandas as gpd

from src.utils.cache import ensure_dir

TIGER_TRACT_ZIP_URL = "https://www2.census.gov/geo/tiger/GENZ2023/shp/cb_2023_37_tract_500k.zip"

def download_nc_tracts_zip(cache_dir: Path, url: str = TIGER_TRACT_ZIP_URL) -> Path:
    """Download the NC census tract shapefile ZIP from TIGER/Line, caching locally.

    Args:
        cache_dir: Directory where the ZIP file is saved after download.
        url: HTTPS URL of the TIGER/Line shapefile ZIP; defaults to the 2023
            500k-resolution NC tract file.

    Returns:
        Path to the downloaded (or already-cached) ZIP file.
    """
    ensure_dir(cache_dir)
    out = cache_dir / "cb_2023_37_tract_500k.zip"
    if out.exists():
        return out
    r = requests.get(url, stream=True, timeout=120)
    r.raise_for_status()
    with out.open("wb") as f:
        for chunk in r.iter_content(chunk_size=1024 * 1024):
            if chunk:
                f.write(chunk)
    return out

def extract_zip(zip_path: Path, extract_dir: Path) -> Path:
    """Extract a ZIP archive into a directory.

    Args:
        zip_path: Path to the ZIP file to extract.
        extract_dir: Destination directory; created if it does not exist.

    Returns:
        Path to the directory containing the extracted files.
    """
    ensure_dir(extract_dir)
    with zipfile.ZipFile(zip_path, "r") as z:
        z.extractall(extract_dir)
    return extract_dir

def load_nc_tracts_gdf(cache_dir: Path) -> gpd.GeoDataFrame:
    """Load NC census tracts as a GeoDataFrame in EPSG:4326, downloading if needed.

    Args:
        cache_dir: Directory used to cache the downloaded ZIP and extracted
            shapefile.

    Returns:
        GeoDataFrame with at least ``GEOID`` (11-digit tract string) and
        ``geometry`` columns, projected to EPSG:4326.
    """
    zip_path = download_nc_tracts_zip(cache_dir)
    shp_dir = extract_zip(zip_path, cache_dir / "cb_2023_37_tract_500k")
    shp_files = list(shp_dir.glob("*.shp"))
    if not shp_files:
        raise FileNotFoundError(f"No .shp found in {shp_dir}")
    gdf = gpd.read_file(shp_files[0])
    if gdf.crs is None:
        gdf = gdf.set_crs("EPSG:4269", allow_override=True)
    gdf = gdf.to_crs("EPSG:4326")
    if "GEOID" not in gdf.columns:
        cols = [c for c in ["STATEFP", "COUNTYFP", "TRACTCE"] if c in gdf.columns]
        if len(cols) == 3:
            gdf["GEOID"] = (
                gdf["STATEFP"].astype(str)
                + gdf["COUNTYFP"].astype(str)
                + gdf["TRACTCE"].astype(str)
            )
        else:
            raise KeyError("GEOID not found and cannot be constructed from STATEFP/COUNTYFP/TRACTCE.")
    return gdf
