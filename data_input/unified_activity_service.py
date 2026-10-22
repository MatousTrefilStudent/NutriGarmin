from datetime import date
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field
from db import ActivityRecord 

# ==========================================
# 1. UNIFIED DATA MODEL
# ==========================================

class UnifiedActivityData(BaseModel):
    """
    Standardized data structure (Adapter target) representing any physical activity,
    regardless of whether it came from Garmin Connect or Manual User Input.
    """
    source: str = Field(..., example="Manual", description="Source of data: 'Garmin Connect' or 'Manual'")
    date: str = Field(..., example="2026-10-18", description="Date in YYYY-MM-DD format")
    activity_name: str = Field(..., example="Running", description="Type or name of activity")
    duration_minutes: float = Field(..., gt=0, example=30.0, description="Duration in minutes")
    active_kcal: float = Field(..., ge=0, example=300.0, description="Active calories burned")
    bmr_kcal: float = Field(default=0.0, ge=0, example=0.0, description="Basal metabolic rate calories")
    total_kcal: float = Field(..., gt=0, example=300.0, description="Total calories burned (active + bmr)")


# ==========================================
# 2. CORE SERVICE LOGIC
# ==========================================

def save_activity_to_db(activity_data: UnifiedActivityData, db_session: Optional[Any] = None) -> Dict[str, Any]:
    """
    Saves unified activity data into the database and recalculates daily energy expenditure.
    
    Args:
        activity_data: Instance of UnifiedActivityData.
        db_session: Optional SQLAlchemy DB session instance.
        
    Returns:
        Dict containing execution status and saved data payload.
    """

    #Temp solution for demonstration purposes (no actual DB operations):
    print(f"DEBUG: Saving activity to DB: {activity_data.dict()}")
    
    # ------------------------------------------------------------------
    # Step A: Database Persistence (Production ORM Example)
    # ------------------------------------------------------------------
    db_activity = ActivityRecord(
        user_id="tesst",
        source=activity_data.source,
        date=activity_data.date,
        activity_name=activity_data.activity_name,
        duration_minutes=activity_data.duration_minutes,
        burned_kcal=activity_data.total_kcal
    )
    db_session.add(db_activity)
    db_session.commit()
    # ------------------------------------------------------------------



    # ------------------------------------------------------------------
    # Step B: Recalculate Daily Summary (DENNI_SOUHRN)
    # ------------------------------------------------------------------
    #updated_summary = recalculate_daily_summary(activity_data.date, db_session)

    # ------------------------------------------------------------------
    # Step C: Return Response Output
    # ------------------------------------------------------------------
    # return {
    #     "status": "success",
    #     "message": f"Activity successfully saved from source '{activity_data.source}' and daily balance updated.",
    #     "data": {
    #         "activity": activity_data.model_dump(),
    #         "daily_summary": updated_summary
    #     }
    # }