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
        grams_of_food=200.0,
        calories_consumed=330.0,
        grams_of_protein=62.0,
        grams_of_carbs=0.0,
        grams_of_fat=7.2,
    )
    assert food.date == "2026-10-17"
    assert food.food_name == "Chicken Breast"
    assert food.grams_of_food == 200.0
    assert food.calories_consumed == 330.0
    assert food.grams_of_protein == 62.0
    assert food.grams_of_carbs == 0.0
    assert food.grams_of_fat == 7.2


def test_food_base_defaults():
    """Verify FoodBase defaults nutrient gram amounts to 0.0."""
    food = FoodBase(
        date="2026-10-17",
        food_name="Apple",
        grams_of_food=150.0,
        calories_consumed=80.0,
    )
    assert food.grams_of_protein == 0.0
    assert food.grams_of_carbs == 0.0
    assert food.grams_of_fat == 0.0


@pytest.mark.parametrize(
    "missing_field",
    ["date", "food_name", "grams_of_food", "calories_consumed"],
)
def test_food_base_missing_required_fields(missing_field):
    """Verify FoodBase raises ValidationError when any required field is missing."""
    valid_data = {
        "date": "2026-10-17",
        "food_name": "Apple",
        "grams_of_food": 150.0,
        "calories_consumed": 80.0,
    }
    valid_data.pop(missing_field)
    with pytest.raises(ValidationError):
        FoodBase(**valid_data)


def test_food_base_amount_positive_validation():
    """Verify grams_of_food must be strictly greater than 0."""
    with pytest.raises(ValidationError):
        FoodBase(
            date="2026-10-17",
            food_name="Apple",
            grams_of_food=0.0,
            calories_consumed=80.0,
        )

    with pytest.raises(ValidationError):
        FoodBase(
            date="2026-10-17",
            food_name="Apple",
            grams_of_food=-10.0,
            calories_consumed=80.0,
        )

    valid_food = FoodBase(
        date="2026-10-17",
        food_name="Apple",
        grams_of_food=0.1,
        calories_consumed=1.0,
    )
    assert valid_food.grams_of_food == 0.1


def test_food_base_calories_non_negative_validation():
    """Verify calories_consumed must be greater than or equal to 0."""
    with pytest.raises(ValidationError):
        FoodBase(
            date="2026-10-17",
            food_name="Diet Soda",
            grams_of_food=330.0,
            calories_consumed=-1.0,
        )

    zero_cal_food = FoodBase(
        date="2026-10-17",
        food_name="Water",
        grams_of_food=250.0,
        calories_consumed=0.0,
    )
    assert zero_cal_food.calories_consumed == 0.0


def test_food_create_subclasses_food_base():
    """Verify FoodCreate inherits from FoodBase and instantiates correctly."""
    assert issubclass(FoodCreate, FoodBase)

    food_create = FoodCreate(
        date="2026-10-17",
        food_name="Banana",
        grams_of_food=120.0,
        calories_consumed=105.0,
        grams_of_protein=1.3,
        grams_of_carbs=27.0,
        grams_of_fat=0.3,
    )
    assert food_create.food_name == "Banana"
    assert food_create.grams_of_food == 120.0


def test_food_response_requires_id():
    """Verify FoodResponse requires an id and inherits FoodBase attributes."""
    response = FoodResponse(
        id=10,
        date="2026-10-17",
        food_name="Greek Yogurt",
        grams_of_food=150.0,
        calories_consumed=130.0,
        grams_of_protein=15.0,
        grams_of_carbs=6.0,
        grams_of_fat=0.0,
    )
    assert response.id == 10
    assert response.food_name == "Greek Yogurt"

    with pytest.raises(ValidationError):
        FoodResponse(
            date="2026-10-17",
            food_name="Greek Yogurt",
            grams_of_food=150.0,
            calories_consumed=130.0,
        )


def test_food_response_from_orm_mode():
    """Verify FoodResponse can be created from an ORM-like object using model_validate."""
    orm_obj = SimpleNamespace(
        id=42,
        date="2026-10-17",
        food_name="Rice",
        grams_of_food=100.0,
        calories_consumed=130.0,
        grams_of_protein=2.7,
        grams_of_carbs=28.0,
        grams_of_fat=0.3,
    )

    response = FoodResponse.model_validate(orm_obj)
    assert response.id == 42
    assert response.food_name == "Rice"
    assert response.grams_of_food == 100.0
    assert response.calories_consumed == 130.0
    assert response.grams_of_protein == 2.7
    assert response.grams_of_carbs == 28.0
    assert response.grams_of_fat == 0.3


def test_model_dump_serialization():
    """Verify model_dump produces a serializable dict containing all model fields."""
    food = FoodCreate(
        date="2026-10-17",
        food_name="Eggs",
        grams_of_food=100.0,
        calories_consumed=143.0,
        grams_of_protein=12.6,
        grams_of_carbs=0.7,
        grams_of_fat=9.5,
    )
    dumped = food.model_dump()
    assert dumped == {
        "date": "2026-10-17",
        "food_name": "Eggs",
        "grams_of_food": 100.0,
        "calories_consumed": 143.0,
        "grams_of_protein": 12.6,
        "grams_of_carbs": 0.7,
        "grams_of_fat": 9.5,
    }
