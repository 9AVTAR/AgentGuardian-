from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from pathlib import Path
from .engine import PolicyEngine

app = FastAPI(title="AgentGuardian", version="1.0")
engine = PolicyEngine()


class CheckRequest(BaseModel):
    agent: str
    tool: str
    params: dict = {}


@app.post("/check")
def check(req: CheckRequest):
    return engine.check(req.agent, req.tool, req.params)


@app.get("/stats")
def stats():
    return {
        "backend": engine.backend,
        "counters": engine.audit.counters,
        "trust_scores": engine.trust.all(),
    }


@app.get("/audit")
def audit():
    return engine.audit.recent()


@app.post("/reload")
def reload():
    engine.yaml_engine.reload()
    return {"status": "reloaded"}


@app.get("/", response_class=HTMLResponse)
def dashboard():
    return Path(__file__).parent.parent.joinpath("dashboard/index.html").read_text(encoding="utf-8")