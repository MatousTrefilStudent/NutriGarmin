from pydantic import BaseModel, Field
from typing import Optional

# Base schema for Food
class FoodBase(BaseModel):
    date: str
    food_name: str
    amount_g: float = Field(..., gt=0)
    calories_kcal: float = Field(..., ge=0)
    protein_g: float = 0.0
    carbs_g: float = 0.0
    fat_g: float = 0.0

# Schema for creating food
class FoodCreate(FoodBase):
    pass

# Schema for reading food (Response Model)
class FoodResponse(FoodBase):
    id: int

    class Config:
        from_attributes = True  # Pydantic v2 ORM mode


class ActivityCreate(BaseModel):
    date: str
    activity_type: str
    duration_seconds: int
    burned_calories: float
    avg_hr: Optional[int] = None