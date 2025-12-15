# from __future__ import annotations
# import pandas as pd
# import folium
# from folium.plugins import HeatMap

# def add_heatmap(m: folium.Map, df: pd.DataFrame, lat_col: str, lon_col: str, weight_col: str, name: str):
#     points = []
#     for row in df.itertuples(index=False):
#         d = row._asdict()
#         lat, lon = d.get(lat_col), d.get(lon_col)
#         w = d.get(weight_col, 1.0)
#         if pd.isna(lat) or pd.isna(lon):
#             continue
#         points.append([float(lat), float(lon), float(w)])
#     HeatMap(points, name=name, radius=18, blur=12, min_opacity=0.25).add_to(m)
