from datetime import date

from sqlalchemy.orm import Session
from sqlalchemy import func
try:
    from db import models, schemas
except ImportError:
    import models, schemas


def create_food_entry(db: Session, food: schemas.FoodCreate, user_id: int = 1):
    """Inserts a new food entry into zaznam_stravy."""
    db_food = models.FoodEntry(
        user_id=user_id,
        date=food.date,
        food_name=food.food_name,
        grams_of_food=food.grams_of_food,
        calories_consumed=food.calories_consumed,
        grams_of_protein=food.grams_of_protein,
        grams_of_carbs=food.grams_of_carbs,
        grams_of_fat=food.grams_of_fat
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


def create_activity_record(db: Session, activity: schemas.ActivityCreate, user_id: int = 1):
    """Inserts a new activity record into zaznam_aktivity."""
    db_activity = models.ActivityRecord(
        user_id=user_id,
        date=activity.date,
        activity_type=activity.activity_type,
        seconds_of_duration=activity.seconds_of_duration,
        calories_burned=activity.calories_burned,
        beats_per_minute_average=activity.beats_per_minute_average
    )
    db.add(db_activity)
    db.commit()
    db.refresh(db_activity)
    return db_activity

def get_activity_records_by_date(db: Session, date_str: str, user_id: int = 1):
    """Retrieves all activity records for a specific day."""
    return db.query(models.ActivityRecord).filter(
        models.ActivityRecord.user_id == user_id,
        models.ActivityRecord.date == date_str
    ).all()


if __name__=="__main__":
    try:
        from db.database import SessionLocal, engine
    except ImportError:
        from database import SessionLocal, engine
    models.Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    # Example usage
    new_food = schemas.FoodCreate(
        date="2026-10-17",
        food_name="Apple",
        grams_of_food=150,
        calories_consumed=80,
        grams_of_protein=0.3,
        grams_of_carbs=21,
        grams_of_fat=0.2
    )
    create_food_entry(db, new_food)

    entries = get_food_entries_by_date(db, "2026-10-17")
    for entry in entries:
        print(entry.food_name, entry.calories_consumed)