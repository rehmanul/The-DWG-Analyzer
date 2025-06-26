"""
DWG/DXF File Compression Tool
"""
import streamlit as st
import tempfile
import os
import subprocess
import zipfile
import base64
from pathlib import Path

def compress_dxf_file(uploaded_file):
    """Compress DXF file to reduce size"""
    try:
        # Save uploaded file to temp location
        with tempfile.NamedTemporaryFile(delete=False, suffix='.dxf') as tmp_file:
            tmp_file.write(uploaded_file.getvalue())
            input_path = tmp_file.name
        
        # Create output path
        output_path = input_path.replace('.dxf', '_compressed.dxf')
        
        # Compress using ezdxf
        import ezdxf
        doc = ezdxf.readfile(input_path)
        
        # Remove unused entities and layers
        doc.purge()
        
        # Save as ASCII DXF (smaller than binary)
        doc.saveas(output_path)
        
        # Read compressed file
        with open(output_path, 'rb') as f:
            compressed_data = f.read()
        
        # Clean up temp files
        os.unlink(input_path)
        os.unlink(output_path)
        
        return compressed_data
    except Exception as e:
        st.error(f"Compression error: {str(e)}")
        return None

def compress_dwg_file(uploaded_file):
    """Compress DWG file to reduce size (requires external tools)"""
    st.warning("DWG compression requires external CAD software.")
    st.info("Please use DXF format for web compression.")
    return None

def get_download_link(file_data, file_name):
    """Generate download link for compressed file"""
    b64 = base64.b64encode(file_data).decode()
    return f'<a href="data:application/octet-stream;base64,{b64}" download="{file_name}">Download Compressed File</a>'

def compress_file_ui():
    """File compression UI"""
    st.title("🗜️ DWG/DXF File Compressor")
    st.write("Compress your DWG/DXF files to meet the 10MB upload limit")
    
    uploaded_file = st.file_uploader(
        "Select file to compress",
        type=['dwg', 'dxf'],
        help="Upload a file to compress"
    )
    
    if uploaded_file:
        file_size_mb = uploaded_file.size / (1024 * 1024)
        st.write(f"Original file size: {file_size_mb:.2f} MB")
        
        if st.button("Compress File"):
            with st.spinner("Compressing..."):
                if uploaded_file.name.lower().endswith('.dxf'):
                    compressed_data = compress_dxf_file(uploaded_file)
                    if compressed_data:
                        compressed_size_mb = len(compressed_data) / (1024 * 1024)
                        st.success(f"Compression complete! New size: {compressed_size_mb:.2f} MB")
                        
                        # Show reduction percentage
                        reduction = (1 - compressed_size_mb / file_size_mb) * 100
                        st.info(f"Size reduced by {reduction:.1f}%")
                        
                        # Provide download link
                        compressed_name = f"compressed_{uploaded_file.name}"
                        st.markdown(get_download_link(compressed_data, compressed_name), unsafe_allow_html=True)
                        
                        if compressed_size_mb > 10:
                            st.warning("File is still larger than 10MB. Try additional compression or run locally.")
                else:
                    compress_dwg_file(uploaded_file)
    
    st.divider()
    st.subheader("📋 Compression Tips")
    st.markdown("""
    1. **Convert DWG to DXF**: DXF files are typically smaller
    2. **Remove unused layers**: Delete unnecessary layers before uploading
    3. **Simplify complex curves**: Reduce precision for non-critical elements
    4. **Use external tools**: AutoCAD's PURGE command or similar
    5. **Split large files**: Divide into multiple smaller files
    """)

if __name__ == "__main__":
    compress_file_ui()