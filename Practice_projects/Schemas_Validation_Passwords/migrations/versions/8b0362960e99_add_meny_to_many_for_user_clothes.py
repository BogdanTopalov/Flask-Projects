"""add meny to many for user clothes

Revision ID: 8b0362960e99
Revises: 0f627eac74a2
Create Date: 2023-02-25 16:15:23.012346

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '8b0362960e99'
down_revision = '0f627eac74a2'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('user_clothes',
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.Column('clothes_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['clothes_id'], ['clothes.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], )
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('user_clothes')
    # ### end Alembic commands ###