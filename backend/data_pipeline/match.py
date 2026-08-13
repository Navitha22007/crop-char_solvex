import geopandas as gpd
import pandas as pd
from shapely.geometry import Point

def hotspots_to_geodf(hotspots_df: pd.DataFrame) -> gpd.GeoDataFrame:
    """
    Converts a pandas DataFrame containing latitude and longitude columns
    into a GeoPandas GeoDataFrame with Point geometry in EPSG:4326.
    """
    if hotspots_df.empty or "latitude" not in hotspots_df.columns or "longitude" not in hotspots_df.columns:
        # Return empty GeoDataFrame
        return gpd.GeoDataFrame(geometry=[], crs="EPSG:4326")

    geometry = [Point(xy) for xy in zip(hotspots_df["longitude"], hotspots_df["latitude"])]
    gdf = gpd.GeoDataFrame(hotspots_df.copy(), geometry=geometry, crs="EPSG:4326")
    return gdf

def match_to_fields(hotspots_gdf: gpd.GeoDataFrame, fields_gdf: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    """
    Performs spatial join between hotspot points and field polygon boundaries.
    Attaches field attributes (e.g., field_id) to hotspots located within fields.
    """
    if hotspots_gdf.empty or fields_gdf.empty:
        return gpd.GeoDataFrame(geometry=[], crs="EPSG:4326")

    # Ensure both GeoDataFrames use the same Coordinate Reference System (EPSG:4326)
    if hotspots_gdf.crs != fields_gdf.crs:
        hotspots_gdf = hotspots_gdf.to_crs(fields_gdf.crs)

    # Perform spatial join using 'within' predicate (hotspot point inside field polygon)
    matched_gdf = gpd.sjoin(hotspots_gdf, fields_gdf, how="inner", predicate="within")

    # Clean up spatial join index columns if present
    if "index_right" in matched_gdf.columns:
        matched_gdf = matched_gdf.drop(columns=["index_right"])

    return matched_gdf
