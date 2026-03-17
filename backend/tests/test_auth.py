"""
Tests for authentication endpoints: /api/v1/auth/login,
/api/v1/auth/signup, /api/v1/auth/me

Covers: success paths, error paths, token presence, role enforcement,
and duplicate account prevention.
"""
import pytest
from httpx import AsyncClient

AUTH_PREFIX = "/api/v1/auth"


class TestSignup:

    async def test_signup_success_returns_200(
        self, client: AsyncClient, valid_signup_payload: dict
    ):
        response = await client.post(
            f"{AUTH_PREFIX}/signup", json=valid_signup_payload
        )
        assert response.status_code == 200

    async def test_signup_success_returns_access_token(
        self, client: AsyncClient, valid_signup_payload: dict
    ):
        response = await client.post(
            f"{AUTH_PREFIX}/signup", json=valid_signup_payload
        )
        data = response.json()
        assert data["success"] is True
        assert "access_token" in data["data"]
        assert data["data"]["access_token"] is not None
        assert len(data["data"]["access_token"]) > 20

    async def test_signup_success_returns_user_object(
        self, client: AsyncClient, valid_signup_payload: dict
    ):
        response = await client.post(
            f"{AUTH_PREFIX}/signup", json=valid_signup_payload
        )
        data = response.json()
        user = data["data"]["user"]
        assert user["email"] == valid_signup_payload["email"]
        assert user["role"] == valid_signup_payload["role"]
        assert "password_hash" not in user
        assert "password" not in user

    async def test_signup_duplicate_email_returns_error(
        self, client: AsyncClient, valid_signup_payload: dict
    ):
        await client.post(f"{AUTH_PREFIX}/signup", json=valid_signup_payload)
        response = await client.post(
            f"{AUTH_PREFIX}/signup", json=valid_signup_payload
        )
        assert response.status_code in [400, 409]
        data = response.json()
        assert data["success"] is False

    async def test_signup_invalid_email_returns_422(
        self, client: AsyncClient, valid_signup_payload: dict
    ):
        payload = {**valid_signup_payload, "email": "not-an-email"}
        response = await client.post(f"{AUTH_PREFIX}/signup", json=payload)
        assert response.status_code == 422

    async def test_signup_missing_password_returns_422(
        self, client: AsyncClient, valid_signup_payload: dict
    ):
        payload = {k: v for k, v in valid_signup_payload.items()
                   if k != "password"}
        response = await client.post(f"{AUTH_PREFIX}/signup", json=payload)
        assert response.status_code == 422

    async def test_signup_password_mismatch_returns_error(
        self, client: AsyncClient, valid_signup_payload: dict
    ):
        payload = {**valid_signup_payload, "confirm_password": "WrongPass999!"}
        response = await client.post(f"{AUTH_PREFIX}/signup", json=payload)
        assert response.status_code in [400, 422]

    async def test_signup_token_type_is_bearer(
        self, client: AsyncClient, valid_signup_payload: dict
    ):
        response = await client.post(
            f"{AUTH_PREFIX}/signup", json=valid_signup_payload
        )
        data = response.json()
        assert data["data"]["token_type"] == "bearer"


class TestLogin:

    async def test_login_success_returns_200(
        self, client: AsyncClient, student_user, valid_login_payload: dict
    ):
        response = await client.post(
            f"{AUTH_PREFIX}/login", json=valid_login_payload
        )
        assert response.status_code == 200

    async def test_login_success_returns_access_token(
        self, client: AsyncClient, student_user, valid_login_payload: dict
    ):
        response = await client.post(
            f"{AUTH_PREFIX}/login", json=valid_login_payload
        )
        data = response.json()
        assert data["success"] is True
        assert "access_token" in data["data"]
        assert len(data["data"]["access_token"]) > 20

    async def test_login_success_returns_correct_user(
        self, client: AsyncClient, student_user, valid_login_payload: dict
    ):
        response = await client.post(
            f"{AUTH_PREFIX}/login", json=valid_login_payload
        )
        data = response.json()
        assert data["data"]["user"]["email"] == student_user.email
        assert data["data"]["user"]["role"] == "student"

    async def test_login_wrong_password_returns_401(
        self, client: AsyncClient, student_user
    ):
        response = await client.post(
            f"{AUTH_PREFIX}/login",
            json={"email": "student@test.com", "password": "WrongPassword!", "role": "student"}
        )
        assert response.status_code == 401

    async def test_login_nonexistent_user_returns_401(
        self, client: AsyncClient
    ):
        response = await client.post(
            f"{AUTH_PREFIX}/login",
            json={"email": "ghost@test.com", "password": "AnyPassword123!", "role": "student"}
        )
        assert response.status_code == 401

    async def test_login_missing_email_returns_422(
        self, client: AsyncClient
    ):
        response = await client.post(
            f"{AUTH_PREFIX}/login",
            json={"password": "TestPassword123!", "role": "student"}
        )
        assert response.status_code == 422

    async def test_login_empty_body_returns_422(
        self, client: AsyncClient
    ):
        response = await client.post(f"{AUTH_PREFIX}/login", json={})
        assert response.status_code == 422

    async def test_login_password_not_returned_in_response(
        self, client: AsyncClient, student_user, valid_login_payload: dict
    ):
        response = await client.post(
            f"{AUTH_PREFIX}/login", json=valid_login_payload
        )
        response_text = response.text
        assert "password_hash" not in response_text
        assert "TestPassword123!" not in response_text


class TestMe:

    async def test_me_authenticated_returns_200(
        self, client: AsyncClient, student_user, student_headers: dict
    ):
        response = await client.get(
            f"{AUTH_PREFIX}/me", headers=student_headers
        )
        assert response.status_code == 200

    async def test_me_returns_correct_user_data(
        self, client: AsyncClient, student_user, student_headers: dict
    ):
        response = await client.get(
            f"{AUTH_PREFIX}/me", headers=student_headers
        )
        data = response.json()
        assert data["data"]["email"] == student_user.email
        assert data["data"]["role"] == "student"

    async def test_me_unauthenticated_returns_401(
        self, client: AsyncClient
    ):
        response = await client.get(f"{AUTH_PREFIX}/me")
        assert response.status_code == 401

    async def test_me_invalid_token_returns_401(
        self, client: AsyncClient
    ):
        response = await client.get(
            f"{AUTH_PREFIX}/me",
            headers={"Authorization": "Bearer invalid.token.here"}
        )
        assert response.status_code == 401

    async def test_me_password_not_in_response(
        self, client: AsyncClient, student_user, student_headers: dict
    ):
        response = await client.get(
            f"{AUTH_PREFIX}/me", headers=student_headers
        )
        assert "password_hash" not in response.text
        assert "password" not in response.json().get("data", {})
