# AgentGuardian

Runtime Policy Engine for Multi-Agent Systems.

A framework-agnostic engine that sits between agents and their tools,
evaluates every tool call against OPA/Rego policies (or a built-in
zero-dependency fallback engine), enforces sub-millisecond decisions,
and shows a live dashboard of allows/blocks and per-agent trust scores.

## Why

Agent frameworks (LangGraph, CrewAI, custom loops) let agents call tools
freely. AgentGuardian adds a policy checkpoint in front of those calls so
you can answer, in real time: *is this agent allowed to do this, under
these conditions, right now?*

## Features

- **Two interchangeable backends** — Open Policy Agent (Rego) if the
  `opa` binary is installed, or a built-in YAML rules engine with zero
  external dependencies. Same decision shape either way.
- **Per-agent trust scores** — climbs slowly on allowed actions, drops
  sharply on blocked ones.
- **Three-way decisions** — `allow`, `deny`, or `require_approval` for
  actions that need a human in the loop (e.g. spend over a limit).
- **Full audit log** — every check is recorded with latency, reason, and
  outcome.
- **Live dashboard** — allow/block/approval counters, trust bars, and a
  streaming action log, auto-refreshing every 3s.
- **Drop-in integrations** — a framework-agnostic `Guard` client/decorator,
  plus ready-made hooks for LangGraph (`BaseCallbackHandler`) and CrewAI
  (tool-wrapping decorator).

## Repo layout

```
agentguardian/
├── README.md
├── requirements.txt
├── policies/
│   ├── agent_policy.rego      # used when OPA is installed
│   └── policies.yaml          # used by the built-in engine
├── agentguardian/
│   ├── __init__.py
│   ├── engine.py               # PolicyEngine — picks backend, tracks trust + audit
│   ├── opa_backend.py          # shells out to the opa binary
│   ├── yaml_backend.py         # dependency-free rule evaluator
│   ├── trust.py                # per-agent trust scoring
│   ├── audit.py                # in-memory audit log + counters
│   └── server.py               # FastAPI app: /check /stats /audit /reload /
├── integrations/
│   ├── guard.py                 # Guard client + @protect decorator
│   ├── langgraph_hook.py        # LangChain/LangGraph callback handler
│   └── crewai_hook.py           # CrewAI tool-wrapping decorator
├── dashboard/
│   └── index.html               # live dashboard served at /
├── examples/
│   └── demo_agents.py           # simulates a fleet of agents, no LLM needed
└── tests/
    └── test_engine.py
```

## Quickstart

```bash
git clone <your-repo> && cd agentguardian
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# 1. Start the policy engine (Terminal 1) — port 8001
uvicorn agentguardian.server:app --reload --port 8001

# 2. Open the dashboard
#    http://localhost:8001

# 3. Run the agent fleet simulation (Terminal 2)
python examples/demo_agents.py

# 4. Run tests
pytest -q
```

OPA itself is optional — a single free static binary. If it isn't
installed, AgentGuardian automatically falls back to the built-in YAML
engine, so you can run everything above with zero external dependencies.

## Writing policies

Edit `policies/policies.yaml` (built-in engine) and/or
`policies/agent_policy.rego` (OPA engine) to match your agents. A rule
can allow/deny specific tools outright, or attach conditions (field
must not be in a blocklist, field must stay under a numeric max, etc.).
Conditions can be scoped to a single tool or to `"*"` (all tools).

Reload YAML policies at runtime without restarting the server:

```bash
curl -X POST http://localhost:8001/reload
```

## Using it from your agent code

```python
from integrations.guard import Guard

guard = Guard("sales-agent")
decision = guard.check("send_email", {"recipient_domain": "acme.com"})
if not decision["allow"]:
    raise PermissionError(decision["reason"])
```

Or protect a function directly:

```python
@guard.protect("send_email")
def send_email(recipient_domain, subject, body):
    ...
```

## License

MIT
