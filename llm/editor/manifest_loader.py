import json
from pathlib import Path
from typing import Dict, Any


MANIFEST_DIR = Path(__file__).resolve().parents[2] / "compiler" / "manifests"

MANIFEST_FILES = [
    "Accordion.manifest.json",
    "Box.manifest.json",
    "Button.manifest.json",
    "Card.manifest.json",
    "GradientText.manifest.json",
    "Icon.manifest.json",
    "Image.manifest.json",
    "Link.manifest.json",
    "List.manifest.json",
    "Table.manifest.json",
    "Text.manifest.json",
    "Textbox.manifest.json"
]


def _load_manifests_from_disk() -> Dict[str, Any]:
    """Internal function to load manifests from disk."""
    manifests = {}
    
    for filename in MANIFEST_FILES:
        manifest_path = MANIFEST_DIR / filename
        try:
            with open(manifest_path, 'r') as f:
                manifest_data = json.load(f)
                component_name = manifest_data.get("friendlyName", filename.replace(".manifest.json", ""))
                manifests[component_name] = manifest_data
        except Exception as e:
            print(f"Warning: Could not load manifest {filename}: {e}")
    
    return manifests


# Module-level manifest cache (loaded once at import time)
_MANIFEST_CACHE = _load_manifests_from_disk()


def load_all_manifests() -> Dict[str, Any]:
    """Get all component manifests from cache."""
    return _MANIFEST_CACHE


def get_component_manifest(component_type: str) -> Dict[str, Any]:
    """Get a specific component manifest by component type from cache."""
    return _MANIFEST_CACHE.get(component_type, {})

