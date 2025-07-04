import streamlit as st

st.title("🏗️ TEST - Is the app working?")
st.success("✅ YES - The app is running!")
st.write("Current time:", st.empty())

# Test if ezdxf works
try:
    import ezdxf
    st.success("✅ ezdxf imported successfully")
except ImportError as e:
    st.error(f"❌ ezdxf import failed: {e}")

# Test if shapely works  
try:
    from shapely.geometry import Polygon
    st.success("✅ shapely imported successfully")
except ImportError as e:
    st.error(f"❌ shapely import failed: {e}")

st.markdown("**If you see this, the app is working and dependencies are loaded.**")