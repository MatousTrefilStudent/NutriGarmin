import unittest
from datetime import date
from unittest.mock import patch

from pydantic import ValidationError

from data_input.adapters import manual_input
from main import app


class ManualActivityInputTests(unittest.TestCase):
    def test_manual_activity_returns_input_and_saves_it(self):
        activity = manual_input.ManualActivityInput(
            date=date(2026, 10, 18),
            activity_type="Running",
            duration_minutes=30,
            calories_burned=300,
        )

        with patch.object(manual_input.unified_activity_service, "save_activity_to_db") as save:
            response = manual_input.add_manual_activity(activity)

        self.assertEqual(response["message"], "Manual activity added successfully")
        self.assertEqual(response["data"], activity.model_dump())
        save.assert_called_once_with(activity)

    def test_manual_activity_rejects_invalid_date(self):
        with self.assertRaises(ValidationError):
            manual_input.ManualActivityInput(
                date="not-a-date",
                activity_type="Running",
                duration_minutes=30,
                calories_burned=300,
            )

    def test_manual_activity_route_is_registered(self):
        operation = app.openapi()["paths"]["/api/manual/activity"]

        self.assertIn("post", operation)


if __name__ == "__main__":
    unittest.main()
