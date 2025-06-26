"""
Advanced AI Room Recognition System
"""
import numpy as np
from typing import Dict, List, Any
import streamlit as st

class AdvancedRoomRecognizer:
    def __init__(self):
        self.room_patterns = {
            'kitchen': {
                'area_range': (8, 25),
                'aspect_ratio': (1.2, 2.5),
                'keywords': ['kitchen', 'cook', 'dining'],
                'typical_furniture': ['counter', 'island', 'cabinet']
            },
            'bathroom': {
                'area_range': (3, 12),
                'aspect_ratio': (1.0, 2.0),
                'keywords': ['bath', 'toilet', 'wc', 'powder'],
                'typical_furniture': ['toilet', 'sink', 'shower']
            },
            'bedroom': {
                'area_range': (10, 30),
                'aspect_ratio': (1.0, 1.8),
                'keywords': ['bed', 'master', 'guest'],
                'typical_furniture': ['bed', 'dresser', 'closet']
            },
            'living_room': {
                'area_range': (15, 50),
                'aspect_ratio': (1.0, 2.0),
                'keywords': ['living', 'family', 'great'],
                'typical_furniture': ['sofa', 'tv', 'coffee']
            },
            'office': {
                'area_range': (8, 25),
                'aspect_ratio': (1.0, 2.0),
                'keywords': ['office', 'study', 'den'],
                'typical_furniture': ['desk', 'chair', 'bookshelf']
            }
        }
    
    def recognize_room_advanced(self, zone: Dict, context: Dict = None) -> Dict:
        """Advanced room recognition with AI scoring"""
        area = zone.get('area', 0)
        points = zone.get('points', [])
        
        if len(points) < 3:
            return {'type': 'Unknown', 'confidence': 0.0}
        
        # Calculate geometric features
        bounds = self._calculate_bounds(points)
        aspect_ratio = self._calculate_aspect_ratio(bounds)
        
        # Score each room type
        scores = {}
        for room_type, pattern in self.room_patterns.items():
            score = self._calculate_room_score(area, aspect_ratio, zone, pattern, context)
            scores[room_type] = score
        
        # Get best match
        best_type = max(scores, key=scores.get)
        confidence = scores[best_type]
        
        # Apply confidence threshold
        if confidence < 0.3:
            best_type = 'Unknown'
            confidence = 0.0
        
        return {
            'type': self._format_room_name(best_type),
            'confidence': confidence,
            'scores': scores,
            'features': {
                'area': area,
                'aspect_ratio': aspect_ratio,
                'bounds': bounds
            }
        }
    
    def _calculate_room_score(self, area: float, aspect_ratio: float, 
                            zone: Dict, pattern: Dict, context: Dict = None) -> float:
        """Calculate room type probability score"""
        score = 0.0
        
        # Area score (40% weight)
        area_min, area_max = pattern['area_range']
        if area_min <= area <= area_max:
            area_score = 1.0
        elif area < area_min:
            area_score = max(0, 1.0 - (area_min - area) / area_min)
        else:
            area_score = max(0, 1.0 - (area - area_max) / area_max)
        score += area_score * 0.4
        
        # Aspect ratio score (30% weight)
        ratio_min, ratio_max = pattern['aspect_ratio']
        if ratio_min <= aspect_ratio <= ratio_max:
            ratio_score = 1.0
        else:
            ratio_score = max(0, 1.0 - abs(aspect_ratio - (ratio_min + ratio_max) / 2) / 2)
        score += ratio_score * 0.3
        
        # Text/label score (20% weight)
        text_score = self._calculate_text_score(zone, pattern['keywords'])
        score += text_score * 0.2
        
        # Context score (10% weight)
        context_score = self._calculate_context_score(zone, pattern, context)
        score += context_score * 0.1
        
        return min(1.0, score)
    
    def _calculate_text_score(self, zone: Dict, keywords: List[str]) -> float:
        """Score based on text labels in or near the zone"""
        zone_text = zone.get('room_label', '').lower()
        zone_type = zone.get('zone_type', '').lower()
        
        combined_text = f"{zone_text} {zone_type}"
        
        for keyword in keywords:
            if keyword in combined_text:
                return 1.0
        
        return 0.0
    
    def _calculate_context_score(self, zone: Dict, pattern: Dict, context: Dict) -> float:
        """Score based on surrounding rooms and building context"""
        if not context:
            return 0.5
        
        # Proximity to other room types
        nearby_rooms = context.get('nearby_rooms', [])
        
        # Kitchen near dining room gets bonus
        if pattern == self.room_patterns['kitchen']:
            if any('dining' in room.lower() for room in nearby_rooms):
                return 1.0
        
        # Bathroom near bedroom gets bonus
        if pattern == self.room_patterns['bathroom']:
            if any('bed' in room.lower() for room in nearby_rooms):
                return 0.8
        
        return 0.5
    
    def _calculate_bounds(self, points: List[tuple]) -> Dict:
        """Calculate bounding box"""
        if not points:
            return {'width': 0, 'height': 0}
        
        x_coords = [p[0] for p in points]
        y_coords = [p[1] for p in points]
        
        width = max(x_coords) - min(x_coords)
        height = max(y_coords) - min(y_coords)
        
        return {'width': width, 'height': height}
    
    def _calculate_aspect_ratio(self, bounds: Dict) -> float:
        """Calculate aspect ratio"""
        width = bounds.get('width', 1)
        height = bounds.get('height', 1)
        
        return max(width, height) / max(min(width, height), 0.1)
    
    def _format_room_name(self, room_type: str) -> str:
        """Format room type name for display"""
        return room_type.replace('_', ' ').title()
    
    def batch_recognize_rooms(self, zones: List[Dict]) -> Dict[str, Dict]:
        """Recognize all rooms in a batch with context"""
        results = {}
        
        # First pass: individual recognition
        for i, zone in enumerate(zones):
            zone_id = f"zone_{i}"
            results[zone_id] = self.recognize_room_advanced(zone)
        
        # Second pass: context-aware refinement
        for i, zone in enumerate(zones):
            zone_id = f"zone_{i}"
            
            # Build context
            context = self._build_context(i, zones, results)
            
            # Re-recognize with context
            refined_result = self.recognize_room_advanced(zone, context)
            
            # Keep better result
            if refined_result['confidence'] > results[zone_id]['confidence']:
                results[zone_id] = refined_result
        
        return results
    
    def _build_context(self, zone_index: int, zones: List[Dict], 
                      initial_results: Dict) -> Dict:
        """Build context for a zone"""
        nearby_rooms = []
        
        current_zone = zones[zone_index]
        current_centroid = self._calculate_centroid(current_zone.get('points', []))
        
        # Find nearby rooms (within reasonable distance)
        for i, other_zone in enumerate(zones):
            if i == zone_index:
                continue
            
            other_centroid = self._calculate_centroid(other_zone.get('points', []))
            distance = self._calculate_distance(current_centroid, other_centroid)
            
            if distance < 20:  # Within 20 units
                zone_id = f"zone_{i}"
                room_type = initial_results.get(zone_id, {}).get('type', 'Unknown')
                nearby_rooms.append(room_type)
        
        return {'nearby_rooms': nearby_rooms}
    
    def _calculate_centroid(self, points: List[tuple]) -> tuple:
        """Calculate centroid of points"""
        if not points:
            return (0, 0)
        
        x = sum(p[0] for p in points) / len(points)
        y = sum(p[1] for p in points) / len(points)
        return (x, y)
    
    def _calculate_distance(self, point1: tuple, point2: tuple) -> float:
        """Calculate distance between two points"""
        return ((point1[0] - point2[0])**2 + (point1[1] - point2[1])**2)**0.5