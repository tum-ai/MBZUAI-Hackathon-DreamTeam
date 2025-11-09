# Integration Example: Container → Template API

This example shows how the container/LLM should integrate with the template generation API.

## Flow Diagram

```
┌─────────────┐
│    User     │
│   Input     │
└──────┬──────┘
       │ "Create a blog about technology"
       ↓
┌─────────────────────┐
│   LLM Processor     │
│  (Clarifier/Actor)  │
│                     │
│  1. Parse intent    │
│  2. Extract vars    │
│  3. Choose template │
└──────┬──────────────┘
       │
       ↓
┌─────────────────────────────────────┐
│  POST /generate-template-variations │
│  {                                  │
│    template_type: "blog",           │
│    variables: {...}                 │
│  }                                  │
└──────┬──────────────────────────────┘
       │
       ↓
┌──────────────────────┐
│  Server Generates    │
│  4 Variations to:    │
│  /tmp/selection/0    │ ← Professional
│  /tmp/selection/1    │ ← Dark
│  /tmp/selection/2    │ ← Minimal
│  /tmp/selection/3    │ ← Energetic
└──────┬───────────────┘
       │
       ↓
┌──────────────────────┐
│  Container Watches   │
│  File Changes        │
│  & Serves 4 Iframes  │
└──────┬───────────────┘
       │
       ↓
┌──────────────────────┐
│  User Selects One    │
│  (e.g., variation 1) │
└──────┬───────────────┘
       │
       ↓
┌──────────────────────┐
│  Copy Selected to    │
│  Active Project      │
└──────────────────────┘
```

## Example: LLM Processing

```python
import requests
import json

class TemplateGenerator:
    """Example integration class for LLM/Container"""
    
    def __init__(self, api_base="http://127.0.0.1:8000"):
        self.api_base = api_base
    
    def parse_user_intent(self, user_input: str) -> dict:
        """
        Parse user input and determine template type + variables.
        This would use your LLM to extract structured data.
        """
        # Example parsing (in reality, this would be your LLM)
        if "blog" in user_input.lower():
            return {
                "template_type": "blog",
                "variables": {
                    "blogName": "My Blog",
                    "tagline": "Thoughts and Ideas",
                    "about": "A personal blog.",
                    "posts": [
                        {
                            "title": "First Post",
                            "date": "Nov 9, 2025",
                            "excerpt": "Welcome to my blog!",
                            "image": "https://images.unsplash.com/photo-1499750310107-5fef28a66643?w=800"
                        }
                    ]
                }
            }
        elif "product" in user_input.lower() or "iphone" in user_input.lower():
            return {
                "template_type": "product",
                "variables": {
                    "productName": "My Product",
                    "tagline": "Amazing product",
                    "heroImage": "https://images.unsplash.com/photo-1695048133142-1a20484d2569?w=1200",
                    "features": [
                        {"title": "Feature 1", "description": "Great feature"}
                    ],
                    "specs": [
                        {"label": "Size", "value": "Large"}
                    ],
                    "galleryImages": [
                        "https://images.unsplash.com/photo-1695048133142-1a20484d2569?w=600"
                    ]
                }
            }
        elif "gallery" in user_input.lower() or "photo" in user_input.lower():
            return {
                "template_type": "gallery",
                "variables": {
                    "name": "Artist Name",
                    "tagline": "Photographer",
                    "heroImage": "https://images.unsplash.com/photo-1542038784456-1ea8e935640e?w=1200",
                    "galleryImages": [
                        "https://images.unsplash.com/photo-1542038784456-1ea8e935640e?w=600",
                        "https://images.unsplash.com/photo-1515378791036-0648a3ef77b2?w=600"
                    ],
                    "about": "Fine art photographer."
                }
            }
        elif "shop" in user_input.lower() or "store" in user_input.lower():
            return {
                "template_type": "ecommerce",
                "variables": {
                    "storeName": "My Store",
                    "tagline": "Quality Products",
                    "heroImage": "https://images.unsplash.com/photo-1555041469-a586c61ea9bc?w=1200",
                    "products": [
                        {
                            "name": "Product 1",
                            "price": "$99",
                            "image": "https://images.unsplash.com/photo-1555041469-a586c61ea9bc?w=400"
                        }
                    ],
                    "about": "Quality products for modern living."
                }
            }
        else:
            # Default to portfolio
            return {
                "template_type": "portfolio",
                "variables": {
                    "name": "Your Name",
                    "title": "Software Developer",
                    "bio": "Building amazing things.",
                    "skills": ["Python", "JavaScript"],
                    "projects": [
                        {
                            "title": "Project 1",
                            "description": "Cool project",
                            "image": "https://images.unsplash.com/photo-1498050108023-c5249f4df085?w=600"
                        }
                    ]
                }
            }
    
    def generate_variations(self, user_input: str) -> dict:
        """
        Main method: Parse user input and generate 4 variations.
        """
        # Parse intent
        request_data = self.parse_user_intent(user_input)
        
        print(f"Generating {request_data['template_type']} template...")
        
        # Call API
        response = requests.post(
            f"{self.api_base}/generate-template-variations",
            json=request_data
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✓ Generated {len(result['variations'])} variations")
            return result
        else:
            print(f"✗ Error: {response.text}")
            return None
    
    def get_variation_paths(self) -> list:
        """Get the paths to all 4 variations for the container to watch."""
        return [
            "/tmp/selection/0",
            "/tmp/selection/1",
            "/tmp/selection/2",
            "/tmp/selection/3"
        ]
    
    def get_variation_info(self, index: int) -> dict:
        """
        Get info about a specific variation.
        Container can use this to display palette/font info.
        """
        palettes = ["professional", "dark", "minimal", "energetic"]
        fonts = ["modern", "tech", "elegant", "playful"]
        descriptions = [
            "Clean and professional design for business",
            "Modern dark theme with tech aesthetics",
            "Minimal and elegant with classic typography",
            "Vibrant and energetic with playful fonts"
        ]
        
        if 0 <= index < 4:
            return {
                "index": index,
                "palette": palettes[index],
                "font": fonts[index],
                "description": descriptions[index],
                "path": f"/tmp/selection/{index}"
            }
        return None


# Example usage
def main():
    gen = TemplateGenerator()
    
    # Example 1: User wants a blog
    print("="*60)
    print("Example 1: Blog Generation")
    print("="*60)
    user_input = "I want to create a blog about technology"
    result = gen.generate_variations(user_input)
    
    if result:
        print("\nVariations generated:")
        for var in result['variations']:
            info = gen.get_variation_info(var['index'])
            print(f"\n[{var['index']}] {info['palette'].upper()}")
            print(f"    {info['description']}")
            print(f"    Path: {var['path']}")
            print(f"    Pages: {', '.join(var['pages'])}")
    
    print("\n" + "="*60)
    print("Container should now watch these paths:")
    for path in gen.get_variation_paths():
        print(f"  - {path}")


if __name__ == "__main__":
    main()
```

