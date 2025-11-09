#!/bin/bash
set -e

echo "🚀 Starting Compiler Services"
echo "=============================="

# Start the API server in the background
echo "📡 Starting API Server on port 8000..."
cd /app/compiler/server
python3 run_server.py &
SERVER_PID=$!
echo "   Server PID: $SERVER_PID"

# Wait for API server to be ready
echo "⏳ Waiting for API server to start..."
for i in {1..30}; do
    if curl -s http://localhost:8000/project > /dev/null 2>&1; then
        echo "✅ API server is ready!"
        break
    fi
    if [ $i -eq 30 ]; then
        echo "❌ API server failed to start"
        exit 1
    fi
    sleep 1
done

echo ""
echo "🎯 Services Ready:"
echo "   API Server: http://localhost:8000"
echo ""
echo "💡 To generate and view variations:"
echo "   1. Generate templates via API:"
echo "      curl -X POST http://localhost:8000/generate-template-variations \\"
echo "        -H 'Content-Type: application/json' \\"
echo "        -d '{...}'"
echo ""
echo "   2. Run variations script:"
echo "      docker exec <container> /app/compiler/server/run_variations.sh"
echo ""
echo "   Or use docker-compose to auto-start both services"
echo ""

# Keep container running and show logs
echo "📋 Monitoring API server logs..."
echo "=============================="
tail -f /dev/null &
wait $SERVER_PID