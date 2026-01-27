# OSWorld Docker Setup

This guide covers running OSWorld in Docker containers for reproducible environments.

## Prerequisites

- Docker 24.0+
- Docker Compose v2
- 8GB+ RAM available for containers
- X11 or VNC for display (optional for headless)

## Quick Start

### 1. Install Docker

```bash
# Ubuntu
curl -fsSL https://get.docker.com | sh
sudo usermod -aG docker $USER

# macOS
brew install --cask docker
```

### 2. Pull OSWorld Image

```bash
docker pull xlangai/osworld:latest
```

### 3. Run Container

**With display (development):**
```bash
docker run -it --rm \
  -e DISPLAY=$DISPLAY \
  -v /tmp/.X11-unix:/tmp/.X11-unix \
  -v $(pwd)/outputs:/workspace/outputs \
  xlangai/osworld:latest
```

**Headless (CI/production):**
```bash
docker run -it --rm \
  -e HEADLESS=1 \
  -v $(pwd)/outputs:/workspace/outputs \
  xlangai/osworld:latest
```

## Docker Compose Setup

Create `docker-compose.yml`:

```yaml
version: "3.8"
services:
  osworld:
    image: xlangai/osworld:latest
    environment:
      - HEADLESS=1
      - DISPLAY=:99
    volumes:
      - ./outputs:/workspace/outputs
      - ./configs:/workspace/configs
    shm_size: "2gb"
    deploy:
      resources:
        limits:
          memory: 8G
```

Run:
```bash
docker compose up -d
docker compose exec osworld python -c "from desktop_env import DesktopEnv; print('OK')"
```

## VNC Access (Optional)

For visual debugging in headless mode:

```yaml
services:
  osworld:
    # ... existing config ...
    ports:
      - "5900:5900"
    environment:
      - VNC_PASSWORD=osworld
```

Connect with any VNC client to `localhost:5900`.

## GPU Support (Optional)

For GPU-accelerated rendering:

```yaml
services:
  osworld:
    # ... existing config ...
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]
```

## Troubleshooting

**Container exits immediately:**
- Check logs: `docker logs <container_id>`
- Ensure sufficient memory allocated

**Display issues:**
- Run `xhost +local:docker` on host
- Verify X11 socket is mounted

**Slow performance:**
- Increase `shm_size` for shared memory
- Use `--privileged` if needed for nested virtualization
