"""added filetype

Revision ID: 25531797da5d
Revises: 06c349300911
Create Date: 2023-05-25 16:10:21.743088

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '25531797da5d'
down_revision = '06c349300911'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('files', sa.Column('filetype', sa.String))

def downgrade():
    op.drop_column('files', 'filetype')