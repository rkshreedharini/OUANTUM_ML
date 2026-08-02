"""FastAPI routes consumed by compliance and Review-UI clients."""

from typing import Literal

from fastapi import APIRouter
from pydantic import BaseModel

from .rules import BuildingMetrics
from .validation_gate import (
    StaticGeometryMetricsProvider,
    ValidationResponse,
    validate_post_generation,
    validate_pre_generation,
)


router = APIRouter(prefix="/api/v1", tags=["validation"])


class ComplianceRequest(BaseModel):
    gate: Literal["pre_generation", "post_generation"] = "pre_generation"
    metrics: BuildingMetrics


@router.post("/compliance/validate", response_model=ValidationResponse)
def validate_compliance(request: ComplianceRequest) -> ValidationResponse:
    if request.gate == "post_generation":
        return validate_post_generation(StaticGeometryMetricsProvider(request.metrics))
    return validate_pre_generation(request.metrics)


@router.post("/review/validate", response_model=ValidationResponse)
def validate_for_review_ui(metrics: BuildingMetrics) -> ValidationResponse:
    """Return all results plus a frontend-friendly failures collection."""

    return validate_post_generation(StaticGeometryMetricsProvider(metrics))
