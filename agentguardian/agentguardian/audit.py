import time
import threading
from collections import deque


class AuditLog:
    def __init__(self, maxlen=500):
        self._log = deque(maxlen=maxlen)
        self._lock = threading.Lock()
        self.counters = {"allowed": 0, "blocked": 0, "approval": 0}

    def add(self, agent, tool, params, decision):
        with self._lock:
            entry = {
                "ts": time.time(),
                "agent": agent, "tool": tool, "params": params,
                "allow": decision["allow"],
                "require_approval": decision.get("require_approval", False),
                "reason": decision["reason"],
            }
            self._log.appendleft(entry)
            if decision.get("require_approval"):
                self.counters["approval"] += 1
            elif decision["allow"]:
                self.counters["allowed"] += 1
            else:
                self.counters["blocked"] += 1
            return entry

    def recent(self, n=100):
        return list(self._log)[:n]
