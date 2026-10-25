from pydantic import BaseModel, Field
from typing import Optional

# Base schema for Food
class FoodBase(BaseModel):
    date: str
    food_name: str
    grams_of_food: float = Field(..., gt=0)
    calories_consumed: float = Field(..., ge=0)
    grams_of_protein: float = 0.0
    grams_of_carbs: float = 0.0
    grams_of_fat: float = 0.0

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
    seconds_of_duration: int
    calories_burned: float
    beats_per_minute_average: Optional[int] = None