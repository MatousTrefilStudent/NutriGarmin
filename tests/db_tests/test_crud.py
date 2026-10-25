from datetime import date

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from db import crud, models, schemas
from db.crud import (
    create_activity_record,
    create_food_entry,
    get_activity_records_by_date,
    get_food_entries_by_date,
)
from db.models import ActivityRecord, FoodEntry
from db.schemas import ActivityCreate, FoodCreate
from data_input.unified_activity_service import UnifiedActivityData, save_activity_to_db


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
def sample_food_create():
    """Fixture providing a valid FoodCreate schema instance."""
    return FoodCreate(
        date="2026-10-17",
        food_name="Apple",
        grams_of_food=150.0,
        calories_consumed=80.0,
        grams_of_protein=0.3,
        grams_of_carbs=21.0,
        grams_of_fat=0.2,
    )


@pytest.fixture
def sample_activity_create():
    """Fixture providing a valid ActivityCreate schema instance."""
    return ActivityCreate(
        date="2026-10-17",
        activity_type="running",
        seconds_of_duration=1800,
        calories_burned=250.0,
        beats_per_minute_average=155,
    )


def test_create_food_entry_default_user(db_session, sample_food_create):
    """Verify create_food_entry stores record with default user_id=1 and returns refreshed model."""
    created = create_food_entry(db=db_session, food=sample_food_create)

    assert isinstance(created, FoodEntry)
    assert created.id is not None
    assert created.user_id == 1
    assert created.date == sample_food_create.date
    assert created.food_name == sample_food_create.food_name
    assert created.grams_of_food == sample_food_create.grams_of_food
    assert created.calories_consumed == sample_food_create.calories_consumed
    assert created.grams_of_protein == sample_food_create.grams_of_protein
    assert created.grams_of_carbs == sample_food_create.grams_of_carbs
    assert created.grams_of_fat == sample_food_create.grams_of_fat

    # Verify directly from database
    persisted = db_session.query(FoodEntry).filter_by(id=created.id).first()
    assert persisted is not None
    assert persisted.food_name == "Apple"


def test_create_activity_record_default_user(db_session, sample_activity_create):
    """Verify create_activity_record persists and returns the activity."""
    created = create_activity_record(db_session, sample_activity_create)

    assert isinstance(created, ActivityRecord)
    assert created.id is not None
    assert created.user_id == 1
    assert created.date == sample_activity_create.date
    assert created.activity_type == sample_activity_create.activity_type
    assert created.seconds_of_duration == sample_activity_create.seconds_of_duration
    assert created.calories_burned == sample_activity_create.calories_burned
    assert created.beats_per_minute_average == sample_activity_create.beats_per_minute_average

    persisted = db_session.query(ActivityRecord).filter_by(id=created.id).first()
    assert persisted is not None
    assert persisted.activity_type == sample_activity_create.activity_type


def test_unified_activity_service_persists_canonical_calorie_name(db_session):
    activity = UnifiedActivityData(
        date=date(2026, 10, 17),
        activity_type="running",
        seconds_of_duration=1800,
        calories_burned=250.0,
    )

    created = save_activity_to_db(activity, db_session)

    assert created.calories_burned == 250.0
    persisted = db_session.query(ActivityRecord).filter_by(id=created.id).one()
    assert persisted.calories_burned == 250.0


def test_create_activity_record_custom_user_id(db_session, sample_activity_create):
    """Verify create_activity_record assigns the provided user_id."""
    created = create_activity_record(
        db_session,
        sample_activity_create,
        user_id=42,
    )

    assert created.user_id == 42
    persisted = db_session.query(ActivityRecord).filter_by(id=created.id).first()
    assert persisted is not None
    assert persisted.user_id == 42


def test_get_activity_records_by_date_filters_by_date_and_user(db_session):
    """Verify activity retrieval is limited to the requested date and user."""
    target_date = "2026-10-17"
    activities = [
        ActivityCreate(
            date=target_date,
            activity_type="running",
            seconds_of_duration=1800,
            calories_burned=250.0,
            beats_per_minute_average=155,
        ),
        ActivityCreate(
            date=target_date,
            activity_type="cycling",
            seconds_of_duration=3600,
            calories_burned=400.0,
            beats_per_minute_average=140,
        ),
        ActivityCreate(
            date="2026-10-18",
            activity_type="walking",
            seconds_of_duration=900,
            calories_burned=50.0,
        ),
    ]
    create_activity_record(db_session, activities[0], user_id=1)
    create_activity_record(db_session, activities[1], user_id=2)
    create_activity_record(db_session, activities[2], user_id=1)

    user1_records = get_activity_records_by_date(db_session, target_date, user_id=1)
    assert len(user1_records) == 1
    assert user1_records[0].activity_type == "running"

    user2_records = get_activity_records_by_date(db_session, target_date, user_id=2)
    assert len(user2_records) == 1
    assert user2_records[0].activity_type == "cycling"

    assert get_activity_records_by_date(db_session, "2026-01-01", user_id=1) == []


