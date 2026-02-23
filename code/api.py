import os
import uuid
from typing import Optional
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from llama import (
    DATASET_LABELS,
    agent,
    load_graph,
    set_active_dataset,
)

@asynccontextmanager
async def lifespan(app: FastAPI):
    choice_raw = os.getenv("FLIGHT_DATASET_CHOICE", "1")
    try:
        choice = int(choice_raw)
    except ValueError:
        raise RuntimeError("FLIGHT_DATASET_CHOICE must be an integer between 1 and 10.")

    if choice < 1 or choice > 10:
        raise RuntimeError("FLIGHT_DATASET_CHOICE must be between 1 and 10.")

    _set_and_load_dataset(choice)

app = FastAPI(lifespan=lifespan)

# User input structure with id -> for short term memory
class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1)
    session_id: Optional[str] = None

# Agent response
class ChatResponse(BaseModel):
    reply: str
    session_id: str


class DatasetRequest(BaseModel):
    choice: int = Field(..., ge=1, le=10)


class DatasetResponse(BaseModel):
    choice: int
    label: str
    filename: str


_active_dataset_choice = 1


def _set_and_load_dataset(choice: int) -> DatasetResponse:
    global _active_dataset_choice

    selected_path = set_active_dataset(choice)
    load_graph()
    _active_dataset_choice = choice

    return DatasetResponse(
        choice=choice,
        label=DATASET_LABELS[choice],
        filename=selected_path.name,
    )


@app.get("/api/health")
def health() -> dict:
    return {"status": "ok"}


@app.get("/api/datasets")
def list_datasets() -> dict:
    return {
        "active_choice": _active_dataset_choice,
        "datasets": [
            {"choice": choice, "label": label}
            for choice, label in DATASET_LABELS.items()
        ],
    }


@app.post("/api/dataset", response_model=DatasetResponse)
def set_dataset(request: DatasetRequest) -> DatasetResponse:
    try:
        return _set_and_load_dataset(request.choice)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.post("/api/chat", response_model=ChatResponse)
def chat(request: ChatRequest) -> ChatResponse:
    message = request.message.strip()
    if not message:
        raise HTTPException(status_code=400, detail="message cannot be empty")

    session_id = request.session_id or str(uuid.uuid4())
    config = {"configurable": {"thread_id": session_id}}

    try:
        response = agent.invoke(
            {"messages": [{"role": "user", "content": message}]},
            config,
        )
        last_message = response["messages"][-1]
        reply = str(last_message.content)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Agent error: {exc}") from exc

    return ChatResponse(reply=reply, session_id=session_id)
