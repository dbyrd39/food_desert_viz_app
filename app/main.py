import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.append(str(PROJECT_ROOT))

import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium

from src.layers.polygons import add_food_desert_layer, add_food_swamp_layer, add_county_boundaries, add_pop_weighted_food_desert_layer, add_pop_weighted_food_swamp_layer
from src.layers.points import add_point_layer

DATA_DIR = Path(__file__).resolve().parents[1] / "data" / "processed"

@st.cache_data(show_spinner=False)
def load_parquet(name: str) -> pd.DataFrame:
    return pd.read_parquet(DATA_DIR / name)

def main():
    st.set_page_config(page_title="NC Food Environment Map", layout="wide")
    st.title("North Carolina Food Environment Map")

    st.sidebar.header("Layers")
    show_deserts = st.sidebar.checkbox("Food deserts (polygons)", value=True)
    show_swamps = st.sidebar.checkbox("Food swamps (polygons)", value=False)
    show_healthy = st.sidebar.checkbox("Healthy food outlets (points)", value=True)
    show_unhealthy = st.sidebar.checkbox("Unhealthy food outlets (points)", value=False)
    show_counties = st.sidebar.checkbox("County boundaries", value=False)
    show_pop_weighted_desert = st.sidebar.checkbox("Food deserts (population-weighted)", value=False)
    show_pop_weighted_swamp = st.sidebar.checkbox("Food swamps (population-weighted)", value=False)


    m = folium.Map(location=[35.5, -79.0], zoom_start=7, tiles="CartoDB positron")
    tracts_geojson = DATA_DIR / "nc_tracts.geojson"

    if show_deserts:
        desert = load_parquet("food_desert_scores.parquet")
        add_food_desert_layer(m, tracts_geojson, desert)

    if show_swamps:
        swamp = load_parquet("food_swamp_scores.parquet")
        add_food_swamp_layer(m, tracts_geojson, swamp)

    if show_healthy:
        healthy = load_parquet("healthy_food.parquet")
        add_point_layer(m, healthy, "Healthy outlets", tooltip_cols=["name", "outlet_type"], color="#1a9850")

    if show_unhealthy:
        unhealthy = load_parquet("unhealthy_food.parquet")
        add_point_layer(m, unhealthy, "Unhealthy outlets", tooltip_cols=["name", "outlet_type"], color="#f46d43")

    if show_counties:
        add_county_boundaries(m, DATA_DIR / "nc_counties.geojson")

    
    if show_pop_weighted_desert:
        df = load_parquet("food_desert_population_weighted.parquet")
        add_pop_weighted_food_desert_layer(m, tracts_geojson, df)

    if show_pop_weighted_swamp:
        df = load_parquet("food_swamp_population_weighted.parquet")
        add_pop_weighted_food_swamp_layer(m, tracts_geojson, df)

    folium.LayerControl(collapsed=False).add_to(m)
    st_folium(m, use_container_width=True, height=720)

    with st.expander("Artifacts found in data/processed"):
        st.write(sorted([p.name for p in DATA_DIR.glob("*") if p.is_file()]))

if __name__ == "__main__":
    main()
