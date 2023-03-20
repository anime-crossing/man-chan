"""invoices

Revision ID: c5b97a6267b8
Revises: 298629fea1bc
Create Date: 2023-03-01 13:28:02.936854

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c5b97a6267b8'
down_revision = '298629fea1bc'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('invoice_participants',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('invoice_id', sa.String(), nullable=True),
    sa.Column('participant_id', sa.Integer(), nullable=True),
    sa.Column('amount_owed', sa.Float(), nullable=True),
    sa.Column('paid', sa.Boolean(), nullable=True),
    sa.Column('paid_on', sa.Integer(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('invoices',
    sa.Column('id', sa.String(), nullable=False),
    sa.Column('payer_id', sa.Integer(), nullable=True),
    sa.Column('total_cost', sa.Float(), nullable=True),
    sa.Column('desc', sa.String(), nullable=True),
    sa.Column('date', sa.Integer(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('invoices')
    op.drop_table('invoice_participants')
    # ### end Alembic commands ###