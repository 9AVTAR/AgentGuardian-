"""
LangGraph / LangChain integration via a BaseCallbackHandler.
Blocks disallowed tool calls before they execute.
"""
from integrations.guard import Guard

try:
    from langchain_core.callbacks import BaseCallbackHandler
except ImportError:
    BaseCallbackHandler = object


class GuardianCallback(BaseCallbackHandler):
    def __init__(self, agent):
        self.guard = Guard(agent)

    def on_tool_start(self, serialized, input_str, **kwargs):
        tool = serialized.get("name", "unknown")
        decision = self.guard.check(tool, {"input": input_str})
        if not decision["allow"]:
            raise PermissionError(f"[AgentGuardian] blocked tool '{tool}': {decision['reason']}")
