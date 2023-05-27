"""visual removed from index

Revision ID: 234914225185
Revises: 25531797da5d
Create Date: 2023-05-27 00:24:58.295770

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '234914225185'
down_revision = '25531797da5d'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.drop_index("ix_files_visual")


def downgrade() -> None:
    op.create_index("ix_files_visual", 'files', ['visual'])
