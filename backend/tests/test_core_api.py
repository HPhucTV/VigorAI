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
    assert len(EXERCISES_SEED) == 39
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


@pytest.mark.asyncio
async def test_sprint2_health_exercises_routines_workouts_sync_analytics(
    async_client: AsyncClient,
) -> None:
    email = f"sprint2_{uuid.uuid4().hex[:8]}@vigorai.app"
    password = "Sprint2Password!"

    reg = await async_client.post(
        "/api/v1/auth/register",
        json={
            "email": email,
            "password": password,
            "full_name": "Sprint 2 Tester",
            "gender": "MALE",
            "height_cm": 175.0,
            "fitness_goal": "BULK",
            "medical_disclaimer_accepted": True,
        },
    )
    assert reg.status_code == 201
    headers = {"Authorization": f"Bearer {reg.json()['access_token']}"}

    # 1. T-M3-09: Exercises & Alternatives (3 bundled MVP + 28 CDN .glb + 8 fallback = 39)
    ex_res = await async_client.get("/api/v1/exercises")
    assert ex_res.status_code == 200
    exercises = ex_res.json()["items"]
    assert len(exercises) == 39
    bench = next(e for e in exercises if e["code"] == "BARBELL_BENCH_PRESS")
    assert bench["bundled"] is True
    assert bench["model_3d_glb_url"] == "assets/3d_bundled/barbell_bench_press.glb"

    lat = next(e for e in exercises if e["code"] == "LAT_PULLDOWN")
    assert lat["bundled"] is False
    assert lat["clips"] == ["Anim_GoodForm", "Anim_BadForm"]
    assert lat["model_3d_glb_url"].endswith("/api/v1/exercises/LAT_PULLDOWN/glb")

    glb_res = await async_client.get("/api/v1/exercises/LAT_PULLDOWN/glb")
    assert glb_res.status_code in {200, 307}
    if glb_res.status_code == 200:
        assert len(glb_res.content) > 100_000
        assert glb_res.headers.get("x-asset-sha256") == lat["asset_checksum"]

    alt_res = await async_client.get("/api/v1/exercises/BARBELL_BENCH_PRESS/alternatives")
    assert alt_res.status_code == 200
    alts = alt_res.json()["alternatives"]
    assert 1 <= len(alts) <= 5
    assert all("Mat_Muscle_Chest" in a["primary_muscles"] for a in alts)

    # 2. T-M3-08: Health (daily default 200 OK, biometrics, catalog, meals, supplements)
    daily_empty = await async_client.get("/api/v1/health/daily/2026-11-20", headers=headers)
    assert daily_empty.status_code == 200
    assert daily_empty.json()["steps_count"] == 0

    bio_res = await async_client.post(
        "/api/v1/health/biometrics",
        headers=headers,
        json={"weight_kg": 72.0, "logged_date": "2026-11-20"},
    )
    assert bio_res.status_code == 201
    assert bio_res.json()["bmi_category_asian"] == "OVERWEIGHT"

    cat_res = await async_client.get("/api/v1/health/catalog?q=ga")
    assert cat_res.status_code == 200
    assert len(cat_res.json()["items"]) >= 1

    meal_res = await async_client.post(
        "/api/v1/health/meals",
        headers=headers,
        json={"class_code": "GRILLED_CHICKEN_BREAST", "grams": 200.0, "meal_type": "LUNCH"},
    )
    assert meal_res.status_code == 201
    assert meal_res.json()["protein_g"] == 62.0

    supp_res = await async_client.post(
        "/api/v1/health/supplements",
        headers=headers,
        json={"supplement_name": "Creatine", "dosage_label": "5g", "reminder_time": "08:00"},
    )
    assert supp_res.status_code == 201

    # 3. T-M3-10: Routines & Workout Sessions (Volume + 1RM + PR)
    routine_res = await async_client.post(
        "/api/v1/routines",
        headers=headers,
        json={
            "name": "Test Push Day",
            "split_type": "PUSH_PULL_LEGS",
            "scheduled_weekdays": [1, 4],
            "exercises": [{"exercise_code": "BARBELL_BENCH_PRESS", "target_sets": 3}],
        },
    )
    assert routine_res.status_code == 201
    routine_id = routine_res.json()["id"]
    assert routine_res.json()["exercises"][0]["exercise_code"] == "BARBELL_BENCH_PRESS"

    sess_res = await async_client.post(
        "/api/v1/workouts/sessions",
        headers=headers,
        json={
            "routine_id": routine_id,
            "session_title": "Push Session 1",
            "duration_seconds": 3700,
            "sets": [
                {"exercise_code": "BARBELL_BENCH_PRESS", "set_number": 1, "weight_kg": 80.0, "reps": 8, "rpe": 8.0},
                {"exercise_code": "BARBELL_BENCH_PRESS", "set_number": 2, "weight_kg": 85.0, "reps": 6, "rpe": 8.5},
            ],
        },
    )
    assert sess_res.status_code == 201
    sess_data = sess_res.json()
    assert sess_data["total_volume_kg"] == 1150.0
    assert sess_data["sets"][0]["is_pr"] is True
    assert sess_data["sets"][1]["estimated_1rm"] > sess_data["sets"][0]["estimated_1rm"]

    # 4. T-M3-07: Sync Push (LWW + max(steps_count) + Idempotent) & Pull
    sync_bio_id = str(uuid.uuid4())
    push1 = await async_client.post(
        "/api/v1/sync/push",
        headers=headers,
        json={
            "biometric_logs": [
                {"id": sync_bio_id, "weight_kg": 73.0, "logged_date": "2026-11-19", "updated_at": "2026-11-19T10:00:00Z"}
            ],
            "daily_health_logs": [
                {"log_date": "2026-11-19", "steps_count": 9000, "water_ml": 2200, "updated_at": "2026-11-19T10:00:00Z"}
            ],
        },
    )
    assert push1.status_code == 200

    # Push older timestamp with smaller steps -> must keep 9000 steps and 73.0 kg
    push2 = await async_client.post(
        "/api/v1/sync/push",
        headers=headers,
        json={
            "biometric_logs": [
                {"id": sync_bio_id, "weight_kg": 71.0, "logged_date": "2026-11-19", "updated_at": "2026-11-19T08:00:00Z"}
            ],
            "daily_health_logs": [
                {"log_date": "2026-11-19", "steps_count": 4000, "water_ml": 1500, "updated_at": "2026-11-19T12:00:00Z"}
            ],
        },
    )
    assert push2.status_code == 200

    pull_res = await async_client.get("/api/v1/sync/pull", headers=headers)
    assert pull_res.status_code == 200
    pulled = pull_res.json()["records"]
    pulled_bio = next(b for b in pulled["biometric_logs"] if b["id"] == sync_bio_id)
    assert pulled_bio["weight_kg"] == 73.0
    pulled_daily = next(d for d in pulled["daily_health_logs"] if d["log_date"] == "2026-11-19")
    assert pulled_daily["steps_count"] == 9000

    # 5. T-M3-11: Analytics Summary (Weekly Volume, 6-axis Radar, PR Wall)
    ana_res = await async_client.get("/api/v1/analytics/summary?days=90", headers=headers)
    assert ana_res.status_code == 200
    ana = ana_res.json()
    assert len(ana["weekly_volume"]) >= 1
    assert ana["muscle_radar"]["chest"] == 2
    assert len(ana["personal_records"]) >= 1

    # Cleanup user created during test
    del_res = await async_client.delete("/api/v1/users/me", headers=headers)
    assert del_res.status_code == 200

