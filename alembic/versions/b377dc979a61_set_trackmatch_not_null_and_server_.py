"""set trackMatch not null and server_defult: False and set the existed values to false

Revision ID: b377dc979a61
Revises: b677a97f8fdc
Create Date: 2026-08-09 19:23:23.130367

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "b377dc979a61"
down_revision: Union[str, Sequence[str], None] = "b677a97f8fdc"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute('UPDATE dim_player SET "trackMatches" = false')
    op.alter_column(
        "dim_player", "trackMatches", nullable=False, server_default=sa.text("false")
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.alter_column("dim_player", "trackMatches", nullable=True, server_default=None)
