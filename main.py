from contextlib import asynccontextmanager
from pathlib import Path
from threading import Timer

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from starlette.requests import Request

from data_input.adapters import manual_input
from data_input.adapters.manual_input import router as manual_input_router

BASE_DIR = Path(__file__).resolve().parent
# Keep the website files in the project's static directory.
STATIC_DIR = BASE_DIR / "static"

app = FastAPI(title="NutriGarmin API")
app.include_router(manual_input_router)

# Prevent browsers from caching files during development
@app.middleware("http")
async def disable_cache_middleware(request: Request, call_next):
    response = await call_next(request)
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response

# Serve CSS, JavaScript, and other files from the static directory.
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


# Serve the main page at each supported entry URL.
@app.get("/", response_class=FileResponse)
@app.get("/index.html", response_class=FileResponse)
@app.get("/static/index.html", response_class=FileResponse)
def read_root():
    return FileResponse(STATIC_DIR / "index.html")


@app.get("/synchronize.html", response_class=FileResponse)
def read_synchronize():
    return FileResponse(STATIC_DIR / "synchronize.html")


if __name__ == "__main__":
    import uvicorn

    print(f"\nNutriGarmin server running on: http://127.0.0.1:8000\n")

    # Run the development server when this file is executed directly.
    uvicorn.run(
        "main:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
        reload_includes=["*.py", "*.html", "*.css"],
        app_dir=str(BASE_DIR),
        reload_dirs=[str(BASE_DIR)],
    )
