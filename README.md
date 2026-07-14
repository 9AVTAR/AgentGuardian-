AgentGuardian
Runtime Policy Engine for Multi-Agent Systems
AgentGuardian is an enterprise-grade, framework-agnostic policy enforcement layer that sits between autonomous AI agents and their tool execution environment. It evaluates every tool call against declarative OPA/Rego policies (or a built-in zero-dependency fallback engine), enforcing sub-millisecond authorization decisions with full auditability and per-agent trust scoring.
Whether you're orchestrating a fleet of LangGraph agents, CrewAI crews, or custom agentic runtimes, AgentGuardian ensures every action is governed, auditable, and accountable — without adding latency to your critical path.
🚀 Key Features
Table
Feature	Description
Dual-Mode Policy Engine	Open Policy Agent (Rego) when the opa binary is present; seamless fallback to a built-in YAML rules engine with zero external dependencies. Identical decision shape across both backends.
Sub-Millisecond Enforcement	Policy decisions are evaluated in under 5ms. No network hops, no heavy inference — just fast, deterministic authorization at the edge of your agent loop.
Three-Way Decision Model	Every tool call resolves to Allow, Deny, or Require Approval — enabling human-in-the-loop governance for high-stakes actions (e.g., spend over a threshold).
Per-Agent Trust Scoring	Trust scores start at 1.0, recover slowly on compliant behavior, and drop sharply on violations. Surface risk posture per agent in real time.
Immutable Audit Ledger	Every check is recorded with timestamp, latency, reason, outcome, and trust delta. Query via REST or stream into your SIEM.
Live Operations Dashboard	Dark-mode dashboard served at / — auto-refreshing counters, trust-score bars, and a streaming action log. Zero frontend build step required.
Drop-In Framework Integrations	Framework-agnostic Guard client + @protect decorator, plus ready-made hooks for LangGraph (BaseCallbackHandler) and CrewAI (tool-wrapping decorator).
📐 System Architecture
AgentGuardian acts as a cryptographic policy checkpoint between your agentic reasoning loop and the execution environment:
plain
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│   Agent Loop    │────▶│  AgentGuardian   │────▶│  Tool Execution │
│ (LangGraph/etc) │     │  Policy Engine   │     │   Environment   │
└─────────────────┘     └──────────────────┘     └─────────────────┘
                               │
                               ▼
                        ┌──────────────────┐
                        │  Audit Ledger    │
                        │  + Trust Scores  │
                        └──────────────────┘
📁 Directory Structure
plain
agentguardian/
├── README.md
├── requirements.txt
├── policies/
│   ├── agent_policy.rego      # OPA/Rego policy definitions
│   └── policies.yaml          # Built-in YAML rule definitions
├── agentguardian/
│   ├── __init__.py
│   ├── engine.py               # PolicyEngine — backend selector, trust + audit orchestration
│   ├── opa_backend.py          # OPA binary shell-out adapter
│   ├── yaml_backend.py         # Zero-dependency rule evaluator
│   ├── trust.py                # Per-agent trust scoring engine
│   ├── audit.py                # In-memory audit log with counters
│   └── server.py               # FastAPI gateway: /check /stats /audit /reload /
├── integrations/
│   ├── guard.py                 # Framework-agnostic Guard client + @protect decorator
│   ├── langgraph_hook.py        # LangChain/LangGraph BaseCallbackHandler integration
│   └── crewai_hook.py           # CrewAI tool-wrapping decorator
├── dashboard/
│   └── index.html               # Live operations dashboard (Tailwind, no build)
├── examples/
│   └── demo_agents.py           # Agent fleet simulation — no LLM required
└── tests/
    └── test_engine.py           # Deterministic backend-agnostic test suite
🛠️ Quickstart
1. Clone & Install
bash
git clone <your-repo> && cd agentguardian
python -m venv .venv && source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
2. Start the Policy Engine
bash
uvicorn agentguardian.server:app --reload --port 8001
Note: OPA is optional. If the opa binary is not on your $PATH, AgentGuardian automatically falls back to the built-in YAML engine. Zero external dependencies required.
3. Open the Dashboard
Navigate to http://localhost:8001 to view live counters, trust scores, and the action stream.
4. Simulate Agent Activity
bash
python examples/demo_agents.py
5. Run the Test Suite
bash
pytest -q
⚙️ Writing Policies
AgentGuardian supports two policy formats. Edit the files in policies/ to govern your agents:
YAML (Built-In Engine)
yaml
# policies/policies.yaml
default: deny

