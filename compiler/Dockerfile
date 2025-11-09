# Multi-stage build for the compiler service
FROM node:20-slim AS node-base

# Install Python and other dependencies
FROM node-base AS base
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    python3-venv \
    curl \
    procps \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app/compiler

# Copy Python requirements from root (build context should be repo root)
COPY requirements.txt /tmp/requirements.txt

# Install Python dependencies
RUN pip3 install --no-cache-dir -r /tmp/requirements.txt --break-system-packages

# Copy the entire compiler directory
COPY compiler/ /app/compiler/

# Make scripts executable
RUN chmod +x /app/compiler/server/run_server.py \
    && chmod +x /app/compiler/server/run_variations.sh \
    && chmod +x /app/compiler/server/stop_variations.sh

# Create shared volume directories
RUN mkdir -p /tmp/selection/0 /tmp/selection/1 /tmp/selection/2 /tmp/selection/3 \
    && mkdir -p /tmp/active

# Expose all necessary ports
# 8000: API server
# 5173-5176: Preview variations
# 5177: Active project
EXPOSE 8000 5173 5174 5175 5176 5177

# Create startup script that runs both services
RUN cat > /app/start.sh << 'EOF'
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
EOF

RUN chmod +x /app/start.sh

# Set the startup command
CMD ["/app/start.sh"]
