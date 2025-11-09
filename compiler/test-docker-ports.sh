#!/bin/bash
# Test script to verify Docker port accessibility

echo "🧪 Testing Docker Port Accessibility"
echo "====================================="
echo ""

# Check if container is running
if ! docker ps | grep -q compiler-api; then
    echo "❌ Container 'compiler-api' is not running"
    echo "   Start it with: docker-compose -f compiler/docker-compose.yml up"
    exit 1
fi

echo "✅ Container is running"
echo ""

# Test from outside container
echo "📡 Testing from HOST (outside container)..."
echo "   curl http://localhost:8000/project"
if curl -s -f http://localhost:8000/project > /dev/null 2>&1; then
    echo "   ✅ SUCCESS - Port 8000 is accessible from host!"
    curl -s http://localhost:8000/project | head -20
else
    echo "   ❌ FAILED - Cannot reach port 8000 from host"
    echo ""
    echo "   Debugging information:"
    echo "   ----------------------"
    
    # Check if port is mapped
    echo ""
    echo "   Port mapping:"
    docker port compiler-api
    
    # Check what's listening inside container
    echo ""
    echo "   Processes inside container:"
    docker exec compiler-api ps aux | grep python
    
    # Check if server is bound to correct interface
    echo ""
    echo "   Network connections inside container:"
    docker exec compiler-api netstat -tuln 2>/dev/null || docker exec compiler-api ss -tuln 2>/dev/null || echo "   (netstat/ss not available)"
    
    # Test from inside container
    echo ""
    echo "   Testing from INSIDE container:"
    if docker exec compiler-api curl -s -f http://localhost:8000/project > /dev/null 2>&1; then
        echo "   ✅ Works inside container (localhost)"
        echo "   ❌ But NOT from host - this means server is bound to 127.0.0.1 instead of 0.0.0.0"
        echo ""
        echo "   Solution:"
        echo "   1. Make sure HOST=0.0.0.0 in docker-compose.yml environment"
        echo "   2. Rebuild: docker-compose -f compiler/docker-compose.yml up --build"
    else
        echo "   ❌ Doesn't work inside container either - server may not be running"
        echo ""
        echo "   Check logs:"
        echo "   docker logs compiler-api"
    fi
fi

echo ""
echo "====================================="
