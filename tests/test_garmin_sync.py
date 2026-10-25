from datetime import date
import pytest
from pydantic import ValidationError

from data_input.adapters import garmin_sync


def test_garmin_connect_login_succeeds(monkeypatch, capsys):
    """Needs to be run manually using: .\venv\Scripts\python.exe -m pytest -s tests\test_garmin_sync.py::test_garmin_connect_login_succeeds"""
    print("inputing")
    email = input("Garmin Connect email: ")
    password = input("Garmin Connect password: ")

    activities = [
        {
            "startTimeLocal": "2026-10-17T08:30:00",
            "activityType": {"typeKey": "running"},
            "duration": 1800,
            "calories": 250,
        }
    ]
    sync_results = []

    def get_activities_by_date(_client, start_date, end_date):
        assert (start_date, end_date) == ("2026-10-17", "2026-10-17")
        return activities

    monkeypatch.setattr(
        garmin_sync.Garmin,
        "get_activities_by_date",
        get_activities_by_date,
    )


    garmin_sync.sync_garmin_data(email, password)

    output = capsys.readouterr().out
    assert "Connecting to Garmin Connect..." in output
    assert "Login successful!" in output
    assert str(activities[0]) in output
    assert "activity_type='running'" in output

""".\venv\Scripts\python.exe -m pytest -s tests\test_garmin_sync.py::test_garmin_connect_login_succeeds"""
""""""
"""passed 25.10.2026"""

def test_garmin_activity_input_parses_date():
    activity = garmin_sync.GarminActivityInput(
        date="2026-10-17",
        activity_type="running",
        seconds_of_duration=1800,
        calories_burned=250,
    )

    assert activity.date == date(2026, 10, 17)
    assert activity.activity_type == "running"
    assert activity.seconds_of_duration == 1800
    assert activity.calories_burned == 250


def test_garmin_activity_input_rejects_invalid_date():
    with pytest.raises(ValidationError):
        garmin_sync.GarminActivityInput(
            date="not-a-date",
            activity_type="running",
            seconds_of_duration=1800,
            calories_burned=250,
        )


def test_add_garmin_activity_returns_input_and_saves_it(monkeypatch):
    activity = garmin_sync.GarminActivityInput(
        date=date(2026, 10, 17),
        activity_type="running",
        seconds_of_duration=1800,
        calories_burned=250,
    )
    saved_activities = []

    def save_activity(saved_activity):
        saved_activities.append(saved_activity)

    monkeypatch.setattr(
        garmin_sync.unified_activity_service,
        "save_activity_to_db",
        save_activity,
    )

    response = garmin_sync.add_garmin_activity(activity)

    assert response["message"] == "Garmin activity added successfully"
    assert response["data"] == activity.model_dump()
    assert saved_activities == [activity]


def test_sync_garmin_data_logs_in_and_maps_activities(monkeypatch):
    activities = [
        {
            "startTimeLocal": "2026-10-17 19:14:02",
            "activityType": {"typeKey": "running"},
            "duration": 9022.275390625,
            "calories": 250,
        },
        {},
    ]
    client_calls = []
    persisted_activities = []

    class FakeGarmin:
        def __init__(self, email, password):
            client_calls.append(("init", email, password))

        def login(self):
            client_calls.append(("login",))

        def get_activities_by_date(self, start_date, end_date):
            client_calls.append(("get_activities_by_date", start_date, end_date))
            return activities

    monkeypatch.setattr(garmin_sync, "Garmin", FakeGarmin)
    monkeypatch.setattr(
        garmin_sync.unified_activity_service,
        "save_activity_to_db",
        persisted_activities.append,
    )

    sync_results = garmin_sync.sync_garmin_data("user@example.com", "secret")

    assert client_calls == [
        ("init", "user@example.com", "secret"),
        ("login",),
        ("get_activities_by_date", "2026-10-17", "2026-10-17"),
    ]
    expected_activities = [
        garmin_sync.GarminActivityInput(
            date=date(2026, 10, 17),
            activity_type="running",
            seconds_of_duration=9022,
            calories_burned=250,
        ),
        garmin_sync.GarminActivityInput(
            date=date(2026, 10, 17),
            activity_type="unknown",
            seconds_of_duration=0,
            calories_burned=0,
        ),
    ]
    assert [item["data"] for item in sync_results] == [
        activity.model_dump() for activity in expected_activities
    ]
    assert persisted_activities == expected_activities


def test_sync_garmin_data_propagates_login_errors(monkeypatch):
    class FakeGarmin:
        def __init__(self, email, password):
            pass

        def login(self):
            raise RuntimeError("Garmin login failed")

    monkeypatch.setattr(garmin_sync, "Garmin", FakeGarmin)

    with pytest.raises(RuntimeError, match="Garmin login failed"):
        garmin_sync.sync_garmin_data("user@example.com", "secret")
