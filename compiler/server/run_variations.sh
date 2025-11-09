#!/bin/bash
# Helper script to run all 4 template variations + active project on different ports
# This simulates what the container should do

SELECTION_DIR="/tmp/selection"
ACTIVE_DIR="/tmp/active"

echo "🚀 Starting Template Variation Servers + Active Project"
echo "========================================================="

# Function to start a variation server
start_variation() {
    local index=$1
    local port=$((5173 + index))
    local dir="$SELECTION_DIR/$index"
    
    if [ ! -d "$dir" ]; then
        echo "⚠️  Variation $index not found at $dir"
        return 1
    fi
    
    echo ""
    echo "📦 Variation $index (Port $port)"
    
    # Install dependencies if not already done
    if [ ! -d "$dir/node_modules" ]; then
        echo "   Installing dependencies..."
        (cd "$dir" && npm install > /dev/null 2>&1)
    fi
    
    # Start dev server in background
    echo "   Starting dev server on port $port..."
    (cd "$dir" && npm run dev -- --port $port > /tmp/variation-$index.log 2>&1) &
    local pid=$!
    echo "   PID: $pid"
    echo "   URL: http://localhost:$port"
    echo "   Logs: /tmp/variation-$index.log"
    
    # Store PID for cleanup
    echo $pid >> /tmp/template-servers.pids
}

# Clean up old PIDs file
rm -f /tmp/template-servers.pids

# Read palette info if available
echo ""
echo "📊 Variation Details:"
echo "  [0] Professional palette + Modern font   → http://localhost:5173"
echo "  [1] Dark palette + Tech font             → http://localhost:5174"
echo "  [2] Minimal palette + Elegant font       → http://localhost:5175"
echo "  [3] Energetic palette + Playful font     → http://localhost:5176"

# Start all 4 variations
for i in 0 1 2 3; do
    start_variation $i
done

# Start active project if it exists
if [ -d "$ACTIVE_DIR" ]; then
    echo ""
    echo "📦 Active Project (Port 5177)"
    
    if [ ! -d "$ACTIVE_DIR/node_modules" ]; then
        echo "   Installing dependencies..."
        (cd "$ACTIVE_DIR" && npm install > /dev/null 2>&1)
    fi
    
    echo "   Starting active project on port 5177..."
    (cd "$ACTIVE_DIR" && npm run dev -- --port 5177 > /tmp/active.log 2>&1) &
    local pid=$!
    echo "   PID: $pid"
    echo "   URL: http://localhost:5177"
    echo "   Logs: /tmp/active.log"
    echo $pid >> /tmp/template-servers.pids
    
    echo ""
    echo "🎯 Active project is the selected variation for editing"
else
    echo ""
    echo "ℹ️  No active project yet. Select a variation via API:"
    echo "   curl -X POST http://localhost:8000/select-template-variation -H 'Content-Type: application/json' -d '{\"variation_index\": 0}'"
fi

echo ""
echo "✅ All servers started!"
echo ""
echo "🌐 Open these URLs:"
echo "  Preview Variations:"
echo "    http://localhost:5173  (Professional)"
echo "    http://localhost:5174  (Dark)"
echo "    http://localhost:5175  (Minimal)"
echo "    http://localhost:5176  (Energetic)"
if [ -d "$ACTIVE_DIR" ]; then
    echo "  Active Project (Selected):"
    echo "    http://localhost:5177  ⭐ (Edit this one)"
fi
echo ""
echo "⏹️  To stop all servers, run:"
echo "  ./stop_variations.sh"
echo ""
echo "📝 View logs:"
echo "  tail -f /tmp/variation-*.log /tmp/active.log"
echo ""
echo "Press Ctrl+C to stop this script (servers will keep running)"

# Wait for user interrupt
trap "echo ''; echo '⏹️  Servers are still running in background'; exit 0" SIGINT SIGTERM
sleep infinity
