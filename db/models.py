from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship
try:
    from db.database import Base
except ImportError:
    from database import Base

class User(Base):
    __tablename__ = "user"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    age = Column(Integer)
    height_cm = Column(Float)
    weight_kg = Column(Float)
    bmr = Column(Float)

class FoodEntry(Base):
    __tablename__ = "food_entry"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("user.id"), default=1)
    date = Column(String, index=True)  # YYYY-MM-DD
    food_name = Column(String)
    grams_of_food = Column("amount_g", Float)
    calories_consumed = Column("calories_kcal", Float)
    grams_of_protein = Column("protein_g", Float, default=0.0)
    grams_of_carbs = Column("carbs_g", Float, default=0.0)
    grams_of_fat = Column("fat_g", Float, default=0.0)

class ActivityRecord(Base):
    __tablename__ = "activity_record"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("user.id"), default=1)
    date = Column(String, index=True)
    activity_type = Column(String)
    seconds_of_duration = Column("duration_seconds", Integer)
    calories_burned = Column("burned_calories", Float)
    beats_per_minute_average = Column("avg_hr", Integer, nullable=True)

class DailySummary(Base):
    __tablename__ = "daily_summary"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("user.id"), default=1)
    date = Column(String, unique=True, index=True)
    calories_consumed = Column("total_intake_kcal", Float, default=0.0)
    calories_burned = Column("total_burned_kcal", Float, default=0.0)
    calories_net_balance = Column("net_balance_kcal", Float, default=0.0)