rules:
  - agent: research-agent
    allow_tools: [web_search, read_crm, read_file]
    deny_tools: [send_email, delete_file]

  - agent: sales-agent
    allow_tools: [read_crm, send_email, create_lead]
    conditions:
      - tool: send_email
        require:
          field: recipient_domain
          not_in: [competitor.com]

  - agent: "*"
    conditions:
      - tool: "*"
        require:
          field: cost_usd
          max: 100
        on_violation: require_approval
Rego (OPA Engine)
rego
# policies/agent_policy.rego
package agentguardian

default decision := {"allow": false, "reason": "default deny"}

decision := {"allow": true, "reason": "allowed by policy"} {
    allowed_tool
    not cost_exceeded
    not denied_tool
}

cost_exceeded {
    input.params.cost_usd > 100
}
Hot-Reload Policies
Reload YAML rules at runtime without restarting the server:
bash
curl -X POST http://localhost:8001/reload
🔌 Using It From Your Agent Code
Direct API Check
Python
from integrations.guard import Guard

guard = Guard("sales-agent")
decision = guard.check("send_email", {"recipient_domain": "acme.com"})

if not decision["allow"]:
    raise PermissionError(decision["reason"])
Decorator-Based Protection
Python
@guard.protect("send_email")
def send_email(recipient_domain, subject, body):
    ...
LangGraph Integration
Python
from integrations.langgraph_hook import GuardianCallback

# Attach to your LangGraph executor
callbacks = [GuardianCallback(agent="research-agent")]
CrewAI Integration
Python
from integrations.crewai_hook import guard_tool

@guard_tool(agent="sales-agent", tool_name="send_email")
def send_email(**kwargs):
    ...
📊 Decision Schema
Every check() call returns a uniform decision envelope:
JSON
{
  "allow": false,
  "reason": "cost_usd=250 exceeds max 100 → needs approval",
  "require_approval": true,
  "latency_ms": 0.847,
  "trust_score": 0.8
}
Table
Field	Type	Description
allow	bool	Whether the action is permitted to execute.
reason	str	Human-readable explanation of the decision.
require_approval	bool	If true, the action is blocked pending human sign-off.
latency_ms	float	Time taken to evaluate the policy (sub-millisecond typical).
trust_score	float	Current trust score of the agent (0.0–1.0).
🧪 Testing
The test suite is backend-agnostic and forces the built-in YAML engine for deterministic results:
bash
pytest tests/test_engine.py -q
Table
Test	Asserts
test_research_cannot_email	Research agents are denied email tools
test_sales_can_email	Sales agents can email non-competitor domains
test_competitor_blocked	Competitor domains are blocklisted
test_cost_needs_approval	Spend > $100 triggers approval gate
test_latency_is_fast	Evaluation completes in < 5ms
☁️ AgentGuardian Cloud & Enterprise
AgentGuardian is an open-core project. Self-host the Community Edition forever, completely free.
For teams requiring managed infrastructure, enterprise policy governance, and advanced compliance features, AgentGuardian Cloud is coming soon.
Table
Feature	Community (Open Source)	Cloud (Managed SaaS)
Hosting	Self-hosted (Python/FastAPI)	Fully Managed Cloud
Policy Engine	YAML + OPA (bring your own)	Hosted multi-tenant OPA cluster
Audit Storage	In-memory (500-entry ring buffer)	Persistent PostgreSQL + S3 archival
Dashboard	Local single-node dashboard	Hosted multi-tenant console
Trust Scoring	Per-agent in-memory scores	Cross-session persistent trust profiles
Integrations	All framework hooks	All hooks + enterprise IdP / SSO
Support	GitHub Issues	Dedicated support channel & SLA
🔔 Join the Cloud Waitlist — Coming Q3 2026
📜 License
This project is licensed under the MIT License — see the LICENSE file for details.
🤝 Contributing
Contributions are welcome. Please open an issue or submit a pull request on GitHub.
Built for agents that need guardrails, not gates.
