"""create ticket tables

Revision ID: 4dc1b9d4bf72
Revises: 
Create Date: 2025-11-13 14:57:38.506271

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '4dc1b9d4bf72'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "analysis_runs",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("timezone('utc', now())"),
            nullable=False,
        ),
        sa.Column("summary", sa.Text(), nullable=True),
    )

    op.create_table(
        "tickets",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("timezone('utc', now())"),
            nullable=False,
        ),
    )

    op.create_table(
        "ticket_analysis",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column("analysis_run_id", sa.Integer(), sa.ForeignKey("analysis_runs.id", ondelete="CASCADE"), nullable=False),
        sa.Column("ticket_id", sa.Integer(), sa.ForeignKey("tickets.id", ondelete="CASCADE"), nullable=False),
        sa.Column("category", sa.String(length=100), nullable=False),
        sa.Column("priority", sa.String(length=50), nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
    )

    op.create_index("ix_ticket_analysis_analysis_run_id", "ticket_analysis", ["analysis_run_id"])
    op.create_index("ix_ticket_analysis_ticket_id", "ticket_analysis", ["ticket_id"])


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index("ix_ticket_analysis_ticket_id", table_name="ticket_analysis")
    op.drop_index("ix_ticket_analysis_analysis_run_id", table_name="ticket_analysis")
    op.drop_table("ticket_analysis")
    op.drop_table("tickets")
    op.drop_table("analysis_runs")
