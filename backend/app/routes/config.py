"""
Configuration and shared state for routes.
"""

from pathlib import Path

# Directory paths (for templates and static only; no file saving)
TEMPLATES_DIR = Path("templates")
STATIC_DIR = Path("static")

TEMPLATES_DIR.mkdir(exist_ok=True)
STATIC_DIR.mkdir(exist_ok=True)

# In-memory storage for results (display only; no persistence to disk)
results_store = {}
