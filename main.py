import webbrowser
from contextlib import asynccontextmanager
from pathlib import Path
from threading import Timer

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

BASE_DIR = Path(__file__).resolve().parent
# Keep the website files in the project's static directory.
STATIC_DIR = BASE_DIR / "static"

app = FastAPI(title="NutriGarmin API")

# Serve CSS, JavaScript, and other files from the static directory.
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


# Serve the main page at each supported entry URL.
@app.get("/", response_class=FileResponse)
@app.get("/index.html", response_class=FileResponse)
@app.get("/static/index.html", response_class=FileResponse)
def read_root():
    return FileResponse(STATIC_DIR / "index.html")


if __name__ == "__main__":
    import uvicorn

    # Run the development server when this file is executed directly.
    uvicorn.run(
        "main:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
        app_dir=str(BASE_DIR),
        reload_dirs=[str(BASE_DIR)],
    )