from __future__ import annotations
import pandas as pd
import folium
from folium.plugins import MarkerCluster

def add_point_layer(
    m: folium.Map,
    points_df: pd.DataFrame,
    name: str,
    tooltip_cols: list[str],
    color: str,
):
    cluster = MarkerCluster(name=name, disableClusteringAtZoom=13)
    cluster.add_to(m)

    for row in points_df.itertuples(index=False):
        d = row._asdict()
        lat, lon = d.get("lat"), d.get("lon")
        if pd.isna(lat) or pd.isna(lon):
            continue

        tooltip_parts = []
        for c in tooltip_cols:
            if c in d and d[c] is not None:
                tooltip_parts.append(f"{c}: {d[c]}")
        tooltip = "<br>".join(tooltip_parts) if tooltip_parts else name

        folium.CircleMarker(
            location=[float(lat), float(lon)],
            radius=3.5,
            color=color,          # outline
            fill=True,
            fill_color=color,     # fill
            fill_opacity=0.85,
            opacity=0.9,
            tooltip=folium.Tooltip(tooltip, sticky=True),
        ).add_to(cluster)

