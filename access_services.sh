#!/bin/bash

# Get WSL IP address
WSL_IP=$(hostname -I | awk '{print $1}')
LOCALHOST="127.0.0.1"

# Print header
echo "======================================================="
echo "NebulaML Platform Service Access Information"
echo "======================================================="
echo

# Function to check if service is accessible
check_service() {
    local url=$1
    local name=$2
    
    if curl -s --head --connect-timeout 2 "$url" > /dev/null; then
        echo "✅ $name is ACCESSIBLE at: $url"
    else
        echo "❌ $name is NOT accessible at: $url"
    fi
}

# Test and display service URLs
echo "From WSL (these should always work):"
echo "-----------------------------------"
check_service "http://$LOCALHOST:8001/health" "API"
check_service "http://$LOCALHOST:9000" "Portainer"
check_service "http://$LOCALHOST:3001" "Grafana"
check_service "http://$LOCALHOST:9090" "Prometheus"
check_service "http://$LOCALHOST:16686" "Jaeger"
echo

echo "From Windows (try these URLs in your browser):"
echo "---------------------------------------------"
echo "API:        http://$WSL_IP:8001/health"
echo "API Docs:   http://$WSL_IP:8001/docs"
echo "Portainer:  http://$WSL_IP:9000"
echo "Grafana:    http://$WSL_IP:3001 (admin/admin)"
echo "Prometheus: http://$WSL_IP:9090"
echo "Jaeger:     http://$WSL_IP:16686"
echo

echo "======================================================="
echo "If Windows access doesn't work, try the following:"
echo "1. Open your browser to 'localhost:8001/health'"
echo "2. Try '127.0.0.1:8001/health'"
echo "3. If still not working, you might need WSL port proxying"
echo "=======================================================" 