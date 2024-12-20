"""Initial migration

Revision ID: 15472e12fd91
Revises: 
Create Date: 2024-12-16 16:58:45.873222

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '15472e12fd91'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('appointment',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('patient_name', sa.String(length=100), nullable=False),
    sa.Column('doctor_id', sa.Integer(), nullable=False),
    sa.Column('appointment_date', sa.DateTime(), nullable=False),
    sa.Column('notes', sa.Text(), nullable=True),
    sa.Column('is_cancelled', sa.Boolean(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('appointment')
    # ### end Alembic commands ###
