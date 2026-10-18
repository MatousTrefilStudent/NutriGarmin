
import datetime
from garminconnect import (
    Garmin,
    GarminConnectAuthenticationError,
    GarminConnectTooManyRequestsError,
)

import os
from garminconnect import Garmin

#just for testing purposes, you can hardcode your credentials here or use environment variables

# 1. Credentials
GARMIN_EMAIL = input("mail ")
GARMIN_PASSWORD = input("password ")

def fetch_garmin_summary():
    try:
        # 2. Initialize client & log in
        print("Connecting to Garmin Connect...")
        client = Garmin(GARMIN_EMAIL, GARMIN_PASSWORD)
        client.login()
        print("Login successful!")

        # 3. Get today's date in YYYY-MM-DD format
        today = "2026-10-17"#datetime.date.today().isoformat()

        # 4. Fetch daily user summary
        stats = client.get_user_summary(today)

        print(stats)
        bmr_calories = stats.get("bmrKilocalories", 0)
        active_calories = stats.get("activeKilocalories", 0)
        total_burned = stats.get("totalKilocalories", 0)

        print(f"\n--- Daily Summary for {today} ---")
        print(f"Basal Metabolic Rate (BMR): {bmr_calories} kcal")
        print(f"Active Calories Burned: {active_calories} kcal")
        print(f"Total Daily Burned Calories: {total_burned} kcal")

        # 5. Fetch specific workouts/activities for today
        activities = client.get_activities_by_date(today, today)
        print(f"\nWorkouts Logged Today ({len(activities)}):")

        for act in activities:
            name = act.get("activityName", "Unnamed Activity")
            activity_type = act.get("activityType", {}).get("typeKey", "unknown")
            duration_min = round(act.get("duration", 0) / 60, 1)
            burned_kcal = act.get("calories", 0)

            print(f" - [{activity_type.upper()}] {name}: {duration_min} mins | {burned_kcal} kcal")

        return {
            "date": today,
            "bmr_kcal": bmr_calories,
            "active_kcal": active_calories,
            "total_burned_kcal": total_burned,
            "activities": activities
        }

    except GarminConnectAuthenticationError:
        print("Error: Invalid email or password.")
    except GarminConnectTooManyRequestsError:
        print("Error: Too many requests sent. Garmin rate limited your IP.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    fetch_garmin_summary()
