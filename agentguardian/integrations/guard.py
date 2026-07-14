import functools
import requests


class Guard:
    def __init__(self, agent, endpoint="http://localhost:8001"):
        self.agent = agent
        self.endpoint = endpoint.rstrip("/")

    def check(self, tool, params=None):
        r = requests.post(f"{self.endpoint}/check",
                          json={"agent": self.agent, "tool": tool, "params": params or {}},
                          timeout=5)
        return r.json()

    def protect(self, tool_name, extract_params=None):
        """Decorator that blocks a tool function if policy denies it."""
        def deco(fn):
            @functools.wraps(fn)
            def wrapper(*args, **kwargs):
                params = extract_params(*args, **kwargs) if extract_params else kwargs
                decision = self.check(tool_name, params)
                if not decision["allow"]:
                    raise PermissionError(
                        f"[AgentGuardian] BLOCKED '{tool_name}': {decision['reason']}"
                    )
                return fn(*args, **kwargs)
            return wrapper
        return deco
