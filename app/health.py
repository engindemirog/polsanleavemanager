"""Health check for monitoring: public by design (docs/security.md), reports status only."""

from fastapi import APIRouter

router = APIRouter()


@router.get("/api/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
