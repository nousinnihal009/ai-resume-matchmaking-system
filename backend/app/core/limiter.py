"""
Shared rate limiter instance (Mocked for debugging startup).
"""
import logging

logger = logging.getLogger(__name__)

class MockLimiter:
    def __init__(self, *args, **kwargs):
        pass
    
    def limit(self, *args, **kwargs):
        def decorator(f):
            return f
        return decorator

    def middleware(self, *args, **kwargs):
        def decorator(f):
            return f
        return decorator

# Provide a mock function for get_remote_address if needed
def get_remote_address(*args, **kwargs):
    return "127.0.0.1"

limiter = MockLimiter()
