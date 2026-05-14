from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = "20260514_stage_b_init"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "learner_profile",
        sa.Column("learner_id", sa.String(), primary_key=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("last_active_at", sa.DateTime(timezone=True), nullable=False),
    )

    op.create_table(
        "knowledge_state",
        sa.Column("learner_id", sa.String(), primary_key=True),
        sa.Column("knowledge_id", sa.String(), primary_key=True),
        sa.Column("mastery", sa.Float(), nullable=False),
        sa.Column("alpha", sa.Float(), nullable=False),
        sa.Column("beta", sa.Float(), nullable=False),
        sa.Column("attempts", sa.Integer(), nullable=False),
        sa.Column("correct_count", sa.Integer(), nullable=False),
        sa.Column("last_attempt", sa.DateTime(timezone=True), nullable=True),
        sa.Column("streak", sa.Integer(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_knowledge_state_learner_id", "knowledge_state", ["learner_id"])

    op.create_table(
        "review_item",
        sa.Column("learner_id", sa.String(), primary_key=True),
        sa.Column("knowledge_id", sa.String(), primary_key=True),
        sa.Column("easiness_factor", sa.Float(), nullable=False),
        sa.Column("interval_days", sa.Float(), nullable=False),
        sa.Column("repetition", sa.Integer(), nullable=False),
        sa.Column("next_review", sa.DateTime(timezone=True), nullable=False),
        sa.Column("last_review", sa.DateTime(timezone=True), nullable=True),
        sa.Column("total_reviews", sa.Integer(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index(
        "ix_review_item_learner_id_due_at",
        "review_item",
        ["learner_id", "next_review"],
    )

    op.create_table(
        "attempt",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("learner_id", sa.String(), nullable=False),
        sa.Column("knowledge_id", sa.String(), nullable=False),
        sa.Column("is_correct", sa.Boolean(), nullable=False),
        sa.Column("time_spent_seconds", sa.Float(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("correlation_id", sa.String(), nullable=True),
    )
    op.create_index("ix_attempt_learner_id", "attempt", ["learner_id"])
    op.create_index("ix_attempt_knowledge_id", "attempt", ["knowledge_id"])
    op.create_index("ix_attempt_created_at", "attempt", ["created_at"])
    op.create_index("ix_attempt_correlation_id", "attempt", ["correlation_id"])

    op.create_table(
        "event_log",
        sa.Column("event_id", sa.String(), primary_key=True),
        sa.Column("type", sa.String(), nullable=False),
        sa.Column("source", sa.String(), nullable=False),
        sa.Column("learner_id", sa.String(), nullable=False),
        sa.Column("timestamp", sa.DateTime(timezone=True), nullable=False),
        sa.Column("correlation_id", sa.String(), nullable=True),
        sa.Column("payload", postgresql.JSONB(), nullable=False),
    )
    op.create_index("ix_event_log_type", "event_log", ["type"])
    op.create_index("ix_event_log_learner_id", "event_log", ["learner_id"])
    op.create_index("ix_event_log_timestamp", "event_log", ["timestamp"])
    op.create_index("ix_event_log_correlation_id", "event_log", ["correlation_id"])


def downgrade() -> None:
    op.drop_index("ix_event_log_correlation_id", table_name="event_log")
    op.drop_index("ix_event_log_timestamp", table_name="event_log")
    op.drop_index("ix_event_log_learner_id", table_name="event_log")
    op.drop_index("ix_event_log_type", table_name="event_log")
    op.drop_table("event_log")

    op.drop_index("ix_attempt_correlation_id", table_name="attempt")
    op.drop_index("ix_attempt_created_at", table_name="attempt")
    op.drop_index("ix_attempt_knowledge_id", table_name="attempt")
    op.drop_index("ix_attempt_learner_id", table_name="attempt")
    op.drop_table("attempt")

    op.drop_index("ix_review_item_learner_id_due_at", table_name="review_item")
    op.drop_table("review_item")

    op.drop_index("ix_knowledge_state_learner_id", table_name="knowledge_state")
    op.drop_table("knowledge_state")

    op.drop_table("learner_profile")

