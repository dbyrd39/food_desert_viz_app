from __future__ import annotations
from pathlib import Path
import geopandas as gpd
import pandas as pd
import folium

def add_food_desert_layer(m: folium.Map, tracts_geojson: Path, desert_df: pd.DataFrame):
    gdf = gpd.read_file(tracts_geojson)
    merged = (
        gdf.merge(desert_df, on="GEOID", how="left")
        .fillna({"desert_severity": 0})
    )

    # Compute max severity for normalization (avoid division by zero)
    max_sev = max(merged["desert_severity"].max(), 1)

    def style_fn(feat):
        sev = feat["properties"].get("desert_severity", 0) or 0

        if sev <= 0:
            return {
                "fillOpacity": 0.0,
                "weight": 0.2,
                "opacity": 0.05,
            }

        # Normalize severity → opacity (0.2 → 0.75)
        norm = sev / max_sev
        fill_opacity = 0.2 + 0.55 * norm

        return {
            "fillColor": "#d73027",  # red
            "color": "#b22222",      # darker red outline
            "fillOpacity": fill_opacity,
            "weight": 0.6,
            "opacity": 0.4,
        }

    folium.GeoJson(
        data=merged.__geo_interface__,
        name="Food Deserts (polygons)",
        style_function=style_fn,
        tooltip=folium.GeoJsonTooltip(
            fields=["GEOID", "population", "desert_severity"],
            aliases=["Census Tract", "Population", "Desert Severity"],
        )

    ).add_to(m)


def add_food_swamp_layer(m: folium.Map, tracts_geojson: Path, swamp_df: pd.DataFrame):
    gdf = gpd.read_file(tracts_geojson)
    merged = (
        gdf.merge(swamp_df[["GEOID", "swamp_index"]], on="GEOID", how="left")
        .fillna({"swamp_index": 0.0})
    )

    # Cap extreme swamp values to stabilize color scaling
    cap = merged["swamp_index"].quantile(0.95)
    cap = max(cap, 1.0)

    def style_fn(feat):
        v = float(feat["properties"].get("swamp_index", 0.0) or 0.0)

        if v <= 0:
            return {
                "fillOpacity": 0.0,
                "weight": 0.2,
                "opacity": 0.05,
            }

        # Normalize and clamp
        norm = min(v / cap, 1.0)

        # Opacity range: 0.2 → 0.7
        fill_opacity = 0.2 + 0.5 * norm

        return {
            "fillColor": "#fee08b",  # yellow
            "color": "#d9a400",      # darker yellow outline
            "fillOpacity": fill_opacity,
            "weight": 0.6,
            "opacity": 0.4,
        }

    folium.GeoJson(
        data=merged.__geo_interface__,
        name="Food Swamps (polygons)",
        style_function=style_fn,
        tooltip=folium.GeoJsonTooltip(
            fields=["GEOID", "population", "swamp_index"],
            aliases=["Census Tract", "Population", "Food Swamp Index"],
        )

    ).add_to(m)

def add_pop_weighted_food_desert_layer(m, tracts_geojson: Path, df: pd.DataFrame):
    gdf = gpd.read_file(tracts_geojson)
    merged = gdf.merge(
        df[["GEOID", "pop_weighted_desert"]],
        on="GEOID",
        how="left"
    ).fillna({"pop_weighted_desert": 0})

    cap = merged["pop_weighted_desert"].quantile(0.95)
    cap = max(cap, 1)

    def style_fn(feat):
        v = feat["properties"].get("pop_weighted_desert", 0)
        if v <= 0:
            return {"fillOpacity": 0.0, "weight": 0.2, "opacity": 0.05}

        norm = min(v / cap, 1.0)
        fill_opacity = 0.25 + 0.55 * norm

        return {
            "fillColor": "#d73027",
            "color": "#b22222",
            "fillOpacity": fill_opacity,
            "weight": 0.6,
            "opacity": 0.4,
        }

    folium.GeoJson(
        merged.__geo_interface__,
        name="Food Deserts (population-weighted)",
        style_function=style_fn,
        tooltip=folium.GeoJsonTooltip(
            fields=["GEOID", "pop_weighted_desert"],
            aliases=["Census Tract", "Population-weighted desert impact"],
        ),
    ).add_to(m)

def add_pop_weighted_food_swamp_layer(m, tracts_geojson: Path, df: pd.DataFrame):
    gdf = gpd.read_file(tracts_geojson)
    merged = gdf.merge(
        df[["GEOID", "pop_weighted_swamp"]],
        on="GEOID",
        how="left"
    ).fillna({"pop_weighted_swamp": 0})

    cap = merged["pop_weighted_swamp"].quantile(0.95)
    cap = max(cap, 1)

    def style_fn(feat):
        v = feat["properties"].get("pop_weighted_swamp", 0)
        if v <= 0:
            return {"fillOpacity": 0.0, "weight": 0.2, "opacity": 0.05}

        norm = min(v / cap, 1.0)
        fill_opacity = 0.25 + 0.5 * norm

        return {
            "fillColor": "#fee08b",
            "color": "#d9a400",
            "fillOpacity": fill_opacity,
            "weight": 0.6,
            "opacity": 0.4,
        }

    folium.GeoJson(
        merged.__geo_interface__,
        name="Food Swamps (population-weighted)",
        style_function=style_fn,
        tooltip=folium.GeoJsonTooltip(
            fields=["GEOID", "pop_weighted_swamp"],
            aliases=["Census Tract", "Population-weighted swamp impact"],
        ),
    ).add_to(m)



def add_county_boundaries(m: folium.Map, counties_geojson: Path):
    gdf = gpd.read_file(counties_geojson)

    folium.GeoJson(
        gdf.__geo_interface__,
        name="County boundaries",
        style_function=lambda _: {
            "fillOpacity": 0.0,
            "color": "#2b2b2b",
            "weight": 1.2,
            "opacity": 0.6,
        },
        tooltip=folium.GeoJsonTooltip(fields=["NAME"], aliases=["County"]),
    ).add_to(m)
