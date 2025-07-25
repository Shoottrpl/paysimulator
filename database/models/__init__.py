import importlib
from pathlib import Path

models_dir = Path(__file__).parent
for filename in models_dir.glob("*.py"):
    if filename.name != "__init__.py" and not filename.name.startswith("_"):
        module_name = f"database.models.{filename.stem}"
        importlib.import_module(module_name)
