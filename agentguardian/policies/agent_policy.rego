package agentguardian

default decision := {"allow": false, "reason": "default deny"}

# Allow if tool is in the agent's allowlist and no condition fails
decision := {"allow": true, "reason": "allowed by policy"} {
    allowed_tool
    not cost_exceeded
    not denied_tool
}

decision := {"allow": false, "reason": "cost exceeds limit", "require_approval": true} {
    cost_exceeded
}

allowed_tool {
    input.agent == "research-agent"
    input.tool == allowed[_]
    allowed := ["web_search", "read_crm", "read_file"]
}

allowed_tool {
    input.agent == "sales-agent"
    input.tool == allowed[_]
    allowed := ["read_crm", "send_email", "create_lead"]
}

denied_tool {
    input.agent == "research-agent"
    input.tool == "send_email"
}

cost_exceeded {
    input.params.cost_usd > 100
}
