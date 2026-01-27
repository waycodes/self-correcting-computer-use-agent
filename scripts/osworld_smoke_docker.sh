#!/usr/bin/env bash
# OSWorld Docker smoke test - fallback when VMware/VirtualBox unavailable
set -euo pipefail

echo "🐳 OSWorld Docker Smoke Test"
echo "============================"

# Check Docker
if ! command -v docker &> /dev/null; then
    echo "❌ Docker not found. Install Docker first."
    exit 1
fi

if ! docker info &> /dev/null; then
    echo "❌ Docker daemon not running."
    exit 1
fi

echo "✓ Docker available"

# Pull image if needed
IMAGE="xlangai/osworld:latest"
if ! docker image inspect "$IMAGE" &> /dev/null; then
    echo "📥 Pulling OSWorld image..."
    docker pull "$IMAGE"
fi

echo "✓ OSWorld image available"

# Run smoke test
echo "🧪 Running smoke test..."
docker run --rm \
    -e HEADLESS=1 \
    "$IMAGE" \
    python -c "from desktop_env import DesktopEnv; print('✓ OSWorld imports OK')"

echo ""
echo "✅ Docker smoke test passed!"
echo "   You can run OSWorld tasks using Docker."
