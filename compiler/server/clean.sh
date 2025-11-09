#!/bin/bash
# Quick clean script - runs the Python clean utility

cd "$(dirname "$0")"

case "${1:-}" in
    --all|-a)
        echo "Cleaning everything (generated files + cache)..."
        python clean.py --all
        ;;
    --cache|-c)
        echo "Cleaning cache only..."
        python clean.py --cache-only
        ;;
    --inputs|-i)
        echo "Cleaning orphaned input files..."
        python clean.py --inputs
        ;;
    --help|-h)
        python clean.py --help
        ;;
    *)
        echo "Cleaning generated files..."
        python clean.py
        ;;
esac
