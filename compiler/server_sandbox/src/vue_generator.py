# src/vue_generator.py
import json
import os
import re
from pathlib import Path

class VueGenerator:
    """
    Takes an AST (with state and events) and compiles
    a single-file .vue component.
    V18: Fixes the Icon component renderer to correctly
    add the `d=` attribute to the <path> tag.
    """
    def __init__(self, manifests_path):
        self.manifests_path = Path(manifests_path)
        self.manifests = self._load_manifests()
        self.state_vars = {}
        self.functions = []

    def _load_manifests(self):
        """Loads all component manifests from a directory."""
        manifests = {}
        if not self.manifests_path.is_dir():
            print(f"Warning: Manifests directory not found at {self.manifests_path}")
            return {}
            
        for f in self.manifests_path.glob("*.manifest.json"):
            component_type = f.name.split('.')[0]
            try:
                with open(f, 'r') as file:
                    manifests[component_type] = json.load(file)
            except json.JSONDecodeError:
                print(f"Warning: Corrupted manifest file: {f.name}")
        return manifests

    def _reset(self):
        """Resets the state for a new file generation."""
        self.state_vars = {}
        self.functions = []

    def _parse_state(self, state_data):
        """Generates state variable definitions (e.g., ref())"""
        for key, value in state_data.items():
            if isinstance(value, dict) and 'defaultValue' in value:
                self.state_vars[key] = value['defaultValue']
            else:
                self.state_vars[key] = value

    def _resolve_expression(self, expr_obj, is_event_handler=False):
        """
        Converts our simple expression (e.g., "${state.clickCount}")
        into Vue-compatible code (e.g., "clickCount").
        V14: Uses a regex to differentiate pure code from string templates.
        
        Returns a tuple: (resolved_string, uses_event_object)
        """
        uses_event = False

        if isinstance(expr_obj, str):
            value = expr_obj
        elif isinstance(expr_obj, (int, bool, float)) or expr_obj is None:
            return json.dumps(expr_obj), False
        elif isinstance(expr_obj, dict):
            value = expr_obj.get('value')
            if expr_obj.get('type') != 'expression':
                return json.dumps(str(expr_obj)), False
        else:
            return json.dumps(expr_obj), False

        if not isinstance(value, str):
            return json.dumps(value), False 

        resolved_value = value

        # --- Handle special keywords (event) ---
        if "event.target.value" in resolved_value:
            resolved_value = resolved_value.replace("event.target.value", "event.target.value")
            uses_event = True

        # --- Handle State Variables ---
        def replace_state_logic(match):
            return f"{match.group(1)}.value"
        def replace_state_template(match):
            if match.group(2):
                return f"{{{{ {match.group(1)}{match.group(2)} }}}}"
            return f"{{{{ {match.group(1)} }}}}"

        if is_event_handler:
            # --- V14: Logic Fix for Event Handlers ---
            
            # 1. Resolve all state variables to their .value equivalent
            resolved_value = re.sub(r'\$\{state\.(\w+)\}', replace_state_logic, resolved_value)

            # 2. Check if it's a special keyword first
            if resolved_value.strip() == "event.target.value":
                return resolved_value, True

            # 3. Check if the original object was an expression
            if isinstance(expr_obj, dict) and expr_obj.get('type') == 'expression':
                
                # V14 FIX: Use a regex to check if the resolved value is PURE code.
                # This regex looks for math, logic, state vars, and parens.
                # V17: Added \ (for modulo) to regex
                pure_code_pattern = re.compile(r"^[\w.()+\-*/%\s\d]+$")

                if pure_code_pattern.match(resolved_value):
                    # It's a pure code expression (like the carousel), return raw
                    return resolved_value, uses_event
                else:
                    # It's a template literal (like the alert), wrap in backticks
                    return f"`{resolved_value}`", uses_event
            
            # 4. If it was NOT an expression, it's just a plain string.
            return json.dumps(resolved_value), uses_event
            # --- End V14 Fix ---

        else:
            # --- Logic for Templates (Unchanged) ---
            # V18: Updated regex to handle simple state vars
            resolved_value = re.sub(r'\$\{state\.(\w+)\}(\s*[+\-*/%]\s*\d+)?', replace_state_template, resolved_value)
            
            if isinstance(expr_obj, str) and "{{" not in resolved_value:
                return resolved_value, False
                
            return f'"{resolved_value}"', False

    def _generate_functions(self, node_id, events):
        """
        Parses the "events" block and generates Vue functions.
        Returns a dictionary of event bindings, e.g., {'@click': 'onBtn1Click'}
        """
        event_bindings = {}
        if not events:
            return {}
            
        for event_name, actions in events.items():
            func_name = f"on{node_id.replace('-', '_')}_{event_name}"
            
            func_body = ""
            needs_event_param = False

            if not isinstance(actions, list):
                print(f"Warning: 'events' for {node_id} is not a list. Skipping.")
                continue

            for action in actions:
                action_type = action.get('type')
                
                if action_type == "action:setState":
                    key = action['stateKey']
                    new_val_expr, uses_event = self._resolve_expression(action['newValue'], is_event_handler=True) 
                    if uses_event:
                        needs_event_param = True
                    func_body += f"\n  {key}.value = {new_val_expr};"
                
                elif action_type == "action:scrollTo":
                    target = action.get('target', 'top')
                    if target == 'top':
                        func_body += "\n  window.scrollTo({ top: 0, behavior: 'smooth' });"
                    elif target == 'bottom':
                        func_body += "\n  window.scrollTo({ top: document.body.scrollHeight, behavior: 'smooth' });"
                    # V15: Add scrolling to an element ID
                    elif target.startswith('#'):
                        func_body += f"\n  const el = document.querySelector('{target}'); if (el) el.scrollIntoView({{ behavior: 'smooth' }});"
                
                elif action_type == "action:showAlert":
                    message_expr, _ = self._resolve_expression(action.get('message', 'Alert!'), is_event_handler=True)
                    func_body += f"\n  alert({message_expr});"

            func_param = "(event)" if needs_event_param else "()"
            event_bindings[f"@{event_name}"] = f"{func_name}"
            self.functions.append(f"function {func_name}{func_param} {{\n{func_body}\n}}")
        
        return event_bindings

    def _generate_style_string(self, style_obj):
        """Converts a style object to an inline style string."""
        if not isinstance(style_obj, dict):
            return ""
        # V18: Convert camelCase to kebab-case
        def camel_to_kebab(name):
            return re.sub(r'(?<!^)(?=[A-Z])', '-', name).lower()
        return "; ".join([f"{camel_to_kebab(k)}: {v}" for k, v in style_obj.items()])

    def _generate_node(self, node):
        """RECURSIVE FUNCTION: Generates HTML for one AST node."""
        node_type = node.get('type')
        if not node_type or node_type not in self.manifests:
            print(f"Warning: Skipping node {node.get('id')}, manifest not found for type '{node_type}'")
            return ""

        manifest = self.manifests[node_type]
        tag = node.get('props', {}).get('as', manifest['componentName'])
        
        props_map = { 'data-component-id': f'"{node["id"]}"' }
        
        v_if = node.get('v-if')
        if isinstance(v_if, dict):
            if 'expression' in v_if:
                # V18: Resolve state vars in v-if expressions
                expr = re.sub(r'\$\{state\.(\w+)\}', r'\1', v_if['expression'])
                props_map['v-if'] = f'"{expr}"'
            elif 'stateKey' in v_if:
                props_map['v-if'] = f'"{v_if["stateKey"]}"'

        # --- Handle Props ---
        content = None
        if 'props' in node:
            for key, value in node['props'].items():
                
                if key == 'id' and 'id' in manifest['props']:
                    if isinstance(value, str):
                        props_map['id'] = f'"{value}"'
                    continue

                if key == 'class' and 'class' in manifest['props']:
                    if isinstance(value, str):
                        props_map['class'] = f'"{value}"'
                    continue
                
                if key == 'as':
                    continue

                # V18: Check against manifest *after* handling global props
                if key not in manifest['props']:
                    continue
                
                if key == 'content' or key == 'text':
                    content_val, _ = self._resolve_expression(value, is_event_handler=False)
                    # V18: Cleaned up content logic
                    if isinstance(value, str):
                        content = content_val
                    elif isinstance(value, dict) and value.get('type') == 'expression':
                         content = content_val.replace('"', '') # Use unquoted value for {{...}}
                    
                    if tag == "button": 
                         continue
                    elif tag != "p": # Put prop on element (e.g., <h1 content="...">)
                         props_map[key] = f'"{content}"'
                    continue
                
                if key == 'style' and isinstance(value, dict):
                    props_map['style'] = f'"{self._generate_style_string(value)}"'
                
                elif key == 'modelValue' and isinstance(value, dict) and value.get('type') == 'stateBinding':
                    props_map[f"v-model"] = f'"{value["stateKey"]}"'

                # V15: Handle SVG props for Icon
                elif node_type == 'Icon' and key == 'svgPath':
                    # This adds 'd="...path..."' to the map
                    props_map['d'] = f'"{value}"'
                    continue
                elif node_type == 'Icon' and key == 'viewBox':
                    props_map['viewBox'] = f'"{value}"'
                    continue
                
                elif isinstance(value, dict) and value.get('type') == 'expression':
                    resolved_value, _ = self._resolve_expression(value, is_event_handler=False)
                    # V18: Simplified binding logic
                    match = re.match(r'^\{\{\s*([\w.]+)\s*\}\}$', resolved_value.replace('"', ''))
                    if match:
                         props_map[f":{key}"] = f'"{match.group(1)}"'
                    else:
                        props_map[key] = resolved_value
                
                elif isinstance(value, (str, int, bool)):
                    props_map[key] = f'"{value}"'

        # --- Handle Events ---
        if 'events' in node:
            event_bindings = self._generate_functions(node['id'], node.get('events', {}))
            props_map.update(event_bindings)

        props_str = " ".join([f'{k}={v}' for k, v in props_map.items()])

        # --- Handle Special Components (List, Table, Icon) ---
        indent = "  "
        if node_type == 'List':
            items_str = node.get('props', {}).get('items', [])
            li_tags = ""
            if items_str:
                li_tags = "\n".join([f"{indent}  <li>{item}</li>" for item in items_str])
            
            children_str = ""
            if 'slots' in node and 'default' in node['slots']:
                 for child_node in node['slots']['default']:
                    children_str += self._generate_node(child_node) + "\n"

            return f"{indent}<{tag} {props_str}>\n{li_tags}{children_str}{indent}</{tag}>"

        if node_type == 'Table':
            headers = node.get('props', {}).get('headers', [])
            rows = node.get('props', {}).get('rows', [])
            
            th_tags = "".join([f"<th>{h}</th>" for h in headers])
            tr_tags = ""
            for row in rows:
                td_tags = "".join([f"<td>{cell}</td>" for cell in row])
                tr_tags += f"{indent}  <tr>{td_tags}</tr>\n"
            
            return (
                f"{indent}<{tag} {props_str}>\n"
                f"{indent}  <thead>\n{indent}    <tr>{th_tags}</tr>\n{indent}  </thead>\n"
                f"{indent}  <tbody>\n{tr_tags}{indent}  </tbody>\n"
                f"{indent}</{tag}>"
            )
        
        # V18: Render Icon component as SVG
        if node_type == 'Icon':
            # This is the fix. We explicitly add `d=`
            path_d_attr = props_map.get('d', '""')
            # We must remove 'd' from props_str to avoid duplicate
            props_str = " ".join([f'{k}={v}' for k, v in props_map.items() if k != 'd'])
            return f"{indent}<svg {props_str} fill=\"currentColor\" width=\"1em\" height=\"1em\">\n{indent}  <path d={path_d_attr}></path>\n{indent}</svg>"

        # --- Handle Children (Slots) ---
        children_str = ""
        if 'slots' in node and 'default' in node['slots']:
            for child_node in node['slots']['default']:
                children_str += self._generate_node(child_node) + "\n"
        
        # --- Assemble Node ---
        if content:
            if "{{" in content:
                return f"{indent}<{tag} {props_str}>{content}</{tag}>"
            else:
                return f"{indent}<{tag} {props_str}>{content}</{tag}>"
        
        if not children_str and tag in ['img', 'input']:
            return f"{indent}<{tag} {props_str} />"

        return f"{indent}<{tag} {props_str}>\n{children_str}{indent}</{tag}>"

    def generate_vue_file(self, ast):
        """Generates the full .vue file content."""
        self._reset()
        
        if 'state' in ast:
            self._parse_state(ast['state'])
        
        template_content = ""
        if 'tree' in ast:
            template_content = self._generate_node(ast['tree'])
        else:
            print("Warning: AST has no 'tree' root. Generating empty template.")
            
        template = f"<template>\n{template_content}\n</template>"

        script_lines = ["<script setup>"]
        if self.state_vars:
            script_lines.append("import { ref } from 'vue'")
            for key, value in self.state_vars.items():
                script_lines.append(f"const {key} = ref({json.dumps(value)})")
        
        if self.functions:
            script_lines.append("\n" + "\n\n".join(self.functions))
        
        script_lines.append("</script>")
        script = "\n".join(script_lines)

        style = "<style scoped>\n/* Add component-specific styles here */\n</style>"

        return f"{template}\n\n{script}\n\n{style}"