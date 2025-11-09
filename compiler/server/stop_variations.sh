#!/bin/bash
# Stop all template variation servers

if [ -f /tmp/template-servers.pids ]; then
    echo "🛑 Stopping template variation servers..."
    while read pid; do
        if ps -p $pid > /dev/null 2>&1; then
            echo "  Killing process $pid"
            kill $pid 2>/dev/null
        fi
    done < /tmp/template-servers.pids
    rm /tmp/template-servers.pids
    echo "✅ All servers stopped"
else
    echo "⚠️  No running servers found (no PID file)"
fi

# Clean up log files
if ls /tmp/variation-*.log /tmp/active.log > /dev/null 2>&1; then
    echo "🗑️  Cleaning up log files..."
    rm -f /tmp/variation-*.log /tmp/active.log
fi

echo "✨ Done!"
