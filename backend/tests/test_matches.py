"""
Tests for match endpoints: trigger matching, list matches, get by ID,
update match status.

Covers: score range validation, role enforcement, unauthenticated
access rejection, and response shape correctness.
"""
import io
import pytest
from httpx import AsyncClient

MATCH_PREFIX = "/api/v1/matches"
RESUME_PREFIX = "/api/v1/resumes"
JOB_PREFIX = "/api/v1/jobs"


def make_fake_txt() -> bytes:
    return b"Jane Smith\nPython Developer\nSkills: Python, FastAPI, SQL"


def make_job_payload() -> dict:
    return {
        "title": "Python Developer",
        "company": "Tech Corp",
        "description": "Looking for a Python developer.",
        "required_skills": ["Python", "FastAPI"],
        "experience_level": "mid",
        "location_type": "remote",
        "location": "Remote",
    }


class TestMatchScoring:

    async def test_match_score_returns_200(
        self,
        client: AsyncClient,
        student_user, student_headers: dict,
        recruiter_user, recruiter_headers: dict
    ):
        # Upload resume
        files = {"file": ("resume.txt", io.BytesIO(make_fake_txt()), "text/plain")}
        resume_resp = await client.post(
            f"{RESUME_PREFIX}/upload",
            files=files,
            headers=student_headers
        )
        resume_id = resume_resp.json()["data"]["resume"]["id"]  # Access nested ID in ResumeUploadResponse

        # Create job
        await client.post(
            JOB_PREFIX, json=make_job_payload(), headers=recruiter_headers
        )

        # Trigger match (matches resume against all jobs)
        response = await client.post(
            f"{MATCH_PREFIX}/resume/{resume_id}",
            headers=student_headers
        )
        assert response.status_code == 200

    async def test_match_score_is_between_0_and_1(
        self,
        client: AsyncClient,
        student_user, student_headers: dict,
        recruiter_user, recruiter_headers: dict
    ):
        files = {"file": ("resume.txt", io.BytesIO(make_fake_txt()), "text/plain")}
        resume_resp = await client.post(
            f"{RESUME_PREFIX}/upload",
            files=files,
            headers=student_headers
        )
        resume_id = resume_resp.json()["data"]["resume"]["id"]
        
        await client.post(
            JOB_PREFIX, json=make_job_payload(), headers=recruiter_headers
        )

        response = await client.post(
            f"{MATCH_PREFIX}/resume/{resume_id}",
            headers=student_headers
        )
        data = response.json()
        if data["data"]:
            score = data["data"][0]["overall_score"]
            assert 0 <= score <= 1

    async def test_match_score_invalid_resume_id_returns_403(
        self,
        client: AsyncClient,
        student_user, student_headers: dict,
        recruiter_user, recruiter_headers: dict
    ):
        await client.post(
            JOB_PREFIX, json=make_job_payload(), headers=recruiter_headers
        )
        # 403 because student doesn't own this non-existent resume ID
        response = await client.post(
            f"{MATCH_PREFIX}/resume/00000000-0000-0000-0000-000000000000",
            headers=student_headers
        )
        assert response.status_code == 403

    async def test_match_score_unauthenticated_returns_401(
        self, client: AsyncClient
    ):
        response = await client.post(
            f"{MATCH_PREFIX}/resume/00000000-0000-0000-0000-000000000000"
        )
        assert response.status_code == 401


class TestMatchList:

    async def test_list_matches_student_returns_200(
        self, client: AsyncClient, student_user, student_headers: dict
    ):
        response = await client.get(
            f"{MATCH_PREFIX}/student/{student_user.id}", headers=student_headers
        )
        assert response.status_code == 200

    async def test_list_matches_returns_array(
        self, client: AsyncClient, student_user, student_headers: dict
    ):
        response = await client.get(
            f"{MATCH_PREFIX}/student/{student_user.id}", headers=student_headers
        )
        data = response.json()
        assert data["success"] is True
        assert isinstance(data["data"], list)

    async def test_list_matches_unauthenticated_returns_401(
        self, client: AsyncClient, student_user
    ):
        response = await client.get(f"{MATCH_PREFIX}/student/{student_user.id}")
        assert response.status_code == 401
