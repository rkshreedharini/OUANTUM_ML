import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.rules import BuildingMetrics, RULES, evaluate_rules
from app.validation_gate import (
    StaticGeometryMetricsProvider,
    validate_post_generation,
    validate_pre_generation,
)


@pytest.fixture
def valid_metrics() -> BuildingMetrics:
    return BuildingMetrics(
        egress_width_mm=1000,
        room_area_m2=12,
        stair_rise_mm=175,
        stair_run_mm=280,
        door_clearance_mm=850,
        corridor_clearance_mm=1000,
        wheelchair_turning_mm=1600,
    )


def with_change(metrics: BuildingMetrics, **change: float) -> BuildingMetrics:
    return metrics.model_copy(update=change)


def failed_ids(metrics: BuildingMetrics) -> set[str]:
    return {result.rule_id for result in evaluate_rules(metrics) if not result.passed}


def test_fully_valid_building(valid_metrics: BuildingMetrics) -> None:
    results = evaluate_rules(valid_metrics)
    assert len(results) == len(RULES) == 7
    assert all(result.passed for result in results)


@pytest.mark.parametrize(
    ("change", "expected_rule"),
    [
        ({"egress_width_mm": 899}, "EGR-001"),
        ({"room_area_m2": 9.4}, "ROOM-001"),
        ({"stair_rise_mm": 191}, "STAIR-001"),
        ({"stair_run_mm": 249}, "STAIR-002"),
    ],
    ids=["invalid-egress", "invalid-room-area", "invalid-stair-rise", "invalid-stair-run"],
)
def test_individual_rule_failures(valid_metrics: BuildingMetrics, change: dict[str, float], expected_rule: str) -> None:
    assert failed_ids(with_change(valid_metrics, **change)) == {expected_rule}


@pytest.mark.parametrize(
    ("metric", "rule_id"),
    [
        ("door_clearance_mm", "ACC-001"),
        ("corridor_clearance_mm", "ACC-002"),
        ("wheelchair_turning_mm", "ACC-003"),
    ],
)
def test_invalid_accessibility(valid_metrics: BuildingMetrics, metric: str, rule_id: str) -> None:
    assert failed_ids(with_change(valid_metrics, **{metric: 1})) == {rule_id}


def test_gate_1_rejection(valid_metrics: BuildingMetrics) -> None:
    response = validate_pre_generation(with_change(valid_metrics, room_area_m2=5))
    assert response.blocked and not response.accepted
    assert response.gate == "pre_generation"


def test_gate_2_rejection(valid_metrics: BuildingMetrics) -> None:
    provider = StaticGeometryMetricsProvider(with_change(valid_metrics, egress_width_mm=500))
    response = validate_post_generation(provider)
    assert response.blocked and response.failures[0].rule_id == "EGR-001"


def test_gate_2_success(valid_metrics: BuildingMetrics) -> None:
    response = validate_post_generation(StaticGeometryMetricsProvider(valid_metrics))
    assert response.accepted and not response.blocked and response.failures == []


def test_review_api_returns_structured_failures(valid_metrics: BuildingMetrics) -> None:
    client = TestClient(app)
    payload = with_change(valid_metrics, stair_run_mm=100).model_dump()
    response = client.post("/api/v1/review/validate", json=payload)
    assert response.status_code == 200
    body = response.json()
    assert body["blocked"] is True
    assert body["failures"][0]["rule_id"] == "STAIR-002"
    assert set(body["failures"][0]) == {
        "rule_id", "ruleset_version", "category", "passed", "actual_value",
        "required_value", "severity", "message",
    }


def test_health_endpoint() -> None:
    response = TestClient(app).get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
