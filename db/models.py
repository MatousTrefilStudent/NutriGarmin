from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship
from database import Base

class User(Base):
    __tablename__ = "uzivatel"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    age = Column(Integer)
    height_cm = Column(Float)
    weight_kg = Column(Float)
    bmr = Column(Float)

class FoodEntry(Base):
    __tablename__ = "zaznam_stravy"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("uzivatel.id"), default=1)
    date = Column(String, index=True)  # YYYY-MM-DD
    food_name = Column(String)
    amount_g = Column(Float)
    calories_kcal = Column(Float)
    protein_g = Column(Float, default=0.0)
    carbs_g = Column(Float, default=0.0)
    fat_g = Column(Float, default=0.0)

class ActivityRecord(Base):
    __tablename__ = "garmin_aktivita"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("uzivatel.id"), default=1)
    date = Column(String, index=True)
    activity_type = Column(String)
    duration_seconds = Column(Integer)
    burned_calories = Column(Float)
    avg_hr = Column(Integer, nullable=True)

class DailySummary(Base):
    __tablename__ = "denni_souhrn"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("uzivatel.id"), default=1)
    date = Column(String, unique=True, index=True)
    total_intake_kcal = Column(Float, default=0.0)
    total_burned_kcal = Column(Float, default=0.0)
    net_balance_kcal = Column(Float, default=0.0)