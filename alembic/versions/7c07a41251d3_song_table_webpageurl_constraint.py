"""song table webpageurl constraint

Revision ID: 7c07a41251d3
Revises: 1b97a3238621
Create Date: 2025-05-29 22:44:02.531220

"""
from alembic import op


# revision identifiers, used by Alembic.
revision = '7c07a41251d3'
down_revision = '1b97a3238621'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_unique_constraint("uq_song_webpage_url", "song", ["webpage_url"])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    pass
    # ### end Alembic commands ###
