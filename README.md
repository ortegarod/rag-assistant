# RAG Assistant

A simple Retrieval-Augmented Generation (RAG) CLI assistant that retrieves context from Weaviate and generates responses via an OpenAI-compatible chat completions API (e.g., Jan AI, Ollama, or OpenAI-compatible gateways).

## Overview

- Interactive CLI in `main.py` that orchestrates the RAG workflow
- Retrieves relevant documents from Weaviate via BM25
- Builds a prompt from template + conversation history + retrieved context
- Sends the prompt to a chat completions API and prints the response
- Persists conversation history in SQLite for continuity across runs

## Architecture

- `main.py` (CLI): Reads user input, calls `RAGPipeline.process_query()`, supports `clear history` and `quit`.
- `RAG_pipeline.py` (Core):
  - Retrieval: `WeaviateRetriever` (BM25)
  - Prompting: `get_prompt()` from `prompt_templates.py`
  - Token control: rough token estimation and history summarization/truncation
  - LLM call: `JanAIPromptNode` (async, retries, exponential backoff)
  - History: works with `ConversationManager` (SQLite)
- `document_retriever.py`: Queries Weaviate class `Document(content:text, source:string)`.
- `jan_ai_service.py`: Async client for `/v1/chat/completions` API, returns `choices[0].message.content`.
- `conversation_manager.py`: SQLite DB (`conversations.db`) with recent messages, clear/prune utilities.
- `prompt_templates.py`: Default prompt template and renderer.
- `tokenizer.py`: Simple token estimator (`len(text)//4`).
- `weaviate/`: `docker-compose.yml` and `populate_weaviate_store.py` to create schema and upsert files from `documents/`.

## Quick Start

1) Python env and deps

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

2) Start Weaviate (local)

```bash
# Requires Docker Desktop running
docker compose -f weaviate/docker-compose.yml up -d
# Check readiness
curl http://localhost:8080/v1/.well-known/ready
```

3) Populate documents

- Create a `documents/` folder at the repo root and drop `.txt` or `.md` files in it.
- Run the ingestion script:

```bash
python weaviate/populate_weaviate_store.py
```

This creates the `Document` schema (if missing) and upserts files by filename (`source`).

4) Start an LLM endpoint

- Default: `JANAI_API_URL=http://localhost:1337/v1/chat/completions`, `JANAI_MODEL_NAME=mistral-ins-7b-q4`
- If your server requires an API token (e.g., Jan AI), export it as `JANAI_API_KEY`. The client will send `Authorization: Bearer $JANAI_API_KEY`.
- Example (Ollama):

```bash
export JANAI_API_URL=http://localhost:11434/v1/chat/completions
export JANAI_MODEL_NAME=llama3.1
# Example for Jan AI on 127.0.0.1 with API key
export JANAI_API_URL=http://127.0.0.1:1337/v1/chat/completions
export JANAI_MODEL_NAME=mistral-ins-7b-q4
export JANAI_API_KEY=YOUR_TOKEN_HERE
```

5) Run the assistant

```bash
python main.py
```

Type your question, or use:
- `clear history` – clears SQLite conversation history
- `quit` – exits the CLI

## Web UI (Next.js)

A minimal Next.js frontend is included in `web/` that connects to the FastAPI backend.

1) Start the Python API

```bash
# In one terminal
pip install -r requirements.txt
python api_server.py  # serves on http://localhost:8000
```

2) Start the Next.js dev server

```bash
# In another terminal
cd web
npm install  # or: pnpm i / yarn
npm run dev  # http://localhost:3000
```

3) Use the chat UI at http://localhost:3000. It calls `POST /chat` on the Python API and `POST /clear` to clear history.

If your API runs on a different host/port, set `NEXT_PUBLIC_API_BASE` in `web/.env.local` (e.g., `http://127.0.0.1:8000`).

## Configuration

Configure via environment variables (see `config.py`):

- `WEAVIATE_URL` (default `http://localhost:8080`)
- `JANAI_API_URL` (default `http://localhost:1337/v1/chat/completions`)
- `JANAI_MODEL_NAME` (default `mistral-ins-7b-q4`)
- `JANAI_MAX_TOKENS` (default `1024`) – output tokens cap; large values can cause 400s
- `MAX_RETRIES` (default `3`)
- `BASE_DELAY` (default `1` second)
- `ALLOWED_API_KEYS` (optional, comma-separated) – if set, API requires header `X-API-Key` to match one of the values; if empty, auth is disabled

Logging outputs to `logs/app.log` (rotating file) and console; set level in `logging_config.setup_logging()`.

### .env Support

