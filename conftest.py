# conftest.py
import sys
from pathlib import Path

pytest_plugins = ["pytest_asyncio"]
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))