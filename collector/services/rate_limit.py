# collector/app/services/rate_limit.py

import time
from collector.core.config import settings

request_timestamps = {}  # {ip: [timestamp1, timestamp2...]}


def is_rate_limited(ip: str) -> bool:
    now = time.time()

    if ip not in request_timestamps:
        request_timestamps[ip] = []

    # Remove old timestamps outside window
    request_timestamps[ip] = [
        ts for ts in request_timestamps[ip]
        if now - ts < settings.RATE_LIMIT_WINDOW
    ]

    # Allow if below limit
    if len(request_timestamps[ip]) < settings.RATE_LIMIT_REQUESTS:
        request_timestamps[ip].append(now)
        return False

    return True
