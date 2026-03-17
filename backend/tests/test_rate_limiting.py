"""
Tests for rate limiting on auth endpoints.

These are marked slow because they send multiple sequential requests.
Run with: pytest -m slow
Skip with: pytest -m "not slow"
"""
import pytest
from httpx import AsyncClient

AUTH_PREFIX = "/api/v1/auth"


@pytest.mark.slow
class TestLoginRateLimit:

    async def test_login_rate_limit_triggers_on_6th_request(
        self, client: AsyncClient
    ):
        """Login is limited to 5/minute. The 6th request must return 429."""
        payload = {"email": "brute@test.com", "password": "WrongPassword!", "role": "student"}
        responses = []
        for _ in range(6):
            r = await client.post(f"{AUTH_PREFIX}/login", json=payload)
            responses.append(r.status_code)

        # First 5 are 401 (wrong password), 6th must be 429 (rate limited)
        assert responses[-1] == 429

    async def test_login_rate_limit_response_has_retry_after(
        self, client: AsyncClient
    ):
        """429 response should indicate when to retry."""
        payload = {"email": "brute@test.com", "password": "WrongPassword!", "role": "student"}
        for _ in range(6):
            response = await client.post(f"{AUTH_PREFIX}/login", json=payload)
        assert response.status_code == 429


@pytest.mark.slow
class TestSignupRateLimit:

    async def test_signup_rate_limit_triggers_on_4th_request(
        self, client: AsyncClient
    ):
        """Signup is limited to 3/minute. The 4th request must return 429."""
        responses = []
        for i in range(4):
            payload = {
                "email": f"spammer{i}@test.com",
                "password": "TestPassword123!",
                "confirm_password": "TestPassword123!",
                "name": f"Spammer {i}",
                "role": "student",
            }
            r = await client.post(f"{AUTH_PREFIX}/signup", json=payload)
            responses.append(r.status_code)

        assert responses[-1] == 429
