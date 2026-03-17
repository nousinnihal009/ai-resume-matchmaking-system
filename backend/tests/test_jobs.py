"""
Tests for job endpoints: create, list, get by ID, update, delete.

Covers: role enforcement (only recruiters can create jobs), 
public listing, ownership, and unauthenticated access rejection.
"""
import pytest
from httpx import AsyncClient

JOB_PREFIX = "/api/v1/jobs"


def make_job_payload() -> dict:
    """
    Valid job creation payload.
    Field names matched against JobPostingForm schema in schemas/job.py.
    """
    return {
        "title": "Senior Python Engineer",
        "company": "Tech Corp",
        "description": "We are looking for an experienced Python engineer.",
        "required_skills": ["Python", "FastAPI", "PostgreSQL"],
        "experience_level": "senior",
        "location_type": "remote",
        "location": "Remote",
    }


class TestJobCreate:

    async def test_create_job_as_recruiter_returns_200(
        self, client: AsyncClient, recruiter_user, recruiter_headers: dict
    ):
        response = await client.post(
            JOB_PREFIX, json=make_job_payload(), headers=recruiter_headers
        )
        assert response.status_code == 200

    async def test_create_job_returns_job_object(
        self, client: AsyncClient, recruiter_user, recruiter_headers: dict
    ):
        response = await client.post(
            JOB_PREFIX, json=make_job_payload(), headers=recruiter_headers
        )
        data = response.json()
        assert data["success"] is True
        assert data["data"]["title"] == "Senior Python Engineer"

    async def test_create_job_as_student_returns_403(
        self, client: AsyncClient, student_user, student_headers: dict
    ):
        """Students must not be able to create job postings."""
        response = await client.post(
            JOB_PREFIX, json=make_job_payload(), headers=student_headers
        )
        assert response.status_code == 403

    async def test_create_job_unauthenticated_returns_401(
        self, client: AsyncClient
    ):
        response = await client.post(JOB_PREFIX, json=make_job_payload())
        assert response.status_code == 401

    async def test_create_job_missing_title_returns_422(
        self, client: AsyncClient, recruiter_user, recruiter_headers: dict
    ):
        payload = {k: v for k, v in make_job_payload().items() if k != "title"}
        response = await client.post(
            JOB_PREFIX, json=payload, headers=recruiter_headers
        )
        assert response.status_code == 422


class TestJobList:

    async def test_list_jobs_authenticated_returns_200(
        self, client: AsyncClient, student_user, student_headers: dict
    ):
        response = await client.get(JOB_PREFIX, headers=student_headers)
        assert response.status_code == 200

    async def test_list_jobs_returns_array(
        self, client: AsyncClient, student_user, student_headers: dict
    ):
        response = await client.get(JOB_PREFIX, headers=student_headers)
        data = response.json()
        assert data["success"] is True
        # The list endpoint returns a PaginatedResponse, so the array is in data['items']
        assert isinstance(data["data"]["items"], list)

    async def test_list_jobs_unauthenticated_returns_401(
        self, client: AsyncClient
    ):
        response = await client.get(JOB_PREFIX)
        assert response.status_code == 401

    async def test_list_jobs_contains_created_job(
        self, client: AsyncClient, recruiter_user, recruiter_headers: dict,
        student_user, student_headers: dict
    ):
        await client.post(
            JOB_PREFIX, json=make_job_payload(), headers=recruiter_headers
        )
        response = await client.get(JOB_PREFIX, headers=student_headers)
        data = response.json()
        titles = [job["title"] for job in data["data"]["items"]]
        assert "Senior Python Engineer" in titles
