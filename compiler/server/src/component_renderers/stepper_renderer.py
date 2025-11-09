"""Renderer for Stepper component."""
from .base_renderer import BaseComponentRenderer


class StepperRenderer(BaseComponentRenderer):
    """Handles rendering of Stepper components."""
    
    @property
    def component_type(self):
        return 'Stepper'
    
    def render(self, node, props_map, manifest, semantic_id, context):
        """Render a Stepper component."""
        tag = node.get('props', {}).get('as', manifest['componentName'])
        indent = "  "
        
        steps = node.get('props', {}).get('steps', [])
        current_step = node.get('props', {}).get('currentStep', 0)
        show_icons = node.get('props', {}).get('showIcons', True)
        completed_color = node.get('props', {}).get('completedColor', '#10b981')
        active_color = node.get('props', {}).get('activeColor', '#3b82f6')
        
        # Handle state binding for currentStep
        if isinstance(current_step, dict) and current_step.get('type') == 'stateBinding':
            current_step_var = current_step.get('stateKey')
            props_str = " ".join([f'{k}={v}' for k, v in props_map.items()])
            
            stepper_html = f'{indent}<{tag} {props_str}>\n'
            
            for idx, step in enumerate(steps):
                step_title = step.get('title', f'Step {idx + 1}')
                step_desc = step.get('description', '')
                step_icon = step.get('icon', '•')
                
                step_html = f'{indent}  <div data-component-id="{semantic_id}.step-{idx}" style="display: flex; align-items: center; gap: 1rem; padding: 1rem;">\n'
                step_html += f'{indent}    <div :style="{{width: \'40px\', height: \'40px\', borderRadius: \'50%\', display: \'flex\', alignItems: \'center\', justifyContent: \'center\', fontWeight: \'bold\', background: {current_step_var}.value > {idx} ? \'{completed_color}\' : {current_step_var}.value === {idx} ? \'{active_color}\' : \'#333\', color: \'white\'}}">\n'
                
                if show_icons:
                    step_html += f'{indent}      <span>{step_icon}</span>\n'
                else:
                    step_html += f'{indent}      <span>{idx + 1}</span>\n'
                
                step_html += f'{indent}    </div>\n'
                step_html += f'{indent}    <div style="flex: 1;">\n'
                step_html += f'{indent}      <div style="font-weight: 600; font-size: 16px;">{step_title}</div>\n'
                
                if step_desc:
                    step_html += f'{indent}      <div style="color: #888; font-size: 14px; margin-top: 0.25rem;">{step_desc}</div>\n'
                
                step_html += f'{indent}    </div>\n'
                step_html += f'{indent}  </div>\n'
                
                stepper_html += step_html
            
            if 'slots' in node and 'default' in node['slots']:
                for idx, child_node in enumerate(node['slots']['default']):
                    stepper_html += context.generate_node(child_node, semantic_id, idx) + "\n"
            
            stepper_html += f'{indent}</{tag}>'
            return stepper_html
        
        # Static version
        props_str = " ".join([f'{k}={v}' for k, v in props_map.items()])
        stepper_html = f'{indent}<{tag} {props_str}>\n'
        
        for idx, step in enumerate(steps):
            step_title = step.get('title', f'Step {idx + 1}')
            step_desc = step.get('description', '')
            step_icon = step.get('icon', '•')
            
            is_completed = idx < current_step
            is_active = idx == current_step
            bg_color = completed_color if is_completed else (active_color if is_active else '#333')
            
            step_html = f'{indent}  <div data-component-id="{semantic_id}.step-{idx}" style="display: flex; align-items: center; gap: 1rem; padding: 1rem;">\n'
            step_html += f'{indent}    <div style="width: 40px; height: 40px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-weight: bold; background: {bg_color}; color: white;">\n'
            
            if show_icons:
                step_html += f'{indent}      <span>{step_icon}</span>\n'
            else:
                step_html += f'{indent}      <span>{idx + 1}</span>\n'
            
            step_html += f'{indent}    </div>\n'
            step_html += f'{indent}    <div style="flex: 1;">\n'
            step_html += f'{indent}      <div style="font-weight: 600; font-size: 16px;">{step_title}</div>\n'
            
            if step_desc:
                step_html += f'{indent}      <div style="color: #888; font-size: 14px; margin-top: 0.25rem;">{step_desc}</div>\n'
            
            step_html += f'{indent}    </div>\n'
            step_html += f'{indent}  </div>\n'
            
            stepper_html += step_html
        
        stepper_html += f'{indent}</{tag}>'
        return stepper_html
