#!/bin/bash
# Active Project Server Controller
# Manages the Vite dev server for /tmp/active with restart capability

ACTIVE_DIR="/tmp/active"
PID_FILE="/tmp/active-vite.pid"
LOG_FILE="/tmp/active-vite.log"
RESTART_SIGNAL="/tmp/active/.restart-signal"

echo "🎯 Active Project Server Controller"
echo "===================================="

# Function to stop Vite server
stop_vite() {
    if [ -f "$PID_FILE" ]; then
        local pid=$(cat "$PID_FILE")
        if ps -p $pid > /dev/null 2>&1; then
            echo "⏹️  Stopping Vite server (PID: $pid)..."
            kill -TERM $pid 2>/dev/null
            
            # Wait up to 10 seconds for graceful shutdown
            for i in {1..10}; do
                if ! ps -p $pid > /dev/null 2>&1; then
                    break
                fi
                sleep 1
            done
            
            # Force kill if still running
            if ps -p $pid > /dev/null 2>&1; then
                echo "⚠️  Force killing Vite..."
                kill -9 $pid 2>/dev/null
            fi
            
            echo "✅ Vite server stopped"
        fi
        rm -f "$PID_FILE"
    fi
}

# Function to start Vite server
start_vite() {
    cd "$ACTIVE_DIR" || exit 1
    
    echo "📦 Checking dependencies..."
    
    # Always run npm install when starting
    if [ -f "package.json" ]; then
        echo "   Running npm install..."
        npm install --legacy-peer-deps > /tmp/npm-install.log 2>&1
        if [ $? -eq 0 ]; then
            echo "   ✅ Dependencies ready"
        else
            echo "   ❌ npm install failed!"
            tail -20 /tmp/npm-install.log
            return 1
        fi
    else
        echo "   ❌ No package.json found!"
        return 1
    fi
    
    # Start Vite
    echo "🚀 Starting Vite server on port 5177..."
    npx vite --host 0.0.0.0 --port 5177 --strictPort > "$LOG_FILE" 2>&1 &
    local pid=$!
    echo $pid > "$PID_FILE"
    
    # Wait a moment and check if it started successfully
    sleep 2
    if ps -p $pid > /dev/null 2>&1; then
        echo "✅ Vite server started successfully"
        echo "   PID: $pid"
        echo "   URL: http://localhost:5177"
        echo "   Logs: $LOG_FILE"
        return 0
    else
        echo "❌ Vite server failed to start!"
        echo "   Check logs: $LOG_FILE"
        tail -20 "$LOG_FILE"
        return 1
    fi
}

# Function to restart Vite
restart_vite() {
    echo ""
    echo "🔄 RESTART TRIGGERED"
    echo "===================="
    stop_vite
    sleep 1
    start_vite
    echo "===================="
    echo ""
}

# Wait for package.json to exist
echo "⏳ Waiting for active project..."
while [ ! -f "$ACTIVE_DIR/package.json" ]; do
    sleep 2
done
echo "✅ Active project detected"

# Initial start
echo ""
start_vite
if [ $? -ne 0 ]; then
    echo "❌ Initial start failed, exiting..."
    exit 1
fi

# Watch for restart signals
echo ""
echo "👀 Watching for restart signals..."
echo "   Signal file: $RESTART_SIGNAL"
echo "   Press Ctrl+C to stop"
echo ""

LAST_SIGNAL=""
while true; do
    sleep 2
    
    # Check if Vite is still running
    if [ -f "$PID_FILE" ]; then
        pid=$(cat "$PID_FILE")
        if ! ps -p $pid > /dev/null 2>&1; then
            echo "⚠️  Vite crashed! Restarting..."
            restart_vite
            continue
        fi
    else
        echo "⚠️  PID file missing! Restarting..."
        restart_vite
        continue
    fi
    
    # Check for restart signal
    if [ -f "$RESTART_SIGNAL" ]; then
        CURRENT_SIGNAL=$(cat "$RESTART_SIGNAL" 2>/dev/null)
        if [ "$CURRENT_SIGNAL" != "$LAST_SIGNAL" ]; then
            echo "📢 Restart signal detected: $CURRENT_SIGNAL"
            LAST_SIGNAL="$CURRENT_SIGNAL"
            restart_vite
        fi
    fi
done
