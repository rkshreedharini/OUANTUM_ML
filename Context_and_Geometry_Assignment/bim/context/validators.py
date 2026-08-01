from shapely.geometry import Polygon

from .schema import (
    BuildingContext,
    ValidationIssue,
    IssueType,
    IssueSeverity
)


class ValidationEngine:

    def __init__(self):
        print("Validation Engine Initialized")

    # --------------------------------------------------
    # 1. Check whether room polygons are valid
    # --------------------------------------------------

    def validate_closed_rooms(self, context: BuildingContext):

        issues = []

        for room in context.rooms:

            # A polygon needs at least 3 points
            if len(room.points) < 3:

                issue = ValidationIssue(
                    issue_type=IssueType.CLOSED_POLYGON,
                    severity=IssueSeverity.ERROR,
                    description=(
                        f"Room {room.room_id} "
                        "does not have enough points."
                    ),
                    related_element_id=room.room_id
                )

                issues.append(issue)
                continue

            coordinates = [
                (point.x, point.y)
                for point in room.points
            ]

            room_polygon = Polygon(coordinates)

            # Check self-crossing or invalid polygon
            if not room_polygon.is_valid:

                issue = ValidationIssue(
                    issue_type=IssueType.CLOSED_POLYGON,
                    severity=IssueSeverity.ERROR,
                    description=(
                        f"Room {room.room_id} has an invalid "
                        "or self-crossing polygon."
                    ),
                    related_element_id=room.room_id
                )

                issues.append(issue)

            # Check zero-area polygon
            elif room_polygon.area == 0:

                issue = ValidationIssue(
                    issue_type=IssueType.CLOSED_POLYGON,
                    severity=IssueSeverity.ERROR,
                    description=(
                        f"Room {room.room_id} has zero area."
                    ),
                    related_element_id=room.room_id
                )

                issues.append(issue)

        return issues

    # --------------------------------------------------
    # 2. Check whether walls are connected
    # --------------------------------------------------

    def validate_connected_walls(
        self,
        context: BuildingContext,
        tolerance: float = 5.0
    ):

        issues = []

        if len(context.walls) <= 1:
            return issues

        for current_wall in context.walls:

            is_connected = False

            for other_wall in context.walls:

                if current_wall.wall_id == other_wall.wall_id:
                    continue

                distances = [
                    (
                        (current_wall.start.x - other_wall.start.x) ** 2 +
                        (current_wall.start.y - other_wall.start.y) ** 2
                    ) ** 0.5,

                    (
                        (current_wall.start.x - other_wall.end.x) ** 2 +
                        (current_wall.start.y - other_wall.end.y) ** 2
                    ) ** 0.5,

                    (
                        (current_wall.end.x - other_wall.start.x) ** 2 +
                        (current_wall.end.y - other_wall.start.y) ** 2
                    ) ** 0.5,

                    (
                        (current_wall.end.x - other_wall.end.x) ** 2 +
                        (current_wall.end.y - other_wall.end.y) ** 2
                    ) ** 0.5
                ]

                if min(distances) <= tolerance:
                    is_connected = True
                    break

            if not is_connected:

                issue = ValidationIssue(
                    issue_type=IssueType.CONNECTED_GRAPH,
                    severity=IssueSeverity.ERROR,
                    description=(
                        f"Wall {current_wall.wall_id} "
                        "is not connected to another wall."
                    ),
                    related_element_id=current_wall.wall_id
                )

                issues.append(issue)

        return issues

    # --------------------------------------------------
    # 3. Check whether room area is reasonable
    # --------------------------------------------------

    def validate_room_area(
        self,
        context: BuildingContext,
        minimum_area: float = 20.0,
        maximum_area: float = 100000.0
    ):

        issues = []

        for room in context.rooms:

            if len(room.points) < 3:
                continue

            coordinates = [
                (point.x, point.y)
                for point in room.points
            ]

            room_polygon = Polygon(coordinates)

            # Invalid polygons are already handled
            if not room_polygon.is_valid:
                continue

            room_area = room_polygon.area

            if room_area < minimum_area:

                issue = ValidationIssue(
                    issue_type=IssueType.AREA_PLAUSIBLE,
                    severity=IssueSeverity.WARNING,
                    description=(
                        f"Room {room.room_id} area is too small. "
                        f"Calculated area: {room_area:.2f}"
                    ),
                    related_element_id=room.room_id
                )

                issues.append(issue)

            elif room_area > maximum_area:

                issue = ValidationIssue(
                    issue_type=IssueType.AREA_PLAUSIBLE,
                    severity=IssueSeverity.WARNING,
                    description=(
                        f"Room {room.room_id} area is too large. "
                        f"Calculated area: {room_area:.2f}"
                    ),
                    related_element_id=room.room_id
                )

                issues.append(issue)

        return issues

    # --------------------------------------------------
    # 4. Check whether rooms overlap
    # --------------------------------------------------

    def validate_room_overlap(self, context: BuildingContext):

        issues = []

        for i in range(len(context.rooms)):

            room_1 = context.rooms[i]

            if len(room_1.points) < 3:
                continue

            polygon_1 = Polygon(
                [(point.x, point.y) for point in room_1.points]
            )

            if not polygon_1.is_valid:
                continue

            for j in range(i + 1, len(context.rooms)):

                room_2 = context.rooms[j]

                if len(room_2.points) < 3:
                    continue

                polygon_2 = Polygon(
                    [(point.x, point.y) for point in room_2.points]
                )

                if not polygon_2.is_valid:
                    continue

                if polygon_1.overlaps(polygon_2):

                    issue = ValidationIssue(
                        issue_type=IssueType.OVERLAP,
                        severity=IssueSeverity.ERROR,
                        description=(
                            f"Room {room_1.room_id} overlaps with "
                            f"Room {room_2.room_id}."
                        ),
                        related_element_id=room_1.room_id
                    )

                    issues.append(issue)

        return issues

    # --------------------------------------------------
    # 5. Check whether opening dimensions are reasonable
    # --------------------------------------------------

    def validate_opening_dimensions(
        self,
        context: BuildingContext,
        minimum_width: float = 0.5,
        maximum_width: float = 5.0
    ):

        issues = []

        for wall in context.walls:

            for opening in wall.openings:

                if opening.width < minimum_width:

                    issue = ValidationIssue(
                        issue_type=IssueType.OPENING_DIMENSION,
                        severity=IssueSeverity.WARNING,
                        description=(
                            f"Opening {opening.opening_id} width is too small. "
                            f"Width: {opening.width:.2f}"
                        ),
                        related_element_id=opening.opening_id
                    )

                    issues.append(issue)

                elif opening.width > maximum_width:

                    issue = ValidationIssue(
                        issue_type=IssueType.OPENING_DIMENSION,
                        severity=IssueSeverity.WARNING,
                        description=(
                            f"Opening {opening.opening_id} width is too large. "
                            f"Width: {opening.width:.2f}"
                        ),
                        related_element_id=opening.opening_id
                    )

                    issues.append(issue)

        return issues

    # --------------------------------------------------
    # Run all validations
    # --------------------------------------------------

    def validate_all(self, context: BuildingContext):

        issues = []

        issues.extend(self.validate_closed_rooms(context))
        issues.extend(self.validate_connected_walls(context))
        issues.extend(self.validate_room_area(context))
        issues.extend(self.validate_room_overlap(context))
        issues.extend(self.validate_opening_dimensions(context))

        context.validation_issues = issues

        return issues