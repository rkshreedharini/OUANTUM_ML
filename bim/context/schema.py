"""
BIM Context Schema
Schema Owner: [Your Name]
Version: 1.0.0 (FROZEN)
Date: 2026-07-22

RULE: Append-only changes. Never mutate in place.
If changes needed, create v1.1.0, v2.0.0, etc.

Used by:
- Fusion Engineer (Role 11): Fills this with building data
- Validation Gates Engineer (Role 12): Reads this to check errors
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Literal
from enum import Enum


# ============================================================
# ENUMS (pick-one options)
# ============================================================

class OpeningType(str, Enum):
    DOOR = "door"
    WINDOW = "window"


class IssueSeverity(str, Enum):
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


class IssueType(str, Enum):
    CLOSED_POLYGON = "closed_polygon"
    CONNECTED_GRAPH = "connected_graph"
    AREA_PLAUSIBLE = "area_plausible"
    OVERLAP = "overlap"
    OPENING_DIMENSION = "opening_dimension"


# ============================================================
# SUB-MODELS
# ============================================================

class Point2D(BaseModel):
    """A single point on the 2D floor plan."""
    x: float
    y: float


class Opening(BaseModel):
    """A door or window inside a wall."""
    opening_id: str = Field(description="Unique ID")
    opening_type: OpeningType = Field(description="Door or window")
    width: float = Field(description="Width in real-world units")
    height: float = Field(description="Height in real-world units")
    position_along_wall: float = Field(description="Distance from wall start")


class WallSegment(BaseModel):
    """A single wall in the building."""
    wall_id: str = Field(description="Unique ID")
    start: Point2D = Field(description="Start coordinate")
    end: Point2D = Field(description="End coordinate")
    thickness: float = Field(description="Wall thickness")
    is_orthogonal_snapped: bool = Field(
        default=False,
        description="True if snapped to 90 degrees"
    )
    openings: List[Opening] = Field(default_factory=list)


class RoomPolygon(BaseModel):
    """A room defined by corner points."""
    room_id: str = Field(description="Unique ID")
    room_label: Optional[str] = Field(
        default=None,
        description="Name like 'Kitchen' or 'B101'"
    )
    points: List[Point2D] = Field(description="Ordered corner points")
    area: Optional[float] = Field(default=None)


class DimensionAnnotation(BaseModel):
    """Text measurement found on drawing."""
    text: str = Field(description="Raw text like '3.5m'")
    value: float = Field(description="Numeric value")
    unit: str = Field(description="Unit: m, ft, mm")
    position: Point2D = Field(description="Where text is located")


class ValidationIssue(BaseModel):
    """A problem found during validation."""
    issue_type: IssueType = Field(description="What kind of problem")
    severity: IssueSeverity = Field(description="How serious")
    description: str = Field(description="Human-readable explanation")
    related_element_id: Optional[str] = Field(default=None)


# ============================================================
# MAIN CONTAINER
# ============================================================

class BuildingContext(BaseModel):
    """
    Main container for all building geometry and context.
    FROZEN at version 1.0.0
    """
    schema_version: str = Field(
        default="1.0.0",
        description="Schema version - NEVER change in place"
    )
    walls: List[WallSegment] = Field(default_factory=list)
    rooms: List[RoomPolygon] = Field(default_factory=list)
    dimensions: List[DimensionAnnotation] = Field(default_factory=list)
    validation_issues: List[ValidationIssue] = Field(default_factory=list)