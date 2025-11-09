#!/bin/bash
# Quick start script for Docker-based compiler services

set -e

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

cd "$REPO_ROOT"

echo "🐳 Docker Compiler Quick Start"
echo "==============================="
echo ""
echo "📍 Repository root: $REPO_ROOT"
echo ""

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker and try again."
    exit 1
fi

echo "✅ Docker is running"
echo ""

# Parse command
COMMAND=${1:-up}

case "$COMMAND" in
    up|start)
        echo "🚀 Starting services..."
        docker compose -f compiler/docker-compose.yml up --build
        ;;
    
    down|stop)
        echo "🛑 Stopping services..."
        docker compose -f compiler/docker-compose.yml down
        ;;
    
    restart)
        echo "🔄 Restarting services..."
        docker compose -f compiler/docker-compose.yml down
        docker compose -f compiler/docker-compose.yml up --build
        ;;
    
    logs)
        SERVICE=${2:-}
        if [ -z "$SERVICE" ]; then
            docker compose -f compiler/docker-compose.yml logs -f
        else
            docker compose -f compiler/docker-compose.yml logs -f "$SERVICE"
        fi
        ;;
    
    clean)
        echo "🧹 Cleaning up containers, volumes, and images..."
        docker compose -f compiler/docker-compose.yml down -v
        docker rmi mbzuai-hackathon-dreamteam-compiler-api 2>/dev/null || true
        docker rmi mbzuai-hackathon-dreamteam-compiler-variations 2>/dev/null || true
        echo "✅ Cleanup complete"
        ;;
    
    test)
        echo "🧪 Testing template generation..."
        echo ""
        echo "Waiting for API server to be ready..."
        sleep 5
        
        echo "Generating product template..."
        curl -X POST http://localhost:8000/generate-template-variations \
          -H "Content-Type: application/json" \
          -d '{
            "template_type": "product",
            "variables": {
              "productName": "iPhone 16 Pro",
              "tagline": "Titanium. So Pro.",
              "heroImage": "https://images.unsplash.com/photo-1695048133142-1a20484d2569?w=1920",
              "features": [
                {"title": "A18 Pro Chip", "description": "Blazing fast performance"},
                {"title": "Pro Camera", "description": "48MP with 10x zoom"}
              ],
              "specs": [
                {"label": "Display", "value": "6.3\" Super Retina XDR"},
                {"label": "Chip", "value": "A18 Pro"}
              ],
              "galleryImages": ["https://images.unsplash.com/photo-1695048133142-1a20484d2569?w=800"]
            }
          }'
        
        echo ""
        echo ""
        echo "✅ Template generated! View at:"
        echo "   http://localhost:5173 (Professional)"
        echo "   http://localhost:5174 (Dark)"
        echo "   http://localhost:5175 (Minimal)"
        echo "   http://localhost:5176 (Energetic)"
        ;;
    
    select)
        INDEX=${2:-0}
        echo "🎯 Selecting variation $INDEX as active..."
        curl -X POST http://localhost:8000/select-template-variation \
          -H "Content-Type: application/json" \
          -d "{\"variation_index\": $INDEX}"
        
        echo ""
        echo ""
        echo "✅ Variation $INDEX selected! Edit at:"
        echo "   http://localhost:5177 ⭐"
        ;;
    
    status)
        echo "📊 Service Status:"
        echo ""
        docker compose -f compiler/docker-compose.yml ps
        echo ""
        echo "🌐 URLs:"
        echo "   API Server:  http://localhost:8000"
        echo "   Variation 0: http://localhost:5173"
        echo "   Variation 1: http://localhost:5174"
        echo "   Variation 2: http://localhost:5175"
        echo "   Variation 3: http://localhost:5176"
        echo "   Active:      http://localhost:5177 ⭐"
        ;;
    
    help|*)
        echo "Usage: $0 [command] [options]"
        echo ""
        echo "Commands:"
        echo "  up, start        Start all services (default)"
        echo "  down, stop       Stop all services"
        echo "  restart          Restart all services"
        echo "  logs [service]   Show logs (optional: compiler-api or compiler-variations)"
        echo "  clean            Remove all containers, volumes, and images"
        echo "  test             Generate a test template"
        echo "  select [0-3]     Select a variation as active (default: 0)"
        echo "  status           Show service status and URLs"
        echo "  help             Show this help message"
        echo ""
        echo "Examples:"
        echo "  $0                    # Start services"
        echo "  $0 up                 # Start services"
        echo "  $0 logs               # View all logs"
        echo "  $0 logs compiler-api  # View API server logs"
        echo "  $0 test               # Generate test template"
        echo "  $0 select 1           # Select variation 1"
        echo "  $0 status             # Check status"
        echo "  $0 clean              # Clean everything"
        ;;
esac
