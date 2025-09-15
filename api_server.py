import logging
from typing import Optional

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import asyncio

from RAG_pipeline import RAGPipeline
from config import Config

logger = logging.getLogger(__name__)


class ChatRequest(BaseModel):
    query: str
    template: Optional[str] = "default"


class ChatResponse(BaseModel):
    answer: str


def create_app() -> FastAPI:
    app = FastAPI(title="RAG Assistant API", version="0.1.0")

    # Allow Next.js dev server and common localhost variants
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "http://localhost:3000",
            "http://127.0.0.1:3000",
            "http://0.0.0.0:3000",
        ],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    rag = RAGPipeline()

    @app.on_event("startup")
    def startup_event():
        # Initialize logging here too just in case API runs standalone
        try:
            rag.initialize()
            logger.info("RAG pipeline initialized for API server")
        except Exception as e:
            logger.exception(f"Failed to initialize RAG pipeline: {e}")

    @app.get("/health")
    def health():
        # Minimal health signal; deeper checks could be added
        return {"status": "ok", "weaviate_url": Config.WEAVIATE_URL, "model": Config.JANAI_MODEL_NAME}

    @app.post("/chat", response_model=ChatResponse)
    async def chat(req: ChatRequest):
        answer = await rag.process_query(req.query, req.template)
        return ChatResponse(answer=answer)

    @app.post("/clear")
    def clear():
        rag.conversation_manager.clear_history()
        return {"status": "cleared"}

    return app


app = create_app()

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "api_server:app",
        host="0.0.0.0",
        port=8000,
        reload=False,
    )

