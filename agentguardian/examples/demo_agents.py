from integrations.guard import Guard

research = Guard("research-agent")
sales = Guard("sales-agent")
coding = Guard("coding-agent")

tests = [
    (research, "web_search",  {"q": "market size"}),          # allow
    (research, "send_email",  {"recipient_domain": "acme.com"}),  # deny (research can't email)
    (sales,    "send_email",  {"recipient_domain": "acme.com"}),  # allow
    (sales,    "send_email",  {"recipient_domain": "competitor.com"}),  # deny (blocklist)
    (sales,    "create_lead", {"cost_usd": 250}),             # require_approval (>$100)
    (coding,   "write_file",  {"path": "main.py"}),           # allow
    (coding,   "shell_exec",  {"cmd": "rm -rf /"}),           # deny (sandbox)
]

if __name__ == "__main__":
    for guard, tool, params in tests:
        d = guard.check(tool, params)
        status = "✅ ALLOW" if d["allow"] else ("⏸️  APPROVAL" if d.get("require_approval") else "⛔ BLOCK")
        print(f"{status:12} {guard.agent:16} {tool:14} → {d['reason']}  ({d['latency_ms']}ms)")
