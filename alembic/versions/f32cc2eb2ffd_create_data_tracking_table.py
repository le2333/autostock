"""create data_tracking table

Revision ID: f32cc2eb2ffd
Revises: 9b27982e2a2d
Create Date: 2025-06-21 02:08:44.578133

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision: str = "f32cc2eb2ffd"
down_revision: Union[str, Sequence[str], None] = "9b27982e2a2d"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "data_tracking",
        sa.Column("symbol", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("name", sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column("has_daily", sa.Boolean(), nullable=False),
        sa.Column("daily_start_date", sa.Date(), nullable=True),
        sa.Column("daily_end_date", sa.Date(), nullable=True),
        sa.Column("daily_last_sync", sa.DateTime(), nullable=True),
        sa.Column("purpose", sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column("auto_sync", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("symbol"),
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table("data_tracking")
    # ### end Alembic commands ###
