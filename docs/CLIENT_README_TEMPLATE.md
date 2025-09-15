# Client README – Private RAG Assistant

This document describes how to run your private, on‑prem RAG Assistant.

## Overview

- UI: Next.js on port 3000 (HTTPS via Nginx)
- API: FastAPI on port 8000 (proxied at `https://your.domain.com`)
- Vector DB: Weaviate via Docker Compose on port 8080 (local only)

## Prerequisites

- Ubuntu 22.04 LTS (or similar), SSH access
- Docker + Docker Compose
- Python 3.10+
- Node.js 18+
- Nginx with TLS certs (Let’s Encrypt or corporate CA)

## Install

1) Create `rag` user and directories

```bash
sudo useradd -r -m -d /opt/rag-assistant -s /bin/bash rag || true
sudo mkdir -p /opt/rag-assistant
sudo chown -R rag:rag /opt/rag-assistant
```

2) Copy release ZIP to server and extract

```bash
sudo -u rag unzip rag-assistant-*.zip -d /opt/rag-assistant
cd /opt/rag-assistant
```

3) Python environment and deps

```bash
sudo -u rag python3 -m venv venv
sudo -u rag bash -lc 'source venv/bin/activate && pip install -r requirements.txt'
```

4) Start Weaviate and ingest documents

```bash
sudo docker compose -f weaviate/docker-compose.yml up -d
sudo -u rag bash -lc 'source venv/bin/activate && python weaviate/populate_weaviate_store.py'
```

5) Configure environment

```bash
sudo mkdir -p /etc/rag-assistant
sudo tee /etc/rag-assistant/api.env >/dev/null <<EOF
WEAVIATE_URL=http://localhost:8080
JANAI_API_URL=https://your-llm-endpoint/v1/chat/completions
JANAI_MODEL_NAME=mistral-ins-7b-q4
JANAI_API_KEY=<your_llm_key_if_needed>
ALLOWED_API_KEYS=<long_random_client_key>
EOF
```

6) Systemd services

```bash
sudo cp deploy/systemd/rag-assistant-api.service /etc/systemd/system/
sudo cp deploy/systemd/rag-assistant-web.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now rag-assistant-api rag-assistant-web
```

7) Nginx reverse proxy

```bash
sudo cp deploy/nginx.conf /etc/nginx/sites-available/rag-assistant.conf
sudo sed -i 's/your.domain.com/your.real.domain/g' /etc/nginx/sites-available/rag-assistant.conf
sudo ln -sf /etc/nginx/sites-available/rag-assistant.conf /etc/nginx/sites-enabled/rag-assistant.conf
sudo nginx -t && sudo systemctl reload nginx
```

8) UI configuration

Set `NEXT_PUBLIC_API_BASE` in `/etc/systemd/system/rag-assistant-web.service` to your domain if needed, then:

```bash
sudo systemctl restart rag-assistant-web
```

## Usage

Open `https://your.domain.com` in your browser. Enter the API key once in the UI field. Ask questions about your ingested docs.

## Operations

- Restart services: `sudo systemctl restart rag-assistant-api rag-assistant-web`
- Logs: `journalctl -u rag-assistant-api -f`, `journalctl -u rag-assistant-web -f`
- Ingest new docs: place files in `documents/` and run `python weaviate/populate_weaviate_store.py`

## Security Notes

- Keep ports 3000/8000 closed to the public; expose only via Nginx HTTPS.
- Use long random API keys; rotate by editing `/etc/rag-assistant/api.env` and restarting API.
- Optionally enable Nginx Basic Auth and/or IP allowlisting.

