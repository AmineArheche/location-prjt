"""create_transactional_models_booking_maintenance

Revision ID: 2026_08_10_0002
Revises: 2026_08_10_0001
Create Date: 2026-08-10 19:21:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '2026_08_10_0002'
down_revision: Union[str, None] = '2026_08_10_0001'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Create Enums
    booking_status_enum = postgresql.ENUM('PENDING', 'ACTIVE', 'COMPLETED', 'CANCELLED', name='booking_status_enum')
    booking_status_enum.create(op.get_bind(), checkfirst=True)

    maintenance_type_enum = postgresql.ENUM('VIDANGE', 'VISITE_TECHNIQUE', 'ASSURANCE', 'REPAIR', name='maintenance_type_enum')
    maintenance_type_enum.create(op.get_bind(), checkfirst=True)

    # 2. Create Bookings Table
    op.create_table(
        'bookings',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column('vehicle_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('vehicles.id', ondelete='RESTRICT'), nullable=False),
        sa.Column('customer_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('customers.id', ondelete='RESTRICT'), nullable=False),
        sa.Column('agent_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='RESTRICT'), nullable=False),
        sa.Column('start_datetime', sa.DateTime(timezone=True), nullable=False),
        sa.Column('end_datetime', sa.DateTime(timezone=True), nullable=False),
        sa.Column('start_mileage', sa.Integer(), nullable=False),
        sa.Column('end_mileage', sa.Integer(), nullable=True),
        sa.Column('total_price', sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column('deposit_amount', sa.Numeric(precision=10, scale=2), nullable=False, server_default='0.00'),
        sa.Column('status', sa.Enum('PENDING', 'ACTIVE', 'COMPLETED', 'CANCELLED', name='booking_status_enum'), nullable=False, server_default='PENDING'),
        sa.Column('damage_report_start', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index(op.f('ix_bookings_id'), 'bookings', ['id'], unique=False)
    op.create_index(op.f('ix_bookings_vehicle_id'), 'bookings', ['vehicle_id'], unique=False)
    op.create_index(op.f('ix_bookings_customer_id'), 'bookings', ['customer_id'], unique=False)
    op.create_index(op.f('ix_bookings_agent_id'), 'bookings', ['agent_id'], unique=False)
    op.create_index(op.f('ix_bookings_start_datetime'), 'bookings', ['start_datetime'], unique=False)
    op.create_index(op.f('ix_bookings_end_datetime'), 'bookings', ['end_datetime'], unique=False)
    op.create_index(op.f('ix_bookings_status'), 'bookings', ['status'], unique=False)

    # 3. Create Maintenance Logs Table
    op.create_table(
        'maintenance_logs',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column('vehicle_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('vehicles.id', ondelete='CASCADE'), nullable=False),
        sa.Column('type', sa.Enum('VIDANGE', 'VISITE_TECHNIQUE', 'ASSURANCE', 'REPAIR', name='maintenance_type_enum'), nullable=False),
        sa.Column('date_performed', sa.Date(), nullable=False),
        sa.Column('next_due_date', sa.Date(), nullable=False),
        sa.Column('cost', sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index(op.f('ix_maintenance_logs_id'), 'maintenance_logs', ['id'], unique=False)
    op.create_index(op.f('ix_maintenance_logs_vehicle_id'), 'maintenance_logs', ['vehicle_id'], unique=False)
    op.create_index(op.f('ix_maintenance_logs_type'), 'maintenance_logs', ['type'], unique=False)
    op.create_index(op.f('ix_maintenance_logs_next_due_date'), 'maintenance_logs', ['next_due_date'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_maintenance_logs_next_due_date'), table_name='maintenance_logs')
    op.drop_index(op.f('ix_maintenance_logs_type'), table_name='maintenance_logs')
    op.drop_index(op.f('ix_maintenance_logs_vehicle_id'), table_name='maintenance_logs')
    op.drop_index(op.f('ix_maintenance_logs_id'), table_name='maintenance_logs')
    op.drop_table('maintenance_logs')

    op.drop_index(op.f('ix_bookings_status'), table_name='bookings')
    op.drop_index(op.f('ix_bookings_end_datetime'), table_name='bookings')
    op.drop_index(op.f('ix_bookings_start_datetime'), table_name='bookings')
    op.drop_index(op.f('ix_bookings_agent_id'), table_name='bookings')
    op.drop_index(op.f('ix_bookings_customer_id'), table_name='bookings')
    op.drop_index(op.f('ix_bookings_vehicle_id'), table_name='bookings')
    op.drop_index(op.f('ix_bookings_id'), table_name='bookings')
    op.drop_table('bookings')

    maintenance_type_enum = postgresql.ENUM('VIDANGE', 'VISITE_TECHNIQUE', 'ASSURANCE', 'REPAIR', name='maintenance_type_enum')
    maintenance_type_enum.drop(op.get_bind(), checkfirst=True)

    booking_status_enum = postgresql.ENUM('PENDING', 'ACTIVE', 'COMPLETED', 'CANCELLED', name='booking_status_enum')
    booking_status_enum.drop(op.get_bind(), checkfirst=True)
