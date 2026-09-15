"""add_subscription_and_agency_tables

Revision ID: 2026_08_10_0003
Revises: 2026_08_10_0002
Create Date: 2026-08-10 20:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '2026_08_10_0003'
down_revision: Union[str, None] = '2026_08_10_0002'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Create Enums
    subscription_plan_enum = postgresql.ENUM('STARTER', 'PRO', 'ENTERPRISE', name='subscription_plan_enum')
    subscription_plan_enum.create(op.get_bind(), checkfirst=True)

    # 2. Create Agencies Table
    op.create_table(
        'agencies',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('city', sa.String(length=100), nullable=False),
        sa.Column('phone', sa.String(length=50), nullable=False),
        sa.Column('rc_number', sa.String(length=50), nullable=False),
        sa.Column('patente_number', sa.String(length=50), nullable=False),
        sa.Column('logo_url', sa.String(length=500), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index(op.f('ix_agencies_id'), 'agencies', ['id'], unique=False)
    op.create_index(op.f('ix_agencies_city'), 'agencies', ['city'], unique=False)
    op.create_index(op.f('ix_agencies_rc_number'), 'agencies', ['rc_number'], unique=True)
    op.create_index(op.f('ix_agencies_patente_number'), 'agencies', ['patente_number'], unique=True)

    # 3. Create Subscriptions Table
    op.create_table(
        'subscriptions',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column('agency_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('agencies.id', ondelete='CASCADE'), nullable=False),
        sa.Column('plan_name', sa.Enum('STARTER', 'PRO', 'ENTERPRISE', name='subscription_plan_enum'), nullable=False, server_default='STARTER'),
        sa.Column('max_vehicles', sa.Integer(), nullable=False, server_default='10'),
        sa.Column('start_date', sa.DateTime(timezone=True), nullable=False),
        sa.Column('end_date', sa.DateTime(timezone=True), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default=sa.text('true')),
        sa.Column('payment_notes', sa.String(length=500), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index(op.f('ix_subscriptions_id'), 'subscriptions', ['id'], unique=False)
    op.create_index(op.f('ix_subscriptions_agency_id'), 'subscriptions', ['agency_id'], unique=True)
    op.create_index(op.f('ix_subscriptions_plan_name'), 'subscriptions', ['plan_name'], unique=False)

    # 4. Add agency_id columns to users and vehicles if not present
    # Check/add agency_id to users
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    users_columns = [col['name'] for col in inspector.get_columns('users')]
    if 'agency_id' not in users_columns:
        op.add_column('users', sa.Column('agency_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('agencies.id', ondelete='SET NULL'), nullable=True))
        op.create_index(op.f('ix_users_agency_id'), 'users', ['agency_id'], unique=False)

    vehicles_columns = [col['name'] for col in inspector.get_columns('vehicles')]
    if 'agency_id' not in vehicles_columns:
        op.add_column('vehicles', sa.Column('agency_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('agencies.id', ondelete='CASCADE'), nullable=True))
        op.create_index(op.f('ix_vehicles_agency_id'), 'vehicles', ['agency_id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_subscriptions_plan_name'), table_name='subscriptions')
    op.drop_index(op.f('ix_subscriptions_agency_id'), table_name='subscriptions')
    op.drop_index(op.f('ix_subscriptions_id'), table_name='subscriptions')
    op.drop_table('subscriptions')

    op.drop_index(op.f('ix_agencies_patente_number'), table_name='agencies')
    op.drop_index(op.f('ix_agencies_rc_number'), table_name='agencies')
    op.drop_index(op.f('ix_agencies_city'), table_name='agencies')
    op.drop_index(op.f('ix_agencies_id'), table_name='agencies')
    op.drop_table('agencies')

    subscription_plan_enum = postgresql.ENUM('STARTER', 'PRO', 'ENTERPRISE', name='subscription_plan_enum')
    subscription_plan_enum.drop(op.get_bind(), checkfirst=True)
