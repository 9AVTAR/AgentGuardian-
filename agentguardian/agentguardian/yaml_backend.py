import yaml
from pathlib import Path


class YamlPolicyEngine:
    """Zero-dependency policy engine. No OPA required."""

    def __init__(self, path="policies/policies.yaml"):
        self.path = Path(path)
        self.reload()

    def reload(self):
        self.policy = yaml.safe_load(self.path.read_text())

    def _matching_rules(self, agent):
        for rule in self.policy.get("rules", []):
            if rule["agent"] == agent or rule["agent"] == "*":
                yield rule

    def evaluate(self, agent, tool, params):
        params = params or {}
        default = self.policy.get("default", "deny")
        allowed = None
        require_approval = False
        reason = "no matching rule"

        for rule in self._matching_rules(agent):
            if tool in rule.get("deny_tools", []):
                return {"allow": False, "reason": f"tool '{tool}' explicitly denied",
                        "require_approval": False}

            if "allow_tools" in rule and tool in rule["allow_tools"]:
                allowed = True
                reason = f"tool '{tool}' allowed for {agent}"

            for cond in rule.get("conditions", []):
                if cond["tool"] in (tool, "*"):
                    req = cond["require"]
                    field = req["field"]
                    val = params.get(field)

                    if "max" in req and val is not None and val > req["max"]:
                        if cond.get("on_violation") == "require_approval":
                            require_approval = True
                            reason = f"{field}={val} exceeds max {req['max']} → needs approval"
                        else:
                            return {"allow": False,
                                    "reason": f"{field}={val} exceeds max {req['max']}",
                                    "require_approval": False}

                    if "not_in" in req and val in req["not_in"]:
                        return {"allow": False,
                                "reason": f"{field}={val} is blocklisted",
                                "require_approval": False}

        if allowed is None:
            allowed = default == "allow"
        if require_approval:
            return {"allow": False, "reason": reason, "require_approval": True}
        return {"allow": allowed, "reason": reason, "require_approval": False}
