from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from datetime import date

from data_input import unified_activity_service

# ==========================================
# ROUTER CONFIGURATION
# ==========================================
# Grouping endpoints under '/api/manual' prefix for Swagger UI documentation
router = APIRouter(prefix="/api/manual", tags=["Manual Input"])


# ==========================================
# 1. INPUT REQUEST PAYLOADS (Pydantic Models)
# ==========================================

class ManualActivityInput(BaseModel):
    date: date
    activity_type: str
    duration_minutes: int
    calories_burned: int

class ManualFoodInput(BaseModel):
    date: date
    food_item: str
    calories_consumed: int
    protein_grams: float
    carbs_grams: float
    fat_grams: float


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
    return {"message": "Manual activity added successfully", "data": activity.dict()}


def main():
    """Save five example manual activities to the database."""
    activities = [
        ManualActivityInput(date=date.today(), activity_type="Walking", duration_minutes=30, calories_burned=150),
        ManualActivityInput(date=date.today(), activity_type="Running", duration_minutes=25, calories_burned=280),
        ManualActivityInput(date=date.today(), activity_type="Cycling", duration_minutes=45, calories_burned=350),
        ManualActivityInput(date=date.today(), activity_type="Swimming", duration_minutes=40, calories_burned=300),
        ManualActivityInput(date=date.today(), activity_type="Strength training", duration_minutes=35, calories_burned=220),
    ]

    for activity in activities:
        unified_activity_service.save_activity_to_db(activity)


if __name__ == "__main__":
    main()

