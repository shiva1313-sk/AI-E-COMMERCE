"""AI Shopping Assistant Backend Package"""
import os
import sys
from pathlib import Path

# Automatically inject backend directory into sys.path
_backend_dir = Path(__file__).resolve().parent
_root_dir = _backend_dir.parent

for _p in [str(_root_dir), str(_backend_dir)]:
    if _p not in sys.path:
        sys.path.insert(0, _p)
