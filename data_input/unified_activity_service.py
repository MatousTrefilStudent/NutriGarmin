from datetime import date as Date
from typing import Optional

from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from db import crud, models, schemas
from db.database import SessionLocal

# ==========================================
# 1. UNIFIED DATA MODEL
# ==========================================

class UnifiedActivityData(BaseModel):
    """
    Standardized data structure (Adapter target) representing any physical activity,
    regardless of whether it came from Garmin Connect or Manual User Input.
    """
    date: Date = Field(
        ...,
        description="Date in YYYY-MM-DD format",
        json_schema_extra={"example": "2026-10-18"},
    )
    activity_type: str = Field(
        ...,
        description="Type or name of activity",
        json_schema_extra={"example": "Running"},
    )
    seconds_of_duration: int = Field(
        ...,
        ge=0,
        description="Duration in seconds",
        json_schema_extra={"example": 1800},
    )
    calories_burned: float = Field(
        ...,
        ge=0,
        description="Total calories burned",
        json_schema_extra={"example": 300.0},
    )
    beats_per_minute_average: Optional[int] = Field(
        None,
        ge=0,
        description="Average heart rate during activity",
        json_schema_extra={"example": 120},
    )


# ==========================================
# 2. CORE SERVICE LOGIC
# ==========================================

def save_activity_to_db(
    activity_data: UnifiedActivityData, db_session: Optional[Session] = None
) -> models.ActivityRecord:
    """
    Save unified activity data through the CRUD layer.
    
    Args:
        activity_data: Instance of UnifiedActivityData.
        db_session: Optional SQLAlchemy DB session instance.
        
    Returns:
        The persisted activity record.
    """

    print(f"DEBUG: Saving activity to DB: {activity_data.model_dump()}")

    activity = schemas.ActivityCreate(
        date=activity_data.date.isoformat(),
        activity_type=activity_data.activity_type,
        seconds_of_duration=activity_data.seconds_of_duration,
        calories_burned=activity_data.calories_burned,
        beats_per_minute_average=activity_data.beats_per_minute_average,
    )
    if db_session is not None:
        return crud.create_activity_record(db=db_session, activity=activity, user_id=1)

    with SessionLocal() as session:
        return crud.create_activity_record(db=session, activity=activity, user_id=1)