The app automatically loads a `.env` file from the project root. You can copy `.env.example` to `.env` and edit values:

```bash
cp .env.example .env
# edit .env
```

If `ALLOWED_API_KEYS` is set, the web UI has an input to store and send the `X-API-Key` header automatically.

## Docker Demo (All-in-one)

Spin up Weaviate, API, and Web with one command on a single VM.

1) Optional: set env variables

```bash
cp .env.example .env
# Edit .env to set JANAI_* and a demo ALLOWED_API_KEYS
```

2) Build and run

```bash
docker compose up -d --build
```

3) Ingest documents

Place `.md`/`.txt` files in `./documents/`, then:

```bash
docker compose exec api python weaviate/populate_weaviate_store.py
```

4) Open the UI

- Web: http://localhost:3000
- API: http://localhost:8000 (`/health` for a quick check)
- Weaviate: http://localhost:8080 (do not expose publicly in prod)

If `ALLOWED_API_KEYS` is set, enter the key in the UI once; it is stored locally and sent as `X-API-Key`.

## Data & Token Limits

- Conversation history is stored in `conversations.db` (SQLite). `ConversationManager` fetches the most recent messages and supports pruning old entries.
- Token budgeting is approximate via `tokenizer.py`. When prompts are too long, the pipeline truncates context and summarizes older history chunks to fit within `max_tokens` (default `32000`).

## Troubleshooting

- Weaviate 422: `no graphql provider present` – You don’t have a schema yet.
  - Run `python weaviate/populate_weaviate_store.py` to create `Document` schema.
- Cannot connect to Weaviate: ensure Docker is running and `docker ps` shows the container; check `WEAVIATE_URL`.
- LLM connection refused: start your API server or point `JANAI_API_URL` to a reachable endpoint; verify with `curl`.
- `NotOpenSSLWarning` on macOS: safe for localhost; consider a newer Python if using HTTPS endpoints with TLS.

## Notes & Future Improvements

- Weaviate client pinned to v3 (`weaviate-client>=3.26.7,<4.0.0`) to match current code.
- History summarization is async and uses the same LLM endpoint.
- Potential enhancements:
  - Weaviate v4 client migration
  - Real tokenizer integration (e.g., tiktoken) for accurate budgeting
  - Optional API key/bearer auth for `JANAI_API_URL`
  - Streaming responses from the LLM
  - More templates and template switching in the CLI

## Productized Setup Playbook

- Scope: Private, on‑prem RAG chat over your docs. Includes install, ingest, and light prompt tuning.
- Deploy: FastAPI on port 8000, Next.js on 3000, Weaviate via Docker (compose in `weaviate/`).
- Security: Set `ALLOWED_API_KEYS` in `.env` and provide the key to users (the web UI sends `X-API-Key`).
- Handoff: Provide a README tailored to the client’s infra and a short Loom showing usage.

## Deployment Templates

- `deploy/nginx.conf`: Reverse proxy with HTTPS, optional Basic Auth, and routing to UI (3000) and API (8000).
- `deploy/systemd/rag-assistant-api.service`: Systemd unit for FastAPI backend.
- `deploy/systemd/rag-assistant-web.service`: Systemd unit for Next.js app (`npm run start`).
- `docs/CLIENT_README_TEMPLATE.md`: Client-facing runbook for install, ops, and support.
- `docs/INSTALL_CHECKLIST.md`: Preflight checks to speed up installs.
- `docs/DEMO_SCRIPT.md`: 2‑minute demo flow for sales calls.
- `docs/SOW_TEMPLATE.md`: Statement of Work template for pilots.
- `docs/DEPLOYMENT_GUIDE.md`: Step‑by‑step guide for demo and production installs.

## Packaging

- `scripts/package-release.sh` builds a clean ZIP in `dist/` excluding dev artifacts.
  - Usage: `./scripts/package-release.sh` or `./scripts/package-release.sh 2024-09-15`


## File Map

- `main.py` – CLI entry point
- `RAG_pipeline.py` – Orchestrates retrieval, prompting, token control, LLM calls
- `document_retriever.py` – Weaviate BM25 retriever
- `jan_ai_service.py` – Async chat completions client with retries
- `prompt_templates.py` – Prompt templates and renderer
- `tokenizer.py` – Token estimation utilities
- `conversation_manager.py` – SQLite persistence for conversation history
- `logging_config.py` – Rotating file + console logging
- `config.py` – Environment-based configuration
- `weaviate/docker-compose.yml` – Local Weaviate
- `weaviate/populate_weaviate_store.py` – Create schema + ingest files from `documents/`
- `requirements.txt` – Dependencies
