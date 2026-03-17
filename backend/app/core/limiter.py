"""
Shared rate limiter instance.

Defined in its own module to prevent circular imports between
main.py (which registers the exception handler) and the API route
handlers (which apply per-endpoint limits via decorators).
"""
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["60/minute"]
)
