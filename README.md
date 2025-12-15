# North Carolina Food Environment Map (Streamlit + Folium)

This project builds an interactive map of **North Carolina** showing:
- **Food deserts** (USDA Food Access Research Atlas, tract polygons)
- **Food swamps** (computed index: unhealthy / (healthy + 1), tract polygons)
- **Healthy outlets** (points)
- **Unhealthy outlets** (points)
- **Heatmaps** for food desert severity and food swamp severity
- **Nutrition layer** (optional; implemented as a stub with a clear extension point)

## Why it’s fast
All heavy geospatial work (downloads, spatial joins, aggregations, geometry simplification) happens **offline**:
```bash
python scripts/build_nc_layers.py
```
The Streamlit app only **loads prebuilt artifacts** from `data/processed/` and renders them.

## Setup
```bash
python -m venv .venv
source .venv/bin/activate           # mac/linux
# .venv\Scripts\activate          # windows

pip install -r requirements.txt
```

## Build data artifacts
Run once (or whenever you want to refresh data):
```bash
python scripts/build_nc_layers.py
```

## Run the app
```bash
streamlit run app/main.py
```

## Data notes
- Census tracts are fetched from US Census TIGER/Line (NC tract cartographic boundary ZIP).
- Food deserts are computed from a USDA Food Access Research Atlas CSV (you provide the CSV in `data/raw/cache/usda_food_access.csv` or pass a URL in the build script).
- Food swamps are computed from OSM outlet counts per tract.
- Nutrition scores are a stub — the architecture is ready, but you’ll need a store→product link to make this meaningful.
