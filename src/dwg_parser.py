import ezdxf
import tempfile
import os
import subprocess
import shutil
from typing import List, Dict, Any, Optional
from pathlib import Path
from shapely.geometry import Polygon, Point


class DWGParser:
    """
    Parser for DWG and DXF files using ezdxf library
    """

    def __init__(self):
        self.supported_entities = [
            'LWPOLYLINE', 'POLYLINE', 'LINE', 'ARC', 'CIRCLE', 'ELLIPSE',
            'SPLINE', 'HATCH'
        ]

    def parse_file(self, file_bytes: bytes,
                   filename: str) -> List[Dict[str, Any]]:
        """
        Parse DWG/DXF file and extract zones (closed polygons)

        Args:
            file_bytes: Raw file content as bytes
            filename: Original filename

        Returns:
            List of zone dictionaries with points and metadata
        """
        zones = []
        temp_file_path = None

        try:
            # Create temporary file
            with tempfile.NamedTemporaryFile(
                    delete=False, suffix=Path(filename).suffix) as temp_file:
                temp_file.write(file_bytes)
                temp_file_path = temp_file.name

            # Check file format and handle accordingly
            file_ext = Path(filename).suffix.lower()

            if file_ext == '.dwg':
                # Try enhanced DWG parser first
                try:
                    from .enhanced_dwg_parser import parse_dwg_file_enhanced
                    result = parse_dwg_file_enhanced(temp_file_path)
                    if result and result.get('zones'):
                        print(f"Enhanced parser successful: {result.get('parsing_method', 'unknown')}")
                        zones = result['zones']
                        if zones:  # Only return if we actually got zones
                            return self._validate_and_clean_zones(zones)
                except Exception as e:
                    print(f"Enhanced parser failed: {e}")
                
                # If enhanced parser failed, don't immediately fallback
                # Let it try DXF parsing methods below
                print(f"DWG file {filename} will be processed with DXF methods")

            # Handle DXF and DWG files differently
            doc = None
            if file_ext == '.dxf':
                # DXF files - use ezdxf directly
                try:
                    doc = ezdxf.readfile(temp_file_path)
                    print(f"Successfully opened {filename} as DXF")
                except ezdxf.DXFStructureError as e:
                    print(f"DXF Structure Error, trying recovery: {e}")
                    try:
                        doc = ezdxf.recover.readfile(temp_file_path)
                        print(f"Recovery successful for {filename}")
                    except Exception as recovery_error:
                        print(f"DXF recovery failed: {recovery_error}")
                        return []
                except Exception as e:
                    print(f"Cannot read DXF file {filename}: {e}")
                    raise Exception(f"Cannot read DXF file {filename}: {str(e)}")
            elif file_ext == '.dwg':
                # DWG files - ezdxf cannot read DWG directly
                print(f"DWG file {filename} cannot be read by ezdxf (DXF library)")
                print(f"DWG files require conversion to DXF format or specialized DWG parser")
                return []
            
            if not doc:
                return []

            modelspace = doc.modelspace()
            print(f"Modelspace entities: {len(list(modelspace))}")

            # Extract layers information
            layers = self._extract_layers(doc)
            print(f"Found {len(layers)} layers")

            # Parse different entity types with detailed logging
            lwpoly_zones = self._parse_lwpolylines(modelspace)
            poly_zones = self._parse_polylines(modelspace)
            hatch_zones = self._parse_hatches(modelspace)
            shape_zones = self._parse_closed_shapes(modelspace)
            line_zones = self._parse_line_networks(
                modelspace)  # New: detect rooms from line networks
            circle_zones = self._parse_circles_as_zones(
                modelspace)  # New: large circles as zones

            zones.extend(lwpoly_zones)
            zones.extend(poly_zones)
            zones.extend(hatch_zones)
            zones.extend(shape_zones)
            zones.extend(line_zones)
            zones.extend(circle_zones)

            print(f"Entity analysis:")
            print(f"  LWPolylines: {len(lwpoly_zones)} zones")
            print(f"  Polylines: {len(poly_zones)} zones")
            print(f"  Hatches: {len(hatch_zones)} zones")
            print(f"  Shapes: {len(shape_zones)} zones")
            print(f"  Line networks: {len(line_zones)} zones")
            print(f"  Circles: {len(circle_zones)} zones")

            # If no zones found, try additional parsing methods
            if len(zones) == 0:
                self._analyze_entity_types(modelspace)
                # Try parsing TEXT entities as room labels and surrounding geometry
                text_zones = self._parse_text_based_zones(modelspace)
                zones.extend(text_zones)

                # Try parsing BLOCK references as rooms
                block_zones = self._parse_block_zones(modelspace)
                zones.extend(block_zones)

            # Add layer information to zones
            for zone in zones:
                layer_name = zone.get('layer', '0')
                if layer_name in layers:
                    zone['layer_info'] = layers[layer_name]

        except ezdxf.DXFError as e:
            print(f"DXF Error: {e}")
            raise Exception(f"DXF parsing error: {str(e)}")
        except Exception as e:
            print(f"Parsing error: {e}")
            raise Exception(f"File parsing error: {str(e)}")
        finally:
            # Clean up temporary file
            try:
                os.unlink(temp_file_path)
            except:
                pass

        # Only validate if we have zones
        if zones:
            validated_zones = self._validate_and_clean_zones(zones)
            print(f"Final validated zones from {filename}: {len(validated_zones)}")
            return validated_zones
        else:
            print(f"No zones found in {filename}")
            return []

    def _parse_dwg_file(self, file_path: str, filename: str) -> List[Dict[str, Any]]:
        """Enhanced DWG file parsing with multiple fallback methods"""
        zones = []
        
        print(f"Attempting to parse DWG file: {filename}")
        
        # Method 1: Try ezdxf with recovery mode (only for DXF files)
        if file_path.lower().endswith('.dxf'):
            try:
                print("Method 1: Trying ezdxf recovery mode on DXF file...")
                doc = ezdxf.recover.readfile(file_path)
                zones = self._extract_zones_from_ezdxf(doc)
                if zones:
                    print(f"Successfully parsed {len(zones)} zones using ezdxf recovery")
                    return zones
            except Exception as e:
                print(f"ezdxf recovery failed: {e}")
        else:
            print("Skipping ezdxf method for DWG file (ezdxf only supports DXF)")
        
        # Method 2: Check for available conversion tools
        try:
            print("Method 2: Attempting DWG to DXF conversion...")
            converted_file = self._try_dwg_conversion(file_path)
            if converted_file:
                if converted_file.lower().endswith('.dxf'):
                    doc = ezdxf.readfile(converted_file)
                    zones = self._extract_zones_from_ezdxf(doc)
                else:
                    print("Conversion did not produce a DXF file")
                    zones = []
                os.unlink(converted_file)  # Clean up converted file
                if zones:
                    print(f"Successfully converted and parsed {len(zones)} zones")
                    return zones
        except Exception as e:
            print(f"DWG conversion failed: {e}")
        
        # If all methods fail, provide helpful error message
        raise Exception(
            f"Unable to parse DWG file '{filename}'. This could be due to:\n"
            f"1. Newer DWG format not supported\n"
            f"2. Encrypted or password-protected file\n"
            f"3. Corrupted file\n\n"
            f"Suggestions:\n"
            f"• Convert to DXF format using AutoCAD, FreeCAD, or LibreCAD\n"
            f"• Use 'Save As' → DXF format in your CAD software\n"
            f"• Try an older DWG format version (R14, 2000, 2004)\n"
            f"• Ensure the file is not password-protected"
        )

    def _extract_zones_from_ezdxf(self, doc) -> List[Dict[str, Any]]:
        """Extract zones using ezdxf (reuse existing method)"""
        zones = []
        modelspace = doc.modelspace()
        
        # Existing zone extraction logic
        lwpolyline_zones = self._parse_lwpolylines(modelspace)
        polyline_zones = self._parse_polylines(modelspace)
        hatch_zones = self._parse_hatches(modelspace)
        
        zones.extend(lwpolyline_zones)
        zones.extend(polyline_zones)
        zones.extend(hatch_zones)
        
        return zones

    def parse_file_from_path(self, file_path: str) -> List[Dict[str, Any]]:
        """Parse DWG/DXF file from file path"""
        zones = []

        try:
            # Only try ezdxf for DXF files
            if not file_path.lower().endswith('.dxf'):
                print(f"File {file_path} is not a DXF file. This parser only handles DXF files.")
                return []
                
            # Try to read the DXF file
            try:
                doc = ezdxf.readfile(file_path)
            except ezdxf.DXFStructureError:
                # Try with recovery mode for corrupted files
                doc = ezdxf.recover.readfile(file_path)

            modelspace = doc.modelspace()

            # Extract layers information
            layers = self._extract_layers(doc)

            # Parse different entity types
            zones.extend(self._parse_lwpolylines(modelspace))
            zones.extend(self._parse_polylines(modelspace))
            zones.extend(self._parse_hatches(modelspace))
            zones.extend(self._parse_closed_shapes(modelspace))

            # Filter out very small zones (likely noise)
            zones = [zone for zone in zones if zone.get('area', 0) > 0.1]

            # Add zone IDs
            for i, zone in enumerate(zones):
                zone['id'] = f"zone_{i+1}"
                zone['layers'] = layers

        except Exception as e:
            print(f"Error parsing DWG file: {str(e)}")
            return []

        return self._validate_and_clean_zones(zones)

    def _extract_layers(self, doc) -> Dict[str, Dict]:
        """Extract layer information from the document"""
        layers = {}

        try:
            for layer in doc.layers:
                layers[layer.dxf.name] = {
                    'name': layer.dxf.name,
                    'color': getattr(layer.dxf, 'color', 7),
                    'linetype': getattr(layer.dxf, 'linetype', 'CONTINUOUS'),
                    'visible':
                    not getattr(layer.dxf, 'flags', 0) & 1  # Check if frozen
                }
        except:
            # Fallback if layer extraction fails
            layers['0'] = {
                'name': '0',
                'color': 7,
                'linetype': 'CONTINUOUS',
                'visible': True
            }

        return layers

    def _parse_lwpolylines(self, modelspace) -> List[Dict[str, Any]]:
        """Parse LWPOLYLINE entities"""
        zones = []

        for entity in modelspace.query('LWPOLYLINE'):
            try:
                points = [(point[0], point[1]) for point in entity]
                if len(points) >= 3:  # Minimum for a polygon
                    # Check if closed or if first and last points are close
                    is_closed = entity.closed or (len(points) > 3 and 
                                abs(points[0][0] - points[-1][0]) < 0.1 and 
                                abs(points[0][1] - points[-1][1]) < 0.1)
                    
                    if is_closed:
                        # Ensure polygon is properly closed
                        if points[0] != points[-1]:
                            points.append(points[0])
                    
                    area = self._calculate_polygon_area(points)
                    if area > 1.0:  # Minimum area threshold
                        zones.append({
                            'points': points,
                            'layer': entity.dxf.layer,
                            'entity_type': 'LWPOLYLINE',
                            'closed': is_closed,
                            'area': area,
                            'perimeter': self._calculate_perimeter(points)
                        })
            except Exception as e:
                continue  # Skip problematic entities

        return zones

    def _parse_polylines(self, modelspace) -> List[Dict[str, Any]]:
        """Parse POLYLINE entities"""
        zones = []

        for entity in modelspace.query('POLYLINE'):
            if entity.is_closed:
                try:
                    points = [(vertex.dxf.location[0], vertex.dxf.location[1])
                              for vertex in entity.vertices]
                    if len(points) >= 3:
                        zones.append({
                            'points':
                            points,
                            'layer':
                            entity.dxf.layer,
                            'entity_type':
                            'POLYLINE',
                            'closed':
                            True,
                            'area':
                            self._calculate_polygon_area(points)
                        })
                except Exception as e:
                    continue

        return zones

    def _parse_hatches(self, modelspace) -> List[Dict[str, Any]]:
        """Parse HATCH entities to extract boundary polygons"""
        zones = []

        for entity in modelspace.query('HATCH'):
            try:
                # Get boundary paths - check both external and polyline boundaries
                for boundary_path in entity.paths:
                    points = []
                    
                    # Handle different path types
                    if hasattr(boundary_path, 'path_type_flags'):
                        # Check for external boundary or polyline boundary
                        if boundary_path.path_type_flags & 2 or boundary_path.path_type_flags & 1:
                            if hasattr(boundary_path, 'edges') and boundary_path.edges:
                                # Process edges
                                for edge in boundary_path.edges:
                                    if hasattr(edge, 'EDGE_TYPE'):
                                        if edge.EDGE_TYPE == 'LineEdge':
                                            points.append((edge.start[0], edge.start[1]))
                                        elif edge.EDGE_TYPE == 'ArcEdge':
                                            arc_points = self._approximate_arc(edge)
                                            points.extend(arc_points)
                            elif hasattr(boundary_path, 'vertices') and boundary_path.vertices:
                                # Handle polyline boundary
                                points = [(v[0], v[1]) for v in boundary_path.vertices]
                    
                    # Alternative: try to get source boundary objects
                    if not points and hasattr(boundary_path, 'source_boundary_objects'):
                        for obj in boundary_path.source_boundary_objects:
                            if hasattr(obj, 'vertices'):
                                points = [(v[0], v[1]) for v in obj.vertices]
                                break
                    
                    if len(points) >= 3:
                        # Ensure closed polygon
                        if points[0] != points[-1]:
                            points.append(points[0])
                        
                        area = self._calculate_polygon_area(points)
                        if area > 1.0:  # Minimum area threshold
                            zones.append({
                                'points': points,
                                'layer': entity.dxf.layer,
                                'entity_type': 'HATCH',
                                'closed': True,
                                'area': area,
                                'perimeter': self._calculate_perimeter(points)
                            })
                            break  # Only take the first valid boundary
                            
            except Exception as e:
                continue

        return zones

    def _parse_closed_shapes(self, modelspace) -> List[Dict[str, Any]]:
        """Parse other closed shapes like circles and rectangles"""
        zones = []

        # Parse circles
        for entity in modelspace.query('CIRCLE'):
            try:
                center = entity.dxf.center
                radius = entity.dxf.radius
                # Approximate circle with polygon
                points = self._circle_to_polygon(center[0], center[1], radius)
                zones.append({
                    'points': points,
                    'layer': entity.dxf.layer,
                    'entity_type': 'CIRCLE',
                    'closed': True,
                    'area': 3.14159 * radius * radius
                })
            except Exception as e:
                continue

        # Parse ellipses
        for entity in modelspace.query('ELLIPSE'):
            try:
                center = entity.dxf.center
                major_axis = entity.dxf.major_axis
                ratio = entity.dxf.ratio
                # Approximate ellipse with polygon
                points = self._ellipse_to_polygon(center, major_axis, ratio)
                zones.append({
                    'points': points,
                    'layer': entity.dxf.layer,
                    'entity_type': 'ELLIPSE',
                    'closed': True,
                    'area': self._calculate_polygon_area(points)
                })
            except Exception as e:
                continue

        return zones

    def _calculate_polygon_area(self, points: List[tuple]) -> float:
        """Calculate polygon area using shoelace formula"""
        if len(points) < 3:
            return 0.0

        area = 0.0
        n = len(points)

        for i in range(n):
            j = (i + 1) % n
            area += points[i][0] * points[j][1]
            area -= points[j][0] * points[i][1]

        return abs(area) / 2.0
    
    def _calculate_perimeter(self, points: List[tuple]) -> float:
        """Calculate polygon perimeter"""
        if len(points) < 2:
            return 0.0
        
        perimeter = 0.0
        for i in range(len(points)):
            j = (i + 1) % len(points)
            dx = points[j][0] - points[i][0]
            dy = points[j][1] - points[i][1]
            perimeter += (dx * dx + dy * dy) ** 0.5
        
        return perimeter
    
    def _calculate_bounds(self, points: List[tuple]) -> tuple:
        """Calculate bounding box of points"""
        if not points:
            return (0, 0, 0, 0)
        
        xs = [p[0] for p in points]
        ys = [p[1] for p in points]
        return (min(xs), min(ys), max(xs), max(ys))

    def _circle_to_polygon(self,
                           cx: float,
                           cy: float,
                           radius: float,
                           num_points: int = 32) -> List[tuple]:
        """Convert circle to polygon approximation"""
        import math
        points = []
        for i in range(num_points):
            angle = 2 * math.pi * i / num_points
            x = cx + radius * math.cos(angle)
            y = cy + radius * math.sin(angle)
            points.append((x, y))
        return points

    def _ellipse_to_polygon(self,
                            center,
                            major_axis,
                            ratio: float,
                            num_points: int = 32) -> List[tuple]:
        """Convert ellipse to polygon approximation"""
        import math
        points = []
        cx, cy = center[0], center[1]
        major_length = math.sqrt(major_axis[0]**2 + major_axis[1]**2)
        minor_length = major_length * ratio

        # Calculate rotation angle
        angle_offset = math.atan2(major_axis[1], major_axis[0])

        for i in range(num_points):
            t = 2 * math.pi * i / num_points
            # Ellipse in local coordinates
            local_x = major_length * math.cos(t)
            local_y = minor_length * math.sin(t)

            # Rotate and translate
            x = cx + local_x * math.cos(angle_offset) - local_y * math.sin(
                angle_offset)
            y = cy + local_x * math.sin(angle_offset) + local_y * math.cos(
                angle_offset)
            points.append((x, y))

        return points

    def _approximate_arc(self, edge, num_segments: int = 8) -> List[tuple]:
        """Approximate arc edge with line segments"""
        import math
        points = []

        center = edge.center
        radius = edge.radius
        start_angle = edge.start_angle
        end_angle = edge.end_angle

        # Handle angle wrapping
        if end_angle < start_angle:
            end_angle += 2 * math.pi

        angle_step = (end_angle - start_angle) / num_segments

        for i in range(num_segments + 1):
            angle = start_angle + i * angle_step
            x = center[0] + radius * math.cos(angle)
            y = center[1] + radius * math.sin(angle)
            points.append((x, y))

        return points

    def _validate_and_clean_zones(
            self, zones: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Validate and clean extracted zones"""
        valid_zones = []

        for zone in zones:
            # Check if zone has valid points
            if not zone.get('points') or len(zone['points']) < 3:
                continue

            # Remove duplicate consecutive points
            cleaned_points = []
            prev_point = None

            for point in zone['points']:
                if prev_point is None or (abs(point[0] - prev_point[0]) > 1e-6
                                          or abs(point[1] - prev_point[1])
                                          > 1e-6):
                    cleaned_points.append(point)
                    prev_point = point

            if len(cleaned_points) >= 3:
                zone['points'] = cleaned_points
                zone['area'] = self._calculate_polygon_area(cleaned_points)

                # Add bounding box
                xs = [p[0] for p in cleaned_points]
                ys = [p[1] for p in cleaned_points]
                zone['bounds'] = (min(xs), min(ys), max(xs), max(ys))

                valid_zones.append(zone)

        return valid_zones

    def _analyze_entity_types(self, modelspace):
        """Analyze entity types in the DXF for debugging"""
        entity_counts = {}
        for entity in modelspace:
            entity_type = entity.dxftype()
            entity_counts[entity_type] = entity_counts.get(entity_type, 0) + 1

        print("Entity types found in DXF:")
        for entity_type, count in sorted(entity_counts.items()):
            print(f"  {entity_type}: {count}")

    def _parse_line_networks(self, modelspace) -> List[Dict]:
        """Parse networks of connected lines to form closed boundaries"""
        zones = []
        lines = []

        # Collect all LINE entities
        for entity in modelspace:
            if entity.dxftype() == 'LINE':
                start = (entity.dxf.start.x, entity.dxf.start.y)
                end = (entity.dxf.end.x, entity.dxf.end.y)
                # Skip very short lines (less than 0.1 units)
                line_length = ((end[0] - start[0])**2 +
                               (end[1] - start[1])**2)**0.5
                if line_length > 0.1:
                    lines.append({
                        'start': start,
                        'end': end,
                        'layer': entity.dxf.layer,
                        'used': False
                    })

        print(f"Found {len(lines)} valid LINE entities")

        # Try to form closed polygons from connected lines
        tolerance = 1.0  # Increase tolerance for better line connection

        for i, start_line in enumerate(lines):
            if start_line['used']:
                continue

            polygon_points = [start_line['start'], start_line['end']]
            current_end = start_line['end']
            used_lines = [i]

            # Try to connect lines to form a closed loop
            for _ in range(50):  # Limit iterations to prevent infinite loops
                found_connection = False

                for j, line in enumerate(lines):
                    if j in used_lines or line['used']:
                        continue

                    if self._points_close(current_end, line['start'],
                                          tolerance):
                        polygon_points.append(line['end'])
                        current_end = line['end']
                        used_lines.append(j)
                        found_connection = True
                        break
                    elif self._points_close(current_end, line['end'],
                                            tolerance):
                        polygon_points.append(line['start'])
                        current_end = line['start']
                        used_lines.append(j)
                        found_connection = True
                        break

                if not found_connection:
                    break

                # Check if we've closed the loop
                if self._points_close(current_end, start_line['start'],
                                      tolerance):
                    # Validate polygon before creating
                    if self._is_valid_polygon_points(polygon_points):
                        try:
                            from shapely.geometry import Polygon
                            # Clean and validate points
                            cleaned_points = self._clean_polygon_points(
                                polygon_points)

                            if len(
                                    cleaned_points
                            ) >= 4:  # Need at least 4 points for linearring
                                # Ensure polygon is closed
                                if cleaned_points[0] != cleaned_points[-1]:
                                    cleaned_points.append(cleaned_points[0])

                                # Only create polygon if we have enough unique points
                                unique_points = []
                                for point in cleaned_points:
                                    if not unique_points or (
                                            abs(point[0] -
                                                unique_points[-1][0]) > 1e-6 or
                                            abs(point[1] -
                                                unique_points[-1][1]) > 1e-6):
                                        unique_points.append(point)

                                # Need at least 3 unique points for a valid polygon
                                if len(unique_points) >= 3:
                                    try:
                                        # Ensure polygon is properly closed for Shapely
                                        if unique_points[0] != unique_points[
                                                -1]:
                                            polygon_coords = unique_points + [
                                                unique_points[0]
                                            ]
                                        else:
                                            polygon_coords = unique_points

                                        # Only create if we have at least 4 coordinates (3 unique + closing)
                                        if len(polygon_coords) >= 4:
                                            poly = Polygon(polygon_coords)
                                            if poly.is_valid and poly.area > 1.0:
                                                zone = {
                                                    'points':
                                                    unique_points,  # Store without closing point
                                                    'area': poly.area,
                                                    'perimeter': poly.length,
                                                    'layer':
                                                    start_line['layer'],
                                                    'source': 'line_network'
                                                }
                                                zones.append(zone)

                                                # Mark lines as used
                                                for line_idx in used_lines:
                                                    lines[line_idx][
                                                        'used'] = True
                                    except Exception:
                                        # Skip invalid polygons silently
                                        pass
                        except Exception:
                            # Skip invalid polygons silently
                            pass
                    break

        print(f"Created {len(zones)} zones from line networks")
        return zones

    def _parse_circles_as_zones(self, modelspace) -> List[Dict]:
        """Parse large circles as potential zones"""
        zones = []

        for entity in modelspace:
            if entity.dxftype() == 'CIRCLE':
                radius = entity.dxf.radius
                center = (entity.dxf.center.x, entity.dxf.center.y)

                if radius > 1.0:
                    import math
                    points = []
                    num_points = max(8, int(radius * 2))
                    for i in range(num_points):
                        angle = 2 * math.pi * i / num_points
                        x = center[0] + radius * math.cos(angle)
                        y = center[1] + radius * math.sin(angle)
                        points.append((x, y))

                    area = math.pi * radius * radius
                    perimeter = 2 * math.pi * radius

                    zone = {
                        'points': points,
                        'area': area,
                        'perimeter': perimeter,
                        'layer': entity.dxf.layer,
                        'source': 'circle'
                    }
                    zones.append(zone)

        return zones

    def _points_close(self, p1, p2, tolerance):
        """Check if two points are within tolerance distance"""
        dx = p1[0] - p2[0]
        dy = p1[1] - p2[1]
        return (dx * dx + dy * dy) <= tolerance * tolerance

    def _is_valid_polygon_points(self, points):
        """Check if points can form a valid polygon"""
        if len(points) < 4:  # Need at least 3 unique points + closing
            return False

        # Remove duplicates and check unique points
        unique_points = []
        for point in points:
            if not unique_points or (
                    abs(point[0] - unique_points[-1][0]) > 1e-6
                    or abs(point[1] - unique_points[-1][1]) > 1e-6):
                unique_points.append(point)

        return len(unique_points) >= 3

    def _clean_polygon_points(self, points):
        """Clean polygon points by removing duplicates and ensuring proper closure"""
        if not points or len(points) < 3:
            return []

        # Remove consecutive duplicate points
        cleaned = []
        for point in points:
            if not cleaned or (abs(point[0] - cleaned[-1][0]) > 1e-6
                               or abs(point[1] - cleaned[-1][1]) > 1e-6):
                cleaned.append(point)

        # Ensure we have enough points for a polygon
        if len(cleaned) < 3:
            return []

        # Remove the last point if it's the same as the first (Shapely handles closure)
        if len(cleaned) > 3 and (abs(cleaned[0][0] - cleaned[-1][0]) < 1e-6 and
                                 abs(cleaned[0][1] - cleaned[-1][1]) < 1e-6):
            cleaned = cleaned[:-1]

        return cleaned

    def _parse_text_based_zones(self, modelspace) -> List[Dict]:
        """Parse zones based on text labels and surrounding geometry"""
        zones = []

        # Find text entities that might be room labels
        room_texts = []
        for entity in modelspace.query('TEXT'):
            text_content = entity.dxf.text.strip().upper()
            # Look for common room keywords
            room_keywords = [
                'ROOM', 'OFFICE', 'BEDROOM', 'KITCHEN', 'BATHROOM', 'LIVING',
                'HALL', 'STORAGE'
            ]
            if any(keyword in text_content for keyword in room_keywords):
                room_texts.append({
                    'text':
                    text_content,
                    'position': (entity.dxf.insert.x, entity.dxf.insert.y),
                    'layer':
                    entity.dxf.layer
                })

        # For each text, try to find surrounding lines that form a room
        for text_info in room_texts:
            nearby_lines = []
            text_pos = text_info['position']
            search_radius = 50.0  # Search within 50 units

            for entity in modelspace.query('LINE'):
                start = (entity.dxf.start.x, entity.dxf.start.y)
                end = (entity.dxf.end.x, entity.dxf.end.y)

                # Check if line is near the text
                for point in [start, end]:
                    dist = ((point[0] - text_pos[0])**2 +
                            (point[1] - text_pos[1])**2)**0.5
                    if dist <= search_radius:
                        nearby_lines.append(entity)
                        break

            # Try to form a polygon from nearby lines
            if len(nearby_lines) >= 3:
                try:
                    polygon = self._create_polygon_from_text_lines(
                        nearby_lines, text_pos)
                    if polygon and polygon.area > 5.0:
                        zone = {
                            'points': list(polygon.exterior.coords)[:-1],
                            'area': polygon.area,
                            'perimeter': polygon.length,
                            'layer': text_info['layer'],
                            'source': 'text_based',
                            'room_label': text_info['text']
                        }
                        zones.append(zone)
                except Exception:
                    continue

        return zones

    def _parse_block_zones(self, modelspace) -> List[Dict]:
        """Parse zones from block references (furniture, fixtures)"""
        zones = []

        # Look for INSERT entities (block references)
        inserts = list(modelspace.query('INSERT'))

        # Group inserts that might form room boundaries
        if len(inserts) >= 4:  # Need at least 4 for a room
            # Try to find rectangular patterns
            for i, insert in enumerate(inserts):
                pos = (insert.dxf.insert.x, insert.dxf.insert.y)

                # Find other inserts that could form a rectangle
                corner_candidates = []
                for j, other_insert in enumerate(inserts[i + 1:], i + 1):
                    other_pos = (other_insert.dxf.insert.x,
                                 other_insert.dxf.insert.y)
                    dist = ((pos[0] - other_pos[0])**2 +
                            (pos[1] - other_pos[1])**2)**0.5

                    # Look for inserts within reasonable distance
                    if 2.0 <= dist <= 50.0:
                        corner_candidates.append(other_pos)

                # If we have enough corners, try to form a rectangle
                if len(corner_candidates) >= 3:
                    try:
                        all_points = [pos] + corner_candidates[:3]
                        # Simple rectangular zone approximation
                        xs = [p[0] for p in all_points]
                        ys = [p[1] for p in all_points]

                        # Create bounding rectangle
                        min_x, max_x = min(xs), max(xs)
                        min_y, max_y = min(ys), max(ys)

                        if (max_x - min_x) > 2.0 and (max_y - min_y) > 2.0:
                            rect_points = [(min_x, min_y), (max_x, min_y),
                                           (max_x, max_y), (min_x, max_y)]

                            area = (max_x - min_x) * (max_y - min_y)
                            perimeter = 2 * ((max_x - min_x) + (max_y - min_y))

                            zone = {
                                'points': rect_points,
                                'area': area,
                                'perimeter': perimeter,
                                'layer': insert.dxf.layer,
                                'source': 'block_pattern'
                            }
                            zones.append(zone)
                            break  # Only create one zone per starting point
                    except Exception:
                        continue

        return zones

    def _create_polygon_from_text_lines(self, lines, center_point):
        """Create polygon from lines near a text label"""
        try:
            # Sort lines by distance from center
            line_data = []
            for line in lines:
                start = (line.dxf.start.x, line.dxf.start.y)
                end = (line.dxf.end.x, line.dxf.end.y)
                mid_point = ((start[0] + end[0]) / 2, (start[1] + end[1]) / 2)
                dist = ((mid_point[0] - center_point[0])**2 +
                        (mid_point[1] - center_point[1])**2)**0.5
                line_data.append((dist, start, end))

            # Sort by distance and take closest lines
            line_data.sort(key=lambda x: x[0])
            closest_lines = line_data[:8]  # Use up to 8 closest lines

            # Extract all endpoints
            points = []
            for _, start, end in closest_lines:
                points.extend([start, end])

            if len(points) >= 6:  # Need at least 3 unique points
                # Remove duplicates
                unique_points = []
                for point in points:
                    is_duplicate = False
                    for existing in unique_points:
                        if abs(point[0] -
                               existing[0]) < 0.5 and abs(point[1] -
                                                          existing[1]) < 0.5:
                            is_duplicate = True
                            break
                    if not is_duplicate:
                        unique_points.append(point)

                if len(unique_points) >= 3:
                    from shapely.geometry import Polygon
                    # Create convex hull
                    from scipy.spatial import ConvexHull
                    import numpy as np

                    hull = ConvexHull(np.array(unique_points))
                    hull_points = [unique_points[i] for i in hull.vertices]

                    return Polygon(hull_points)
        except Exception:
            pass

        return None

    def _sort_connected_lines(self, lines):
        """Sort lines to form a connected sequence"""
        if not lines:
            return []

        sorted_lines = [lines[0]]
        remaining_lines = lines[1:]
        tolerance = 0.1

        while remaining_lines:
            last_line = sorted_lines[-1]
            last_end = (last_line.dxf.end.x, last_line.dxf.end.y)

            found_connection = False
            for i, line in enumerate(remaining_lines):
                line_start = (line.dxf.start.x, line.dxf.start.y)
                line_end = (line.dxf.end.x, line.dxf.end.y)

                if self._points_close(last_end, line_start, tolerance):
                    sorted_lines.append(line)
                    remaining_lines.pop(i)
                    found_connection = True
                    break
                elif self._points_close(last_end, line_end, tolerance):
                    # Reverse the line direction
                    line.dxf.start, line.dxf.end = line.dxf.end, line.dxf.start
                    sorted_lines.append(line)
                    remaining_lines.pop(i)
                    found_connection = True
                    break

            if not found_connection:
                break

        return sorted_lines

    def _create_polygon_from_lines(self, lines):
        """Create a polygon from connected lines"""
        try:
            # Sort lines to form a closed loop
            sorted_lines = self._sort_connected_lines(lines)

            if not sorted_lines or len(sorted_lines) < 3:
                return None

            # Extract points from sorted lines
            points = []
            for line in sorted_lines:
                start_point = (line.dxf.start.x, line.dxf.start.y)
                end_point = (line.dxf.end.x, line.dxf.end.y)

                if not points or points[-1] != start_point:
                    points.append(start_point)
                points.append(end_point)

            # Remove duplicate consecutive points
            unique_points = []
            for point in points:
                if not unique_points or point != unique_points[-1]:
                    unique_points.append(point)

            # Ensure the polygon is closed
            if len(unique_points
                   ) > 2 and unique_points[0] != unique_points[-1]:
                unique_points.append(unique_points[0])

            # Validate minimum requirements for a polygon
            if len(unique_points
                   ) >= 4:  # At least 3 unique points + closing point
                # Additional validation: check if points form a valid polygon
                unique_coords = list(set(
                    unique_points[:-1]))  # Remove duplicates and closing point
                if len(unique_coords) >= 3:
                    return Polygon(unique_points)
                else:
                    return None
            else:
                return None

        except Exception as e:
            # Suppress repeated error messages for cleaner console output
            return None
    
    def _try_dwg_conversion(self, file_path: str) -> Optional[str]:
        """Try to convert DWG to DXF using available tools"""
        try:
            # This is a placeholder for DWG conversion
            # In a real implementation, you would use tools like:
            # - ODA File Converter
            # - LibreCAD command line
            # - FreeCAD Python API
            # - Commercial conversion libraries
            
            print("DWG to DXF conversion not implemented")
            print("To convert DWG files:")
            print("1. Use AutoCAD: File -> Save As -> DXF")
            print("2. Use FreeCAD: Import DWG -> Export as DXF")
            print("3. Use LibreCAD: Open DWG -> Save As DXF")
            print("4. Use online converters")
            
            return None
        except Exception as e:
            print(f"DWG conversion failed: {e}")
            return None
