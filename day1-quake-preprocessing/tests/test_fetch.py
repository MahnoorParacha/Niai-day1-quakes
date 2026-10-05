from quakes.fetch import geojson_to_df

SAMPLE = {"features": [
    {"id": "us1",
     "properties": {"mag": 4.6, "place": "10 km SW of Ridgecrest, CA",
                    "time": 1700000000000, "updated": 1700000100000,
                    "type": "earthquake", "status": "reviewed", "nst": None},
     "geometry": {"coordinates": [-117.5, 35.6, 8.2]}},
    {"id": "us2",
     "properties": {"mag": None, "place": "Mid-Atlantic Ridge",
                    "time": 1700000500000, "updated": 1700000600000,
                    "type": "Explosion", "status": "automatic"},
     "geometry": {"coordinates": [-30.1, 10.2, 10.0]}},
]}


def test_geojson_to_df():
    df = geojson_to_df(SAMPLE)
    assert len(df) == 2
    assert {"id", "mag", "lon", "lat", "depth_km"} <= set(df.columns)
    assert df.loc[0, "lon"] == -117.5 and df.loc[0, "depth_km"] == 8.2
