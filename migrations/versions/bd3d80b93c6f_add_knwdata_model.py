"""Add KNWData model

Revision ID: bd3d80b93c6f
Revises: 
Create Date: 2022-07-24 21:22:22.106165

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "bd3d80b93c6f"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "knw_data",
        sa.Column("dtg", sa.DateTime(), nullable=False),
        sa.Column("f010", sa.Float(), nullable=False),
        sa.Column("d010", sa.Float(), nullable=False),
        sa.Column("to10", sa.Float(), nullable=False),
        sa.Column("q010", sa.Float(), nullable=False),
        sa.Column("p010", sa.Float(), nullable=False),
        sa.Column("f020", sa.Float(), nullable=False),
        sa.Column("d020", sa.Float(), nullable=False),
        sa.Column("to20", sa.Float(), nullable=False),
        sa.Column("q020", sa.Float(), nullable=False),
        sa.Column("p020", sa.Float(), nullable=False),
        sa.Column("f040", sa.Float(), nullable=False),
        sa.Column("d040", sa.Float(), nullable=False),
        sa.Column("to40", sa.Float(), nullable=False),
        sa.Column("q040", sa.Float(), nullable=False),
        sa.Column("p040", sa.Float(), nullable=False),
        sa.Column("f060", sa.Float(), nullable=False),
        sa.Column("d060", sa.Float(), nullable=False),
        sa.Column("to60", sa.Float(), nullable=False),
        sa.Column("q060", sa.Float(), nullable=False),
        sa.Column("p060", sa.Float(), nullable=False),
        sa.Column("f080", sa.Float(), nullable=False),
        sa.Column("d080", sa.Float(), nullable=False),
        sa.Column("to80", sa.Float(), nullable=False),
        sa.Column("q080", sa.Float(), nullable=False),
        sa.Column("p080", sa.Float(), nullable=False),
        sa.Column("f0100", sa.Float(), nullable=False),
        sa.Column("d0100", sa.Float(), nullable=False),
        sa.Column("to100", sa.Float(), nullable=False),
        sa.Column("q0100", sa.Float(), nullable=False),
        sa.Column("p0100", sa.Float(), nullable=False),
        sa.Column("f0150", sa.Float(), nullable=False),
        sa.Column("d0150", sa.Float(), nullable=False),
        sa.Column("to150", sa.Float(), nullable=False),
        sa.Column("q0150", sa.Float(), nullable=False),
        sa.Column("p0150", sa.Float(), nullable=False),
        sa.Column("f0200", sa.Float(), nullable=False),
        sa.Column("d0200", sa.Float(), nullable=False),
        sa.Column("to200", sa.Float(), nullable=False),
        sa.Column("q0200", sa.Float(), nullable=False),
        sa.Column("p0200", sa.Float(), nullable=False),
        sa.PrimaryKeyConstraint("dtg"),
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table("knw_data")
    # ### end Alembic commands ###
