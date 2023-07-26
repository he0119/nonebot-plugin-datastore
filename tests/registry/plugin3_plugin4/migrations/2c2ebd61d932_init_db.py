"""init db

Revision ID: 2c2ebd61d932
Revises: 
Create Date: 2023-07-26 16:29:04.779418

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "2c2ebd61d932"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "plugin3_plugin4_test",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("example_id", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(
            ["example_id"],
            ["plugin3_example.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table("plugin3_plugin4_test")
    # ### end Alembic commands ###