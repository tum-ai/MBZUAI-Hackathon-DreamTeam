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
COPY compiler/docker-ref/start.sh /app/start.sh

# Make scripts executable
RUN chmod a+x /app/compiler/server/run_server.py \
    && chmod a+x /app/compiler/server/run_variations.sh \
    && chmod a+x /app/compiler/server/stop_variations.sh \
    && chmod a+x /app/compiler/server/active_server_controller.sh \
    && chmod a+x /app/compiler/server/trigger_restart.sh

# Create shared volume directories
RUN mkdir -p /tmp/selection/0 /tmp/selection/1 /tmp/selection/2 /tmp/selection/3 \
    && mkdir -p /tmp/active

# Expose all necessary ports
# 8000: API server
# 5173-5176: Preview variations
# 5177: Active project
EXPOSE 8000 5173 5174 5175 5176 5177

# Create startup script that runs both services
RUN chmod +x /app/start.sh

# Set the startup command
CMD ["/app/start.sh"]
