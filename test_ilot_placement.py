"""
Test script for îlot placement functionality
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from src.enhanced_ilot_engine import EnhancedIlotEngine

def test_ilot_placement():
    """Test the îlot placement engine"""
    
    print("🏗️ Testing AI Îlot Placement Engine...")
    
    # Create test DXF entities (simple rectangular room)
    test_entities = [
        {
            'type': 'LWPOLYLINE',
            'color': 7,  # Black walls
            'geometry': [(0, 0), (20, 0), (20, 15), (0, 15)]  # 20x15m room
        },
        {
            'type': 'LWPOLYLINE', 
            'color': 5,  # Blue restricted area (stairs)
            'geometry': [(2, 2), (4, 2), (4, 4), (2, 4)]
        },
        {
            'type': 'LWPOLYLINE',
            'color': 1,  # Red entrance
            'geometry': [(9, 0), (11, 0), (11, 1), (9, 1)]
        }
    ]
    
    # Test configuration
    profile_config = {
        '0-1': 0.10,   # 10% small îlots
        '1-3': 0.25,   # 25% medium îlots  
        '3-5': 0.30,   # 30% large îlots
        '5-10': 0.35   # 35% extra large îlots
    }
    
    # Initialize engine
    engine = EnhancedIlotEngine()
    
    try:
        # Process layout
        result = engine.process_complete_layout(
            test_entities, 
            profile_config, 
            total_ilots=30
        )
        
        if result['success']:
            metrics = result['metrics']
            print(f"✅ Success! Generated {metrics['placed_ilots']} îlots")
            print(f"📊 Placement rate: {metrics['placement_rate']:.1%}")
            print(f"🚪 Corridors: {metrics['corridor_count']}")
            print(f"📐 Space utilization: {metrics['space_utilization']:.1%}")
            
            # Show îlot breakdown
            placed_ilots = [i for i in result['ilots'] if i.placed]
            categories = {}
            for ilot in placed_ilots:
                cat = ilot.category
                categories[cat] = categories.get(cat, 0) + 1
            
            print("\n📋 Îlot Breakdown:")
            for category, count in categories.items():
                print(f"  {category}: {count} îlots")
            
            return True
            
        else:
            print("❌ Failed to generate îlot layout")
            return False
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_ilot_placement()
    if success:
        print("\n🎉 Îlot placement engine is working correctly!")
        print("🚀 Ready to use in the main application")
    else:
        print("\n⚠️ Issues detected - check the implementation")