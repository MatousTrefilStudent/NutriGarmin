from datetime import date as Date
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field
from db import crud 

# ==========================================
# 1. UNIFIED DATA MODEL
# ==========================================

class UnifiedActivityData(BaseModel):
    """
    Standardized data structure (Adapter target) representing any physical activity,
    regardless of whether it came from Garmin Connect or Manual User Input.
    """
    source: Optional[str] = Field(None, example="Manual", description="Source of data: 'Garmin Connect' or 'Manual'")
    date: Optional[Date] = Field(None, example="2026-10-18", description="Date in YYYY-MM-DD format")
    activity_type: Optional[str] = Field(None, example="Running", description="Type or name of activity")
    duration_seconds: Optional[float] = Field(None, gt=0, example=1800.0, description="Duration in seconds")
    active_kcal: Optional[float] = Field(None, ge=0, example=300.0, description="Active calories burned")
    bmr_kcal: Optional[float] = Field(None, ge=0, example=0.0, description="Basal metabolic rate calories")
    calories_burned: Optional[float] = Field(None, gt=0, example=300.0, description="Total calories burned (active + bmr)")
    avg_hr: Optional[int] = Field(None, ge=0, example=120, description="Average heart rate during activity")


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


    
    crud.create_activity_record(activity=UnifiedActivityData(**activity_data.dict()), db=db_session, user_id=1
    )


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