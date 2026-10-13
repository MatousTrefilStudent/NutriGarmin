from datetime import date
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from garminconnect import Garmin

app = FastAPI()

# ==========================================
# LAYER 2: UNIFIED DATA MODEL & SAVING
# ==========================================

class UnifiedActivityData(BaseModel):
    source: str
    date: str
    active_kcal: float
    bmr_kcal: float
    total_kcal: float

def save_activity_to_db(data: UnifiedActivityData):
    """
    Unified function to save data into the database and update daily summary.
    Works for both Garmin and Manual inputs.
    """
    # Zde v budoucnu implementujete SQLAlchemy zápis do databáze[cite: 1]
    print(f"Saving data from {data.source}: {data.total_kcal} kcal burned.")
    
    return {
        "status": "success",
        "message": "Activity successfully saved and daily balance updated",
        "data": data
    }


# ==========================================
# LAYER 1: ADAPTERS (MANUAL & GARMIN)
# ==========================================

# --- 1A. Manual Input Adapter ---
class ManualInputPayload(BaseModel):
    date: str
    active_kcal: float
    bmr_kcal: float

@app.post("/api/activity/manual")
def save_activity_manual_input(payload: ManualInputPayload):
    """
    Fallback option for manual calorie entry if Garmin API is offline[cite: 1].
    """
    unified_data = UnifiedActivityData(
        source="Manual",
        date=payload.date,
        active_kcal=payload.active_kcal,
        bmr_kcal=payload.bmr_kcal,
        total_kcal=payload.active_kcal + payload.bmr_kcal
    )
    
    return save_activity_to_db(unified_data)


# --- 1B. Garmin Connect Adapter ---
class GarminCredentials(BaseModel):
    email: str
    password: str

@app.post("/api/activity/sync-garmin")
def sync_garmin_data(credentials: GarminCredentials):
    """
    Connects to Garmin API, fetches today's summary, and transforms it[cite: 1].
    """
    today = date.today().isoformat()
    
    try:
        # Inicializace a přihlášení ke Garmin Connect[cite: 1]
        client = Garmin(credentials.email, credentials.password)
        client.login()
        
        # Stažení souhrnných dat pro dnešní den[cite: 1]
        stats = client.get_user_summary(today)
        
        bmr = stats.get("bmrCalories", 0)
        active = stats.get("activeCalories", 0)
        
        # Transformace dat do sjednoceného formátu
        unified_data = UnifiedActivityData(
            source="Garmin Connect",
            date=today,
            active_kcal=active,
            bmr_kcal=bmr,
            total_kcal=bmr + active
        )
        
        return save_activity_to_db(unified_data)

    except Exception as e:
        # Zachycení chyb API (např. špatné heslo nebo rate limit)[cite: 1]
        raise HTTPException(
            status_code=400, 
            detail=f"Garmin synchronization failed. Use manual input. Error: {str(e)}"
        )

sync_garmin_data({"email": "matous.trefil@gmail.com", "password":"123456789"})