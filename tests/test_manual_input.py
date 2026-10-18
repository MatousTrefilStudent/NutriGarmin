from datetime import date

import pytest
from pydantic import ValidationError

from data_input.adapters import manual_input
from main import app


def test_manual_activity_returns_input_and_saves_it(monkeypatch):
    activity = manual_input.ManualActivityInput(
        date=date(2026, 10, 18),
        activity_type="Running",
        duration_minutes=30,
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


def test_manual_activity_uses_service_and_prints_debug_message(capsys):
    activity = manual_input.ManualActivityInput(
        date=date(2026, 10, 18),
        activity_type="Running",
        duration_minutes=30,
        calories_burned=300,
    )

    manual_input.add_manual_activity(activity)

    captured = capsys.readouterr()
    assert captured.out.strip() == (
        "DEBUG: Saving activity to DB: "
        "{'date': datetime.date(2026, 10, 18), 'activity_type': 'Running', "
        "'duration_minutes': 30, 'calories_burned': 300}"
    )
    assert captured.err == ""


def test_manual_activity_rejects_invalid_date():
    with pytest.raises(ValidationError):
        manual_input.ManualActivityInput(
            date="not-a-date",
            activity_type="Running",
            duration_minutes=30,
            calories_burned=300,
        )


def test_manual_activity_route_is_registered():
    operation = app.openapi()["paths"]["/api/manual/activity"]

    assert "post" in operation
