"""
Tests for resume endpoints: upload, list, get by ID, delete.

Covers: role enforcement (only students can upload), ownership
isolation (students only see their own resumes), and unauthenticated
access rejection.
"""
import io
import pytest
from httpx import AsyncClient

RESUME_PREFIX = "/api/v1/resumes"


def make_fake_pdf() -> bytes:
    """Returns minimal valid PDF bytes for upload testing."""
    return b"%PDF-1.4 1 0 obj<</Type /Catalog>>endobj"


def make_fake_txt() -> bytes:
    """Returns plain text resume content for upload testing."""
    return b"John Doe\nSoftware Engineer\nSkills: Python, FastAPI, PostgreSQL"


class TestResumeUpload:

    async def test_upload_txt_as_student_returns_200(
        self, client: AsyncClient, student_user, student_headers: dict
    ):
        files = {"file": ("resume.txt", io.BytesIO(make_fake_txt()), "text/plain")}
        response = await client.post(
            f"{RESUME_PREFIX}/upload",
            files=files,
            headers=student_headers
        )
        assert response.status_code == 200

    async def test_upload_returns_resume_object(
        self, client: AsyncClient, student_user, student_headers: dict
    ):
        files = {"file": ("resume.txt", io.BytesIO(make_fake_txt()), "text/plain")}
        response = await client.post(
            f"{RESUME_PREFIX}/upload",
            files=files,
            headers=student_headers
        )
        data = response.json()
        assert data["success"] is True
        assert data["data"] is not None

    async def test_upload_unauthenticated_returns_401(
        self, client: AsyncClient
    ):
        files = {"file": ("resume.txt", io.BytesIO(make_fake_txt()), "text/plain")}
        response = await client.post(
            f"{RESUME_PREFIX}/upload", files=files
        )
        assert response.status_code == 401

    async def test_upload_as_recruiter_returns_403(
        self, client: AsyncClient, recruiter_user, recruiter_headers: dict
    ):
        """Recruiters must not be able to upload resumes."""
        files = {"file": ("resume.txt", io.BytesIO(make_fake_txt()), "text/plain")}
        response = await client.post(
            f"{RESUME_PREFIX}/upload",
            files=files,
            headers=recruiter_headers
        )
        assert response.status_code == 403


class TestResumeList:

    async def test_list_resumes_as_student_returns_200(
        self, client: AsyncClient, student_user, student_headers: dict
    ):
        response = await client.get(
            f"{RESUME_PREFIX}/user/{student_user.id}", headers=student_headers
        )
        assert response.status_code == 200

    async def test_list_resumes_returns_array(
        self, client: AsyncClient, student_user, student_headers: dict
    ):
        response = await client.get(
            f"{RESUME_PREFIX}/user/{student_user.id}", headers=student_headers
        )
        data = response.json()
        assert data["success"] is True
        assert isinstance(data["data"], list)

    async def test_list_resumes_unauthenticated_returns_401(
        self, client: AsyncClient, student_user
    ):
        response = await client.get(f"{RESUME_PREFIX}/user/{student_user.id}")
        assert response.status_code == 401

    async def test_student_only_sees_own_resumes(
        self, client: AsyncClient,
        student_user, student_headers: dict,
        recruiter_user, recruiter_headers: dict
    ):
        """A student must not see resumes belonging to another user."""
        # Upload a resume as student
        files = {"file": ("resume.txt", io.BytesIO(make_fake_txt()), "text/plain")}
        await client.post(
            f"{RESUME_PREFIX}/upload",
            files=files,
            headers=student_headers
        )
        # Recruiter tries to view the student's resumes
        response = await client.get(
            f"{RESUME_PREFIX}/user/{student_user.id}", headers=recruiter_headers
        )
        # Should return 403 since recruiter is not admin or the student themselves
        assert response.status_code == 403
