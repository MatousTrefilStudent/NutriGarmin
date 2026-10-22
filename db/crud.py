from datetime import date

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


def create_sample_food_entries(db: Session, user_id: int = 1):
    """Creates today's sample food entries, skipping exact duplicates."""
    today = date.today().isoformat()
    foods = [
        schemas.FoodCreate(
            date=today,
            food_name="Oatmeal",
            amount_g=80,
            calories_kcal=311,
            protein_g=13.5,
            carbs_g=52.8,
            fat_g=5.5,
        ),
        schemas.FoodCreate(
            date=today,
            food_name="Banana",
            amount_g=118,
            calories_kcal=105,
            protein_g=1.3,
            carbs_g=27.0,
            fat_g=0.4,
        ),
        schemas.FoodCreate(
            date=today,
            food_name="Greek yogurt",
            amount_g=150,
            calories_kcal=146,
            protein_g=15.0,
            carbs_g=5.9,
            fat_g=7.5,
        ),
    ]

    entries = []
    for food in foods:
        existing_entry = db.query(models.FoodEntry).filter_by(
            user_id=user_id,
            date=food.date,
            food_name=food.food_name,
            amount_g=food.amount_g,
            calories_kcal=food.calories_kcal,
            protein_g=food.protein_g,
            carbs_g=food.carbs_g,
            fat_g=food.fat_g,
        ).first()
        entries.append(
            existing_entry
            if existing_entry is not None
            else create_food_entry(db, food, user_id)
        )

    return entries


def get_food_entries_by_date(db: Session, date_str: str, user_id: int = 1):
    """Retrieves all food entries for a specific day."""
    return db.query(models.FoodEntry).filter(
        models.FoodEntry.user_id == user_id,
        models.FoodEntry.date == date_str
    ).all()

if __name__=="__main__":
    from database import Base, SessionLocal
    import models

    Base.metadata.create_all(bind=SessionLocal.kw["bind"])
    with SessionLocal() as db:
        create_sample_food_entries(db)