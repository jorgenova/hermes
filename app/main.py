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
		"prompt": req.message,
		"stream": False,
	}

	async with httpx.AsyncClient(
		base_url=settings.ollama_base_url,
		timeout=3000
	) as client:
		try:
			resp = await client.post("/api/generate", json=payload)
			resp.raise_for_status()
			data = resp.json()
		except httpx.HTTPError as e:
			raise HTTPException(status_code=502, detail=f"Erro ao chamar Ollama: {e}")

	return ChatResponse(
		reply=data.get("response", ""),
		model=data.get("model", settings.ollama_model),
	)
