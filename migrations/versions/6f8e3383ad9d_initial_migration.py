"""Initial migration

Revision ID: 6f8e3383ad9d
Revises: 
Create Date: 2025-03-18 10:20:00

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '6f8e3383ad9d'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # This migration script is just a placeholder since the database already has the tables
    pass


def downgrade():
    # This is intentionally left empty as this is a placeholder for an already-applied migration
    pass
