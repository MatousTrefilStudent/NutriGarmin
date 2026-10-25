from datetime import datetime

from garminconnect import Garmin

from fastapi import APIRouter

from data_input import unified_activity_service

# ==========================================
# ROUTER CONFIGURATION
# ==========================================
# Grouping endpoints under '/api/manual' prefix for Swagger UI documentation
router = APIRouter(prefix="/api/garmin", tags=["Manual Input"])

# ==========================================
# 1. INPUT REQUEST PAYLOADS (Pydantic Models)
# ==========================================

class GarminActivityInput(unified_activity_service.UnifiedActivityData):
    pass


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

    return {"message": "Garmin activity added successfully", "data": activity.model_dump()}


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

    activities = client.get_activities_by_date("2025-01-17", "2026-10-25")  # Example date range; adjust as needed

    #activities = client.get_activities()

    saved_activities = []
    for i in activities:
        print(i)
        start_time_local = i.get("startTimeLocal", "2026-10-17")
        activity = GarminActivityInput(
            date=datetime.fromisoformat(start_time_local).date(),
            activity_type=i.get("activityType", {}).get("typeKey", "unknown"),
            seconds_of_duration=round(float(i.get("duration", 0))),
            calories_burned=i.get("calories", 0)
        )
        saved_activities.append(add_garmin_activity(activity))
        print(activity)

    return saved_activities
        
