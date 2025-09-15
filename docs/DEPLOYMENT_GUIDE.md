# Deployment Guide

This guide covers fast demo deployment and a production‑ready single‑VM install with HTTPS, access control, and operations.

## Overview

- UI: Next.js (port 3000)
- API: FastAPI (port 8000)
- Vector DB: Weaviate (port 8080)
- Access Gate: `ALLOWED_API_KEYS` (header `X-API-Key`)

## Prerequisites

- Ubuntu 22.04+ (or similar) VM with SSH
- Docker + Docker Compose
- Python 3.10+, Node 18+ (for non‑Docker paths)
- Nginx + TLS certs for public HTTPS (Let’s Encrypt or corporate CA)

## Option A: All‑in‑one Docker (Quick Demo)

Best for demos and pilots on a single VM.

1) Optional env

```bash
cp .env.example .env
# Edit .env to set JANAI_* and ALLOWED_API_KEYS
```

2) Build and run

```bash
docker compose up -d --build
```

3) Ingest documents

Place `.md`/`.txt` in `./documents/` then:

```bash
docker compose exec api python weaviate/populate_weaviate_store.py
```

4) Open

- UI: http://YOUR_VM:3000
- API: http://YOUR_VM:8000 (check `/health`)
- Weaviate: http://YOUR_VM:8080 (demo only; do not expose in prod)

5) Set key in UI

If `ALLOWED_API_KEYS` is set, enter the key in the header input; the app will send `X-API-Key`.

Notes:
- To use a public domain with HTTPS, place Nginx in front and set `NEXT_PUBLIC_API_BASE=https://your.domain` (build arg in compose).
- For production, avoid mapping Weaviate to host; keep it internal to the Docker network.

## Option B: Single‑VM Production (systemd + Nginx)

Best for stable, private installs (client on‑prem or client cloud).

1) OS user and dirs

```bash
sudo useradd -r -m -d /opt/rag-assistant -s /bin/bash rag || true
sudo mkdir -p /opt/rag-assistant
sudo chown -R rag:rag /opt/rag-assistant
```

2) Upload release

```bash
# Build on your machine
./scripts/package-release.sh
# Copy ZIP to server, then:
sudo -u rag unzip rag-assistant-*.zip -d /opt/rag-assistant
cd /opt/rag-assistant
```

3) Python env

```bash
sudo -u rag python3 -m venv venv
sudo -u rag bash -lc 'source venv/bin/activate && pip install -r requirements.txt'
```

4) Start Weaviate

```bash
sudo docker compose -f weaviate/docker-compose.yml up -d
```

5) Ingest documents

```bash
# Place docs in /opt/rag-assistant/documents
sudo -u rag bash -lc 'source venv/bin/activate && python weaviate/populate_weaviate_store.py'
```

6) Configure environment

```bash
sudo mkdir -p /etc/rag-assistant
sudo tee /etc/rag-assistant/api.env >/dev/null <<EOF
WEAVIATE_URL=http://localhost:8080
JANAI_API_URL=https://your-llm-endpoint/v1/chat/completions
JANAI_MODEL_NAME=mistral-ins-7b-q4
JANAI_API_KEY=<your_llm_key_if_needed>
ALLOWED_API_KEYS=<long_random_client_key>
MAX_RETRIES=3
BASE_DELAY=1
EOF
```

7) Systemd services

```bash
sudo cp deploy/systemd/rag-assistant-api.service /etc/systemd/system/
sudo cp deploy/systemd/rag-assistant-web.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now rag-assistant-api rag-assistant-web
```

8) Nginx reverse proxy + TLS

```bash
sudo cp deploy/nginx.conf /etc/nginx/sites-available/rag-assistant.conf
sudo sed -i 's/your.domain.com/your.real.domain/g' /etc/nginx/sites-available/rag-assistant.conf
sudo ln -sf /etc/nginx/sites-available/rag-assistant.conf /etc/nginx/sites-enabled/rag-assistant.conf
sudo nginx -t && sudo systemctl reload nginx
```

9) Test

- Open `https://your.real.domain` → paste API key → chat
- `curl -s https://your.real.domain/health` should return `{ status: ok, ... }`

10) Lock down ports

- Expose only 80/443 publicly
- Keep 3000/8000 local only; Weaviate 8080 local only (firewall/UFW/security groups)

## LLM Endpoint Options

- Jan AI / OpenAI‑compatible: set `JANAI_API_URL`, `JANAI_MODEL_NAME`, `JANAI_API_KEY` if required
- Local LLM: point `JANAI_API_URL` to a local Jan AI/Ollama; no external calls leave the network

## Security Hardening

- Gate: use long, random `ALLOWED_API_KEYS`; rotate periodically
- TLS: always use HTTPS for public access (Nginx + Let’s Encrypt)
- Proxy auth: add Nginx Basic Auth or IP allowlist as needed
- Rate limiting: enable Nginx `limit_req` for `/chat`
- Weaviate: do not expose 8080 to the internet; keep internal

## Operations

- Restart: `sudo systemctl restart rag-assistant-api rag-assistant-web`
- Logs: `journalctl -u rag-assistant-api -f`, `journalctl -u rag-assistant-web -f`
- Health: GET `/health` via domain; set up a simple monitor
- Ingest: add files to `documents/` and run `python weaviate/populate_weaviate_store.py`
- Backups: Docker volumes for Weaviate, `/opt/rag-assistant/conversations.db`, `/etc/rag-assistant/api.env`

## Upgrades

- Build release: `./scripts/package-release.sh`
- Replace code: unzip over `/opt/rag-assistant`
- Update deps: `pip install -r requirements.txt`
- Rebuild UI (if serving prod build): `cd web && npm ci && npm run build`
- Restart services
- Rollback: keep prior ZIP to restore

## Multi‑Client Installs

- Separate paths: `/opt/rag-assistant-CLIENTX`
- Separate env: `/etc/rag-assistant/CLIENTX.env` with unique `ALLOWED_API_KEYS`
- Duplicate systemd units per client (e.g., `rag-assistant-api-clientx.service`)

## Troubleshooting

- Weaviate 422: run `python weaviate/populate_weaviate_store.py` to create schema
- Connection refused: ensure Docker is running and ports are open locally
- 401 from API: missing or wrong `X-API-Key`; set `ALLOWED_API_KEYS` and pass the header
- TLS errors: confirm Nginx cert paths; run `nginx -t`

