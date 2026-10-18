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
