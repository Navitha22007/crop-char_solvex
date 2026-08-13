import os
import pandas as pd
from datetime import datetime

DEFAULT_PERMITS_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "data",
    "permits_mock.csv"
)

def load_permits(filepath: str = None) -> pd.DataFrame:
    """Loads permit CSV file and formats dates."""
    if filepath is None:
        filepath = DEFAULT_PERMITS_PATH

    if not os.path.exists(filepath):
        print(f"Warning: Permits file not found at {filepath}. Returning empty permits DataFrame.")
        return pd.DataFrame(columns=["field_id", "permitted", "season_start", "season_end"])

    df = pd.read_csv(filepath)
    # Parse dates safely
    df["season_start"] = pd.to_datetime(df["season_start"]).dt.date
    df["season_end"] = pd.to_datetime(df["season_end"]).dt.date
    
    # Normalize permitted column to boolean
    if "permitted" in df.columns:
        df["permitted"] = df["permitted"].astype(str).str.lower().isin(["true", "1", "yes", "t"])

    return df

def is_unauthorized(field_id: str, acq_date_val, permits_df: pd.DataFrame) -> bool:
    """
    Logic:
    - Locate field in permit dataset.
    - If field not found in permit dataset -> Unauthorized (True).
    - Convert acquisition date and season dates to date objects.
    - Check if acquisition date falls within season window.
    - If in season and permitted is False -> Unauthorized (True).
    - Otherwise -> Authorized / Cleared (False).
    """
    field_permits = permits_df[permits_df["field_id"] == field_id]
    if field_permits.empty:
        # No permit record found for field
        return True

    record = field_permits.iloc[0]
    permitted = bool(record["permitted"])
    season_start = record["season_start"]
    season_end = record["season_end"]

    # Convert acquisition date to datetime.date
    if isinstance(acq_date_val, str):
        try:
            acq_date = datetime.strptime(acq_date_val, "%Y-%m-%d").date()
        except ValueError:
            acq_date = pd.to_datetime(acq_date_val).date()
    elif isinstance(acq_date_val, (pd.Timestamp, datetime)):
        acq_date = acq_date_val.date()
    else:
        acq_date = acq_date_val

    # Check if hotspot occurred during the burn season
    is_in_season = (season_start <= acq_date <= season_end)

    if is_in_season and not permitted:
        return True
    
    return False

def evaluate_hotspot_rules(matched_gdf, permits_df: pd.DataFrame):
    """
    Applies unauthorized burn rules across all matched hotspots in a GeoDataFrame.
    Adds 'unauthorized' boolean column.
    """
    if matched_gdf.empty:
        matched_gdf["unauthorized"] = []
        return matched_gdf

    unauthorized_flags = []
    for _, row in matched_gdf.iterrows():
        field_id = row.get("field_id", "unknown")
        acq_date = row.get("acq_date", datetime.now().strftime("%Y-%m-%d"))
        flag = is_unauthorized(field_id, acq_date, permits_df)
        unauthorized_flags.append(flag)

    matched_gdf["unauthorized"] = unauthorized_flags
    return matched_gdf
