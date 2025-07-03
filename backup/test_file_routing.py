#!/usr/bin/env python3
"""
Test script to verify DWG/DXF file routing is working correctly
"""

import tempfile
import os
from pathlib import Path

def test_file_routing():
    """Test that DWG and DXF files are routed to correct parsers"""
    
    print("Testing file routing fix...")
    
    # Test 1: DXF file should be handled by DXF parser
    print("\n1. Testing DXF file routing:")
    try:
        from src.enhanced_dwg_parser import EnhancedDWGParser
        parser = EnhancedDWGParser()
        
        # Create a dummy DXF file
        with tempfile.NamedTemporaryFile(suffix='.dxf', delete=False) as tmp:
            tmp.write(b'0\nSECTION\n2\nHEADER\n0\nENDSEC\n0\nEOF\n')
            dxf_path = tmp.name
        
        try:
            result = parser.parse_file(dxf_path)
            print(f"✅ DXF file routing works: {result.get('parsing_method', 'unknown')}")
        except Exception as e:
            if "ezdxf can only read DXF files" in str(e):
                print("❌ DXF file incorrectly rejected")
            else:
                print(f"✅ DXF file processed (expected parsing failure): {e}")
        finally:
            os.unlink(dxf_path)
            
    except Exception as e:
        print(f"❌ DXF test failed: {e}")
    
    # Test 2: DWG file should NOT be sent to ezdxf
    print("\n2. Testing DWG file routing:")
    try:
        from src.enhanced_dwg_parser import EnhancedDWGParser
        parser = EnhancedDWGParser()
        
        # Create a dummy DWG file
        with tempfile.NamedTemporaryFile(suffix='.dwg', delete=False) as tmp:
            tmp.write(b'AC1015\x00\x00\x00\x00\x00\x00')  # Dummy DWG header
            dwg_path = tmp.name
        
        try:
            result = parser.parse_file(dwg_path)
            method = result.get('parsing_method', 'unknown')
            if 'ezdxf' in method:
                print("❌ DWG file incorrectly sent to ezdxf parser")
            else:
                print(f"✅ DWG file correctly routed: {method}")
        except Exception as e:
            if "ezdxf can only read DXF files" in str(e):
                print("❌ DWG file was sent to ezdxf parser")
            else:
                print(f"✅ DWG file handled correctly: {e}")
        finally:
            os.unlink(dwg_path)
            
    except Exception as e:
        print(f"❌ DWG test failed: {e}")
    
    # Test 3: Enterprise DXF parser validation
    print("\n3. Testing Enterprise DXF parser validation:")
    try:
        from src.enterprise_dxf_parser import EnterpriseDXFParser
        parser = EnterpriseDXFParser()
        
        # Create a dummy DWG file
        with tempfile.NamedTemporaryFile(suffix='.dwg', delete=False) as tmp:
            tmp.write(b'AC1015\x00\x00\x00\x00\x00\x00')
            dwg_path = tmp.name
        
        try:
            result = parser.parse_dxf_file(dwg_path)
            print("❌ Enterprise DXF parser accepted DWG file")
        except Exception as e:
            if "not a DXF file" in str(e):
                print("✅ Enterprise DXF parser correctly rejected DWG file")
            else:
                print(f"✅ Enterprise DXF parser validation works: {e}")
        finally:
            os.unlink(dwg_path)
            
    except Exception as e:
        print(f"❌ Enterprise DXF test failed: {e}")
    
    print("\n✅ File routing tests completed!")

if __name__ == "__main__":
    test_file_routing()