"""
Template Generator - Command Line Interface
Use this to generate initial site templates from the command line.
"""

import json
import argparse
from templates import generate_from_template, get_available_templates, get_template_info

def main():
    parser = argparse.ArgumentParser(
        description="Generate initial website templates",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # List available templates
  python template_generator.py --list
  
  # Get template information
  python template_generator.py --info portfolio
  
  # Generate from JSON variables file
  python template_generator.py portfolio --input vars.json --output output.json
  
  # Generate with inline JSON variables
  python template_generator.py portfolio --vars '{"name":"John","tagline":"Developer"}'
        """
    )
    
    parser.add_argument(
        'template',
        nargs='?',
        help='Template name (e.g., portfolio)'
    )
    
    parser.add_argument(
        '--list',
        action='store_true',
        help='List all available templates'
    )
    
    parser.add_argument(
        '--info',
        metavar='TEMPLATE',
        help='Show information about a template'
    )
    
    parser.add_argument(
        '--input', '-i',
        metavar='FILE',
        help='JSON file containing template variables'
    )
    
    parser.add_argument(
        '--vars',
        metavar='JSON',
        help='Inline JSON string with template variables'
    )
    
    parser.add_argument(
        '--output', '-o',
        metavar='FILE',
        help='Output file for generated patches (default: print to stdout)'
    )
    
    args = parser.parse_args()
    
    # List templates
    if args.list:
        print("Available templates:")
        for template in get_available_templates():
            print(f"  - {template}")
        return
    
    # Show template info
    if args.info:
        try:
            info = get_template_info(args.info)
            print(json.dumps(info, indent=2))
        except ValueError as e:
            print(f"Error: {e}")
            return
    
    # Generate from template
    if args.template:
        # Load variables
        variables = {}
        
        if args.input:
            with open(args.input, 'r') as f:
                variables = json.load(f)
        elif args.vars:
            variables = json.loads(args.vars)
        else:
            print("Error: Must provide --input or --vars with template variables")
            print("Use --info <template> to see required variables")
            return
        
        try:
            # Generate patches
            patches = generate_from_template(args.template, variables)
            
            # Output
            output_json = json.dumps(patches, indent=2)
            
            if args.output:
                with open(args.output, 'w') as f:
                    f.write(output_json)
                print(f"Generated {len(patches)} patches and saved to {args.output}")
            else:
                print(output_json)
                
        except ValueError as e:
            print(f"Error: {e}")
        except Exception as e:
            print(f"Error generating template: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    main()
