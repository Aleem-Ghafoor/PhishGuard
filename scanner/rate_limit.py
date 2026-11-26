"""Lightweight per-client throttling for the public URL scan endpoint.

The default Django local-memory cache is suitable for local development only.
Deployments with multiple workers/instances should configure a shared cache
backend (for example Redis) so all workers enforce the same limit.
"""
from functools import wraps
import hashlib

from django.core.cache import cache
from django.http import JsonResponse


SCAN_LIMIT = 10
SCAN_WINDOW_SECONDS = 60


def scan_rate_limit(view_func):
    """Allow at most 10 scan requests per client IP in each 60-second window."""
    @wraps(view_func)
    def wrapped(request, *args, **kwargs):
        client_ip = request.META.get("REMOTE_ADDR", "unknown")
        ip_digest = hashlib.sha256(client_ip.encode("utf-8")).hexdigest()
        cache_key = f"phishguard:scan-rate:{ip_digest}"

        if cache.add(cache_key, 1, timeout=SCAN_WINDOW_SECONDS):
            request_count = 1
        else:
            try:
                request_count = cache.incr(cache_key)
            except ValueError:
                # The key may expire between add() and incr().
                cache.add(cache_key, 1, timeout=SCAN_WINDOW_SECONDS)
                request_count = 1

        if request_count > SCAN_LIMIT:
            return JsonResponse({
                "success": False,
                "message": "Too many scan requests. Please wait a minute and try again."
            }, status=429)

        return view_func(request, *args, **kwargs)

    return wrapped
