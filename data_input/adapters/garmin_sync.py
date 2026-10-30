from datetime import date, datetime
from typing import Optional

from fastapi import APIRouter, HTTPException
from garminconnect import Garmin
from pydantic import BaseModel, Field

from data_input import unified_activity_service

# ==========================================
# ROUTER CONFIGURATION
# ==========================================
router = APIRouter(prefix="/api/garmin", tags=["Garmin Connect"])

# ==========================================
# 1. INPUT REQUEST PAYLOADS (Pydantic Models)
# ==========================================

class GarminActivityInput(unified_activity_service.UnifiedActivityData):
    pass


class GarminSyncRequest(BaseModel):
    email: str = Field(..., description="Garmin Connect e-mail")
    password: str = Field(..., description="Garmin Connect heslo")
    date_start: str = Field("2026-10-17", description="Počáteční datum (YYYY-MM-DD)")
    date_end: str = Field("2026-10-17", description="Koncové datum (YYYY-MM-DD)")


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


@router.post("/sync")
def sync_activities(payload: GarminSyncRequest):
    """
    Endpoint to trigger Garmin Connect activity synchronization for a given date range.
    Downloads activities from Garmin and inserts them into the database.
    """
    try:
        saved_activities = sync_garmin_data(
            GARMIN_EMAIL=payload.email,
            GARMIN_PASSWORD=payload.password,
            date_start=payload.date_start,
            date_end=payload.date_end,
        )
        return {
            "status": "success",
            "message": f"Úspěšně synchronizováno {len(saved_activities)} aktivit.",
            "count": len(saved_activities),
            "data": saved_activities,
        }
    except Exception as exc:
        print(f"Error during Garmin sync: {exc}")
        raise HTTPException(
            status_code=400,
            detail=f"Chyba při synchronizaci s Garmin Connect: {str(exc)}"
        )


def sync_garmin_data(
    GARMIN_EMAIL: str,
    GARMIN_PASSWORD: str,
    date_start: str = "2026-10-17",
    date_end: str = "2026-10-17"
):
    """
    Function to sync data from Garmin Connect.
    This function can be called periodically or triggered by an event.

    Args:
        GARMIN_EMAIL (str): Garmin Connect email.
        GARMIN_PASSWORD (str): Garmin Connect password.
        date_start (str): Start date string YYYY-MM-DD.
        date_end (str): End date string YYYY-MM-DD.
    """
    print("Connecting to Garmin Connect...")
    client = Garmin(GARMIN_EMAIL, GARMIN_PASSWORD)
    client.login()
    print("Login successful!")

    activities = client.get_activities_by_date(date_start, date_end)

    saved_activities = []
    for i in activities:
        print(i)
        start_time_local = i.get("startTimeLocal") or date_start or "2026-10-17"
        if isinstance(start_time_local, str):
            activity_date = datetime.fromisoformat(start_time_local).date()
        elif hasattr(start_time_local, "date"):
            activity_date = start_time_local.date()
        else:
            activity_date = datetime.fromisoformat(str(start_time_local)).date()

        raw_duration = i.get("duration")
        seconds_of_duration = round(float(raw_duration)) if raw_duration is not None else 0

        raw_calories = i.get("calories")
        calories_burned = float(raw_calories) if raw_calories is not None else 0.0

        act_type = i.get("activityType")
        activity_type = (
            act_type.get("typeKey", "unknown")
            if isinstance(act_type, dict)
            else "unknown"
        )

        avg_hr = i.get("averageHR") or i.get("avgHR") or i.get("averageHeartRate")
        beats_per_minute_average = round(float(avg_hr)) if avg_hr is not None else None

        activity = GarminActivityInput(
            date=activity_date,
            activity_type=activity_type,
            seconds_of_duration=seconds_of_duration,
            calories_burned=calories_burned,
            beats_per_minute_average=beats_per_minute_average,
        )
        saved_activities.append(add_garmin_activity(activity))
        print(activity)

    return saved_activities
