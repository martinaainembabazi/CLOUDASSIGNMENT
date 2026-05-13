# Entry point for Streamlit Cloud deployment
import sys
from pathlib import Path

# Add the correct path to sys.path so we can import from the nested structure
project_dir = Path(__file__).parent / "Desktop" / "CLOUD ASSIGN"
sys.path.insert(0, str(project_dir))

# Import and run the dashboard
from src.dashboard import main

if __name__ == "__main__":
    main()
