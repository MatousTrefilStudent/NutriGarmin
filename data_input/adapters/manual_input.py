from datetime import date

from fastapi import APIRouter
from db.schemas import FoodBase

from data_input import unified_activity_service

# ==========================================
# ROUTER CONFIGURATION
# ==========================================
# Grouping endpoints under '/api/manual' prefix for Swagger UI documentation
router = APIRouter(prefix="/api/manual", tags=["Manual Input"])


# ==========================================
# 1. INPUT REQUEST PAYLOADS (Pydantic Models)
# ==========================================

class ManualActivityInput(unified_activity_service.UnifiedActivityData):
    pass

class ManualFoodInput(FoodBase):
    date: date


# ==========================================
# 2. ADAPTER ENDPOINTS
# ==========================================

@router.post("/activity")
def add_manual_activity(activity: ManualActivityInput):
    """
    Endpoint to add a manual activity entry.
    Backup in case the Garmin API is unavailable. Accepts a JSON payload with activity details.
    """
    unified_activity_service.save_activity_to_db(activity)

    # Here you would typically process the input and save it to a database or another service.
    # For demonstration, we will just return the received data.
    return {"message": "Manual activity added successfully", "data": activity.model_dump()}


def main():
    """Save five example manual activities to the database."""
    activities = [
        ManualActivityInput(date=date.today(), activity_type="Walking", seconds_of_duration=1800, calories_burned=150),
        ManualActivityInput(date=date.today(), activity_type="Running", seconds_of_duration=1500, calories_burned=280),
        ManualActivityInput(date=date.today(), activity_type="Cycling", seconds_of_duration=2700, calories_burned=350),
        ManualActivityInput(date=date.today(), activity_type="Swimming", seconds_of_duration=2400, calories_burned=300),
        ManualActivityInput(date=date.today(), activity_type="Strength training", seconds_of_duration=2100, calories_burned=220),
    ]

    for activity in activities:
        unified_activity_service.save_activity_to_db(activity)


if __name__ == "__main__":
    main()
