"""add status to analysis_runs

Revision ID: abc123def456
Revises: 4dc1b9d4bf72
Create Date: 2025-01-15 10:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'abc123def456'
down_revision: Union[str, Sequence[str], None] = '4dc1b9d4bf72'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Create enum type
    op.execute("CREATE TYPE analysis_status AS ENUM ('pending', 'processing', 'completed', 'failed')")
    
    # Add status column with default value
    op.add_column(
        'analysis_runs',
        sa.Column('status', sa.Enum('pending', 'processing', 'completed', 'failed', name='analysis_status', create_type=False), 
                  server_default=sa.text("'pending'"), nullable=False)
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('analysis_runs', 'status')
    op.execute("DROP TYPE analysis_status")

