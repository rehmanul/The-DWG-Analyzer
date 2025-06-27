"""
PDF to DWG/DXF Converter
Converts architectural PDF plans to DWG/DXF format for analysis
"""
import streamlit as st
import tempfile
import os
from pathlib import Path
import fitz  # PyMuPDF
import cv2
import numpy as np
from typing import List, Dict, Tuple, Optional
import ezdxf

class PDFToDWGConverter:
    def __init__(self):
        self.dpi = 300  # High resolution for better line detection
        self.line_threshold = 50  # Minimum line length
        self.contour_area_threshold = 100  # Minimum contour area
    
    def convert_pdf_to_dwg(self, pdf_file) -> Optional[bytes]:
        """Convert PDF to DWG format"""
        try:
            # Extract lines and shapes from PDF
            lines, shapes = self.extract_geometry_from_pdf(pdf_file)
            
            if not lines and not shapes:
                st.error("No architectural elements detected in PDF")
                return None
            
            # Create DXF file (more compatible than DWG)
            dxf_content = self.create_dxf_from_geometry(lines, shapes)
            return dxf_content.encode('utf-8')
            
        except Exception as e:
            st.error(f"PDF conversion error: {str(e)}")
            return None
    
    def extract_geometry_from_pdf(self, pdf_file) -> Tuple[List[Dict], List[Dict]]:
        """Extract lines and shapes from PDF using computer vision"""
        try:
            # Save PDF to temp file
            with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp_file:
                tmp_file.write(pdf_file.getvalue())
                pdf_path = tmp_file.name
            
            # Open PDF with PyMuPDF
            doc = fitz.open(pdf_path)
            
            all_lines = []
            all_shapes = []
            
            # Process each page
            for page_num in range(len(doc)):
                page = doc[page_num]
                
                # Convert page to image
                mat = fitz.Matrix(self.dpi/72, self.dpi/72)  # Scale factor
                pix = page.get_pixmap(matrix=mat)
                img_data = pix.tobytes("png")
                
                # Convert to OpenCV format
                nparr = np.frombuffer(img_data, np.uint8)
                img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
                
                # Extract lines and shapes from image
                lines, shapes = self.detect_architectural_elements(img, page_num)
                all_lines.extend(lines)
                all_shapes.extend(shapes)
            
            doc.close()
            os.unlink(pdf_path)
            
            return all_lines, all_shapes
            
        except Exception as e:
            st.error(f"Geometry extraction error: {str(e)}")
            return [], []
    
    def detect_architectural_elements(self, img: np.ndarray, page_num: int) -> Tuple[List[Dict], List[Dict]]:
        """Detect lines and shapes using computer vision"""
        try:
            # Convert to grayscale
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            
            # Apply edge detection
            edges = cv2.Canny(gray, 50, 150, apertureSize=3)
            
            # Detect lines using HoughLinesP
            lines = cv2.HoughLinesP(edges, 1, np.pi/180, threshold=100, 
                                   minLineLength=self.line_threshold, maxLineGap=10)
            
            detected_lines = []
            if lines is not None:
                for line in lines:
                    x1, y1, x2, y2 = line[0]
                    # Convert pixel coordinates to real-world coordinates (assuming 1 pixel = 0.1 units)
                    scale = 0.1
                    detected_lines.append({
                        'start': (x1 * scale, y1 * scale),
                        'end': (x2 * scale, y2 * scale),
                        'page': page_num,
                        'type': 'line'
                    })
            
            # Detect contours for shapes/rooms
            contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            detected_shapes = []
            for contour in contours:
                area = cv2.contourArea(contour)
                if area > self.contour_area_threshold:
                    # Approximate contour to polygon
                    epsilon = 0.02 * cv2.arcLength(contour, True)
                    approx = cv2.approxPolyDP(contour, epsilon, True)
                    
                    if len(approx) >= 3:  # Valid polygon
                        points = []
                        scale = 0.1
                        for point in approx:
                            x, y = point[0]
                            points.append((x * scale, y * scale))
                        
                        detected_shapes.append({
                            'points': points,
                            'area': area * (scale ** 2),
                            'page': page_num,
                            'type': 'polygon'
                        })
            
            return detected_lines, detected_shapes
            
        except Exception as e:
            st.error(f"Element detection error: {str(e)}")
            return [], []
    
    def create_dxf_from_geometry(self, lines: List[Dict], shapes: List[Dict]) -> str:
        """Create DXF content from detected geometry"""
        try:
            # Create new DXF document
            doc = ezdxf.new('R2010')
            msp = doc.modelspace()
            
            # Add lines
            for line in lines:
                start = line['start']
                end = line['end']
                msp.add_line(start, end, dxfattribs={'layer': 'WALLS'})
            
            # Add shapes/rooms
            for shape in shapes:
                points = shape['points']
                if len(points) >= 3:
                    # Close the polygon
                    closed_points = points + [points[0]]
                    msp.add_lwpolyline(closed_points, dxfattribs={'layer': 'ROOMS', 'closed': True})
            
            # Create layers
            doc.layers.new('WALLS', dxfattribs={'color': 1})  # Red
            doc.layers.new('ROOMS', dxfattribs={'color': 3})  # Green
            
            # Convert to string without temp file
            from io import StringIO
            output = StringIO()
            doc.write(output)
            return output.getvalue()
                
        except Exception as e:
            st.error(f"DXF creation error: {str(e)}")
            return ""
    
    def display_conversion_ui(self):
        """Display PDF to DWG conversion interface"""
        st.subheader("📄➡️🏗️ PDF to DWG/DXF Converter")
        st.write("Convert architectural PDF plans to DWG/DXF format for analysis")
        
        # File upload
        uploaded_pdf = st.file_uploader(
            "Upload Architectural PDF",
            type=['pdf'],
            help="Upload a PDF containing architectural floor plans"
        )
        
        if uploaded_pdf:
            file_size_mb = uploaded_pdf.size / (1024 * 1024)
            st.write(f"PDF file size: {file_size_mb:.2f} MB")
            
            # Conversion options
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("**Conversion Settings:**")
                dpi = st.slider("Image Resolution (DPI)", 150, 600, 300, 50)
                line_threshold = st.slider("Line Detection Sensitivity", 20, 100, 50, 10)
            
            with col2:
                st.write("**Output Options:**")
                output_format = st.selectbox("Output Format", ["DXF (Recommended)", "Both DXF & Preview"])
                auto_analyze = st.checkbox("Auto-analyze after conversion", value=True)
            
            # Convert button
            if st.button("🔄 Convert PDF to DWG/DXF", type="primary"):
                with st.spinner("Converting PDF to DWG/DXF..."):
                    # Update settings
                    self.dpi = dpi
                    self.line_threshold = line_threshold
                    
                    # Convert
                    dxf_data = self.convert_pdf_to_dwg(uploaded_pdf)
                    
                    if dxf_data:
                        # Provide download
                        st.download_button(
                            "📥 Download Converted DXF",
                            data=dxf_data,
                            file_name=f"converted_{uploaded_pdf.name.replace('.pdf', '.dxf')}",
                            mime="application/octet-stream"
                        )
                        
                        st.success("✅ PDF converted successfully!")
                        
                        # Auto-analyze if requested
                        if auto_analyze:
                            st.info("🔄 Auto-analyzing converted file...")
                            # Create a file-like object from the DXF data
                            from io import BytesIO
                            dxf_file = BytesIO(dxf_data)
                            dxf_file.name = f"converted_{uploaded_pdf.name.replace('.pdf', '.dxf')}"
                            
                            # Load into session state for analysis
                            from streamlit_app import load_uploaded_file
                            zones = load_uploaded_file(dxf_file)
                            
                            if zones:
                                st.success(f"✅ Auto-analysis complete! Found {len(zones)} zones.")
                                st.rerun()
                    else:
                        st.error("❌ Conversion failed. Please check your PDF format.")
        
        # Help section
        with st.expander("📚 PDF Conversion Help"):
            st.markdown("""
            **Supported PDF Types:**
            • Architectural floor plans
            • Technical drawings with clear lines
            • Black and white or color plans
            
            **Best Results:**
            • High-resolution PDFs (300+ DPI)
            • Clear, distinct lines
            • Minimal text overlay on drawings
            • Single floor plan per page
            
            **Conversion Process:**
            1. PDF pages converted to high-resolution images
            2. Computer vision detects lines and shapes
            3. Geometric elements converted to DXF format
            4. Ready for architectural analysis
            
            **Tips:**
            • Use higher DPI for detailed drawings
            • Adjust line sensitivity for better detection
            • Clean PDFs work better than scanned documents
            """)

def display_pdf_converter():
    """Display PDF converter interface"""
    converter = PDFToDWGConverter()
    converter.display_conversion_ui()