# Statement of Work (Template)

## Project
Private, on‑prem Retrieval‑Augmented Generation (RAG) Assistant over client documents.

## Scope
- Deploy FastAPI + Next.js + Weaviate on client server
- Ingest provided documents (Markdown/text; others by agreement)
- Configure LLM endpoint (Jan AI/Ollama/OpenAI-compatible)
- Light prompt/template tuning (up to 2 templates)
- Basic access gate (API key) and HTTPS reverse proxy

## Deliverables
- Running instance accessible at client domain over HTTPS
- Client README with runbooks and support contacts
- Short Loom walkthrough (~2 min)
- 30-minute handoff session

## Timeline
- Kickoff to install: 1–2 business days
- Tuning and validation: by end of day 3

## Acceptance Criteria
- `/health` returns ok via client domain
- Representative queries (agreed list) produce accurate answers
- API gating enabled; direct ports closed externally

## Assumptions
- Client provides server, DNS, and TLS (or allows Let’s Encrypt)
- Client provides LLM API access or approves a local LLM
- Client provides documents and permissions to ingest

## Out of Scope (v1)
- Enterprise SSO (OIDC/SAML), RBAC, multi-tenant
- Non-text ingestion (PDF parsing) unless specified
- Complex data connectors (Drive/Confluence/Jira) unless specified

## Pricing
- Fixed fee: $X,XXX (one-time)
- Optional support: $YYY/month (updates, ingestion help, prompt tweaks)

## Payment Terms
- 50% upfront, 50% on acceptance (Net 7)

## Change Management
- Material scope changes via written change orders with updated fees/timeline.

## Confidentiality & IP
- Client retains ownership of their data/content.
- Vendor retains ownership of core code; client receives a perpetual license to operate their deployed instance.

## Contacts
- Client PM: Name, email
- Vendor PM: Name, email

