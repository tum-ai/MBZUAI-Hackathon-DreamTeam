#!/usr/bin/env python3
"""
Clean utility for the Vue Bits Generator

This script cleans generated artifacts and optionally cache files.
Use this to start fresh or resolve stale file issues.

Usage:
    python clean.py                    # Clean generated files only
    python clean.py --all              # Clean everything including cache
    python clean.py --cache-only       # Clean only the cache
    python clean.py --inputs           # Clean orphaned input AST files
"""

import argparse
import shutil
from pathlib import Path
import config


def clean_generated_files(verbose=True):
    """Remove all generated files in the output directory."""
    output_dir = config.OUTPUT_DIR
    
    if not output_dir.exists():
        if verbose:
            print(f"Output directory doesn't exist: {output_dir}")
        return
    
    # List of directories/files to remove
    items_to_remove = [
        output_dir / 'src',
        output_dir / 'public',
        output_dir / 'node_modules',
        output_dir / 'dist',
        output_dir / 'package.json',
        output_dir / 'package-lock.json',
        output_dir / 'vite.config.js',
        output_dir / 'index.html',
    ]
    
    removed_count = 0
    for item in items_to_remove:
        if item.exists():
            if item.is_dir():
                shutil.rmtree(item)
                if verbose:
                    print(f"✓ Removed directory: {item.name}")
            else:
                item.unlink()
                if verbose:
                    print(f"✓ Removed file: {item.name}")
            removed_count += 1
    
    if removed_count == 0 and verbose:
        print("No generated files found to remove.")
    elif verbose:
        print(f"\nCleaned {removed_count} items from output directory.")


def clean_cache(verbose=True):
    """Remove the generation cache file."""
    cache_file = config.GENERATION_CACHE_FILE
    
    if cache_file.exists():
        cache_file.unlink()
        if verbose:
            print(f"✓ Removed cache: {cache_file}")
    else:
        if verbose:
            print("Cache file doesn't exist.")


def clean_orphaned_inputs(verbose=True):
    """
    Remove AST input files that aren't referenced in project.json.
    This helps clean up old relics like landing.json.
    """
    import json
    
    # Load project.json to get valid page AST files
    if not config.PROJECT_CONFIG_FILE.exists():
        if verbose:
            print("project.json not found. Cannot determine orphaned files.")
        return
    
    try:
        with open(config.PROJECT_CONFIG_FILE, 'r') as f:
            project_data = json.load(f)
    except json.JSONDecodeError:
        if verbose:
            print("Error: project.json is corrupted.")
        return
    
    # Get list of valid AST files from project.json
    valid_ast_files = set()
    for page in project_data.get('pages', []):
        ast_file = page.get('astFile')
        if ast_file:
            valid_ast_files.add(ast_file.lower())
    
    # Find all JSON files in inputs directory
    inputs_dir = config.AST_INPUT_DIR
    if not inputs_dir.exists():
        if verbose:
            print(f"Inputs directory doesn't exist: {inputs_dir}")
        return
    
    json_files = list(inputs_dir.glob('*.json'))
    orphaned_files = [
        f for f in json_files 
        if f.name.lower() not in valid_ast_files
    ]
    
    if not orphaned_files:
        if verbose:
            print("No orphaned input files found.")
        return
    
    if verbose:
        print(f"\nFound {len(orphaned_files)} orphaned input file(s):")
        for f in orphaned_files:
            print(f"  - {f.name}")
        
        response = input("\nDelete these files? (y/N): ").strip().lower()
        if response != 'y':
            print("Cancelled.")
            return
    
    removed_count = 0
    for f in orphaned_files:
        f.unlink()
        if verbose:
            print(f"✓ Removed: {f.name}")
        removed_count += 1
    
    if verbose:
        print(f"\nRemoved {removed_count} orphaned input file(s).")


def main():
    parser = argparse.ArgumentParser(
        description="Clean utility for Vue Bits Generator",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python clean.py                 # Clean generated files
  python clean.py --all           # Clean everything
  python clean.py --cache-only    # Clean only cache
  python clean.py --inputs        # Clean orphaned input files
        """
    )
    
    parser.add_argument(
        '--all',
        action='store_true',
        help='Clean everything (generated files + cache)'
    )
    
    parser.add_argument(
        '--cache-only',
        action='store_true',
        help='Clean only the generation cache'
    )
    
    parser.add_argument(
        '--inputs',
        action='store_true',
        help='Clean orphaned input AST files not in project.json'
    )
    
    parser.add_argument(
        '-y', '--yes',
        action='store_true',
        help='Skip confirmation prompts'
    )
    
    parser.add_argument(
        '-q', '--quiet',
        action='store_true',
        help='Minimal output'
    )
    
    args = parser.parse_args()
    verbose = not args.quiet
    
    # Determine what to clean
    if args.cache_only:
        if verbose:
            print("Cleaning cache only...\n")
        clean_cache(verbose=verbose)
    elif args.inputs:
        if verbose:
            print("Cleaning orphaned input files...\n")
        clean_orphaned_inputs(verbose=verbose)
    elif args.all:
        if verbose:
            print("Cleaning all generated artifacts and cache...\n")
        clean_generated_files(verbose=verbose)
        clean_cache(verbose=verbose)
    else:
        # Default: clean generated files only
        if verbose:
            print("Cleaning generated files...\n")
        clean_generated_files(verbose=verbose)
    
    if verbose:
        print("\n✓ Clean complete!")


if __name__ == '__main__':
    main()
