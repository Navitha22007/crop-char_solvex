from .fetch_firms import fetch_hotspots
from .validate_boundaries import load_and_validate_boundaries
from .match import hotspots_to_geodf, match_to_fields
from .rules import load_permits, evaluate_hotspot_rules
from .offenders import update_offender_log, load_offender_log

def run_pipeline():
    """
    Runs the complete CropChar data processing pipeline:
    NASA FIRMS / Fallback Hotspots -> Spatial Join with Field Boundaries -> Permit & Season Checks -> Unauthorized Burn Detection -> Offender Tracking.

    Returns dict with source, hotspots list, and offender_counts dictionary.
    """
    # 1. Fetch hotspots (live or fallback)
    hotspots_df, source = fetch_hotspots()

    # 2. Convert points to GeoDataFrame
    hotspots_gdf = hotspots_to_geodf(hotspots_df)

    # 3. Load field boundaries
    fields_gdf = load_and_validate_boundaries()

    # 4. Perform spatial matching
    matched_gdf = match_to_fields(hotspots_gdf, fields_gdf)

    # 5. Load permits and evaluate rules
    permits_df = load_permits()
    evaluated_gdf = evaluate_hotspot_rules(matched_gdf, permits_df)

    # 6. Update repeat offender log
    offender_counts = update_offender_log(evaluated_gdf)

    # 7. Convert GeoDataFrame to clean JSON records (exclude Shapely geometry objects)
    hotspots_list = []
    if not evaluated_gdf.empty:
        for _, row in evaluated_gdf.iterrows():
            record = {
                "field_id": str(row.get("field_id", "unknown")),
                "owner": str(row.get("owner", "Unknown")),
                "crop_type": str(row.get("crop_type", "Unknown")),
                "latitude": float(row.get("latitude")),
                "longitude": float(row.get("longitude")),
                "acq_date": str(row.get("acq_date")),
                "acq_time": str(row.get("acq_time", "")) if "acq_time" in row and not str(row.get("acq_time")).startswith("nan") else "",
                "confidence": str(row.get("confidence", "high")),
                "unauthorized": bool(row.get("unauthorized", False))
            }
            hotspots_list.append(record)

    return {
        "source": source,
        "hotspots": hotspots_list,
        "offender_counts": offender_counts
    }

if __name__ == "__main__":
    result = run_pipeline()
    print(f"Pipeline executed successfully. Source: {result['source']}")
    print(f"Total matched hotspots: {len(result['hotspots'])}")
    print("Sample record:", result["hotspots"][0] if result["hotspots"] else "None")
    print("Offender counts:", result["offender_counts"])
