# Deploy — Operations Guide

## Architecture

```
git push main
    |
    v
GitHub Actions (.github/workflows/deploy.yml)
    |  builds 3 images in parallel
    |  pushes to ghcr.io/ku113p/...
    v
GHCR (GitHub Container Registry)
    |
    v
Watchtower (on VPS, polls every 30s)
    |  detects new image digest
    |  pulls + restarts container
    v
Live
```

After initial VPS setup, deploy is fully automatic: just `git push origin main`.

## Services

| Service | Image | Port | URL |
|---------|-------|------|-----|
| promo | `ghcr.io/ku113p/interview-promo` | 80 | https://promo.interview.syncapp.tech |
| backend | `ghcr.io/ku113p/interview-backend` | 8080 | https://api.interview.syncapp.tech |
| mcp | `ghcr.io/ku113p/interview-mcp` | 8080 | https://mcp.interview.syncapp.tech |
| watchtower | `containrrr/watchtower` | — | — |

## VPS Layout

```
/opt/services/
├── interview/          # docker-compose.yml + .env
├── watchtower/         # docker-compose.yml
└── traefik/            # reverse proxy (manages TLS)
```

## Traefik Routing

Traefik runs as a separate compose stack and handles:
- TLS termination via Let's Encrypt (`certresolver=letsencrypt`)
- Host-based routing (each service gets its own subdomain)
- Middleware: `security-headers@file`, `gzip@file`, `rate-limit-api@file`

Services join the `proxy` network and declare Traefik labels to register routes.

## How to Add a New Service

1. Add a Dockerfile in `docker/`
2. Add a job in `.github/workflows/deploy.yml` (copy an existing job, change context/file/tags)
3. Add the service to `deploy/compose/interview/docker-compose.yml` with:
   - `image: ghcr.io/ku113p/<name>:latest`
   - `com.centurylinklabs.watchtower.enable=true` label
   - Traefik labels for routing
4. Create DNS A record pointing to VPS IP
5. Deploy: `bash deploy/deploy-interview.sh` (first time) or just `git push`

## Common Operations

### View logs

```bash
ssh root@187.124.9.212

# All interview services
cd /opt/services/interview && docker compose logs -f

# Single service
docker logs -f interview-backend
docker logs -f interview-promo
docker logs -f interview-mcp

# Watchtower (see pull activity)
docker logs -f watchtower
```

### Restart a service

```bash
ssh root@187.124.9.212
cd /opt/services/interview && docker compose restart backend
```

### Rollback

Pull a previous image digest and restart:

```bash
ssh root@187.124.9.212

# Find previous digest
docker images ghcr.io/ku113p/interview-backend --digests

# Pin to specific digest in docker-compose.yml, then:
cd /opt/services/interview && docker compose up -d backend
```

Or revert the git commit and push — CI will build and deploy the old code.

### Check resource usage

```bash
ssh root@187.124.9.212
docker stats --no-stream --format "table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}"
```

### Force pull (skip Watchtower wait)

```bash
ssh root@187.124.9.212
cd /opt/services/interview && docker compose pull && docker compose up -d
```

### Manual deploy (fallback)

```bash
bash deploy/deploy-interview.sh
```

## DNS Reference

| Subdomain | Target | Purpose |
|-----------|--------|---------|
| `promo.interview.syncapp.tech` | VPS IP (A record) | Landing page |
| `api.interview.syncapp.tech` | VPS IP (A record) | Backend API |
| `mcp.interview.syncapp.tech` | VPS IP (A record) | MCP server |

## One-Time VPS Setup

```bash
# 1. Auth VPS to GHCR (need GitHub PAT with read:packages)
ssh root@187.124.9.212
echo "ghp_..." | docker login ghcr.io -u ku113p --password-stdin

# 2. Deploy watchtower
scp deploy/compose/watchtower/docker-compose.yml root@187.124.9.212:/opt/services/watchtower/
ssh root@187.124.9.212 "cd /opt/services/watchtower && docker compose up -d"

# 3. Update interview compose on VPS
bash deploy/deploy-interview.sh
```
