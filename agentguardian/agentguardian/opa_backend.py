import subprocess
import json
import shutil


class OPAPolicyEngine:
    """Uses the free open-source OPA binary if available."""

    def __init__(self, rego_path="policies/agent_policy.rego"):
        self.rego_path = rego_path
        self.available = shutil.which("opa") is not None

    def evaluate(self, agent, tool, params):
        if not self.available:
            raise RuntimeError("OPA binary not found")
        input_doc = {"agent": agent, "tool": tool, "params": params or {}}
        result = subprocess.run(
            ["opa", "eval", "-I", "-d", self.rego_path,
             "data.agentguardian.decision"],
            input=json.dumps(input_doc), capture_output=True, text=True,
        )
        if result.returncode != 0:
            raise RuntimeError(result.stderr)
        out = json.loads(result.stdout)
        return out["result"][0]["expressions"][0]["value"]
