"""
Shared test fixtures for the AI Resume Matchmaking System test suite.

Database strategy: SQLite in-memory via aiosqlite for speed and isolation.
All fixtures are function-scoped unless explicitly marked session-scoped.
The real PostgreSQL database is never touched during testing.
"""
import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.db.models import Base
from app.db.session import get_db
from app.core.security import hash_password, create_access_token
from app.db.models import User

# ── Test Database Setup ───────────────────────────────────────────────────

TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

test_engine = create_async_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
)

TestSessionLocal = sessionmaker(
    bind=test_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


@pytest_asyncio.fixture(scope="function", autouse=True)
async def setup_database():
    """Create all tables before each test, drop after."""
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


async def override_get_db():
    """Dependency override — uses test SQLite DB instead of PostgreSQL."""
    async with TestSessionLocal() as session:
        yield session


app.dependency_overrides[get_db] = override_get_db

# ── HTTP Client ───────────────────────────────────────────────────────────

@pytest_asyncio.fixture
async def client() -> AsyncClient:
    """Async HTTP test client for the FastAPI app."""
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as ac:
        yield ac

# ── User Fixtures ─────────────────────────────────────────────────────────

@pytest_asyncio.fixture
async def student_user():
    """A persisted student user for use in tests."""
    async with TestSessionLocal() as session:
        user = User(
            email="student@test.com",
            name="Test Student",
            password_hash=hash_password("TestPassword123!"),
            role="student",
        )
        session.add(user)
        await session.commit()
        await session.refresh(user)
        return user


@pytest_asyncio.fixture
async def recruiter_user():
    """A persisted recruiter user for use in tests."""
    async with TestSessionLocal() as session:
        user = User(
            email="recruiter@test.com",
            name="Test Recruiter",
            password_hash=hash_password("TestPassword123!"),
            role="recruiter",
        )
        session.add(user)
        await session.commit()
        await session.refresh(user)
        return user


@pytest_asyncio.fixture
async def admin_user():
    """A persisted admin user for use in tests."""
    async with TestSessionLocal() as session:
        user = User(
            email="admin@test.com",
            name="Test Admin",
            password_hash=hash_password("TestPassword123!"),
            role="admin",
        )
        session.add(user)
        await session.commit()
        await session.refresh(user)
        return user

# ── Auth Header Fixtures ──────────────────────────────────────────────────

@pytest.fixture
def student_headers(student_user):
    """Bearer token headers for the student user."""
    token = create_access_token(data={"sub": str(student_user.id)})
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def recruiter_headers(recruiter_user):
    """Bearer token headers for the recruiter user."""
    token = create_access_token(data={"sub": str(recruiter_user.id)})
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def admin_headers(admin_user):
    """Bearer token headers for the admin user."""
    token = create_access_token(data={"sub": str(admin_user.id)})
    return {"Authorization": f"Bearer {token}"}

# ── Payload Factories ─────────────────────────────────────────────────────

@pytest.fixture
def valid_signup_payload():
    """Valid signup request body. Field names match SignupRequest schema."""
    return {
        "email": "newuser@test.com",
        "password": "TestPassword123!",
        "confirm_password": "TestPassword123!",
        "name": "New User",
        "role": "student",
    }


@pytest.fixture
def valid_login_payload():
    """Valid login request body. Field names match LoginRequest schema."""
    return {
        "email": "student@test.com",
        "password": "TestPassword123!",
        "role": "student",
    }
