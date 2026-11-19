# [OWNER: M3] Pytest cho Sprint 1 Core API (Auth, Export, Cascade Delete 401, Web Delete, Seed Integrity)
import sys
import uuid
from collections.abc import AsyncGenerator
from pathlib import Path

# Dam bao import duoc package `app` khi chay truc tiep `pytest tests/test_core_api.py`
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool

from app.core.config import Settings, settings
from app.db.base import Base
from app.db.seed_catalog_and_exercises import (
    CANONICAL_MUSCLE_MATERIALS,
    EXERCISES_SEED,
    FOOD_CATALOG_SEED,
)
from app.db.session import get_db
from app.main import app


@pytest_asyncio.fixture
async def async_client() -> AsyncGenerator[AsyncClient, None]:
    # Dung NullPool tren PostgreSQL 16 de moi test co ket noi async doc lap, khong xung dot event loop
    test_engine = create_async_engine(
        settings.DATABASE_URL,
        poolclass=NullPool,
        future=True,
    )

    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    session_factory = async_sessionmaker(
        bind=test_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    async def _override_get_db() -> AsyncGenerator[AsyncSession, None]:
        async with session_factory() as session:
            yield session

    app.dependency_overrides[get_db] = _override_get_db
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        yield client
    app.dependency_overrides.clear()
    await test_engine.dispose()


def test_seed_catalog_and_30_exercises_contracts() -> None:
    assert len(FOOD_CATALOG_SEED) >= 35
    assert len(EXERCISES_SEED) == 30
    assert len(CANONICAL_MUSCLE_MATERIALS) == 11
    for ex in EXERCISES_SEED:
        all_muscles = (
            ex["primary_muscles"] + ex["secondary_muscles"] + ex["stabilizer_muscles"]
        )
        assert all(m in CANONICAL_MUSCLE_MATERIALS for m in all_muscles)
        assert len(ex["asset_checksum"]) == 64


@pytest.mark.asyncio
async def test_healthz_and_openapi_docs(async_client: AsyncClient) -> None:
    res_health = await async_client.get("/healthz")
    assert res_health.status_code == 200
    assert res_health.json()["status"] == "ok"

    res_openapi = await async_client.get("/openapi.json")
    assert res_openapi.status_code == 200
    paths = res_openapi.json()["paths"]
    assert "/api/v1/auth/register" in paths
    assert "/api/v1/auth/login" in paths
    assert "/api/v1/auth/refresh" in paths
    assert "/api/v1/users/me/export" in paths
    assert "/api/v1/users/me" in paths


@pytest.mark.asyncio
async def test_register_requires_medical_disclaimer(async_client: AsyncClient) -> None:
    res = await async_client.post(
        "/api/v1/auth/register",
        json={
            "email": "no_disclaimer@vigorai.app",
            "password": "Password123!",
            "full_name": "Test User",
            "medical_disclaimer_accepted": False,
        },
    )
    assert res.status_code == 400


@pytest.mark.asyncio
async def test_auth_export_and_cascade_delete_returns_401(
    async_client: AsyncClient,
) -> None:
    email = f"m3_{uuid.uuid4().hex[:8]}@vigorai.app"
    password = "StrongPassword123!"

    reg_res = await async_client.post(
        "/api/v1/auth/register",
        json={
            "email": email,
            "password": password,
            "full_name": "M3 Architect",
            "gender": "MALE",
            "height_cm": 175.0,
            "fitness_goal": "BULK",
            "medical_disclaimer_accepted": True,
        },
    )
    assert reg_res.status_code == 201
    tokens = reg_res.json()
    assert tokens["access_token"]
    assert tokens["refresh_token"]
    assert tokens["user"]["email"] == email
    assert tokens["user"]["medical_disclaimer_accepted"] is True
    assert tokens["user"]["disclaimer_accepted_at"] is not None

    # Login
    login_res = await async_client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": password},
    )
    assert login_res.status_code == 200
    access_token = login_res.json()["access_token"]
    refresh_token = login_res.json()["refresh_token"]

    # Refresh
    refresh_res = await async_client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": refresh_token},
    )
    assert refresh_res.status_code == 200
    new_access = refresh_res.json()["access_token"]

    # Export JSON
    export_res = await async_client.get(
        "/api/v1/users/me/export",
        headers={"Authorization": f"Bearer {new_access}"},
    )
    assert export_res.status_code == 200
    export_data = export_res.json()
    assert export_data["user"]["email"] == email
    assert "biometric_logs" in export_data
    assert "workout_sessions" in export_data

    # Delete Account (Cascade Delete)
    del_res = await async_client.delete(
        "/api/v1/users/me",
        headers={"Authorization": f"Bearer {new_access}"},
    )
    assert del_res.status_code == 200
    assert del_res.json()["status"] == "deleted"

    # Old token must now return 401 Unauthorized
    after_del_res = await async_client.get(
        "/api/v1/users/me/export",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert after_del_res.status_code == 401


@pytest.mark.asyncio
async def test_public_web_delete_account_flow(async_client: AsyncClient) -> None:
    page_res = await async_client.get("/delete-account")
    assert page_res.status_code == 200
    assert "/api/v1/users/delete-via-web" in page_res.text

    email = f"webdel_{uuid.uuid4().hex[:8]}@vigorai.app"
    password = "WebDelete123!"
    await async_client.post(
        "/api/v1/auth/register",
        json={
            "email": email,
            "password": password,
            "full_name": "Web Delete User",
            "medical_disclaimer_accepted": True,
        },
    )

    # Wrong password -> 401 HTML
    bad_res = await async_client.post(
        "/api/v1/users/delete-via-web",
        data={"email": email, "password": "wrong-password"},
    )
    assert bad_res.status_code == 401

    # Valid credentials -> 200 HTML and account removed
    ok_res = await async_client.post(
        "/api/v1/users/delete-via-web",
        data={"email": email, "password": password},
    )
    assert ok_res.status_code == 200

    # Subsequent login fails with 401
    login_after = await async_client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": password},
    )
    assert login_after.status_code == 401


def test_settings_database_url_normalization() -> None:
    assert (
        Settings.normalize_database_url("postgres://u:p@host:5432/db")
        == "postgresql+asyncpg://u:p@host:5432/db"
    )
    assert (
        Settings.normalize_database_url("postgresql://u:p@host:5432/db")
        == "postgresql+asyncpg://u:p@host:5432/db"
    )
    assert (
        Settings.normalize_database_url("postgresql+psycopg2://u:p@host:5432/db")
        == "postgresql+asyncpg://u:p@host:5432/db"
    )
    assert (
        Settings.normalize_database_url("postgresql+asyncpg://u:p@host:5432/db")
        == "postgresql+asyncpg://u:p@host:5432/db"
    )
    assert (
        Settings.normalize_database_url(
            "postgresql://u:p@host:5432/db?sslmode=require&application_name=vigorai"
        )
        == "postgresql+asyncpg://u:p@host:5432/db?ssl=require&application_name=vigorai"
    )
    assert (
        Settings.normalize_database_url("postgresql://u:p@host:5432/db?sslmode=disable")
        == "postgresql+asyncpg://u:p@host:5432/db"
    )


def test_settings_cors_origins_parsing() -> None:
    assert Settings.parse_cors_origins("*") == ["*"]
    assert Settings.parse_cors_origins(
        "https://vigorai.app, https://admin.vigorai.app"
    ) == ["https://vigorai.app", "https://admin.vigorai.app"]
    assert Settings.parse_cors_origins(
        '["https://a.com", "https://b.com"]'
    ) == ["https://a.com", "https://b.com"]
