from datetime import date

import pytest
from pydantic import ValidationError

from data_input.adapters import manual_input
from main import app


def test_manual_activity_returns_input_and_saves_it(monkeypatch):
    activity = manual_input.ManualActivityInput(
        date=date(2026, 10, 18),
        activity_type="Running",
        seconds_of_duration=1800,
        calories_burned=300,
    )
    saved_activities = []

    def save_activity(saved_activity):
        saved_activities.append(saved_activity)

    monkeypatch.setattr(
        manual_input.unified_activity_service,
        "save_activity_to_db",
        save_activity,
    )

    response = manual_input.add_manual_activity(activity)

    assert response["message"] == "Manual activity added successfully"
    assert response["data"] == activity.model_dump()
    assert saved_activities == [activity]


def test_manual_activity_uses_service_and_prints_debug_message(capsys, monkeypatch):
    activity = manual_input.ManualActivityInput(
        date=date(2026, 10, 18),
        activity_type="Running",
        seconds_of_duration=1800,
        calories_burned=300,
    )
    saved_records = []

    class FakeSession:
        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc_value, traceback):
            return False

    def save_activity_record(db, activity, user_id):
        saved_records.append((db, activity, user_id))

    monkeypatch.setattr(manual_input.unified_activity_service, "SessionLocal", FakeSession)
    monkeypatch.setattr(
        manual_input.unified_activity_service.crud,
        "create_activity_record",
        save_activity_record,
    )

    manual_input.add_manual_activity(activity)

    captured = capsys.readouterr()
    assert captured.out.strip() == (
        "DEBUG: Saving activity to DB: "
        "{'date': datetime.date(2026, 10, 18), 'activity_type': 'Running', "
        "'seconds_of_duration': 1800, 'calories_burned': 300.0, "
        "'beats_per_minute_average': None}"
    )
    assert captured.err == ""
    assert saved_records[0][1].calories_burned == 300
    assert saved_records[0][1].date == "2026-10-18"
    assert saved_records[0][2] == 1


def test_manual_activity_rejects_invalid_date():
    with pytest.raises(ValidationError):
        manual_input.ManualActivityInput(
            date="not-a-date",
            activity_type="Running",
            seconds_of_duration=1800,
            calories_burned=300,
        )


def test_manual_activity_route_is_registered():
    operation = app.openapi()["paths"]["/api/manual/activity"]

    assert "post" in operation


def test_manual_food_uses_canonical_unit_first_fields():
    food = manual_input.ManualFoodInput(
        date=date(2026, 10, 18),
        food_name="Avocado",
        grams_of_food=150,
        calories_consumed=240,
        grams_of_protein=3,
        grams_of_carbs=13,
        grams_of_fat=22,
    )

    assert food.model_dump() == {
        "date": date(2026, 10, 18),
        "food_name": "Avocado",
        "grams_of_food": 150,
        "calories_consumed": 240,
        "grams_of_protein": 3,
        "grams_of_carbs": 13,
        "grams_of_fat": 22,
    }
