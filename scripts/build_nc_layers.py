from __future__ import annotations
from pathlib import Path

from src.ingest.fetch_census_tracts import load_nc_tracts_gdf
from src.ingest.fetch_usda_food_access import load_usda_food_access
from src.ingest.fetch_osm_outlets import fetch_healthy_outlets, fetch_unhealthy_outlets
from src.ingest.fetch_nc_counties import load_nc_counties
from src.ingest.fetch_population import fetch_nc_tract_population
from src.spatial.geometry_optimize import simplify_polygons, drop_large_columns
from src.spatial.tract_joins import points_to_gdf, spatial_join_points_to_tracts
from src.spatial.centroids import tract_centroids
from src.metrics.food_desert import compute_food_desert_scores
from src.metrics.food_swamp import compute_food_swamp_index
from src.metrics.nutrition import compute_nutrition_scores_stub

PROJECT_ROOT = Path(__file__).resolve().parents[1]
RAW_CACHE = PROJECT_ROOT / "data" / "raw" / "cache"
PROCESSED = PROJECT_ROOT / "data" / "processed"

def main():
    PROCESSED.mkdir(parents=True, exist_ok=True)
    RAW_CACHE.mkdir(parents=True, exist_ok=True)

    print("1) Fetching NC census tracts…")
    tracts = load_nc_tracts_gdf(RAW_CACHE)

    print("1.5) Fetching ACS population data…")
    pop_df = fetch_nc_tract_population()
    pop_path = PROCESSED / "tract_population.parquet"
    pop_df.to_parquet(pop_path, index=False)
    print(f"   wrote {pop_path}")


    print("2) Simplifying tract geometries (offline)…")
    tracts_s = simplify_polygons(tracts, tolerance=0.001)
    tracts_s = tracts_s.merge(pop_df, on="GEOID", how="left")
    tracts_s["population"] = tracts_s["population"].fillna(0).astype(int)
    tracts_s = drop_large_columns(tracts_s, keep=["GEOID", "NAME", "COUNTYFP", "STATEFP", "population"])
    tracts_geojson_path = PROCESSED / "nc_tracts.geojson"
    tracts_s.to_file(tracts_geojson_path, driver="GeoJSON")
    print(f"   wrote {tracts_geojson_path}")




    print("3) Loading USDA Food Access data (official deserts)…")
    # Place your CSV here:
    #   data/raw/cache/usda_food_access.csv
    usda = load_usda_food_access(RAW_CACHE, url=None)
    desert_scores = compute_food_desert_scores(usda)
    desert_path = PROCESSED / "food_desert_scores.parquet"
    desert_scores.to_parquet(desert_path, index=False)
    print(f"   wrote {desert_path}")

    print("3.5) Computing population-weighted food desert impact…")

    desert_pop = desert_scores.merge(pop_df, on="GEOID", how="left")
    desert_pop["population"] = desert_pop["population"].fillna(0)

    desert_pop["pop_weighted_desert"] = (
        desert_pop["desert_severity"] * desert_pop["population"]
    )

    desert_pop_path = PROCESSED / "food_desert_population_weighted.parquet"
    desert_pop.to_parquet(desert_pop_path, index=False)
    print(f"   wrote {desert_pop_path}")


    print("4) Fetching outlets from OSM Overpass (points)…")
    healthy_pts = fetch_healthy_outlets()
    unhealthy_pts = fetch_unhealthy_outlets()

    print("5) Spatial join: outlets → tract GEOID…")
    healthy_gdf = points_to_gdf(healthy_pts)
    unhealthy_gdf = points_to_gdf(unhealthy_pts)

    joined_h = spatial_join_points_to_tracts(healthy_gdf, tracts_s)[["name", "lat", "lon", "outlet_type", "GEOID"]]
    joined_u = spatial_join_points_to_tracts(unhealthy_gdf, tracts_s)[["name", "lat", "lon", "outlet_type", "GEOID"]]

    healthy_path = PROCESSED / "healthy_food.parquet"
    unhealthy_path = PROCESSED / "unhealthy_food.parquet"
    joined_h.to_parquet(healthy_path, index=False)
    joined_u.to_parquet(unhealthy_path, index=False)
    print(f"   wrote {healthy_path}")
    print(f"   wrote {unhealthy_path}")

    print("6) Compute food swamp index (computed)…")
    swamp = compute_food_swamp_index(joined_h, joined_u)
    swamp_path = PROCESSED / "food_swamp_scores.parquet"
    swamp.to_parquet(swamp_path, index=False)
    print(f"   wrote {swamp_path}")

    print("6.5) Computing population-weighted food swamp impact…")

    swamp_pop = swamp.merge(pop_df, on="GEOID", how="left")
    swamp_pop["population"] = swamp_pop["population"].fillna(0)

    swamp_pop["pop_weighted_swamp"] = (
        swamp_pop["swamp_index"] * swamp_pop["population"]
    )

    swamp_pop_path = PROCESSED / "food_swamp_population_weighted.parquet"
    swamp_pop.to_parquet(swamp_pop_path, index=False)
    print(f"   wrote {swamp_pop_path}")


    print("7) Build heatmap inputs from tract centroids…")
    cents = tract_centroids(tracts_s)

    desert_w = desert_scores.merge(cents, on="GEOID", how="left")
    desert_w["weight"] = desert_w["desert_severity"].fillna(0).astype(float)
    desert_heat = desert_w[["lat", "lon", "weight"]].dropna()
    desert_heat_path = PROCESSED / "desert_heat.parquet"
    desert_heat.to_parquet(desert_heat_path, index=False)
    print(f"   wrote {desert_heat_path}")

    swamp_w = swamp.merge(cents, on="GEOID", how="left")
    swamp_w["weight"] = swamp_w["swamp_index"].fillna(0).astype(float)
    swamp_heat = swamp_w[["lat", "lon", "weight"]].dropna()
    swamp_heat_path = PROCESSED / "swamp_heat.parquet"
    swamp_heat.to_parquet(swamp_heat_path, index=False)
    print(f"   wrote {swamp_heat_path}")

    print("8) Nutrition scores (stub)…")
    store_nutrition, tract_nutrition = compute_nutrition_scores_stub(joined_h)
    store_nutrition.to_parquet(PROCESSED / "store_nutrition.parquet", index=False)
    tract_nutrition.to_parquet(PROCESSED / "nutrition_scores.parquet", index=False)
    print(f"   wrote {PROCESSED / 'store_nutrition.parquet'}")
    print(f"   wrote {PROCESSED / 'nutrition_scores.parquet'}")

    print("9) Fetching NC county boundaries…")
    counties = load_nc_counties(RAW_CACHE)
    counties.to_file(PROCESSED / "nc_counties.geojson", driver="GeoJSON")

    print("\nDone. Now run:")
    print("  streamlit run app/main.py")

if __name__ == "__main__":
    main()
