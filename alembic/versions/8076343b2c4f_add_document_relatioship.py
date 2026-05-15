"""add document relatioship

Revision ID: 8076343b2c4f
Revises: b2df607963fc
Create Date: 2026-05-15 09:51:18.052079

"""

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "8076343b2c4f"
down_revision: Union[str, Sequence[str], None] = "b2df607963fc"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
