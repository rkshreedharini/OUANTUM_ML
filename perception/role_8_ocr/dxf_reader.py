import ezdxf

def read_dxf(file_path):
    doc = ezdxf.readfile(file_path)
    msp = doc.modelspace()

    walls = []

    for entity in msp:
        if entity.dxftype() == "LWPOLYLINE":
            points = []

            for point in entity.get_points():
                points.append((point[0], point[1]))

            walls.append(points)

    return walls