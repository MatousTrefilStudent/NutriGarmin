from garminconnect import Garmin

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from datetime import date

from data_input import unified_activity_service

# ==========================================
# ROUTER CONFIGURATION
# ==========================================
# Grouping endpoints under '/api/manual' prefix for Swagger UI documentation
router = APIRouter(prefix="/api/garmin", tags=["Manual Input"])

# ==========================================
# 1. INPUT REQUEST PAYLOADS (Pydantic Models)
# ==========================================

class GarminActivityInput(BaseModel):
    date: date
    activity_type: str
    duration_minutes: int
    calories_burned: int


# ==========================================
# 2. ADAPTER ENDPOINTS
# ==========================================

@router.post("/activity")
def add_garmin_activity(activity: GarminActivityInput):
    """
    Endpoint to add a manual activity entry.
    Backup in case the Garmin API is unavailable. Accepts a JSON payload with activity details.
    """

    unified_activity_service.save_activity_to_db(activity)

    # Here you would typically process the input and save it to a database or another service.
    # For demonstration, we will just return the received data.
    return {"message": "Manual activity added successfully", "data": activity.dict()}


def sync_garmin_data(GARMIN_EMAIL: str, GARMIN_PASSWORD: str):
    """
    Function to sync data from Garmin Connect.
    This function can be called periodically or triggered by an event.

    Args:
        GARMIN_EMAIL (str): Garmin Connect email.
        GARMIN_PASSWORD (str): Garmin Connect password.
    """
    print("Connecting to Garmin Connect...")
    client = Garmin(GARMIN_EMAIL, GARMIN_PASSWORD)
    client.login()
    print("Login successful!")

    activities = client.get_activities_by_date("2026-10-17", "2026-10-17")  # Example date range; adjust as needed

    for i in activities:
        print(i)
        temp= GarminActivityInput(
            date=i.get("startTimeLocal", "2026-10-17").split("T")[0],  # Extract date from datetime string
            activity_type=i.get("activityType", {}).get("typeKey", "unknown"),
            duration_minutes=round(i.get("duration", 0) / 60, 1),
            calories_burned=i.get("calories", 0)
        )
        add_garmin_activity(temp)  # Save each activity to the database
        print(temp)
        

