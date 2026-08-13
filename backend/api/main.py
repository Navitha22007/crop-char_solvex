from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import sys
import os

# Ensure backend directory is in python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data_pipeline import run_pipeline
from alerts import send_alert

app = FastAPI(
    title="CropChar API",
    description="Crop Residue & Unauthorized Burning Monitoring Backend API",
    version="1.0.0"
)

# Enable CORS for local development (React frontend on localhost:3000)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class AlertRequest(BaseModel):
    field_id: str
    acq_date: str

@app.get("/")
def read_root():
    return {"status": "CropChar backend is alive"}

@app.get("/favicon.ico", include_in_schema=False)
def favicon():
    from fastapi.responses import Response
    return Response(status_code=204)


@app.get("/hotspots")
def get_hotspots():
    """
    Executes the spatial matching & rule evaluation pipeline.
    Returns detected hotspots and offender frequency statistics.
    """
    try:
        data = run_pipeline()
        return data
    except Exception as e:
        print(f"[API ERROR] Pipeline failed: {e}")
        raise HTTPException(
            status_code=500,
            detail="An error occurred while processing crop hotspot data."
        )

@app.post("/alerts/trigger")
def trigger_alert(request: AlertRequest):
    """
    Triggers an email notification for an unauthorized burn detection on a specified field.
    """
    if not request.field_id:
        raise HTTPException(status_code=400, detail="field_id is required.")

    result = send_alert(request.field_id, request.acq_date)
    return result
