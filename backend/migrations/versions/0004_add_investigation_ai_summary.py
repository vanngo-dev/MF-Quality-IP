"""Add investigation AI summary.

Revision ID: 0004_ai_summary
Revises: 0003_ingestion
Create Date: 2026-06-17
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa

revision: str = "0004_ai_summary"
down_revision: str | None = "0003_ingestion"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("investigations", sa.Column("ai_summary", sa.JSON(), nullable=True))


def downgrade() -> None:
    op.drop_column("investigations", "ai_summary")
