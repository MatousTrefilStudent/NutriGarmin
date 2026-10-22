import pytest
from sqlalchemy import create_engine
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from db import models
from db.models import ActivityRecord, DailySummary, FoodEntry, User


@pytest.fixture
def db_session():
    """Provides an isolated, in-memory SQLite database session for each test function."""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    models.Base.metadata.create_all(bind=engine)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        models.Base.metadata.drop_all(bind=engine)


@pytest.fixture
def sample_user(db_session):
    """Fixture providing a persisted sample User."""
    user = User(
        id=1,
        username="testuser",
        age=28,
        height_cm=178.5,
        weight_kg=74.0,
        bmr=1720.0,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


def test_model_tablenames():
    """Verify ORM models have the expected table names."""
    assert User.__tablename__ == "user"
    assert FoodEntry.__tablename__ == "food_entry"
    assert ActivityRecord.__tablename__ == "activity_record"
    assert DailySummary.__tablename__ == "daily_summary"


def test_create_and_retrieve_user(db_session):
    """Verify creating and retrieving a User record."""
    user = User(
        username="johndoe",
        age=30,
        height_cm=182.0,
        weight_kg=78.5,
        bmr=1760.0,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    assert user.id is not None
    queried = db_session.query(User).filter_by(username="johndoe").first()
    assert queried is not None
    assert queried.id == user.id
    assert queried.age == 30
    assert queried.height_cm == 182.0
    assert queried.weight_kg == 78.5
    assert queried.bmr == 1760.0


def test_user_unique_username_constraint(db_session):
    """Verify that creating two users with the same username raises an IntegrityError."""
    user1 = User(username="unique_user", age=25)
    db_session.add(user1)
    db_session.commit()

    user2 = User(username="unique_user", age=35)
    db_session.add(user2)
    with pytest.raises(IntegrityError):
        db_session.commit()
    db_session.rollback()


def test_create_and_retrieve_food_entry(db_session, sample_user):
    """Verify creating and retrieving a FoodEntry record."""
    food = FoodEntry(
        user_id=sample_user.id,
        date="2026-10-17",
        food_name="Oatmeal with Honey",
        amount_g=200.0,
        calories_kcal=250.0,
        protein_g=8.0,
        carbs_g=45.0,
        fat_g=4.0,
    )
    db_session.add(food)
    db_session.commit()
    db_session.refresh(food)

    assert food.id is not None
    queried = db_session.query(FoodEntry).filter_by(id=food.id).first()
    assert queried is not None
    assert queried.user_id == sample_user.id
    assert queried.date == "2026-10-17"
    assert queried.food_name == "Oatmeal with Honey"
    assert queried.amount_g == 200.0
    assert queried.calories_kcal == 250.0
    assert queried.protein_g == 8.0
    assert queried.carbs_g == 45.0
    assert queried.fat_g == 4.0


def test_food_entry_default_values(db_session, sample_user):
    """Verify default values for protein_g, carbs_g, fat_g, and user_id in FoodEntry."""
    food = FoodEntry(
        date="2026-10-17",
        food_name="Water",
        amount_g=250.0,
        calories_kcal=0.0,
    )
    db_session.add(food)
    db_session.commit()
    db_session.refresh(food)

    assert food.user_id == 1
    assert food.protein_g == 0.0
    assert food.carbs_g == 0.0
    assert food.fat_g == 0.0


def test_create_and_retrieve_activity_record(db_session, sample_user):
    """Verify creating and retrieving an ActivityRecord."""
    activity = ActivityRecord(
        user_id=sample_user.id,
        date="2026-10-17",
        activity_type="running",
        duration_seconds=3600,
        burned_calories=600.0,
        avg_hr=155,
    )
    db_session.add(activity)
    db_session.commit()
    db_session.refresh(activity)

    assert activity.id is not None
    queried = db_session.query(ActivityRecord).filter_by(id=activity.id).first()
    assert queried is not None
    assert queried.user_id == sample_user.id
    assert queried.date == "2026-10-17"
    assert queried.activity_type == "running"
    assert queried.duration_seconds == 3600
    assert queried.burned_calories == 600.0
    assert queried.avg_hr == 155


def test_activity_record_nullable_avg_hr_and_default_user(db_session, sample_user):
    """Verify avg_hr is nullable and user_id defaults to 1."""
    activity = ActivityRecord(
        date="2026-10-17",
        activity_type="walking",
        duration_seconds=1800,
        burned_calories=120.0,
        avg_hr=None,
    )
    db_session.add(activity)
    db_session.commit()
    db_session.refresh(activity)

    assert activity.user_id == 1
    assert activity.avg_hr is None


def test_create_and_retrieve_daily_summary(db_session, sample_user):
    """Verify creating and retrieving a DailySummary."""
    summary = DailySummary(
        user_id=sample_user.id,
        date="2026-10-17",
        total_intake_kcal=2200.0,
        total_burned_kcal=2400.0,
        net_balance_kcal=-200.0,
    )
    db_session.add(summary)
    db_session.commit()
    db_session.refresh(summary)

    assert summary.id is not None
    queried = db_session.query(DailySummary).filter_by(date="2026-10-17").first()
    assert queried is not None
    assert queried.user_id == sample_user.id
    assert queried.total_intake_kcal == 2200.0
    assert queried.total_burned_kcal == 2400.0
    assert queried.net_balance_kcal == -200.0


def test_daily_summary_defaults(db_session, sample_user):
    """Verify default values in DailySummary (user_id=1, and all kcal metrics default to 0.0)."""
    summary = DailySummary(date="2026-10-18")
    db_session.add(summary)
    db_session.commit()
    db_session.refresh(summary)

    assert summary.user_id == 1
    assert summary.total_intake_kcal == 0.0
    assert summary.total_burned_kcal == 0.0
    assert summary.net_balance_kcal == 0.0


def test_daily_summary_unique_date_constraint(db_session, sample_user):
    """Verify that DailySummary date column enforces unique constraint."""
    summary1 = DailySummary(date="2026-10-17")
    db_session.add(summary1)
    db_session.commit()

    summary2 = DailySummary(date="2026-10-17")
    db_session.add(summary2)
    with pytest.raises(IntegrityError):
        db_session.commit()
    db_session.rollback()


def test_foreign_key_references():
    """Verify that foreign keys are configured to point to user.id."""
    food_fks = list(FoodEntry.__table__.c.user_id.foreign_keys)
    assert len(food_fks) == 1
    assert food_fks[0].target_fullname == "user.id"

    activity_fks = list(ActivityRecord.__table__.c.user_id.foreign_keys)
    assert len(activity_fks) == 1
    assert activity_fks[0].target_fullname == "user.id"

    summary_fks = list(DailySummary.__table__.c.user_id.foreign_keys)
    assert len(summary_fks) == 1
    assert summary_fks[0].target_fullname == "user.id"
