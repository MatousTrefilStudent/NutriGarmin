from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"

app = FastAPI(title="NutriGarmin API")

app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


@app.get("/", response_class=FileResponse)
@app.get("/index.html", response_class=FileResponse)
@app.get("/static/index.html", response_class=FileResponse)
def read_root():
    return FileResponse(STATIC_DIR / "index.html")

"""uvicorn main:app --reload"""