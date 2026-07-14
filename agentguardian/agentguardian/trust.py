import threading


class TrustScorer:
    """Per-agent trust score: starts at 1.0, drops on violations, slowly recovers."""

    def __init__(self):
        self._scores = {}
        self._lock = threading.Lock()

    def record(self, agent, allowed):
        with self._lock:
            s = self._scores.get(agent, 1.0)
            if allowed:
                s = min(1.0, s + 0.01)
            else:
                s = max(0.0, s - 0.1)
            self._scores[agent] = s
            return s

    def get(self, agent):
        return self._scores.get(agent, 1.0)

    def all(self):
        return dict(self._scores)
