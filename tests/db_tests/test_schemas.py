from types import SimpleNamespace
import pytest
from pydantic import ValidationError

from db import schemas
from db.schemas import FoodBase, FoodCreate, FoodResponse


def test_food_base_valid():
    """Verify FoodBase instantiates properly with all valid fields."""
    food = FoodBase(
        date="2026-10-17",
        food_name="Chicken Breast",
        amount_g=200.0,
        calories_kcal=330.0,
        protein_g=62.0,
        carbs_g=0.0,
        fat_g=7.2,
    )
    assert food.date == "2026-10-17"
    assert food.food_name == "Chicken Breast"
    assert food.amount_g == 200.0
    assert food.calories_kcal == 330.0
    assert food.protein_g == 62.0
    assert food.carbs_g == 0.0
    assert food.fat_g == 7.2


def test_food_base_defaults():
    """Verify FoodBase defaults protein_g, carbs_g, and fat_g to 0.0."""
    food = FoodBase(
        date="2026-10-17",
        food_name="Apple",
        amount_g=150.0,
        calories_kcal=80.0,
    )
    assert food.protein_g == 0.0
    assert food.carbs_g == 0.0
    assert food.fat_g == 0.0


@pytest.mark.parametrize("missing_field", ["date", "food_name", "amount_g", "calories_kcal"])
def test_food_base_missing_required_fields(missing_field):
    """Verify FoodBase raises ValidationError when any required field is missing."""
    valid_data = {
        "date": "2026-10-17",
        "food_name": "Apple",
        "amount_g": 150.0,
        "calories_kcal": 80.0,
    }
    valid_data.pop(missing_field)
    with pytest.raises(ValidationError):
        FoodBase(**valid_data)


def test_food_base_amount_positive_validation():
    """Verify amount_g must be strictly greater than 0."""
    with pytest.raises(ValidationError):
        FoodBase(
            date="2026-10-17",
            food_name="Apple",
            amount_g=0.0,
            calories_kcal=80.0,
        )

    with pytest.raises(ValidationError):
        FoodBase(
            date="2026-10-17",
            food_name="Apple",
            amount_g=-10.0,
            calories_kcal=80.0,
        )

    valid_food = FoodBase(
        date="2026-10-17",
        food_name="Apple",
        amount_g=0.1,
        calories_kcal=1.0,
    )
    assert valid_food.amount_g == 0.1


def test_food_base_calories_non_negative_validation():
    """Verify calories_kcal must be greater than or equal to 0."""
    with pytest.raises(ValidationError):
        FoodBase(
            date="2026-10-17",
            food_name="Diet Soda",
            amount_g=330.0,
            calories_kcal=-1.0,
        )

    zero_cal_food = FoodBase(
        date="2026-10-17",
        food_name="Water",
        amount_g=250.0,
        calories_kcal=0.0,
    )
    assert zero_cal_food.calories_kcal == 0.0


def test_food_create_subclasses_food_base():
    """Verify FoodCreate inherits from FoodBase and instantiates correctly."""
    assert issubclass(FoodCreate, FoodBase)

    food_create = FoodCreate(
        date="2026-10-17",
        food_name="Banana",
        amount_g=120.0,
        calories_kcal=105.0,
        protein_g=1.3,
        carbs_g=27.0,
        fat_g=0.3,
    )
    assert food_create.food_name == "Banana"
    assert food_create.amount_g == 120.0


def test_food_response_requires_id():
    """Verify FoodResponse requires an id and inherits FoodBase attributes."""
    response = FoodResponse(
        id=10,
        date="2026-10-17",
        food_name="Greek Yogurt",
        amount_g=150.0,
        calories_kcal=130.0,
        protein_g=15.0,
        carbs_g=6.0,
        fat_g=0.0,
    )
    assert response.id == 10
    assert response.food_name == "Greek Yogurt"

    with pytest.raises(ValidationError):
        FoodResponse(
            date="2026-10-17",
            food_name="Greek Yogurt",
            amount_g=150.0,
            calories_kcal=130.0,
        )


def test_food_response_from_orm_mode():
    """Verify FoodResponse can be created from an ORM-like object using model_validate."""
    orm_obj = SimpleNamespace(
        id=42,
        date="2026-10-17",
        food_name="Rice",
        amount_g=100.0,
        calories_kcal=130.0,
        protein_g=2.7,
        carbs_g=28.0,
        fat_g=0.3,
    )

    response = FoodResponse.model_validate(orm_obj)
    assert response.id == 42
    assert response.food_name == "Rice"
    assert response.amount_g == 100.0
    assert response.calories_kcal == 130.0
    assert response.protein_g == 2.7
    assert response.carbs_g == 28.0
    assert response.fat_g == 0.3


def test_model_dump_serialization():
    """Verify model_dump produces a serializable dict containing all model fields."""
    food = FoodCreate(
        date="2026-10-17",
        food_name="Eggs",
        amount_g=100.0,
        calories_kcal=143.0,
        protein_g=12.6,
        carbs_g=0.7,
        fat_g=9.5,
    )
    dumped = food.model_dump()
    assert dumped == {
        "date": "2026-10-17",
        "food_name": "Eggs",
        "amount_g": 100.0,
        "calories_kcal": 143.0,
        "protein_g": 12.6,
        "carbs_g": 0.7,
        "fat_g": 9.5,
    }
