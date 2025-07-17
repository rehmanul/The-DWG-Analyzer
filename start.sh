#!/bin/bash
# Render deployment startup script

# Set default port if not provided
PORT=${PORT:-8501}

# Start Streamlit with proper configuration
exec streamlit run streamlit_app.py \
    --server.port=$PORT \
    --server.address=0.0.0.0 \
    --server.headless=true \
    --browser.gatherUsageStats=false \
    --server.enableCORS=false \
    --server.enableXsrfProtection=false