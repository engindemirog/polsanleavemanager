"""Application factory: routers, error handling, static landing page."""

from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app import health
from app.shared.http import install_error_handling

STATIC_DIR = Path(__file__).parent / "static"


def create_app() -> FastAPI:
    # Interactive API docs off: they load third-party assets (CSP) and are unauthenticated.
    app = FastAPI(title="Polsan Leave Manager", docs_url=None, redoc_url=None, openapi_url=None)
    app.include_router(health.router)
    install_error_handling(app)
    # Mounted last: "/" matches every path, so API routes must be registered before it.
    app.mount("/", StaticFiles(directory=STATIC_DIR, html=True), name="static")
    return app


app = create_app()
