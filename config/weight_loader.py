import yaml
from functools import lru_cache
from pathlib import Path
from typing import Dict, Any

_DEFAULT_PATH = Path(__file__).with_suffix("").parent / "weight_config.yml"


@lru_cache(maxsize=1)
def get_config(path: str | Path | None = None) -> Dict[str, Any]:
    """Load weight configuration from YAML file.

    The file can be edited on disk and will be re-read only when this function
    is called with *reload=True* (or the process restarts). To hot-reload, just
    call ``get_config.cache_clear()`` then ``get_config()`` again.
    """
    path = Path(path or _DEFAULT_PATH)
    if not path.exists():
        raise FileNotFoundError(f"Weight config file not found: {path}")
    with path.open("r", encoding="utf-8") as f:
        cfg = yaml.safe_load(f)
    # basic sanity defaults
    cfg.setdefault("weights", {})
    cfg.setdefault("penalties", {})
    cfg.setdefault("education_hierarchy", {})
    return cfg 