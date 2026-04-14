"""create otp tables

Revision ID: 0001_create_otp_tables
Revises: 
Create Date: 2026-03-28 15:50:00.000000

"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "0001_create_otp_tables"
down_revision: str | None = None
branch_labels: str | None = None
depends_on: str | None = None


def upgrade() -> None:
    op.create_table(
        "otp_requests",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("phone_number", sa.String(length=32), nullable=False),
        sa.Column("channel", sa.String(length=16), nullable=False),
        sa.Column(
            "status",
            sa.Enum(
                "pending",
                "approved",
                "failed",
                "expired",
                "canceled",
                name="otpstatus",
                native_enum=False,
            ),
            nullable=False,
        ),
        sa.Column("twilio_verification_sid", sa.String(length=64), nullable=True),
        sa.Column("twilio_service_sid", sa.String(length=64), nullable=False),
        sa.Column("attempt_count", sa.Integer(), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("twilio_verification_sid", name="uq_otp_requests_twilio_verification_sid"),
    )
    op.create_index("ix_otp_requests_phone_number", "otp_requests", ["phone_number"])
    op.create_index("ix_otp_requests_status", "otp_requests", ["status"])
    op.create_index(
        "ix_otp_requests_twilio_verification_sid",
        "otp_requests",
        ["twilio_verification_sid"],
    )

    op.create_table(
        "otp_events",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("otp_request_id", sa.Integer(), sa.ForeignKey("otp_requests.id"), nullable=False),
        sa.Column(
            "event_type",
            sa.Enum(
                "send_attempt",
                "verify_attempt",
                "status_update",
                name="otpeventtype",
                native_enum=False,
            ),
            nullable=False,
        ),
        sa.Column(
            "status",
            sa.Enum(
                "pending",
                "approved",
                "failed",
                "expired",
                "canceled",
                name="otpstatus",
                native_enum=False,
            ),
            nullable=False,
        ),
        sa.Column("detail_json", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_otp_events_otp_request_id", "otp_events", ["otp_request_id"])


def downgrade() -> None:
    op.drop_index("ix_otp_events_otp_request_id", table_name="otp_events")
    op.drop_table("otp_events")

    op.drop_index("ix_otp_requests_twilio_verification_sid", table_name="otp_requests")
    op.drop_index("ix_otp_requests_status", table_name="otp_requests")
    op.drop_index("ix_otp_requests_phone_number", table_name="otp_requests")
    op.drop_table("otp_requests")