def test_create_food_entry_custom_user_id(db_session, sample_food_create):
    """Verify create_food_entry assigns the provided custom user_id."""
    custom_user_id = 42
    created = create_food_entry(
        db=db_session,
        food=sample_food_create,
        user_id=custom_user_id,
    )

    assert created.user_id == custom_user_id
    persisted = db_session.query(FoodEntry).filter_by(id=created.id).first()
    assert persisted.user_id == custom_user_id


def test_get_food_entries_by_date_returns_matching_entries(db_session):
    """Verify get_food_entries_by_date retrieves only records for the requested date."""
    food1 = FoodCreate(
        date="2026-10-17",
        food_name="Oatmeal",
        grams_of_food=100.0,
        calories_consumed=150.0,
        grams_of_protein=5.0,
        grams_of_carbs=27.0,
        grams_of_fat=2.5,
    )
    food2 = FoodCreate(
        date="2026-10-17",
        food_name="Banana",
        grams_of_food=120.0,
        calories_consumed=105.0,
        grams_of_protein=1.3,
        grams_of_carbs=27.0,
        grams_of_fat=0.3,
    )
    food_other_day = FoodCreate(
        date="2026-10-18",
        food_name="Chicken Breast",
        grams_of_food=200.0,
        calories_consumed=330.0,
        grams_of_protein=62.0,
        grams_of_carbs=0.0,
        grams_of_fat=7.2,
    )

    create_food_entry(db_session, food1, user_id=1)
    create_food_entry(db_session, food2, user_id=1)
    create_food_entry(db_session, food_other_day, user_id=1)

    entries = get_food_entries_by_date(db_session, "2026-10-17", user_id=1)

    assert len(entries) == 2
    names = [e.food_name for e in entries]
    assert "Oatmeal" in names
    assert "Banana" in names
    assert "Chicken Breast" not in names


def test_get_food_entries_by_date_empty_when_no_records(db_session):
    """Verify get_food_entries_by_date returns an empty list when no entries exist."""
    entries = get_food_entries_by_date(db_session, "2026-01-01", user_id=1)
    assert entries == []


def test_get_food_entries_by_date_filters_by_user_id(db_session):
    """Verify get_food_entries_by_date properly scopes query by user_id."""
    target_date = "2026-10-17"
    food_user1 = FoodCreate(
        date=target_date,
        food_name="Apple",
        grams_of_food=150.0,
        calories_consumed=80.0,
    )
    food_user2 = FoodCreate(
        date=target_date,
        food_name="Orange",
        grams_of_food=130.0,
        calories_consumed=60.0,
    )

    create_food_entry(db_session, food_user1, user_id=1)
    create_food_entry(db_session, food_user2, user_id=2)

    user1_entries = get_food_entries_by_date(db_session, target_date, user_id=1)
    assert len(user1_entries) == 1
    assert user1_entries[0].food_name == "Apple"

    user2_entries = get_food_entries_by_date(db_session, target_date, user_id=2)
    assert len(user2_entries) == 1
    assert user2_entries[0].food_name == "Orange"

    non_existent_entries = get_food_entries_by_date(db_session, target_date, user_id=999)
    assert non_existent_entries == []


def test_create_multiple_food_entries_and_verify_total_calories(db_session):
    """Verify total calories calculation over multiple entries inserted via crud."""
    target_date = "2026-10-17"
    foods = [
        FoodCreate(date=target_date, food_name="Breakfast Eggs", grams_of_food=150.0, calories_consumed=210.0),
        FoodCreate(date=target_date, food_name="Lunch Salad", grams_of_food=250.0, calories_consumed=350.0),
        FoodCreate(date=target_date, food_name="Dinner Salmon", grams_of_food=200.0, calories_consumed=420.0),
    ]

    for item in foods:
        create_food_entry(db_session, item, user_id=1)

    entries = get_food_entries_by_date(db_session, target_date, user_id=1)
    assert len(entries) == 3
    total_calories = sum(e.calories_consumed for e in entries)
    assert total_calories == pytest.approx(980.0)
