"""
Cloud Run & Production Entrypoint for Crypto Risk Manager Backend.
Handles both top-level execution (from repo root) and isolated directory execution (Cloud Buildpacks inside backend/).
"""
import sys
import os
from pathlib import Path

current_dir = Path(__file__).resolve().parent
if str(current_dir) not in sys.path:
    sys.path.insert(0, str(current_dir))

# Enable both `import backend.src...` and `import src...` seamlessly
if "backend" not in sys.modules:
    import types
    backend_module = types.ModuleType("backend")
    backend_module.__path__ = [str(current_dir)]
    sys.modules["backend"] = backend_module
    try:
        import src
        backend_module.src = src
    except ImportError:
        pass

from src.main import app

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)
