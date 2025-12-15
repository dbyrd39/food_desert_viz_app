from __future__ import annotations
from pathlib import Path
import json
from dataclasses import dataclass
import requests
import time
import pandas as pd

OVERPASS_URLS = [
    "https://overpass-api.de/api/interpreter",
    "https://overpass.kumi.systems/api/interpreter",
    "https://overpass.nchc.org.tw/api/interpreter",
]


@dataclass(frozen=True)
class BoundingBox:
    south: float
    west: float
    north: float
    east: float

NC_BBOX = BoundingBox(south=33.75, west=-84.45, north=36.6, east=-75.4)

def _overpass_query(bbox: BoundingBox, q_body: str) -> str:
    return f"""[out:json][timeout:180];
(
{q_body}
);
out center;"""


def _fetch_overpass(query: str) -> dict:
    last_err = None
    for url in OVERPASS_URLS:
        try:
            r = requests.post(url, data={"data": query}, timeout=300)
            r.raise_for_status()
            return r.json()
        except Exception as e:
            last_err = e
            time.sleep(5)
    raise RuntimeError(f"All Overpass endpoints failed. Last error: {last_err}")


CACHE_DIR = Path(__file__).resolve().parents[3] / "data" / "raw" / "cache"

def _fetch_with_cache(cache_name: str, query: str) -> dict:
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    path = CACHE_DIR / cache_name
    if path.exists():
        return json.loads(path.read_text())
    data = _fetch_overpass(query)
    path.write_text(json.dumps(data))
    return data

def _elements_to_points(elements: list[dict], outlet_type: str) -> pd.DataFrame:
    rows = []
    for el in elements:
        tags = el.get("tags", {})
        name = tags.get("name") or tags.get("brand") or tags.get("operator") or "Unknown"
        lat = el.get("lat") or (el.get("center") or {}).get("lat")
        lon = el.get("lon") or (el.get("center") or {}).get("lon")
        if lat is None or lon is None:
            continue
        rows.append({
            "name": name,
            "lat": float(lat),
            "lon": float(lon),
            "outlet_type": outlet_type,
            "osm_id": f"{el.get('type','')}/{el.get('id','')}",
        })
    return pd.DataFrame(rows)

def fetch_healthy_outlets(bbox: BoundingBox = NC_BBOX) -> pd.DataFrame:
    s,w,n,e = bbox.south, bbox.west, bbox.north, bbox.east
    q_body = f"""
node[shop=supermarket]({s},{w},{n},{e});
way[shop=supermarket]({s},{w},{n},{e});
node[shop=grocery]({s},{w},{n},{e});
way[shop=grocery]({s},{w},{n},{e});
node[amenity=marketplace]({s},{w},{n},{e});
way[amenity=marketplace]({s},{w},{n},{e});
"""
    data = _fetch_with_cache("osm_healthy.json", _overpass_query(bbox, q_body))
    return _elements_to_points(data.get("elements", []), "healthy")

def fetch_unhealthy_outlets(bbox: BoundingBox = NC_BBOX) -> pd.DataFrame:
    s,w,n,e = bbox.south, bbox.west, bbox.north, bbox.east
    q_body = f"""
node[amenity=fast_food]({s},{w},{n},{e});
way[amenity=fast_food]({s},{w},{n},{e});
"""
    data = _fetch_with_cache("osm_unhealthy.json", _overpass_query(bbox, q_body))
    return _elements_to_points(data.get("elements", []), "unhealthy")


