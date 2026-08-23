"""AI Shopping Assistant Application Package"""
import os
import sys
import types
from pathlib import Path

# Automatically configure sys.path and backend namespace
_app_dir = Path(__file__).resolve().parent
_backend_dir = _app_dir.parent
_root_dir = _backend_dir.parent

for _p in [str(_root_dir), str(_backend_dir), str(_app_dir)]:
    if _p not in sys.path:
        sys.path.insert(0, _p)

if "backend" not in sys.modules:
    _backend_mod = types.ModuleType("backend")
    _backend_mod.__path__ = [str(_backend_dir)]
    _backend_mod.app = sys.modules[__name__]
    sys.modules["backend"] = _backend_mod
    sys.modules["backend.app"] = sys.modules[__name__]

__version__ = "1.0.0"