## Container File Watcher Example

```python
import time
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class VariationWatcher(FileSystemEventHandler):
    """Watches for changes in variation directories."""
    
    def __init__(self, variation_index: int, callback):
        self.variation_index = variation_index
        self.callback = callback
        self.path = Path(f"/tmp/selection/{variation_index}")
    
    def on_modified(self, event):
        if not event.is_directory:
            print(f"[Variation {self.variation_index}] File changed: {event.src_path}")
            self.callback(self.variation_index, event.src_path)
    
    def on_created(self, event):
        if not event.is_directory:
            print(f"[Variation {self.variation_index}] File created: {event.src_path}")
            self.callback(self.variation_index, event.src_path)


class ContainerManager:
    """Manages 4 variation containers."""
    
    def __init__(self):
        self.observers = []
        self.variations = [None, None, None, None]
    
    def handle_file_change(self, variation_index: int, file_path: str):
        """Called when a file changes in a variation directory."""
        # Reload the variation
        variation_dir = Path(f"/tmp/selection/{variation_index}")
        
        # Read project.json
        project_file = variation_dir / "project.json"
        if project_file.exists():
            with open(project_file) as f:
                project_config = json.load(f)
                self.variations[variation_index] = {
                    "config": project_config,
                    "path": str(variation_dir)
                }
        
        # Trigger iframe refresh for this variation
        print(f"Refreshing variation {variation_index}...")
        self.refresh_iframe(variation_index)
    
    def refresh_iframe(self, variation_index: int):
        """Refresh the iframe for a specific variation."""
        # Send webhook or message to frontend
        # This would be your actual iframe refresh logic
        pass
    
    def start_watching(self):
        """Start watching all 4 variation directories."""
        for i in range(4):
            path = Path(f"/tmp/selection/{i}")
            path.mkdir(parents=True, exist_ok=True)
            
            event_handler = VariationWatcher(i, self.handle_file_change)
            observer = Observer()
            observer.schedule(event_handler, str(path), recursive=True)
            observer.start()
            self.observers.append(observer)
            print(f"Started watching variation {i}: {path}")
    
    def stop_watching(self):
        """Stop all watchers."""
        for observer in self.observers:
            observer.stop()
            observer.join()


# Example usage
def run_container():
    manager = ContainerManager()
    
    print("Starting container manager...")
    manager.start_watching()
    
    print("Watching for changes. Press Ctrl+C to stop.")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nStopping...")
        manager.stop_watching()


if __name__ == "__main__":
    run_container()
```

## User Selection Flow

```python
def handle_user_selection(selected_index: int):
    """
    User selected one of the 4 variations.
    Copy it to the active project directory.
    """
    import shutil
    
    source = Path(f"/tmp/selection/{selected_index}")
    destination = Path("/path/to/active/project")
    
    if not source.exists():
        print(f"Error: Variation {selected_index} not found")
        return False
    
    # Clear destination
    if destination.exists():
        shutil.rmtree(destination)
    
    # Copy selected variation
    shutil.copytree(source, destination)
    
    print(f"✓ Selected variation {selected_index}")
    print(f"  Copied to: {destination}")
    
    return True


# Example: User clicks on variation 1 (dark theme)
handle_user_selection(1)
```

## Quick Test

To test the integration:

```bash
# Terminal 1: Start server
cd /home/kesava89/Repos/MBZUAI-Hackathon-DreamTeam/compiler/server
python run_server.py

# Terminal 2: Generate variations
python test_template_api.py

# Terminal 3: Watch the output
watch -n 1 'ls -la /tmp/selection/*/project.json'
```

## Notes

- The API is **synchronous** - it waits until all 4 variations are generated
- Each generation takes ~2-5 seconds depending on template complexity
- Variations are **immediately available** after the API returns
- Container should watch `/tmp/selection/{0,1,2,3}` recursively
- On file change, reload the corresponding iframe
- User can select any of the 4 variations to continue editing
