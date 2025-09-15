# Install Checklist

- Infra
  - [ ] Host OS and SSH access confirmed
  - [ ] Open ports 80/443 (public), 3000/8000 (local only)
  - [ ] DNS points to server (A/AAAA)

- Software
  - [ ] Docker + Compose installed
  - [ ] Python 3.10+ installed
  - [ ] Node 18+ installed
  - [ ] Nginx installed with TLS certs provisioned

- App Config
  - [ ] `.env` or `/etc/rag-assistant/api.env` filled (LLM URL, model, key)
  - [ ] `ALLOWED_API_KEYS` set to long random value(s)
  - [ ] `NEXT_PUBLIC_API_BASE` set to site origin

- Data
  - [ ] `documents/` collected and approved for ingestion
  - [ ] Ingestion run and verified (Weaviate has `Document` objects)

- Validation
  - [ ] `/health` returns ok via domain
  - [ ] UI loads over HTTPS and accepts API key
  - [ ] 3–5 representative questions return correct answers

