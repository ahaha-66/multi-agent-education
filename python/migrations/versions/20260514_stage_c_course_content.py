from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = "20260514_stage_c_course_content"
down_revision = "20260514_stage_b_init"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "course",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("code", sa.String(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("subject", sa.String(), nullable=False),
        sa.Column("version", sa.String(), nullable=False, server_default="1.0"),
        sa.Column("grade_level", sa.Integer(), nullable=True),
        sa.Column("description", sa.String(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_course_code", "course", ["code"], unique=True)
    op.create_index("ix_course_subject", "course", ["subject"])

    op.create_table(
        "chapter",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("course_id", sa.String(), nullable=False),
        sa.Column("code", sa.String(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("order_index", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("description", sa.String(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_chapter_course_id", "chapter", ["course_id"])

    op.create_table(
        "knowledge_point",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("chapter_id", sa.String(), nullable=False),
        sa.Column("course_id", sa.String(), nullable=False),
        sa.Column("code", sa.String(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("difficulty", sa.Float(), nullable=False, server_default="0.5"),
        sa.Column("description", sa.String(), nullable=True),
        sa.Column("tags", postgresql.JSONB(), nullable=False, server_default="[]"),
        sa.Column("order_index", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("version", sa.String(), nullable=False, server_default="1.0"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_knowledge_point_code", "knowledge_point", ["code"], unique=True)
    op.create_index("ix_knowledge_point_chapter_id", "knowledge_point", ["chapter_id"])
    op.create_index("ix_knowledge_point_course_id", "knowledge_point", ["course_id"])

    op.create_table(
        "knowledge_edge",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("source_kp_id", sa.String(), nullable=False),
        sa.Column("target_kp_id", sa.String(), nullable=False),
        sa.Column("relation_type", sa.String(), nullable=False, server_default="prerequisite"),
        sa.Column("strength", sa.Float(), nullable=False, server_default="1.0"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_knowledge_edge_source", "knowledge_edge", ["source_kp_id"])
    op.create_index("ix_knowledge_edge_target", "knowledge_edge", ["target_kp_id"])

    op.create_table(
        "exercise",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("knowledge_point_id", sa.String(), nullable=False),
        sa.Column("chapter_id", sa.String(), nullable=False),
        sa.Column("course_id", sa.String(), nullable=False),
        sa.Column("code", sa.String(), nullable=False),
        sa.Column("type", sa.String(), nullable=False, server_default="single_choice"),
        sa.Column("difficulty", sa.Float(), nullable=False, server_default="0.5"),
        sa.Column("content", postgresql.JSONB(), nullable=False),
        sa.Column("answer", postgresql.JSONB(), nullable=False),
        sa.Column("analysis", postgresql.JSONB(), nullable=True),
        sa.Column("hint_levels", postgresql.JSONB(), nullable=False, server_default="[]"),
        sa.Column("tags", postgresql.JSONB(), nullable=False, server_default="[]"),
        sa.Column("version", sa.String(), nullable=False, server_default="1.0"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_exercise_code", "exercise", ["code"], unique=True)
    op.create_index("ix_exercise_kp_id", "exercise", ["knowledge_point_id"])
    op.create_index("ix_exercise_chapter_id", "exercise", ["chapter_id"])
    op.create_index("ix_exercise_course_id", "exercise", ["course_id"])

    op.create_table(
        "learner_exercise_history",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("learner_id", sa.String(), nullable=False),
        sa.Column("exercise_id", sa.String(), nullable=False),
        sa.Column("is_correct", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("attempt_count", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("last_attempt_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("first_attempt_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("correlation_id", sa.String(), nullable=True),
    )
    op.create_index("ix_learner_exercise_learner_id", "learner_exercise_history", ["learner_id"])
    op.create_index("ix_learner_exercise_exercise_id", "learner_exercise_history", ["exercise_id"])


def downgrade() -> None:
    op.drop_index("ix_learner_exercise_exercise_id", table_name="learner_exercise_history")
    op.drop_index("ix_learner_exercise_learner_id", table_name="learner_exercise_history")
    op.drop_table("learner_exercise_history")

    op.drop_index("ix_exercise_course_id", table_name="exercise")
    op.drop_index("ix_exercise_chapter_id", table_name="exercise")
    op.drop_index("ix_exercise_kp_id", table_name="exercise")
    op.drop_index("ix_exercise_code", table_name="exercise")
    op.drop_table("exercise")

    op.drop_index("ix_knowledge_edge_target", table_name="knowledge_edge")
    op.drop_index("ix_knowledge_edge_source", table_name="knowledge_edge")
    op.drop_table("knowledge_edge")

    op.drop_index("ix_knowledge_point_course_id", table_name="knowledge_point")
    op.drop_index("ix_knowledge_point_chapter_id", table_name="knowledge_point")
    op.drop_index("ix_knowledge_point_code", table_name="knowledge_point")
    op.drop_table("knowledge_point")

    op.drop_index("ix_chapter_course_id", table_name="chapter")
    op.drop_table("chapter")

    op.drop_index("ix_course_subject", table_name="course")
    op.drop_index("ix_course_code", table_name="course")
    op.drop_table("course")
