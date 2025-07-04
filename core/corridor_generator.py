from shapely.geometry import Polygon
import numpy as np

def generate_corridors(ilots, corridor_width=1.5):
    if len(ilots) < 4:
        return []
    y_positions = [ilot['position'][1] for ilot in ilots]
    y_sorted = sorted(y_positions)
    bins = []
    bin_size = 2.0
    for y in y_sorted:
        if not bins or abs(y - bins[-1][0]) > bin_size:
            bins.append([y])
        else:
            bins[-1].append(y)
    row_centers = [np.mean(row) for row in bins if len(row) >= 2]
    corridors = []
    for i in range(len(row_centers) - 1):
        y1 = row_centers[i]
        y2 = row_centers[i + 1]
        row1_ilots = [ilot for ilot in ilots if abs(ilot['position'][1] - y1) < bin_size]
        row2_ilots = [ilot for ilot in ilots if abs(ilot['position'][1] - y2) < bin_size]
        if len(row1_ilots) >= 2 and len(row2_ilots) >= 2:
            x_min = min(min(ilot['polygon'].bounds[0] for ilot in row1_ilots), min(ilot['polygon'].bounds[0] for ilot in row2_ilots))
            x_max = max(max(ilot['polygon'].bounds[2] for ilot in row1_ilots), max(ilot['polygon'].bounds[2] for ilot in row2_ilots))
            y_center = (y1 + y2) / 2
            corridor = Polygon([
                (x_min, y_center - corridor_width/2),
                (x_max, y_center - corridor_width/2),
                (x_max, y_center + corridor_width/2),
                (x_min, y_center + corridor_width/2)
            ])
            overlap = False
            for ilot in ilots:
                if corridor.intersects(ilot['polygon']):
                    overlap = True
                    break
            if not overlap:
                corridors.append(corridor)
    return corridors
