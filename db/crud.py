from sqlalchemy.orm import Session
from sqlalchemy import func
import models, schemas

def create_food_entry(db: Session, food: schemas.FoodCreate, user_id: int = 1):
    """Inserts a new food entry into zaznam_stravy."""
    db_food = models.FoodEntry(
        user_id=user_id,
        date=food.date,
        food_name=food.food_name,
        amount_g=food.amount_g,
        calories_kcal=food.calories_kcal,
        protein_g=food.protein_g,
        carbs_g=food.carbs_g,
        fat_g=food.fat_g
    )
    db.add(db_food)
    db.commit()
    db.refresh(db_food)
    return db_food

def get_food_entries_by_date(db: Session, date_str: str, user_id: int = 1):
    """Retrieves all food entries for a specific day."""
    return db.query(models.FoodEntry).filter(
        models.FoodEntry.user_id == user_id,
        models.FoodEntry.date == date_str
    ).all()