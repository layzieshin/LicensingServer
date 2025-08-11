from __future__ import annotations
import time
from typing import Callable, Dict, Tuple
from fastapi import Request, HTTPException

# sehr einfacher Token-Bucket (pro IP + Pfad)
# Default: 60 req / 60s je Route/IP
_LIMIT = 60
_WINDOW = 60.0
_buckets: Dict[Tuple[str, str], Tuple[float, int]] = {}  # (ip,path) -> (reset_ts, tokens)

def rate_limit(limit: int = _LIMIT, window_sec: float = _WINDOW) -> Callable:
    def dependency(request: Request):
        ip = request.client.host if request.client else "unknown"
        key = (ip, request.url.path)
        now = time.time()
        reset, tokens = _buckets.get(key, (now + window_sec, limit))
        # reset window?
        if now > reset:
            reset, tokens = (now + window_sec, limit)
        if tokens <= 0:
            raise HTTPException(status_code=429, detail="Too Many Requests")
        tokens -= 1
        _buckets[key] = (reset, tokens)
    return dependency
