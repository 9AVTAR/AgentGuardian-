"""
CrewAI integration: wrap a tool's callable with a Guard.protect decorator.
Works with any @tool-decorated function.
"""
from integrations.guard import Guard


def guard_tool(agent, tool_name):
    g = Guard(agent)
    def deco(fn):
        def wrapper(*args, **kwargs):
            decision = g.check(tool_name, kwargs)
            if not decision["allow"]:
                return f"ACTION BLOCKED by AgentGuardian: {decision['reason']}"
            return fn(*args, **kwargs)
        return wrapper
    return deco
