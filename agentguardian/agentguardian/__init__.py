"""
AgentGuardian — Runtime Policy Engine for Multi-Agent Systems.

A framework-agnostic engine that sits between agents and their tools,
evaluates each tool call against OPA/Rego policies (or a built-in YAML
fallback engine), enforces sub-ms decisions, and tracks per-agent trust
scores with a full audit log.
"""

from .engine import PolicyEngine

__version__ = "1.0.0"
__all__ = ["PolicyEngine"]
