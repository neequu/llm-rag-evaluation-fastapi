"""document relation

Revision ID: 6e139fe0efbd
Revises: 8076343b2c4f
Create Date: 2026-05-16 08:35:14.641816

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '6e139fe0efbd'
down_revision: Union[str, Sequence[str], None] = '8076343b2c4f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
