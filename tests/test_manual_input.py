from datetime import date
from unittest.mock import Mock

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
    save_activity = Mock()
    monkeypatch.setattr(
        manual_input.unified_activity_service,
        "save_activity_to_db",
        save_activity,
    )

    response = manual_input.add_manual_activity(activity)

    assert response["message"] == "Manual activity added successfully"
    assert response["data"] == activity.model_dump()
    save_activity.assert_called_once_with(activity)


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
