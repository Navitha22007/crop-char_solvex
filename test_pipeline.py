import os
import sys
import unittest

# Add root directory to python path
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(ROOT_DIR)

from backend.data_pipeline import (
    load_and_validate_boundaries,
    fetch_hotspots,
    hotspots_to_geodf,
    match_to_fields,
    load_permits,
    is_unauthorized,
    run_pipeline,
    load_offender_log
)
from backend.alerts import send_alert
from fastapi.testclient import TestClient
from backend.api.main import app

class TestCropCharPipeline(unittest.TestCase):

    def test_01_load_boundaries(self):
        """Test GeoJSON field boundary loading and EPSG:4326 CRS validation."""
        gdf = load_and_validate_boundaries()
        self.assertFalse(gdf.empty, "Field boundaries GeoDataFrame should not be empty")
        self.assertIn("field_id", gdf.columns, "field_id column must exist in GeoJSON")
        self.assertEqual(str(gdf.crs), "EPSG:4326", "CRS must be EPSG:4326")
        print("[PASS] GeoJSON boundary validation test passed.")

    def test_02_fetch_hotspots(self):
        """Test hotspot data fetching (with fallback verification)."""
        df, source = fetch_hotspots()
        self.assertIn(source, ["live", "fallback"], "Source must be 'live' or 'fallback'")
        self.assertFalse(df.empty, "Hotspots DataFrame should not be empty")
        self.assertIn("latitude", df.columns)
        self.assertIn("longitude", df.columns)
        print(f"[PASS] Hotspot fetch test passed. Source: {source}, rows: {len(df)}")

    def test_03_spatial_matching(self):
        """Test Shapely conversion and GeoPandas spatial join matching."""
        df, _ = fetch_hotspots()
        hotspots_gdf = hotspots_to_geodf(df)
        fields_gdf = load_and_validate_boundaries()
        matched = match_to_fields(hotspots_gdf, fields_gdf)
        
        self.assertFalse(matched.empty, "Spatial join should match hotspots to field polygons")
        self.assertIn("field_id", matched.columns)
        print(f"[PASS] Spatial matching test passed. Matched points: {len(matched)}")

    def test_04_permit_rules(self):
        """Test permit window and unauthorized burn determination logic."""
        permits_df = load_permits()
        
        # Test unpermitted field during season -> Unauthorized (True)
        unauth_1 = is_unauthorized("field_01", "2026-11-02", permits_df)
        self.assertTrue(unauth_1, "field_01 should be flagged as unauthorized")

        # Test permitted field during season -> Cleared (False)
        unauth_2 = is_unauthorized("field_02", "2026-11-03", permits_df)
        self.assertFalse(unauth_2, "field_02 should be cleared / authorized")

        print("[PASS] Permit and unauthorized burn rule tests passed.")

    def test_05_full_pipeline(self):
        """Test end-to-end run_pipeline execution."""
        res = run_pipeline()
        self.assertIn("source", res)
        self.assertIn("hotspots", res)
        self.assertIn("offender_counts", res)
        self.assertTrue(isinstance(res["hotspots"], list))
        print("[PASS] End-to-end pipeline test passed.")

    def test_06_fastapi_endpoints(self):
        """Test FastAPI endpoints via TestClient."""
        client = TestClient(app)
        
        # GET /
        res_root = client.get("/")
        self.assertEqual(res_root.status_code, 200)
        self.assertEqual(res_root.json()["status"], "CropChar backend is alive")

        # GET /hotspots
        res_hotspots = client.get("/hotspots")
        self.assertEqual(res_hotspots.status_code, 200)
        data = res_hotspots.json()
        self.assertIn("hotspots", data)
        self.assertIn("offender_counts", data)

        # POST /alerts/trigger
        res_alert = client.post("/alerts/trigger", json={"field_id": "field_01", "acq_date": "2026-11-02"})
        self.assertEqual(res_alert.status_code, 200)
        self.assertIn("status", res_alert.json())

        print("[PASS] FastAPI endpoint tests passed.")

    def test_07_email_notifier_fallback(self):
        """Test that missing email credentials return simulated status without crashing."""
        res = send_alert("field_01", "2026-11-02")
        self.assertIn(res["status"], ["sent", "simulated", "error"])
        print(f"[PASS] Alert notifier test passed. Result status: {res['status']}")

if __name__ == "__main__":
    unittest.main()
