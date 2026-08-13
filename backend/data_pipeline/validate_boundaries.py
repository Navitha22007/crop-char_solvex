import os
import geopandas as gpd

DEFAULT_BOUNDARIES_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "data",
    "sample_boundaries.geojson"
)

def load_and_validate_boundaries(filepath=None):
    """
    Loads field boundaries GeoJSON file and validates its coordinate reference system (CRS).
    Returns GeoDataFrame with EPSG:4326 geometry.
    """
    if filepath is None:
        filepath = DEFAULT_BOUNDARIES_PATH

    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Field boundaries file not found at: {filepath}")

    gdf = gpd.read_file(filepath)

    # Inspect and validate CRS
    crs = gdf.crs
    print(f"Loaded {len(gdf)} field boundaries from {filepath}")
    print(f"CRS detected: {crs}")

    # Ensure CRS is EPSG:4326 (WGS84 lat/lon)
    if gdf.crs is None or gdf.crs.to_string() != "EPSG:4326":
        print("Warning: CRS was not explicitly EPSG:4326. Converting to EPSG:4326...")
        gdf = gdf.set_crs("EPSG:4326", allow_override=True)

    print("Sample field attributes:")
    print(gdf[["field_id", "owner", "crop_type", "geometry"]].head())

    return gdf

if __name__ == "__main__":
    load_and_validate_boundaries()
