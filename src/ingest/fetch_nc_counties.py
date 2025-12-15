from pathlib import Path
import geopandas as gpd
import requests
import zipfile

from src.utils.cache import ensure_dir

TIGER_COUNTY_URL = (
    "https://www2.census.gov/geo/tiger/TIGER2022/COUNTY/tl_2022_us_county.zip"
)

def load_nc_counties(cache_dir: Path) -> gpd.GeoDataFrame:
    ensure_dir(cache_dir)

    zip_path = cache_dir / "tl_2022_us_county.zip"

    # Download once
    if not zip_path.exists():
        print("   downloading TIGER/Line US counties…")
        r = requests.get(TIGER_COUNTY_URL, stream=True, timeout=120)
        r.raise_for_status()
        with zip_path.open("wb") as f:
            for chunk in r.iter_content(1024 * 1024):
                if chunk:
                    f.write(chunk)

    extract_dir = cache_dir / "tl_2022_us_county"
    if not extract_dir.exists():
        with zipfile.ZipFile(zip_path, "r") as z:
            z.extractall(extract_dir)

    shp_files = list(extract_dir.glob("*.shp"))
    if not shp_files:
        raise FileNotFoundError("County shapefile not found after extraction.")

    gdf = gpd.read_file(shp_files[0]).to_crs("EPSG:4326")

    # Filter to North Carolina (STATEFP = '37')
    gdf = gdf[gdf["STATEFP"] == "37"]

    # Keep only what we need
    return gdf[["NAME", "geometry"]]
