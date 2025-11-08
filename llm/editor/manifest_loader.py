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


def load_all_manifests() -> Dict[str, Any]:
    """Load all component manifests from the compiler/manifests directory."""
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


def get_component_manifest(component_type: str) -> Dict[str, Any]:
    """Get a specific component manifest by component type."""
    manifests = load_all_manifests()
    return manifests.get(component_type, {})

