import statistics


class ScaleEstimator:
    """
    Estimate drawing scale using multiple cues.
    """

    def __init__(self):
        print("Scale Estimator Initialized")

    # -----------------------------------------
    # Dimension Text
    # -----------------------------------------

    def estimate_from_dimensions(self, dimensions):
        """
        Estimate scale using OCR dimension text.
        """

        if len(dimensions) == 0:
            return None

        return statistics.mean(dimensions)

    # -----------------------------------------
    # Scale Bar
    # -----------------------------------------

    def estimate_from_scalebar(self, scalebar_value):
        """
        Estimate scale using scale bar.
        """

        if scalebar_value is None:
            return None

        return scalebar_value

    # -----------------------------------------
    # Door Width Prior
    # -----------------------------------------

    def estimate_from_doors(self, door_widths):
        """
        Estimate scale using detected door widths.
        """

        if len(door_widths) == 0:
            return None

        return statistics.mean(door_widths)

    # -----------------------------------------
    # Resolve
    # -----------------------------------------

    def resolve_scale(
        self,
        dimension_scale,
        scalebar_scale,
        door_scale
    ):

        candidates = []

        if dimension_scale is not None:
            candidates.append(dimension_scale)

        if scalebar_scale is not None:
            candidates.append(scalebar_scale)

        if door_scale is not None:
            candidates.append(door_scale)

        if len(candidates) == 0:
            return None

        return statistics.mean(candidates)