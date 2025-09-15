#!/usr/bin/env bash
set -euo pipefail

echo "==> Creating venv (if missing)"
if [ ! -d "venv" ]; then
  python3 -m venv venv
fi
source venv/bin/activate

echo "==> Installing Python deps"
pip install -r requirements.txt

echo "==> Starting Weaviate via Docker Compose"
docker compose -f weaviate/docker-compose.yml up -d

echo "==> Waiting for Weaviate readiness"
for i in {1..30}; do
  if curl -sSf http://localhost:8080/v1/.well-known/ready >/dev/null; then
    echo "Weaviate is ready"; break
  fi
  echo "...not ready yet ($i)"; sleep 1
done

echo "==> Populating documents into Weaviate"
python weaviate/populate_weaviate_store.py || true

echo "==> Starting API server (http://localhost:8000)"
python api_server.py

