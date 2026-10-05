"""Task 1: fetch the USGS GeoJSON feed and turn it into a DataFrame."""
import pandas as pd
import requests

BASE = "https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary"


def fetch_feed(feed: str = "all_week") -> dict:
    """GET {BASE}/{feed}.geojson and return the parsed dict.

    Use a timeout and raise_for_status(). A misspelled feed name returns
    HTTP 200 with a plain-text body, so raise a clear error if the body
    is not valid JSON.
    """
    url = f"{BASE}/{feed}.geojson"
    response = requests.get(url, timeout=15)
    response.raise_for_status()
    try:
        return response.json()
    except ValueError:
        raise ValueError(f"Feed '{feed}' did not return valid JSON (check the feed name)")


def geojson_to_df(payload: dict) -> pd.DataFrame:
    """One row per event.
    Columns: 'id' (top level of each feature), every key in 'properties',
    plus 'lon', 'lat', 'depth_km' from geometry.coordinates = [lon, lat, depth].
    """
    rows = []
    for feature in payload["features"]:
        lon, lat, depth_km = feature["geometry"]["coordinates"]
        row = {"id": feature["id"], **feature["properties"]}
        row["lon"] = lon
        row["lat"] = lat
        row["depth_km"] = depth_km
        rows.append(row)
    return pd.DataFrame(rows)

