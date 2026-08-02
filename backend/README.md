# Rule Engine + Review-UI Backend

A minimal deterministic building-compliance service built with Python, FastAPI,
and pytest. It uses no LLM, prompts, or AI compliance logic.

> **Important:** Every threshold in `backend/app/rules.py` is a clearly marked
> sample value. The ruleset is versioned as `sample-2026.1`, but is not an
> official code for any jurisdiction. Replace and validate these values with the
> authority having jurisdiction before production use.

## Setup

Python 3.10 or newer is recommended.

```bash
cd backend
python -m venv .venv
# Windows PowerShell: .venv\Scripts\Activate.ps1
# macOS/Linux: source .venv/bin/activate
python -m pip install -r requirements.txt
```

## Run tests

```bash
cd backend
python -m pytest -q
```

## Start the API

```bash
cd backend
python -m uvicorn app.main:app --reload
```

Open `http://127.0.0.1:8000/docs` for interactive API documentation.

## Endpoints

- `GET /health` — service health and active ruleset version.
- `POST /api/v1/compliance/validate` — run Gate 1 or Gate 2 by setting `gate`
  to `pre_generation` or `post_generation` and supplying `metrics`.
- `POST /api/v1/review/validate` — validate generated geometry metrics and
  return all results plus a frontend-friendly `failures` list.

Example Gate 1 request:

```json
{
  "gate": "pre_generation",
  "metrics": {
    "egress_width_mm": 1000,
    "room_area_m2": 12,
    "stair_rise_mm": 175,
    "stair_run_mm": 280,
    "door_clearance_mm": 850,
    "corridor_clearance_mm": 1000,
    "wheelchair_turning_mm": 1600
  }
}
```

## Validation flow

Gate 1 evaluates proposed design metrics before generation. Any failed rule sets
`accepted` to false and `blocked` to true, so generation should not begin.

Gate 2 calls the same deterministic evaluator using a `GeometryMetricsProvider`.
The included static provider accepts request measurements for now; a future 3D
adapter can implement `get_metrics()` to return measured geometry. Any failure
blocks the generated result.

The CI workflow installs dependencies and runs pytest on every push and pull
request. A failed test produces a failed compliance-gate job.
