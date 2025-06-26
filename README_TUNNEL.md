# DWG Analyzer - Tunnel Deployment Guide

## File Size Limitations

When deploying through a tunnel or proxy service, there are strict file size limitations:

### Web Deployment Limits
- **Maximum file size: 10MB**
- **Recommended size: 1-5MB**

These limits are imposed by the tunnel/proxy service, not by the application itself.

## Solutions for Large Files

### 1. Compress Your Files
Use the built-in compression tool:
```
python -m streamlit run compress_dwg.py
```

### 2. Run Locally
For full functionality with large files:
```
python -m streamlit run streamlit_app.py
```
Local deployment supports files up to 190MB.

### 3. Split Large Files
Divide complex drawings into smaller sections using CAD software.

### 4. Use DXF Format
DXF files are typically smaller than DWG files.

## Optimizing DWG/DXF Files

1. **Remove unused layers**
2. **Purge unused blocks and styles**
3. **Simplify complex curves**
4. **Export as ASCII DXF** (smaller than binary)
5. **Use external compression tools** like AutoCAD's AUDIT and PURGE commands

## Technical Explanation

The 413 error (Request Entity Too Large) occurs because:
- Tunnel services have built-in size limits
- Proxy servers restrict payload sizes
- Web servers have maximum request size configurations

The local version doesn't have these restrictions because it doesn't go through these intermediary services.