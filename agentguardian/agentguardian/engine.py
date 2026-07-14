import time
from .yaml_backend import YamlPolicyEngine
from .opa_backend import OPAPolicyEngine
from .trust import TrustScorer
from .audit import AuditLog


class PolicyEngine:
    def __init__(self, prefer_opa=True):
        self.yaml_engine = YamlPolicyEngine()
        self.opa_engine = OPAPolicyEngine()
        self.use_opa = prefer_opa and self.opa_engine.available
        self.trust = TrustScorer()
        self.audit = AuditLog()
        self.backend = "OPA" if self.use_opa else "YAML (built-in)"

    def check(self, agent, tool, params=None):
        start = time.perf_counter()
        try:
            if self.use_opa:
                decision = self.opa_engine.evaluate(agent, tool, params)
                decision.setdefault("require_approval", False)
            else:
                decision = self.yaml_engine.evaluate(agent, tool, params)
        except Exception as e:
            decision = {"allow": False, "reason": f"engine error: {e}",
                        "require_approval": False}

        latency_ms = (time.perf_counter() - start) * 1000
        effective_allow = decision["allow"] and not decision.get("require_approval")
        self.trust.record(agent, effective_allow)
        self.audit.add(agent, tool, params or {}, decision)
        decision["latency_ms"] = round(latency_ms, 3)
        decision["trust_score"] = round(self.trust.get(agent), 3)
        return decision
