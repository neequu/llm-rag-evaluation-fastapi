"""add document relatioship

Revision ID: b2df607963fc
Revises: 8e0d9430e07b
Create Date: 2026-05-15 09:48:20.692915

"""

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "b2df607963fc"
down_revision: Union[str, Sequence[str], None] = "8e0d9430e07b"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
