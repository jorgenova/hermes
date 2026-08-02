from contextlib import asynccontextmanager
from typing import AsyncIterator

import httpx
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from config import settings
from database import engine, Base

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield


app = FastAPI(
    title="Hermes AI",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    reply: str
    model: str

@app.get("/health")
async def health():
    return {"status": "ok", "service": "hermes"}

@app.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest):
    payload = {
        "model": settings.ollama_model,
        "messages": [{"role": "user", "content": req.message}],
        "stream": False,
        "options": {
            "num_thread": settings.ollama_num_thread,
            "num_ctx": settings.ollama_num_ctx,
        },
    }

    async with httpx.AsyncClient(
        base_url=settings.ollama_base_url,
        timeout=3000
    ) as client:
        try:
            resp = await client.post("/api/chat", json=payload)
            resp.raise_for_status()
            data = resp.json()
        except httpx.HTTPStatusError as e:
            raise HTTPException(
                status_code=502,
                detail=f"Erro do Ollama ({e.response.status_code}): {e.response.text}",
            )
        except httpx.RequestError as e:
            raise HTTPException(status_code=502, detail=f"Erro ao conectar ao Ollama: {e}")

    return ChatResponse(
        reply=data.get("message", {}).get("content", ""),
        model=data.get("model", settings.ollama_model),
    )
