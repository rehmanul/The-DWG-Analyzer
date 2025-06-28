import streamlit as st
from streamlit.web import cli as stcli
import sys

# Snowflake-specific configuration
st.set_page_config(
    page_title="AI DWG Analyzer - Snowflake",
    page_icon="🏗️",
    layout="wide"
)

# Import main app
from streamlit_app import main

if __name__ == "__main__":
    # Run main app
    main()