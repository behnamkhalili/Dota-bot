"""change dim_player lastMatchId type to BigInteger

Revision ID: 9d3d3fae8bc1
Revises: b377dc979a61
Create Date: 2026-08-10 00:44:37.040340

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "9d3d3fae8bc1"
down_revision: Union[str, Sequence[str], None] = "b377dc979a61"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.alter_column(
        "dim_player",
        "lastMatchId",
        type_=sa.BigInteger,
        existing_type=sa.Integer,
        existing_nullable=True,
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.alter_column(
        "dim_player",
        "lastMatchId",
        type_=sa.Integer,
        existing_type=sa.BigInteger,
        existing_nullable=True,
    )
