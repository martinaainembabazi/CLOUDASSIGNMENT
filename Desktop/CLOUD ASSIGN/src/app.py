# app.py at the correct path for Streamlit Cloud
# This file acts as the entry point when Streamlit runs the nested dashboard
import sys
from pathlib import Path

# Ensure proper import path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

# Now run the dashboard - import will trigger Streamlit execution
from dashboard import *
