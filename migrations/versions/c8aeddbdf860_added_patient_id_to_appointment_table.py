"""Added patient_id to appointment table

Revision ID: c8aeddbdf860
Revises: 15472e12fd91
Create Date: 2024-12-21 18:43:14.624886

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = 'c8aeddbdf860'
down_revision = '15472e12fd91'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('appointment', schema=None) as batch_op:
        batch_op.add_column(sa.Column('patient_id', sa.Integer(), nullable=False))
        batch_op.drop_column('patient_name')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('appointment', schema=None) as batch_op:
        batch_op.add_column(sa.Column('patient_name', mysql.VARCHAR(length=100), nullable=False))
        batch_op.drop_column('patient_id')

    # ### end Alembic commands ###