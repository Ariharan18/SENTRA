"""Frontend configuration loaded from the project-root environment."""

from pathlib import Path

from dotenv import load_dotenv
import os


PROJECT_ROOT = Path(__file__).resolve().parents[2]
load_dotenv(PROJECT_ROOT / ".env", override=False)

API_BASE_URL = os.getenv("API_BASE_URL", "http://127.0.0.1:8000")
