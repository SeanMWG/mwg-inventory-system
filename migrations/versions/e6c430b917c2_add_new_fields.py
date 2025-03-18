"""Add new fields

Revision ID: e6c430b917c2
Revises: 6f8e3383ad9d
Create Date: 2025-03-18 10:18:51.435855

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import text

# revision identifiers, used by Alembic.
revision = 'e6c430b917c2'
down_revision = '6f8e3383ad9d'
branch_labels = None
depends_on = None


def upgrade():
    # ### Modified commands to preserve data ### 
    # First, add the new inventory_id column without making it NOT NULL yet
    with op.batch_alter_table('checkout', schema=None) as batch_op:
        batch_op.add_column(sa.Column('inventory_id', sa.Integer(), nullable=True))
    
    # Copy data from item_id to inventory_id
    op.execute(text('UPDATE checkout SET inventory_id = item_id'))
    
    # Now make inventory_id NOT NULL and update foreign key
    with op.batch_alter_table('checkout', schema=None) as batch_op:
        batch_op.alter_column('inventory_id', nullable=False)
        batch_op.create_foreign_key('fk_checkout_inventory_id', 'inventory', ['inventory_id'], ['id'])
    
    # We'll leave the old columns (item_id, user_id) in place for now
    # This preserves the data while allowing the models to work correctly
    
    # ### end Alembic commands ###


def downgrade():
    # ### commands to reverse the migration ### 
    with op.batch_alter_table('checkout', schema=None) as batch_op:
        batch_op.drop_constraint('fk_checkout_inventory_id', type_='foreignkey')
        batch_op.drop_column('inventory_id')
    # ### end Alembic commands ###
