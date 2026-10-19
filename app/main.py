"""Application factory: routers, error handling, static landing page."""

import stat
from pathlib import Path

import anyio
from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from starlette.exceptions import HTTPException
from starlette.responses import Response
from starlette.types import Scope

from app import health
from app.shared.http import install_error_handling

STATIC_DIR = Path(__file__).parent / "static"


class _StaticFiles(StaticFiles):
    """A missing file is "not found" for every method; only existing files answer 405 (R-6)."""

    async def get_response(self, path: str, scope: Scope) -> Response:
        if scope["method"] not in ("GET", "HEAD"):
            try:
                _, stat_result = await anyio.to_thread.run_sync(self.lookup_path, path)
            except (OSError, ValueError):
                stat_result = None
            if stat_result is None or not stat.S_ISREG(stat_result.st_mode):
                raise HTTPException(status_code=404)
        return await super().get_response(path, scope)


def create_app() -> FastAPI:
    # Interactive API docs off: they load third-party assets (CSP) and are unauthenticated.
    app = FastAPI(title="Polsan Leave Manager", docs_url=None, redoc_url=None, openapi_url=None)
    app.include_router(health.router)

    @app.api_route("/", methods=["GET", "HEAD"], include_in_schema=False)
    def landing_page() -> FileResponse:
        return FileResponse(STATIC_DIR / "index.html")

    install_error_handling(app)
    # A narrow mount, not "/": a catch-all would shadow the router's 404/405 distinction.
    app.mount("/static", _StaticFiles(directory=STATIC_DIR), name="static")
    return app


app = create_app()
