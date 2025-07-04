import ezdxf
from shapely.geometry import Polygon

def parse_dxf(file_path):
    """Parse DXF file and extract wall, restricted, and entrance polygons."""
    doc = ezdxf.readfile(file_path)
    msp = doc.modelspace()
    walls, restricted, entrances = [], [], []
    for e in msp:
        if e.dxftype() == 'LWPOLYLINE':
            color = e.dxf.color
            points = [(p[0], p[1]) for p in e.get_points()]
            poly = Polygon(points)
            if color == 7:  # Black (walls)
                walls.append(poly)
            elif color == 5:  # Blue (restricted)
                restricted.append(poly)
            elif color == 1:  # Red (entrance)
                entrances.append(poly)
    return walls, restricted, entrances
