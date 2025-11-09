#!/bin/bash
# Manual script to restart variation servers inside container
# Use this if the automatic startup failed

echo "🔄 Manually Starting Variation Servers"
echo "======================================="

cd /tmp/selection/0 && npm install && npm run dev -- --port 5173 --host 0.0.0.0 > /tmp/variation-0.log 2>&1 &
echo "Started variation 0 on port 5173 (PID: $!)"

cd /tmp/selection/1 && npm install && npm run dev -- --port 5174 --host 0.0.0.0 > /tmp/variation-1.log 2>&1 &
echo "Started variation 1 on port 5174 (PID: $!)"

cd /tmp/selection/2 && npm install && npm run dev -- --port 5175 --host 0.0.0.0 > /tmp/variation-2.log 2>&1 &
echo "Started variation 2 on port 5175 (PID: $!)"

cd /tmp/selection/3 && npm install && npm run dev -- --port 5176 --host 0.0.0.0 > /tmp/variation-3.log 2>&1 &
echo "Started variation 3 on port 5176 (PID: $!)"

if [ -d /tmp/active ] && [ -f /tmp/active/package.json ]; then
    cd /tmp/active && npm install && npm run dev -- --port 5177 --host 0.0.0.0 > /tmp/active.log 2>&1 &
    echo "Started active project on port 5177 (PID: $!)"
fi

echo ""
echo "✅ Servers starting in background"
echo "📝 Check logs: tail -f /tmp/variation-*.log"
