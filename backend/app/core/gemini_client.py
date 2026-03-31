"""
Google Gemini API client with caching, retry, and graceful degradation.

Architecture:
  - All calls are async (run_in_executor for the sync SDK)
  - Redis caching keyed by SHA-256 hash of prompt
  - Exponential backoff retry via tenacity (3 attempts)
  - 30-second timeout per request
  - Graceful degradation: returns None on any failure
    so callers can fall back to rule-based logic

Usage:
    from app.core.gemini_client import gemini_call

    result = await gemini_call(
        prompt="Analyze this resume: ...",
        cache_key="resume_analysis_abc123",
        expect_json=True,
    )
    if result is None:
        # Gemini unavailable — use fallback
"""
import asyncio
import hashlib
import json
import os
from typing import Any
from app.core.logging_config import get_logger

logger = get_logger(__name__)


def _get_redis_client():
    """Get a synchronous Redis client for caching."""
    try:
        import redis
        from app.core.config import settings
        return redis.from_url(
            settings.redis_url,
            decode_responses=True,
            socket_timeout=5,
            socket_connect_timeout=5,
        )
    except Exception as exc:
        logger.warning(
            "gemini_cache_redis_unavailable",
            error=str(exc),
        )
        return None


def _cache_key(prompt: str, prefix: str = "gemini") -> str:
    """Generate a deterministic cache key from prompt content."""
    prompt_hash = hashlib.sha256(prompt.encode()).hexdigest()[:16]
    return f"{prefix}:{prompt_hash}"


def _call_gemini_sync(prompt: str) -> str | None:
    """
    Synchronous Gemini API call with retry logic.
    Runs in thread pool executor — never call from async context directly.

    Returns:
        Response text string on success, None on any failure.
    """
    from tenacity import (
        retry, stop_after_attempt, wait_exponential,
        retry_if_exception_type
    )
    from app.core.config import settings

    if not settings.gemini_api_key:
        logger.warning(
            "gemini_api_key_not_configured",
            note="Set GEMINI_API_KEY to enable AI features",
        )
        return None

    try:
        import google.generativeai as genai
        genai.configure(api_key=settings.gemini_api_key)
        model = genai.GenerativeModel(settings.gemini_model)

        @retry(
            stop=stop_after_attempt(settings.gemini_max_retries),
            wait=wait_exponential(multiplier=1, min=2, max=10),
            retry=retry_if_exception_type(Exception),
            reraise=False,
        )
        def _attempt():
            response = model.generate_content(
                prompt,
                generation_config={
                    "temperature": 0.1,
                    "max_output_tokens": 2048,
                },
            )
            return response.text

        return _attempt()

    except Exception as exc:
        logger.error(
            "gemini_call_failed",
            error=str(exc),
        )
        return None


async def gemini_call(
    prompt: str,
    cache_key: str | None = None,
    expect_json: bool = False,
    cache_prefix: str = "gemini",
) -> Any | None:
    """
    Make an async Gemini API call with Redis caching.

    Args:
        prompt: The prompt to send to Gemini
        cache_key: Optional explicit cache key. If None, derived
                   from SHA-256 hash of the prompt.
        expect_json: If True, parse response as JSON before returning.
                     Returns None if JSON parsing fails.
        cache_prefix: Redis key prefix for namespace separation.

    Returns:
        Parsed JSON dict/list if expect_json=True,
        raw string if expect_json=False,
        None if Gemini is unavailable or call fails.
    """
    from app.core.config import settings

    key = cache_key or _cache_key(prompt, cache_prefix)

    # Check Redis cache first
    redis_client = _get_redis_client()
    if redis_client:
        try:
            cached = redis_client.get(key)
            if cached:
                logger.info(
                    "gemini_cache_hit",
                    cache_key=key,
                )
                if expect_json:
                    return json.loads(cached)
                return cached
        except Exception as exc:
            logger.warning(
                "gemini_cache_read_failed",
                cache_key=key,
                error=str(exc),
            )

    # Call Gemini in thread pool (SDK is synchronous)
    loop = asyncio.get_event_loop()
    try:
        raw_response = await asyncio.wait_for(
            loop.run_in_executor(None, _call_gemini_sync, prompt),
            timeout=settings.gemini_timeout_seconds,
        )
    except asyncio.TimeoutError:
        logger.error(
            "gemini_call_timeout",
            timeout_seconds=settings.gemini_timeout_seconds,
        )
        return None

    if raw_response is None:
        return None

    # Parse JSON if requested
    result = raw_response
    if expect_json:
        try:
            # Strip markdown code fences if present
            clean = raw_response.strip()
            if clean.startswith("```"):
                lines = clean.split("\n")
                clean = "\n".join(lines[1:-1])
            result = json.loads(clean)
        except json.JSONDecodeError as exc:
            logger.error(
                "gemini_json_parse_failed",
                error=str(exc),
                raw_response=raw_response[:200],
            )
            return None

    # Cache the result
    if redis_client:
        try:
            cache_value = (
                json.dumps(result) if expect_json else result
            )
            redis_client.setex(
                key,
                settings.gemini_cache_ttl_seconds,
                cache_value,
            )
            logger.info(
                "gemini_response_cached",
                cache_key=key,
                ttl=settings.gemini_cache_ttl_seconds,
            )
        except Exception as exc:
            logger.warning(
                "gemini_cache_write_failed",
                cache_key=key,
                error=str(exc),
            )

    return result
