"""FastAPI application entry point."""

from fastapi import FastAPI

from .review_api import router
from .rules import RULESET_VERSION


app = FastAPI(
    title="Rule Engine + Review-UI Backend",
    version="0.1.0",
    description="Deterministic validation using sample, configurable thresholds.",
)
app.include_router(router)


@app.get("/health", tags=["system"])
def health() -> dict[str, str]:
    return {"status": "ok", "ruleset_version": RULESET_VERSION}
