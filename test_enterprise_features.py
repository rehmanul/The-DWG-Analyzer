"""
Test script for enterprise features
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test if all enterprise modules can be imported"""
    try:
        from src.enterprise_dxf_parser import EnterpriseDXFParser
        print("✅ EnterpriseDXFParser imported successfully")
        
        from src.ilot_layout_engine import IlotLayoutEngine, IlotProfile
        print("✅ IlotLayoutEngine imported successfully")
        
        from src.enterprise_visualization import EnterpriseVisualizationEngine
        print("✅ EnterpriseVisualizationEngine imported successfully")
        
        from src.enterprise_export_functions import export_layout_report
        print("✅ Enterprise export functions imported successfully")
        
        return True
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

def test_basic_functionality():
    """Test basic functionality of enterprise modules"""
    try:
        # Test DXF Parser initialization
        parser = EnterpriseDXFParser()
        print("✅ DXF Parser initialized")
        
        # Test Layout Engine initialization
        layout_engine = IlotLayoutEngine()
        print("✅ Layout Engine initialized")
        
        # Test predefined profiles
        profiles = layout_engine.predefined_profiles
        print(f"✅ {len(profiles)} predefined îlot profiles loaded")
        
        # Test Visualization Engine initialization
        viz_engine = EnterpriseVisualizationEngine()
        print("✅ Visualization Engine initialized")
        
        return True
    except Exception as e:
        print(f"❌ Functionality test error: {e}")
        return False

def test_ilot_profiles():
    """Test îlot profile creation and validation"""
    try:
        layout_engine = IlotLayoutEngine()
        
        # Test predefined profiles
        for profile_name, profile in layout_engine.predefined_profiles.items():
            print(f"  - {profile_name}: {profile.width}×{profile.height}cm, {profile.area/10000:.1f}m²")
        
        # Test custom profile creation
        custom_profile = layout_engine.create_custom_profile(
            "Test Office",
            {
                'width': 350,
                'height': 250,
                'area': 87500,
                'shape_type': 'rectangular'
            }
        )
        print(f"✅ Custom profile created: {custom_profile.name}")
        
        return True
    except Exception as e:
        print(f"❌ Profile test error: {e}")
        return False

def main():
    """Run all tests"""
    print("🧪 Testing Enterprise Features\n")
    
    print("1. Testing module imports...")
    if not test_imports():
        return False
    
    print("\n2. Testing basic functionality...")
    if not test_basic_functionality():
        return False
    
    print("\n3. Testing îlot profiles...")
    if not test_ilot_profiles():
        return False
    
    print("\n✅ All tests passed! Enterprise features are ready.")
    print("\n🚀 To run the application:")
    print("   streamlit run streamlit_app.py")
    
    return True

if __name__ == "__main__":
    main()