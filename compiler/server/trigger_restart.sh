#!/bin/bash
# Trigger restart of active project Vite server
# This script runs in the compiler-api container and signals the variations container

SIGNAL_FILE="/tmp/active/.restart-signal"
TIMESTAMP=$(date +%s)

echo "🔄 Creating restart signal..."
echo "$TIMESTAMP" > "$SIGNAL_FILE"

echo "✅ Restart signal created at $SIGNAL_FILE"
echo "   Variations container will detect this and restart"

exit 0
