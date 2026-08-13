import os
import json

DEFAULT_OFFENDER_LOG_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "data",
    "offender_log.json"
)

def load_offender_log(filepath: str = None) -> dict:
    """Loads repeat offender counts from JSON file."""
    if filepath is None:
        filepath = DEFAULT_OFFENDER_LOG_PATH

    if not os.path.exists(filepath):
        return {}

    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading offender log ({e}). Starting fresh dictionary.")
        return {}

def save_offender_log(counts: dict, filepath: str = None):
    """Saves offender counts to JSON file."""
    if filepath is None:
        filepath = DEFAULT_OFFENDER_LOG_PATH

    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    try:
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(counts, f, indent=2)
    except Exception as e:
        print(f"Failed to save offender log: {e}")

def update_offender_log(records, filepath: str = None) -> dict:
    """
    Updates offender count log for all unauthorized burn records.
    Records can be a GeoDataFrame or a list of record dicts.
    """
    counts = load_offender_log(filepath)

    if hasattr(records, "iterrows"):
        for _, row in records.iterrows():
            if row.get("unauthorized", False):
                field_id = row.get("field_id")
                if field_id:
                    counts[field_id] = counts.get(field_id, 0) + 1
    elif isinstance(records, list):
        for rec in records:
            if rec.get("unauthorized", False):
                field_id = rec.get("field_id")
                if field_id:
                    counts[field_id] = counts.get(field_id, 0) + 1

    save_offender_log(counts, filepath)
    return counts
