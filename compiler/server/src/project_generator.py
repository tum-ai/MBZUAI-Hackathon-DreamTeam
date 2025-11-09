# src/project_generator.py
import os
import json
import shutil
import hashlib
from pathlib import Path
import config
from .vue_generator import VueGenerator

class ProjectGenerator:
    """
    Orchestrates the creation of the entire Vue.js project.
    V19: Injects the automation_agent.js script.
    V22: Incremental generation with file hashing and shared components support.
    """
    def __init__(self):
        self.manifests_dir = config.MANIFESTS_DIR
        self.static_dir = config.STATIC_DIR
        self.output_dir = config.OUTPUT_DIR
        self.ast_input_dir = config.AST_INPUT_DIR
        self.project_config_file = config.PROJECT_CONFIG_FILE
        self.cache_file = config.GENERATION_CACHE_FILE

        self.project_data = config.DEFAULT_PROJECT_CONFIG
        try:
            if self.project_config_file.exists():
                with open(self.project_config_file, 'r') as f:
                    self.project_data = json.load(f)
            else:
                print("Info: project.json not found. Using default config for build.")
        except json.JSONDecodeError:
            print(f"Warning: {self.project_config_file.name} corrupted. Using default.")
        
        self.file_generator = VueGenerator(self.manifests_dir)
        
        # Load generation cache
        self.cache_existed = self.cache_file.exists()
        self.cache = self._load_cache()
        
    def _load_cache(self):
        """Load the generation cache from disk."""
        if self.cache_file.exists():
            try:
                with open(self.cache_file, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                print("Warning: Cache file corrupted. Starting fresh.")
        return {
            "project_hash": None,
            "page_hashes": {},
            "generated_files": []
        }
    
    def _save_cache(self):
        """Save the generation cache to disk."""
        try:
            with open(self.cache_file, 'w') as f:
                json.dump(self.cache, f, indent=2)
        except IOError as e:
            print(f"Warning: Could not save cache: {e}")
    
    def _compute_file_hash(self, file_path: Path) -> str:
        """Compute SHA256 hash of a file."""
        if not file_path.exists():
            return ""
        try:
            with open(file_path, 'rb') as f:
                return hashlib.sha256(f.read()).hexdigest()
        except IOError:
            return ""
    
    def _compute_json_hash(self, data: dict) -> str:
        """Compute SHA256 hash of JSON data."""
        json_str = json.dumps(data, sort_keys=True)
        return hashlib.sha256(json_str.encode()).hexdigest()
    
    def _detect_changes(self):
        """
        Detect what has changed since last generation.
        Returns: (project_changed, pages_list_changed, changed_pages, all_pages)
        """
        # If cache didn't exist on disk, treat as first run (everything changed)
        is_first_run = not self.cache_existed
        
        # Compute current project hash (excluding page list for page-level tracking)
        project_config_copy = self.project_data.copy()
        pages_list = project_config_copy.pop('pages', [])
        current_project_hash = self._compute_json_hash(project_config_copy)
        
        project_changed = self.cache.get("project_hash") != current_project_hash or is_first_run
        
        # Check if pages list changed (added/removed pages)
        current_page_names = set(p.get('name') for p in pages_list if p.get('name'))
        cached_page_names = set(self.cache.get("page_hashes", {}).keys())
        pages_list_changed = current_page_names != cached_page_names
        
        # Compute page hashes
        changed_pages = []
        all_pages = []
        
        for page in pages_list:
            ast_file = page.get('astFile')
            page_name = page.get('name')
            if not ast_file or not page_name:
                continue
                
            all_pages.append(page_name)
            ast_path = self.ast_input_dir / ast_file.lower()
            current_hash = self._compute_file_hash(ast_path)
            cached_hash = self.cache.get("page_hashes", {}).get(page_name)
            
            if current_hash != cached_hash:
                changed_pages.append(page_name)
                self.cache.setdefault("page_hashes", {})[page_name] = current_hash
        
        # Remove deleted pages from cache
        for old_page in (cached_page_names - current_page_names):
            self.cache.get("page_hashes", {}).pop(old_page, None)
        
        # Update project hash in cache
        self.cache["project_hash"] = current_project_hash
        
        return project_changed, pages_list_changed, changed_pages, all_pages

    def generate_project(self):
        """
        Main method to generate the entire project.
        V22: Implements incremental generation.
        """
        print(f"Starting project generation in: {self.output_dir}")
        
        # Detect changes
        project_changed, pages_list_changed, changed_pages, all_pages = self._detect_changes()
        
        if not project_changed and not pages_list_changed and not changed_pages:
            print("No changes detected. Skipping generation.")
            return
        
        print(f"Change detection:")
        print(f"  - Project config changed: {project_changed}")
        print(f"  - Pages list changed (added/removed): {pages_list_changed}")
        print(f"  - Changed pages: {changed_pages if changed_pages else 'None'}")
        
        # Always create skeleton (lightweight)
        self._create_skeleton()
        
        # Regenerate infrastructure if project changed OR pages list changed
        if project_changed or pages_list_changed:
            if project_changed:
                print("Project config changed. Regenerating infrastructure files...")
            if pages_list_changed:
                print("Pages list changed. Regenerating router...")
            
            self._copy_static_files()
            self._generate_router()  # Always regenerate router when pages list changes
            self._generate_app_vue()  # Includes shared navbar/footer
            self._generate_dynamic_files()
            
            # When project changes, regenerate all pages (cascading)
            # When only pages list changes, regenerate only new/changed pages
            if project_changed:
                self._generate_views(all_pages)
            else:
                self._generate_views(changed_pages)
        else:
            # Only regenerate changed pages
            print(f"Regenerating only changed pages: {changed_pages}")
            self._generate_views(changed_pages)
        
        # Save cache
        self._save_cache()
        
        print("Project generation complete.")
        # Removed the `npm install` instructions as the container server will handle it

    def _create_skeleton(self):
        """
        Creates the basic directory structure.
        """
        (self.output_dir / 'src' / 'views').mkdir(parents=True, exist_ok=True)
        (self.output_dir / 'src' / 'router').mkdir(parents=True, exist_ok=True)
        (self.output_dir / 'src' / 'assets').mkdir(parents=True, exist_ok=True)
        (self.output_dir / 'public').mkdir(parents=True, exist_ok=True)
        print("Created project skeleton...")

    def _copy_static_files(self):
        """
        Copies boilerplate files like index.html, vite.config.js, etc.
        V19: Also copies the new automation_agent.js
        """
        # --- V19: Copy automation_agent.js to the output 'public' directory ---
        agent_src = self.static_dir / 'automation_agent.js'
        # --- THIS IS THE FIX ---
        agent_dest = self.output_dir / 'public' / 'automation_agent.js'
        # --- END OF FIX ---
        
        if agent_src.exists():
            shutil.copy(agent_src, agent_dest)
        else:
            print(f"Warning: Static file not found: {agent_src}")
        # --- End V19 Change ---

        static_files_to_root = ['vite.config.js', 'index.html']
        for file_name in static_files_to_root:
            src = self.static_dir / file_name
            dest = self.output_dir / file_name
            if src.exists():
                shutil.copy(src, dest)
            else:
                print(f"Warning: Static file not found: {src}")

        static_files_to_src = ['main.js']
        for file_name in static_files_to_src:
            src = self.static_dir / file_name
            dest = self.output_dir / 'src' / file_name
            if src.exists():
                shutil.copy(src, dest)
            else:
                print(f"Warning: Static file not found: {src}")

        print("Copied static files...")

    def _generate_router(self):
# ... (rest of the file is unchanged) ...
        """
        Generates the src/router/index.js file based on project.json.
        """
        router_path = self.output_dir / 'src' / 'router' / 'index.js'
        
        imports = []
        routes = []
        
        pages = self.project_data.get('pages', [])
        num_pages = len(pages)
        
        for page in pages:
            component_name = page.get('name', 'UnnamedPage')
            route_path = page.get('path', '/')
            ast_file = page.get('astFile')
            
            if not ast_file:
                print(f"Warning: Skipping page '{component_name}' - no astFile defined.")
                continue

            # V6: If there's only one page, force it to be the homepage '/'
            if num_pages == 1:
                route_path = "/"
            
            imports.append(f"import {component_name} from '../views/{component_name}.vue'")
            
            routes.append(
                f"  {{\n"
                f"    path: '{route_path}',\n"
                f"    name: '{component_name}',\n"
                f"    component: {component_name}\n"
                f"  }}"
            )
            
        router_content = (
            "import { createRouter, createWebHashHistory } from 'vue-router'\n"
            + "\n".join(imports) + "\n\n"
            + "const routes = [\n"
            + ",\n".join(routes) + "\n]\n\n"
            + "const router = createRouter({\n"
            + "  history: createWebHashHistory(),\n"
            + "  routes\n"
            + "})\n\n"
            + "export default router\n"
        )
        
        self._write_file(router_path, router_content)

    def _generate_app_vue(self):
        """
        Generates the root App.vue file.
        V11: This is now a "dumb" shell. It only contains the
        router-view and the global styles. All navs are
        now controlled by the page ASTs.
        V20: Added animations for advanced components.
        V22: Supports shared navbar/footer from project.json.
        """
        print("Generating root App.vue...")
        
        global_styles = self.project_data.get('globalStyles', '')
        shared_components = self.project_data.get('sharedComponents', {})
        
        # Generate shared navbar if enabled
        navbar_html = ""
        navbar_enabled = shared_components.get('navbar', {}).get('enabled', False)
        if navbar_enabled:
            navbar_ast = shared_components.get('navbar', {}).get('ast')
            if navbar_ast:
                print("  - Generating shared navbar in App.vue")
                navbar_html = self._generate_component_html(navbar_ast, indent=2)
                print(f"  - Navbar HTML length: {len(navbar_html)} chars")
            else:
                print("  - Warning: navbar enabled but AST is None")
        
        # Generate shared footer if enabled
        footer_html = ""
        footer_enabled = shared_components.get('footer', {}).get('enabled', False)
        if footer_enabled:
            footer_ast = shared_components.get('footer', {}).get('ast')
            if footer_ast:
                print("  - Generating shared footer in App.vue")
                footer_html = self._generate_component_html(footer_ast, indent=2)

        # V23: Template now includes optional navbar and footer with dynamic padding
        # Use Vue's ref and onMounted to dynamically calculate navbar height
        script_section = ""
        template = f"""
<template>
{navbar_html}
  <div :style="contentStyle">
    <router-view/>
  </div>
{footer_html}
</template>"""

        # Add script section for dynamic navbar height calculation if navbar is enabled
        if navbar_enabled:
            print("  - Adding dynamic navbar padding script")
            script_section = """

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'

const navbarHeight = ref(0)
const contentStyle = ref({})

const updateNavbarHeight = () => {
  const navbar = document.querySelector('[data-component-id="navbar"]')
  if (navbar) {
    navbarHeight.value = navbar.offsetHeight
    contentStyle.value = { paddingTop: `${navbarHeight.value}px` }
    // Set CSS variable for navbar height so pages can use it
    document.documentElement.style.setProperty('--navbar-height', `${navbarHeight.value}px`)
  }
}

onMounted(() => {
  updateNavbarHeight()
  // Update on window resize in case navbar height changes
  window.addEventListener('resize', updateNavbarHeight)
})

onUnmounted(() => {
  window.removeEventListener('resize', updateNavbarHeight)
})
</script>
"""

        # V20: Added animations for GradientText and other advanced components
        # V21: Added animations for all new Vue Bits components
        animations = """
/* --- V20/V21: Animations for Advanced Components --- */
@keyframes gradient-shift {
  0% { background-position: 0% 50%; }
  50% { background-position: 100% 50%; }
  100% { background-position: 0% 50%; }
}

@keyframes blur-in {
  0% {
    filter: blur(10px);
    opacity: 0;
  }
  100% {
    filter: blur(0);
    opacity: 1;
  }
}

@keyframes ribbon-flow {
  0% {
    transform: translateX(-50%) rotate(-15deg);
  }
  100% {
    transform: translateX(50%) rotate(-15deg);
  }
}

@keyframes color-flow {
  0%, 100% {
    transform: translate(0%, 0%) scale(1);
  }
  25% {
    transform: translate(-25%, 25%) scale(1.2);
  }
  50% {
    transform: translate(25%, -25%) scale(0.8);
  }
  75% {
    transform: translate(-25%, -25%) scale(1.1);
  }
}

@keyframes plasma-flow {
  0%, 100% {
    transform: translate(0, 0) scale(1);
    opacity: 0.6;
  }
  33% {
    transform: translate(-30%, 30%) scale(1.3);
    opacity: 0.8;
  }
  66% {
    transform: translate(30%, -30%) scale(0.9);
    opacity: 0.5;
  }
}

@keyframes square-animation {
  0%, 100% {
    opacity: 0.2;
  }
  50% {
    opacity: 0.4;
  }
}

/* CardSwap hover effect */
.card-swap-hover:hover .card-swap-inner {
  transform: rotateY(180deg);
}

/* MagicBento hover effects */
.magic-bento > * {
  transition: transform 0.3s ease, box-shadow 0.3s ease;
}

/* Navigation link hover effects */
a[href^="#/"]:hover {
  color: #667eea !important;
}

.magic-bento > *:hover {
  transform: translateY(-8px);
  box-shadow: 0 12px 40px rgba(0, 0, 0, 0.4);
}
/* --- End Animations --- */
"""

        # V11: Only global_styles are injected. No default CSS.
        style = f"""
<style>
/* --- Global Styles from project.json --- */
{global_styles}
/* --- End Global Styles --- */

{animations}
</style>
"""
        self._write_file(self.output_dir / 'src' / 'App.vue', f"{template}\n{script_section}\n{style}\n")

    def _generate_views(self, pages_to_generate=None):
        """
        Generates .vue files for specified pages (or all if None).
        V22: Supports selective page regeneration.
        
        Args:
            pages_to_generate: List of page names to generate, or None for all pages.
        """
        print("Generating views...")
        views_dir = self.output_dir / 'src' / 'views'
        
        all_pages = self.project_data.get('pages', [])
        
        for page in all_pages:
            ast_file = page.get('astFile')
            view_name = page.get('name')
            if not ast_file or not view_name:
                print(f"Warning: Skipping page with incomplete config: {page}")
                continue
            
            # Skip if we're doing selective generation and this page isn't in the list
            if pages_to_generate is not None and view_name not in pages_to_generate:
                continue

            ast_path = self.ast_input_dir / ast_file.lower()
            view_file_path = views_dir / f"{view_name}.vue"
            
            self._generate_page(ast_path, view_file_path)

    def _generate_page(self, ast_path, output_path):
        """
        Generates a single .vue file from a single AST file.
        """
        try:
            with open(ast_path, 'r') as f:
                ast_data = json.load(f)
        except FileNotFoundError:
            print(f"Error: AST file not found at {ast_path}. Generating blank page.")
            ast_data = {
                "state": {},
                "tree": {"id": "root", "type": "Box", "props": {}, "slots": { "default": [
                    {"id": "error-text", "type": "Text", "props": {"content": f"Error: AST file {ast_path.name} not found.", "as": "h1"}}
                ]}}
            }
        except json.JSONDecodeError:
            print(f"Error: AST file corrupted at {ast_path}. Skipping page.")
            return
            
        try:
            vue_content = self.file_generator.generate_vue_file(ast_data)
            self._write_file(output_path, vue_content)
        except Exception as e:
            print(f"Error generating {output_path}: {e}")

    def _generate_dynamic_files(self):
        """
        Generates files that depend on project config, like package.json
        and main.js (for plugins in the future).
        """
        print("Generating dynamic files (package.json, main.js)...")
        
        pkg_json = {"name": "default-project", "dependencies": {}, "devDependencies": {}}
        static_pkg_path = self.static_dir / 'package.json'
        
        if static_pkg_path.exists():
            try:
                with open(static_pkg_path, 'r') as f:
                    pkg_json = json.load(f)
            except Exception:
                print(f"Warning: {static_pkg_path.name} corrupted. Using default.")
        else:
            print(f"Warning: {static_pkg_path.name} not found. Using default.")

        pkg_json['name'] = self.project_data.get('projectName', 'my-new-site').lower().replace(" ", "-")
        
        self._write_file(self.output_dir / 'package.json', json.dumps(pkg_json, indent=2))
            
        main_js_path = self.output_dir / 'src' / 'main.js'
        if not main_js_path.exists():
            print("Warning: src/main.js was not copied correctly. Creating default.")
            main_js_content = "import { createApp } from 'vue'\nimport App from './App.vue'\nimport router from './router'\n\ncreateApp(App).use(router).mount('#app')\n"
            self._write_file(main_js_path, main_js_content)
            
    def _generate_component_html(self, component_ast: dict, indent: int = 0) -> str:
        """
        Generate HTML for a component from its AST (for shared components).
        Uses the vue_generator's _generate_node method directly.
        
        Args:
            component_ast: The AST node for the component
            indent: Number of spaces to indent
            
        Returns:
            HTML string for the component
        """
        try:
            # Reset the generator state
            self.file_generator._reset()
            
            # Generate the HTML directly from the node
            html = self.file_generator._generate_node(component_ast, parent_context="")
            
            # Add indentation to each line
            if indent > 0 and html:
                indent_str = ' ' * indent
                lines = html.split('\n')
                html = '\n'.join(indent_str + line if line.strip() else line for line in lines)
            
            return html if html else f"{'  ' * indent}<!-- Empty component -->"
                
        except Exception as e:
            print(f"Error generating component HTML: {e}")
            import traceback
            traceback.print_exc()
            return f"{'  ' * indent}<!-- Error generating shared component: {e} -->"
    
    def _write_file(self, file_path: Path, content: str):
        """Utility to write a file and print success."""
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"Successfully generated {file_path}")
        except Exception as e:
            print(f"Error writing file {file_path}: {e}")