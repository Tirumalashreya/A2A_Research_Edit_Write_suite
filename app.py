# app.py
import uvicorn
import asyncio
from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from Orchestration_Agent.orchestrator_a2a import GoogleA2AOrchestrator
from utils.export_utils import export_to_pdf, export_to_word

import os
from typing import Optional
import types

app = FastAPI()

# ✅ Add CORS so React (localhost:3000) and Streamlit (localhost:8501) can call it
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:8501"],  # React and Streamlit
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

orchestrator = GoogleA2AOrchestrator()

@app.on_event("startup")
async def startup_event():
    await orchestrator.initialize()

class UserInput(BaseModel):
    user_input: str

class ResearchRequest(BaseModel):
    topic: str

class EditRequest(BaseModel):
    content: str

class WriteRequest(BaseModel):
    topic: str
    research: Optional[str] = None

class FullWorkflowRequest(BaseModel):
    topic: str

class StructureResearchRequest(BaseModel):
    research: str

@app.post("/process")
async def process_request(payload: UserInput):
    result = await orchestrator.process_request(payload.user_input)
    return {"result": result}

@app.post("/research")
async def research_endpoint(payload: ResearchRequest):
    result = await orchestrator._research_workflow(payload.topic)
    return {"result": result}

@app.post("/edit")
async def edit_endpoint(payload: EditRequest):
    result = await orchestrator._edit_workflow(payload.content)
    return {"result": result}

@app.post("/write")
async def write_endpoint(payload: WriteRequest):
    # If research is provided, pass it to the writer agent, else run research first
    if payload.research:
        # Simulate writing with provided research
        # (You may want to add a new orchestrator method for this in the future)
        result = await orchestrator._edit_workflow(payload.research)
    else:
        result = await orchestrator._write_with_research_workflow(payload.topic)
    return {"result": result}

@app.post("/full_workflow")
async def full_workflow_endpoint(payload: FullWorkflowRequest):
    result = await orchestrator._full_workflow(payload.topic)
    return {"result": result}

# Standalone structuring/cleaning function
async def structure_research(research: str) -> str:
    # Placeholder: just return the input for now
    return f"[Structured Research]\n{research.strip()}"

@app.post("/structure_research")
async def structure_research_endpoint(payload: StructureResearchRequest):
    result = await structure_research(payload.research)
    return {"result": result}

# Serve outputs folder for download
os.makedirs("outputs", exist_ok=True)
from fastapi.staticfiles import StaticFiles
app.mount("/outputs", StaticFiles(directory="outputs"), name="outputs")

if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
