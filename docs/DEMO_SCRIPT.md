# 2-Minute Demo Script

Goal: Show private, on‑prem RAG answering real questions from your docs.

1) Open the site
   - Navigate to `https://your.domain.com`.
   - Paste the API key once (saved locally).

2) Explain setup (10s)
   - “This runs on your server. Docs are stored in Weaviate locally. The LLM runs via your chosen provider (Jan AI/Ollama/OpenAI-compatible). Nothing leaves your network except the LLM call if using a cloud model.”

3) Ask a targeted question (30s)
   - Pick a well‑covered policy or runbook page.
   - Example: “What’s our PTO policy carryover?”
   - Show answer + mention sources if present in the assistant’s response.

4) Follow‑up (20s)
   - “Summarize PTO policy in 5 bullets.”
   - “What’s different for contractors?”

5) Show safety controls (20s)
   - Show `/health` response.
   - Mention API key gate, HTTPS, and that ports 3000/8000 are internal behind Nginx.

6) Close (20s)
   - “Install + ingest in 72 hours. Light tuning included. If you’re not getting accurate answers on day 3, full refund.”

