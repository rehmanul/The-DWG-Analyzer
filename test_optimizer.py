#!/usr/bin/env python3
"""
Simple test script to verify the optimized îlot generation
"""
import sys
import os
sys.path.append('.')

from core.ilot_optimizer import generate_ilots
from shapely.geometry import Polygon

def test_optimizer():
    """Test the optimized îlot generator"""
    
    # Create simple test zones
    zones = [
        {
            'points': [(0, 0), (50, 0), (50, 50), (0, 50), (0, 0)],
            'area': 2500
        },
        {
            'points': [(100, 0), (150, 0), (150, 50), (100, 50), (100, 0)],
            'area': 2500
        }
    ]
    
    bounds = (0, 0, 150, 50)
    
    config = {
        'size_0_1': 0.1,
        'size_1_3': 0.3,
        'size_3_5': 0.3,
        'size_5_10': 0.3
    }
    
    try:
        result = generate_ilots(zones, bounds, config, None, max_generations=5, population_size=10)
        
        print(f"Test Results:")
        print(f"- Generated {len(result.get('ilots', []))} ilots")
        print(f"- Generated {len(result.get('corridors', []))} corridors")
        print(f"- Total area used: {result.get('total_area', 0):.2f}")
        print(f"- Efficiency: {result.get('efficiency', 0):.2f}%")
        print("✓ Test passed!")
        
        return True
        
    except Exception as e:
        print(f"✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_optimizer()