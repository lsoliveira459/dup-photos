"""empty message

Revision ID: 6bd5b529ea78
Revises: 234914225185
Create Date: 2023-06-02 14:27:20.563794

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '6bd5b529ea78'
down_revision = '234914225185'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('hashes',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('hashtype', sa.String(), nullable=True, default=""),
    sa.Column('hashvalue', sa.String(), nullable=False, default=""),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('association_table',
    sa.Column('file_id', sa.Integer(), nullable=False),
    sa.Column('hash_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['file_id'], ['files.id'], ),
    sa.ForeignKeyConstraint(['hash_id'], ['hashes.id'], ),
    sa.PrimaryKeyConstraint('file_id', 'hash_id')
    )
    op.add_column('files', sa.Column('id', sa.Integer(), nullable=False))
    op.drop_column('files', 'sha224')
    op.drop_column('files', 'sm3')
    op.drop_column('files', 'sha384')
    op.drop_column('files', 'blake2s')
    op.drop_column('files', 'sha1')
    op.drop_column('files', 'sha512_224')
    op.drop_column('files', 'md5')
    op.drop_column('files', 'sha3_224')
    op.drop_column('files', 'shake_256')
    op.drop_column('files', 'blake2b')
    op.drop_column('files', 'visual')
    op.drop_column('files', 'shake_128')
    op.drop_column('files', 'mdc2')
    op.drop_column('files', 'sha3_256')
    op.drop_column('files', 'sha512')
    op.drop_column('files', 'sha3_512')
    op.drop_column('files', 'md5-sha1')
    op.drop_column('files', 'sha256')
    op.drop_column('files', 'sha3_384')
    op.drop_column('files', 'md4')
    op.drop_column('files', 'ripemd160')
    op.drop_column('files', 'whirlpool')
    op.drop_column('files', 'sha512_256')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('files', sa.Column('sha512_256', sa.VARCHAR(), nullable=True))
    op.add_column('files', sa.Column('whirlpool', sa.VARCHAR(), nullable=True))
    op.add_column('files', sa.Column('ripemd160', sa.VARCHAR(), nullable=True))
    op.add_column('files', sa.Column('md4', sa.VARCHAR(), nullable=True))
    op.add_column('files', sa.Column('sha3_384', sa.VARCHAR(), nullable=True))
    op.add_column('files', sa.Column('sha256', sa.VARCHAR(), nullable=True))
    op.add_column('files', sa.Column('md5-sha1', sa.VARCHAR(), nullable=True))
    op.add_column('files', sa.Column('sha3_512', sa.VARCHAR(), nullable=True))
    op.add_column('files', sa.Column('sha512', sa.VARCHAR(), nullable=True))
    op.add_column('files', sa.Column('sha3_256', sa.VARCHAR(), nullable=True))
    op.add_column('files', sa.Column('mdc2', sa.VARCHAR(), nullable=True))
    op.add_column('files', sa.Column('shake_128', sa.VARCHAR(), nullable=True))
    op.add_column('files', sa.Column('visual', sa.VARCHAR(), nullable=True))
    op.add_column('files', sa.Column('blake2b', sa.VARCHAR(), nullable=True))
    op.add_column('files', sa.Column('shake_256', sa.VARCHAR(), nullable=True))
    op.add_column('files', sa.Column('sha3_224', sa.VARCHAR(), nullable=True))
    op.add_column('files', sa.Column('md5', sa.VARCHAR(), nullable=True))
    op.add_column('files', sa.Column('sha512_224', sa.VARCHAR(), nullable=True))
    op.add_column('files', sa.Column('sha1', sa.VARCHAR(), nullable=True))
    op.add_column('files', sa.Column('blake2s', sa.VARCHAR(), nullable=True))
    op.add_column('files', sa.Column('sha384', sa.VARCHAR(), nullable=True))
    op.add_column('files', sa.Column('sm3', sa.VARCHAR(), nullable=True))
    op.add_column('files', sa.Column('sha224', sa.VARCHAR(), nullable=True))
    op.drop_column('files', 'id')
    op.drop_table('association_table')
    op.drop_table('hashes')
    # ### end Alembic commands ###
