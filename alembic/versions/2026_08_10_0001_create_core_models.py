"""create_core_models_user_customer_vehicle

Revision ID: 2026_08_10_0001
Revises: 
Create Date: 2026-08-10 19:16:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '2026_08_10_0001'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Create Enums
    user_role_enum = postgresql.ENUM('SUPERADMIN', 'AGENCY_MANAGER', 'AGENT', name='user_role_enum')
    user_role_enum.create(op.get_bind(), checkfirst=True)

    vehicle_status_enum = postgresql.ENUM('AVAILABLE', 'RENTED', 'MAINTENANCE', 'RESERVED', name='vehicle_status_enum')
    vehicle_status_enum.create(op.get_bind(), checkfirst=True)

    # 2. Create Users Table
    op.create_table(
        'users',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('password_hash', sa.String(length=255), nullable=False),
        sa.Column('role', sa.Enum('SUPERADMIN', 'AGENCY_MANAGER', 'AGENT', name='user_role_enum'), nullable=False, server_default='AGENT'),
        sa.Column('agency_location', sa.String(length=255), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default=sa.text('true')),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index(op.f('ix_users_id'), 'users', ['id'], unique=False)
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)
    op.create_index(op.f('ix_users_role'), 'users', ['role'], unique=False)

    # 3. Create Customers Table
    op.create_table(
        'customers',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column('full_name', sa.String(length=255), nullable=False),
        sa.Column('phone_number', sa.String(length=50), nullable=False),
        sa.Column('cin_or_passport', sa.String(length=50), nullable=False),
        sa.Column('driver_license_number', sa.String(length=50), nullable=False),
        sa.Column('document_scans', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('is_blacklisted', sa.Boolean(), nullable=False, server_default=sa.text('false')),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index(op.f('ix_customers_id'), 'customers', ['id'], unique=False)
    op.create_index(op.f('ix_customers_phone_number'), 'customers', ['phone_number'], unique=False)
    op.create_index(op.f('ix_customers_cin_or_passport'), 'customers', ['cin_or_passport'], unique=True)
    op.create_index(op.f('ix_customers_driver_license_number'), 'customers', ['driver_license_number'], unique=True)
    op.create_index(op.f('ix_customers_is_blacklisted'), 'customers', ['is_blacklisted'], unique=False)

    # 4. Create Vehicles Table
    op.create_table(
        'vehicles',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column('matriculation', sa.String(length=50), nullable=False),
        sa.Column('make_model', sa.String(length=255), nullable=False),
        sa.Column('year', sa.Integer(), nullable=False),
        sa.Column('current_mileage', sa.Integer(), nullable=False, server_default=sa.text('0')),
        sa.Column('daily_rate_mad', sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column('status', sa.Enum('AVAILABLE', 'RENTED', 'MAINTENANCE', 'RESERVED', name='vehicle_status_enum'), nullable=False, server_default='AVAILABLE'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index(op.f('ix_vehicles_id'), 'vehicles', ['id'], unique=False)
    op.create_index(op.f('ix_vehicles_matriculation'), 'vehicles', ['matriculation'], unique=True)
    op.create_index(op.f('ix_vehicles_status'), 'vehicles', ['status'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_vehicles_status'), table_name='vehicles')
    op.drop_index(op.f('ix_vehicles_matriculation'), table_name='vehicles')
    op.drop_index(op.f('ix_vehicles_id'), table_name='vehicles')
    op.drop_table('vehicles')

    op.drop_index(op.f('ix_customers_is_blacklisted'), table_name='customers')
    op.drop_index(op.f('ix_customers_driver_license_number'), table_name='customers')
    op.drop_index(op.f('ix_customers_cin_or_passport'), table_name='customers')
    op.drop_index(op.f('ix_customers_phone_number'), table_name='customers')
    op.drop_index(op.f('ix_customers_id'), table_name='customers')
    op.drop_table('customers')

    op.drop_index(op.f('ix_users_role'), table_name='users')
    op.drop_index(op.f('ix_users_email'), table_name='users')
    op.drop_index(op.f('ix_users_id'), table_name='users')
    op.drop_table('users')

    vehicle_status_enum = postgresql.ENUM('AVAILABLE', 'RENTED', 'MAINTENANCE', 'RESERVED', name='vehicle_status_enum')
    vehicle_status_enum.drop(op.get_bind(), checkfirst=True)

    user_role_enum = postgresql.ENUM('SUPERADMIN', 'AGENCY_MANAGER', 'AGENT', name='user_role_enum')
    user_role_enum.drop(op.get_bind(), checkfirst=True)
