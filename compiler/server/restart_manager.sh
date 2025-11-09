#!/bin/bash
# Template Selection Fix - Restart Manager
# This script runs in the Docker container and manages the active project server
# It watches for .needs-install marker and restarts Vite with fresh dependencies

ACTIVE_DIR="/tmp/active"
LOG_FILE="/tmp/active-server.log"
PID_FILE="/tmp/active-server.pid"

echo "🚀 Template Selection Restart Manager"
echo "======================================"

# Function to stop current server
stop_server() {
    if [ -f "$PID_FILE" ]; then
        local pid=$(cat "$PID_FILE")
        if kill -0 $pid 2>/dev/null; then
            echo "⏹️  Stopping server (PID: $pid)..."
            kill $pid 2>/dev/null
            wait $pid 2>/dev/null
        fi
        rm -f "$PID_FILE"
    fi
}

# Function to start server
start_server() {
    cd "$ACTIVE_DIR"
    
    # Check if we need to reinstall
    if [ -f ".needs-install" ]; then
        echo "📦 Installing dependencies..."
        npm install --legacy-peer-deps > /tmp/npm-install.log 2>&1
        if [ $? -eq 0 ]; then
            echo "✅ Dependencies installed"
            rm -f ".needs-install"
        else
            echo "❌ npm install failed, check /tmp/npm-install.log"
            tail -20 /tmp/npm-install.log
            return 1
        fi
    elif [ ! -d "node_modules" ]; then
        echo "📦 node_modules missing, installing..."
        npm install --legacy-peer-deps > /tmp/npm-install.log 2>&1
        echo "✅ Dependencies installed"
    fi
    
    # Start Vite server
    echo "🚀 Starting Vite on port 5177..."
    npx vite --host 0.0.0.0 --port 5177 --strictPort > "$LOG_FILE" 2>&1 &
    local pid=$!
    echo $pid > "$PID_FILE"
    echo "✅ Server started (PID: $pid)"
    echo "   URL: http://localhost:5177"
    echo "   Logs: $LOG_FILE"
}

# Wait for package.json
echo "⏳ Waiting for active project..."
while [ ! -f "$ACTIVE_DIR/package.json" ]; do
    sleep 2
done
echo "✅ Active project detected"

# Start initial server
start_server

# Watch for changes
echo ""
echo "👀 Watching for template selection changes..."
echo "   (Looking for .needs-install marker)"
echo ""

while true; do
    sleep 2
    
    # Check if server is still running
    if [ -f "$PID_FILE" ]; then
        pid=$(cat "$PID_FILE")
        if ! kill -0 $pid 2>/dev/null; then
            echo "⚠️  Server crashed, restarting..."
            start_server
        fi
    fi
    
    # Check for reinstall marker
    if [ -f "$ACTIVE_DIR/.needs-install" ]; then
        echo ""
        echo "🔄 Template selection changed!"
        stop_server
        start_server
        echo ""
        echo "👀 Watching for more changes..."
    fi
done
