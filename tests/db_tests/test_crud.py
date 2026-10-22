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
        amount_g=150.0,
        calories_kcal=80.0,
        protein_g=0.3,
        carbs_g=21.0,
        fat_g=0.2,
    )


@pytest.fixture
def sample_activity_create():
    """Fixture providing a valid ActivityCreate schema instance."""
    return ActivityCreate(
        date="2026-10-17",
        activity_type="running",
        duration_seconds=1800,
        burned_calories=250.0,
        avg_hr=155,
    )


def test_create_food_entry_default_user(db_session, sample_food_create):
    """Verify create_food_entry stores record with default user_id=1 and returns refreshed model."""
    created = create_food_entry(db=db_session, food=sample_food_create)

    assert isinstance(created, FoodEntry)
    assert created.id is not None
    assert created.user_id == 1
    assert created.date == sample_food_create.date
    assert created.food_name == sample_food_create.food_name
    assert created.amount_g == sample_food_create.amount_g
    assert created.calories_kcal == sample_food_create.calories_kcal
    assert created.protein_g == sample_food_create.protein_g
    assert created.carbs_g == sample_food_create.carbs_g
    assert created.fat_g == sample_food_create.fat_g

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
    assert created.duration_seconds == sample_activity_create.duration_seconds
    assert created.burned_calories == sample_activity_create.burned_calories
    assert created.avg_hr == sample_activity_create.avg_hr

    persisted = db_session.query(ActivityRecord).filter_by(id=created.id).first()
    assert persisted is not None
    assert persisted.activity_type == sample_activity_create.activity_type


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
            duration_seconds=1800,
            burned_calories=250.0,
            avg_hr=155,
        ),
        ActivityCreate(
            date=target_date,
            activity_type="cycling",
            duration_seconds=3600,
            burned_calories=400.0,
            avg_hr=140,
        ),
        ActivityCreate(
            date="2026-10-18",
            activity_type="walking",
            duration_seconds=900,
            burned_calories=50.0,
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
        amount_g=100.0,
        calories_kcal=150.0,
        protein_g=5.0,
        carbs_g=27.0,
        fat_g=2.5,
    )
    food2 = FoodCreate(
        date="2026-10-17",
        food_name="Banana",
        amount_g=120.0,
        calories_kcal=105.0,
        protein_g=1.3,
        carbs_g=27.0,
        fat_g=0.3,
    )
    food_other_day = FoodCreate(
        date="2026-10-18",
        food_name="Chicken Breast",
        amount_g=200.0,
        calories_kcal=330.0,
        protein_g=62.0,
        carbs_g=0.0,
        fat_g=7.2,
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
        amount_g=150.0,
        calories_kcal=80.0,
    )
    food_user2 = FoodCreate(
        date=target_date,
        food_name="Orange",
        amount_g=130.0,
        calories_kcal=60.0,
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
        FoodCreate(date=target_date, food_name="Breakfast Eggs", amount_g=150.0, calories_kcal=210.0),
        FoodCreate(date=target_date, food_name="Lunch Salad", amount_g=250.0, calories_kcal=350.0),
        FoodCreate(date=target_date, food_name="Dinner Salmon", amount_g=200.0, calories_kcal=420.0),
    ]

    for item in foods:
        create_food_entry(db_session, item, user_id=1)

    entries = get_food_entries_by_date(db_session, target_date, user_id=1)
    assert len(entries) == 3
    total_calories = sum(e.calories_kcal for e in entries)
    assert total_calories == pytest.approx(980.0)
