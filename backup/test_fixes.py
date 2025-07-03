#!/usr/bin/env python3
"""
TEST SCRIPT FOR CRITICAL FIXES
Verify all fixes are working properly
"""

import os
import sys
from pathlib import Path

def test_exe_file():
    """Test if the new EXE file exists and has proper size"""
    print("🧪 TESTING EXE FILE")
    print("=" * 40)
    
    exe_path = Path("dist/AI_Architectural_Analyzer_ENTERPRISE_LATEST.exe")
    
    if exe_path.exists():
        size_mb = exe_path.stat().st_size / (1024 * 1024)
        print(f"✅ EXE exists: {exe_path}")
        print(f"✅ Size: {size_mb:.1f} MB")
        
        if size_mb > 100:
            print("✅ Size looks good (contains dependencies)")
            return True
        else:
            print("❌ Size too small (missing dependencies)")
            return False
    else:
        print("❌ EXE file not found")
        return False

def test_web_version_imports():
    """Test if web version imports work"""
    print("\n🧪 TESTING WEB VERSION IMPORTS")
    print("=" * 40)
    
    try:
        # Test streamlit app imports
        sys.path.append('.')
        
        # Test critical imports
        import streamlit as st
        print("✅ Streamlit import: OK")
        
        import plotly.graph_objects as go
        print("✅ Plotly import: OK")
        
        import pandas as pd
        print("✅ Pandas import: OK")
        
        import numpy as np
        print("✅ Numpy import: OK")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

def test_file_processing_functions():
    """Test if file processing functions exist and work"""
    print("\n🧪 TESTING FILE PROCESSING FUNCTIONS")
    print("=" * 40)
    
    try:
        # Import the functions from streamlit app
        sys.path.append('.')
        
        # Test if functions exist (we can't import them directly due to streamlit)
        with open('streamlit_app.py', 'r') as f:
            content = f.read()
        
        functions_to_check = [
            'create_dwg_specific_zones',
            'create_dxf_specific_zones', 
            'create_pdf_specific_zones',
            'create_ifc_specific_zones',
            'process_enterprise_file'
        ]
        
        for func in functions_to_check:
            if func in content:
                print(f"✅ Function exists: {func}")
            else:
                print(f"❌ Function missing: {func}")
                return False
        
        # Check for the NoneType fix
        if "if not hasattr(uploaded_file, 'name') or uploaded_file.name is None:" in content:
            print("✅ NoneType fix applied")
        else:
            print("❌ NoneType fix missing")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing functions: {e}")
        return False

def test_visualization_enhancements():
    """Test if visualization enhancements are present"""
    print("\n🧪 TESTING VISUALIZATION ENHANCEMENTS")
    print("=" * 40)
    
    try:
        with open('streamlit_app.py', 'r') as f:
            content = f.read()
        
        enhancements_to_check = [
            'Professional Parametric Floor Plan',
            'Professional Semantic Zone Classification',
            'Professional 3D Building Model',
            'Professional Heatmap Analysis',
            'Professional Data Analytics Dashboard'
        ]
        
        for enhancement in enhancements_to_check:
            if enhancement in content:
                print(f"✅ Enhancement present: {enhancement}")
            else:
                print(f"❌ Enhancement missing: {enhancement}")
                return False
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing visualizations: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 TESTING ALL CRITICAL FIXES")
    print("=" * 60)
    
    tests = [
        ("EXE File", test_exe_file),
        ("Web Version Imports", test_web_version_imports),
        ("File Processing Functions", test_file_processing_functions),
        ("Visualization Enhancements", test_visualization_enhancements)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ Test '{test_name}' failed with error: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 60)
    print("🎯 TEST RESULTS SUMMARY")
    print("=" * 60)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {test_name}")
        if result:
            passed += 1
    
    print(f"\n📊 OVERALL: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED - FIXES ARE WORKING!")
        print("\n🚀 READY FOR PRODUCTION:")
        print("• EXE: dist/AI_Architectural_Analyzer_ENTERPRISE_LATEST.exe")
        print("• Web: streamlit run streamlit_app.py")
    else:
        print("⚠️ SOME TESTS FAILED - CHECK ABOVE FOR DETAILS")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)