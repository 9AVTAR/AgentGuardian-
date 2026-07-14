from agentguardian.engine import PolicyEngine

engine = PolicyEngine(prefer_opa=False)  # force built-in engine for deterministic tests


def test_research_cannot_email():
    d = engine.check("research-agent", "send_email", {"recipient_domain": "x.com"})
    assert d["allow"] is False


def test_sales_can_email():
    d = engine.check("sales-agent", "send_email", {"recipient_domain": "acme.com"})
    assert d["allow"] is True


def test_competitor_blocked():
    d = engine.check("sales-agent", "send_email", {"recipient_domain": "competitor.com"})
    assert d["allow"] is False


def test_cost_needs_approval():
    d = engine.check("sales-agent", "create_lead", {"cost_usd": 500})
    assert d["require_approval"] is True


def test_latency_is_fast():
    d = engine.check("research-agent", "web_search", {})
    assert d["latency_ms"] < 5.0
