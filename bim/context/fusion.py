from skimage.morphology import skeletonize
from shapely.geometry import Point, Polygon
from .scale import ScaleEstimator
from .schema import (
    BuildingContext,
    WallSegment,
    RoomPolygon,
    Point2D,
    Opening,
    OpeningType,
    DimensionAnnotation
)

import cv2
import math


class FusionEngine:

    def __init__(self):
        print("Fusion Engine Initialized")
        self.scale_estimator = ScaleEstimator()

    # --------------------------------------------------
    # Skeletonization
    # --------------------------------------------------

    def skeletonize_mask(self, mask):

        binary = mask > 0
        skeleton = skeletonize(binary)

        return skeleton.astype("uint8")

    # --------------------------------------------------
    # Centerline Extraction
    # --------------------------------------------------

    def extract_centerlines(self, skeleton):

        contours, _ = cv2.findContours(
            skeleton,
            cv2.RETR_EXTERNAL,
            cv2.CHAIN_APPROX_NONE
        )

        centerlines = []

        for contour in contours:

            line = []

            for point in contour:

                x, y = point[0]
                line.append((int(x), int(y)))

            centerlines.append(line)

        return centerlines

    # --------------------------------------------------
    # Orthogonal Snapping
    # --------------------------------------------------

    def snap_to_orthogonal(self, line, threshold=10):

        if len(line) < 2:
            return line, False

        x1, y1 = line[0]
        x2, y2 = line[-1]

        angle = abs(
            math.degrees(
                math.atan2(
                    y2 - y1,
                    x2 - x1
                )
            )
        )

        # Horizontal

        if angle < threshold or angle > (180 - threshold):

            avg_y = (y1 + y2) // 2

            snapped = [
                (x, avg_y)
                for x, y in line
            ]

            return snapped, True

        # Vertical

        elif abs(angle - 90) < threshold:

            avg_x = (x1 + x2) // 2

            snapped = [
                (avg_x, y)
                for x, y in line
            ]

            return snapped, True

        return line, False

    # --------------------------------------------------
    # Room Labels
    # --------------------------------------------------

    def attach_room_labels(
        self,
        room_polygons,
        ocr_results
    ):

        room_mapping = {}

        for room_id, polygon_points in room_polygons.items():

            polygon = Polygon(polygon_points)

            for item in ocr_results:

                point = Point(
                    item["x"],
                    item["y"]
                )

                if polygon.contains(point):

                    room_mapping[room_id] = item["text"]

        return room_mapping

    # --------------------------------------------------
    # Door / Window Projection
    # --------------------------------------------------

    def project_openings(
    self,
    centerlines: list,
    openings: list) -> dict:

        mapping = {}

        for opening in openings:

            ox = opening["x"]
            oy = opening["y"]

            best_wall = None
            best_distance = float("inf")

            for wall_id, line in enumerate(centerlines):

                for px, py in line:

                    d = math.sqrt(
                        (ox - px) ** 2 +
                        (oy - py) ** 2
                    )

                    if d < best_distance:

                        best_distance = d
                        best_wall = wall_id

            mapping[opening["id"]] = {

                "wall_id": best_wall,
                "distance": round(best_distance, 2)

            }

        return mapping

    # --------------------------------------------------
    # Full Pipeline
    # --------------------------------------------------

        # --------------------------------------------------
    # Full Pipeline
    # --------------------------------------------------

    def run(
        self,
        mask,
        room_polygons,
        ocr_results,
        openings,
        dimensions=None,
        scalebar=None,
        door_widths=None
    ):
        """
        Execute the complete Fusion pipeline and
        return a BuildingContext object.
        """

        # ----------------------------
        # Skeletonization
        # ----------------------------

        skeleton = self.skeletonize_mask(mask)

        # ----------------------------
        # Centerline Extraction
        # ----------------------------

        centerlines = self.extract_centerlines(skeleton)

        snapped_lines = []

        for line in centerlines:

            snapped, status = self.snap_to_orthogonal(line)

            snapped_lines.append((snapped, status))

        # ----------------------------
        # Room Labels
        # ----------------------------

        room_labels = self.attach_room_labels(
            room_polygons,
            ocr_results
        )

        # ----------------------------
        # Opening Projection
        # ----------------------------

        opening_map = self.project_openings(
            [line for line, _ in snapped_lines],
            openings
        )

        # ----------------------------
        # Scale Estimation
        # ----------------------------

        dimension_scale = self.scale_estimator.estimate_from_dimensions(
            dimensions or []
        )

        scalebar_scale = self.scale_estimator.estimate_from_scalebar(
            scalebar
        )

        door_scale = self.scale_estimator.estimate_from_doors(
            door_widths or []
        )

        final_scale = self.scale_estimator.resolve_scale(
            dimension_scale,
            scalebar_scale,
            door_scale
        )

        # =========================================================
        # Build Schema Objects
        # =========================================================

        walls = []

        for idx, (line, snapped) in enumerate(snapped_lines):

            if len(line) < 2:
                continue

            start = Point2D(
                x=float(line[0][0]),
                y=float(line[0][1])
            )

            end = Point2D(
                x=float(line[-1][0]),
                y=float(line[-1][1])
            )

            wall = WallSegment(
                wall_id=f"Wall_{idx+1}",
                start=start,
                end=end,
                thickness=200.0,
                is_orthogonal_snapped=snapped,
                openings=[]
            )

            walls.append(wall)

        # ---------------- Rooms ----------------

        rooms = []

        for room_id, polygon in room_polygons.items():

            pts = []

            for x, y in polygon:

                pts.append(
                    Point2D(
                        x=float(x),
                        y=float(y)
                    )
                )

            room = RoomPolygon(
                room_id=room_id,
                room_label=room_labels.get(room_id),
                points=pts,
                area=None
            )

            rooms.append(room)

        # --------------- Dimensions -------------

        dimension_objects = []

        if dimensions:

            for value in dimensions:

                dimension_objects.append(
                    DimensionAnnotation(
                        text=str(value),
                        value=float(value),
                        unit="mm",
                        position=Point2D(
                            x=0,
                            y=0
                        )
                    )
                )

        # =========================================================
        # Final Building Context
        # =========================================================

        context = BuildingContext(
            walls=walls,
            rooms=rooms,
            dimensions=dimension_objects
        )

        return context