"""Initial 12-table VigorAI schema (11 core + food_nutrition_catalog)

Revision ID: 0001_initial_schema
Revises:
Create Date: 2026-11-18 18:45:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "0001_initial_schema"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. users
    op.create_table(
        "users",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("password_hash", sa.String(length=255), nullable=False),
        sa.Column("full_name", sa.String(length=150), nullable=False),
        sa.Column("gender", sa.String(length=20), nullable=False),
        sa.Column("birth_date", sa.Date(), nullable=True),
        sa.Column("height_cm", sa.Float(), nullable=False),
        sa.Column("activity_level", sa.String(length=30), nullable=False),
        sa.Column("fitness_goal", sa.String(length=20), nullable=False),
        sa.Column("avatar_preset", sa.String(length=30), nullable=False),
        sa.Column("medical_disclaimer_accepted", sa.Boolean(), nullable=False),
        sa.Column("disclaimer_accepted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_users_email", "users", ["email"], unique=True)

    # 2. food_nutrition_catalog
    op.create_table(
        "food_nutrition_catalog",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("class_code", sa.String(length=80), nullable=False),
        sa.Column("name_vi", sa.String(length=150), nullable=False),
        sa.Column("name_en", sa.String(length=150), nullable=False),
        sa.Column("kcal_per_100g", sa.Float(), nullable=False),
        sa.Column("protein_per_100g", sa.Float(), nullable=False),
        sa.Column("carbs_per_100g", sa.Float(), nullable=False),
        sa.Column("fat_per_100g", sa.Float(), nullable=False),
        sa.Column("default_serving_g", sa.Float(), nullable=False),
        sa.Column("source_standard", sa.String(length=80), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_food_nutrition_catalog_class_code",
        "food_nutrition_catalog",
        ["class_code"],
        unique=True,
    )

    # 3. exercises
    op.create_table(
        "exercises",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("code", sa.String(length=80), nullable=False),
        sa.Column("name_vi", sa.String(length=150), nullable=False),
        sa.Column("name_en", sa.String(length=150), nullable=False),
        sa.Column("equipment_type", sa.String(length=30), nullable=False),
        sa.Column("model_3d_glb_url", sa.String(length=500), nullable=False),
        sa.Column("asset_checksum", sa.String(length=128), nullable=False),
        sa.Column(
            "primary_muscles",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
        ),
        sa.Column(
            "secondary_muscles",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
        ),
        sa.Column(
            "stabilizer_muscles",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
        ),
        sa.Column(
            "phase_keyframes",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
        ),
        sa.Column(
            "bad_form_warnings",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
        ),
        sa.Column(
            "setup_guide",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_exercises_code", "exercises", ["code"], unique=True)
    op.create_index(
        "ix_exercises_primary_muscles_gin",
        "exercises",
        ["primary_muscles"],
        unique=False,
        postgresql_using="gin",
    )

    # 4. biometric_logs
    op.create_table(
        "biometric_logs",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("weight_kg", sa.Float(), nullable=False),
        sa.Column("body_fat_pct", sa.Float(), nullable=True),
        sa.Column("muscle_mass_kg", sa.Float(), nullable=True),
        sa.Column("bmi", sa.Float(), nullable=False),
        sa.Column(
            "circumferences_cm",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
        ),
        sa.Column("logged_date", sa.Date(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_biometric_user_date",
        "biometric_logs",
        ["user_id", "logged_date"],
        unique=False,
    )

    # 5. daily_health_logs
    op.create_table(
        "daily_health_logs",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("log_date", sa.Date(), nullable=False),
        sa.Column("steps_count", sa.Integer(), nullable=False),
        sa.Column("distance_km", sa.Float(), nullable=False),
        sa.Column("active_calories_kcal", sa.Integer(), nullable=False),
        sa.Column("water_ml", sa.Integer(), nullable=False),
        sa.Column("target_water_ml", sa.Integer(), nullable=False),
        sa.Column("sleep_hours", sa.Float(), nullable=False),
        sa.Column("sleep_quality_score", sa.Integer(), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id", "log_date", name="uq_daily_health_user_date"),
    )

    # 6. supplement_schedules
    op.create_table(
        "supplement_schedules",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("supplement_name", sa.String(length=120), nullable=False),
        sa.Column("dosage_label", sa.String(length=80), nullable=False),
        sa.Column("reminder_time", sa.Time(), nullable=False),
        sa.Column("workout_days_only", sa.Boolean(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_supplement_user_active",
        "supplement_schedules",
        ["user_id", "is_active"],
        unique=False,
    )

    # 7. meal_logs
    op.create_table(
        "meal_logs",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("catalog_food_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("meal_type", sa.String(length=20), nullable=False),
        sa.Column("image_url", sa.String(length=500), nullable=True),
        sa.Column(
            "ai_detected_items",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
        ),
        sa.Column("total_calories", sa.Float(), nullable=False),
        sa.Column("protein_g", sa.Float(), nullable=False),
        sa.Column("carbs_g", sa.Float(), nullable=False),
        sa.Column("fat_g", sa.Float(), nullable=False),
        sa.Column("logged_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(
            ["catalog_food_id"], ["food_nutrition_catalog.id"], ondelete="SET NULL"
        ),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_meal_user_logged", "meal_logs", ["user_id", "logged_at"], unique=False
    )

    # 8. workout_routines
    op.create_table(
        "workout_routines",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("name", sa.String(length=150), nullable=False),
        sa.Column("split_type", sa.String(length=40), nullable=False),
        sa.Column(
            "scheduled_weekdays",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
        ),
        sa.Column("is_template", sa.Boolean(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_routine_user_deleted",
        "workout_routines",
        ["user_id", "deleted_at"],
        unique=False,
    )

    # 9. routine_exercises
    op.create_table(
        "routine_exercises",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("routine_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("exercise_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("order_index", sa.Integer(), nullable=False),
        sa.Column("superset_group_id", sa.Integer(), nullable=True),
        sa.Column("target_sets", sa.Integer(), nullable=False),
        sa.Column("target_rep_min", sa.Integer(), nullable=False),
        sa.Column("target_rep_max", sa.Integer(), nullable=False),
        sa.Column("default_rest_seconds", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["exercise_id"], ["exercises.id"], ondelete="RESTRICT"
        ),
        sa.ForeignKeyConstraint(
            ["routine_id"], ["workout_routines.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_routine_ex_order",
        "routine_exercises",
        ["routine_id", "order_index"],
        unique=False,
    )

    # 10. workout_sessions
    op.create_table(
        "workout_sessions",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("routine_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("session_title", sa.String(length=150), nullable=False),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("duration_seconds", sa.Integer(), nullable=False),
        sa.Column("total_volume_kg", sa.Float(), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(
            ["routine_id"], ["workout_routines.id"], ondelete="SET NULL"
        ),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_session_user_started",
        "workout_sessions",
        ["user_id", "started_at"],
        unique=False,
    )

    # 11. workout_sets
    op.create_table(
        "workout_sets",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("session_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("exercise_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("set_number", sa.Integer(), nullable=False),
        sa.Column("set_type", sa.String(length=20), nullable=False),
        sa.Column("weight_kg", sa.Float(), nullable=False),
        sa.Column("reps", sa.Integer(), nullable=False),
        sa.Column("rpe", sa.Float(), nullable=True),
        sa.Column("estimated_1rm", sa.Float(), nullable=False),
        sa.Column("is_pr", sa.Boolean(), nullable=False),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["exercise_id"], ["exercises.id"], ondelete="RESTRICT"
        ),
        sa.ForeignKeyConstraint(
            ["session_id"], ["workout_sessions.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_set_session_ex_num",
        "workout_sets",
        ["session_id", "exercise_id", "set_number"],
        unique=False,
    )

    # 12. ai_readiness_logs
    op.create_table(
        "ai_readiness_logs",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("target_date", sa.Date(), nullable=False),
        sa.Column("readiness_score", sa.Float(), nullable=False),
        sa.Column("readiness_level", sa.String(length=20), nullable=False),
        sa.Column(
            "muscle_fatigue_map",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
        ),
        sa.Column(
            "weight_recommendations",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
        ),
        sa.Column(
            "feature_snapshot",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
        ),
        sa.Column("model_version", sa.String(length=60), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "user_id", "target_date", name="uq_ai_readiness_user_date"
        ),
    )


def downgrade() -> None:
    op.drop_table("ai_readiness_logs")
    op.drop_index("ix_set_session_ex_num", table_name="workout_sets")
    op.drop_table("workout_sets")
    op.drop_index("ix_session_user_started", table_name="workout_sessions")
    op.drop_table("workout_sessions")
    op.drop_index("ix_routine_ex_order", table_name="routine_exercises")
    op.drop_table("routine_exercises")
    op.drop_index("ix_routine_user_deleted", table_name="workout_routines")
    op.drop_table("workout_routines")
    op.drop_index("ix_meal_user_logged", table_name="meal_logs")
    op.drop_table("meal_logs")
    op.drop_index("ix_supplement_user_active", table_name="supplement_schedules")
    op.drop_table("supplement_schedules")
    op.drop_table("daily_health_logs")
    op.drop_index("ix_biometric_user_date", table_name="biometric_logs")
    op.drop_table("biometric_logs")
    op.drop_index("ix_exercises_primary_muscles_gin", table_name="exercises")
    op.drop_index("ix_exercises_code", table_name="exercises")
    op.drop_table("exercises")
    op.drop_index(
        "ix_food_nutrition_catalog_class_code", table_name="food_nutrition_catalog"
    )
    op.drop_table("food_nutrition_catalog")
    op.drop_index("ix_users_email", table_name="users")
    op.drop_table("users")
