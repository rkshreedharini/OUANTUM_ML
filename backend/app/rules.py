"""Deterministic, versioned building-code rule evaluation.

All values below are SAMPLE CONFIGURABLE THRESHOLDS. They are not a claim of
compliance with any jurisdiction and must be replaced or approved before use.
"""

from dataclasses import dataclass
from typing import Literal

from pydantic import BaseModel, Field


RULESET_VERSION = "sample-2026.1"
Severity = Literal["error", "warning"]


@dataclass(frozen=True)
class RuleDefinition:
    rule_id: str
    metric: str
    category: str
    comparison: Literal["minimum", "maximum"]
    required_value: float
    unit: str
    severity: Severity = "error"


# SAMPLE values only. Keeping them in one immutable registry makes replacing
# them with jurisdiction-approved values straightforward and auditable.
RULES: tuple[RuleDefinition, ...] = (
    RuleDefinition("EGR-001", "egress_width_mm", "egress", "minimum", 900, "mm"),
    RuleDefinition("ROOM-001", "room_area_m2", "habitable_space", "minimum", 9.5, "m²"),
    RuleDefinition("STAIR-001", "stair_rise_mm", "stairs", "maximum", 190, "mm"),
    RuleDefinition("STAIR-002", "stair_run_mm", "stairs", "minimum", 250, "mm"),
    RuleDefinition("ACC-001", "door_clearance_mm", "accessibility", "minimum", 815, "mm"),
    RuleDefinition("ACC-002", "corridor_clearance_mm", "accessibility", "minimum", 915, "mm"),
    RuleDefinition("ACC-003", "wheelchair_turning_mm", "accessibility", "minimum", 1500, "mm"),
)


class BuildingMetrics(BaseModel):
    """Measurements required by the current sample ruleset."""

    egress_width_mm: float = Field(ge=0)
    room_area_m2: float = Field(ge=0)
    stair_rise_mm: float = Field(ge=0)
    stair_run_mm: float = Field(ge=0)
    door_clearance_mm: float = Field(ge=0)
    corridor_clearance_mm: float = Field(ge=0)
    wheelchair_turning_mm: float = Field(ge=0)


class RuleResult(BaseModel):
    rule_id: str
    ruleset_version: str
    category: str
    passed: bool
    actual_value: float
    required_value: float
    severity: Severity
    message: str


def evaluate_rules(metrics: BuildingMetrics) -> list[RuleResult]:
    """Evaluate every rule with no external state, AI, or nondeterminism."""

    results: list[RuleResult] = []
    for rule in RULES:
        actual = getattr(metrics, rule.metric)
        passed = actual >= rule.required_value if rule.comparison == "minimum" else actual <= rule.required_value
        relation = "at least" if rule.comparison == "minimum" else "at most"
        status = "passes" if passed else "fails"
        message = (
            f"{rule.rule_id} {status}: {rule.metric} is {actual:g} {rule.unit}; "
            f"required {relation} {rule.required_value:g} {rule.unit}."
        )
        results.append(
            RuleResult(
                rule_id=rule.rule_id,
                ruleset_version=RULESET_VERSION,
                category=rule.category,
                passed=passed,
                actual_value=actual,
                required_value=rule.required_value,
                severity=rule.severity,
                message=message,
            )
        )
    return results
