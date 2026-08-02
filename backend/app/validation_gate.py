"""Pre-generation and post-generation compliance gates."""

from typing import Protocol

from pydantic import BaseModel

from .rules import BuildingMetrics, RULESET_VERSION, RuleResult, evaluate_rules


class GeometryMetricsProvider(Protocol):
    """Future adapters for a 3D engine implement this measurement contract."""

    def get_metrics(self) -> BuildingMetrics: ...


class StaticGeometryMetricsProvider:
    """Temporary adapter for geometry measurements supplied in an API request."""

    def __init__(self, metrics: BuildingMetrics) -> None:
        self._metrics = metrics

    def get_metrics(self) -> BuildingMetrics:
        return self._metrics


class ValidationResponse(BaseModel):
    gate: str
    ruleset_version: str
    accepted: bool
    blocked: bool
    results: list[RuleResult]
    failures: list[RuleResult]


def _response(gate: str, metrics: BuildingMetrics) -> ValidationResponse:
    results = evaluate_rules(metrics)
    failures = [result for result in results if not result.passed]
    accepted = not failures
    return ValidationResponse(
        gate=gate,
        ruleset_version=RULESET_VERSION,
        accepted=accepted,
        blocked=not accepted,
        results=results,
        failures=failures,
    )


def validate_pre_generation(metrics: BuildingMetrics) -> ValidationResponse:
    """Gate 1: reject design inputs before 3D generation."""

    return _response("pre_generation", metrics)


def validate_post_generation(provider: GeometryMetricsProvider) -> ValidationResponse:
    """Gate 2: block generated geometry measured by the provider."""

    return _response("post_generation", provider.get_metrics())
