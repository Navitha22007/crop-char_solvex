import os
import io
import requests
import pandas as pd
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
FALLBACK_CSV_PATH = os.path.join(BASE_DIR, "data", "sample_hotspots.csv")
RAW_HOTSPOTS_PATH = os.path.join(BASE_DIR, "data", "raw_hotspots.csv")

def filter_by_confidence(df: pd.DataFrame) -> pd.DataFrame:
    """
    Filters out low-confidence hotspot detections.
    Handles numeric confidence values (e.g. 0-100) and categorical strings ('low', 'nominal', 'high').
    """
    if "confidence" not in df.columns or df.empty:
        return df

    def is_valid_confidence(val):
        if pd.isna(val):
            return True
        val_str = str(val).strip().lower()
        if val_str == "low":
            return False
        if val_str in ("nominal", "high"):
            return True
        # Try numeric conversion
        try:
            num = float(val_str)
            return num >= 50.0  # Accept confidence >= 50%
        except ValueError:
            return True

    valid_mask = df["confidence"].apply(is_valid_confidence)
    return df[valid_mask].copy()

def fetch_hotspots() -> tuple[pd.DataFrame, str]:
    """
    Fetches thermal fire hotspot data from NASA FIRMS API.
    If the API key is missing, network fails, or response is invalid/empty,
    it gracefully falls back to data/sample_hotspots.csv.

    Returns:
        (DataFrame, data_source) where data_source is 'live' or 'fallback'.
    """
    firms_key = os.getenv("FIRMS_MAP_KEY", "").strip()
    source = os.getenv("FIRMS_SOURCE", "VIIRS_SNPP_NRT").strip()
    area = os.getenv("FIRMS_BBOX", "78.0,10.5,78.5,11.0").strip()
    day_range = os.getenv("FIRMS_DAY_RANGE", "1").strip()

    # Check if a real FIRMS key is configured
    if firms_key and firms_key != "YOUR_NASA_FIRMS_MAP_KEY":
        url = f"https://firms.modaps.eosdis.nasa.gov/api/area/csv/{firms_key}/{source}/{area}/{day_range}"
        print(f"Attempting live NASA FIRMS fetch from: {url}")
        try:
            response = requests.get(url, timeout=3)
            if response.status_code == 200 and response.text.strip():
                df = pd.read_csv(io.StringIO(response.text))
                
                # Check for required columns
                required_cols = {"latitude", "longitude", "acq_date"}
                if required_cols.issubset(df.columns) and not df.empty:
                    # Save raw live hotspots for audit
                    os.makedirs(os.path.dirname(RAW_HOTSPOTS_PATH), exist_ok=True)
                    df.to_csv(RAW_HOTSPOTS_PATH, index=False)

                    filtered_df = filter_by_confidence(df)
                    print(f"Live FIRMS data successfully fetched ({len(filtered_df)} hotspots after filtering).")
                    return filtered_df, "live"
                else:
                    print("Live FIRMS response lacked required columns or was empty.")
            else:
                print(f"NASA FIRMS API returned status code {response.status_code}")
        except Exception as e:
            print(f"Failed to fetch live NASA FIRMS data: {e}")

    # Fallback Mode
    print(f"Using fallback offline dataset from {FALLBACK_CSV_PATH}")
    if os.path.exists(FALLBACK_CSV_PATH):
        df = pd.read_csv(FALLBACK_CSV_PATH)
        filtered_df = filter_by_confidence(df)
        return filtered_df, "fallback"
    else:
        print("Fallback CSV file not found! Returning empty DataFrame.")
        return pd.DataFrame(columns=["latitude", "longitude", "acq_date", "confidence"]), "fallback"

if __name__ == "__main__":
    df, source = fetch_hotspots()
    print(f"Fetch completed. Source: {source}, Records: {len(df)}")
    print(df.head())
