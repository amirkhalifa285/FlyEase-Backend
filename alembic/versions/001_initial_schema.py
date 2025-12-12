"""initial_schema

Revision ID: 001
Revises: 
Create Date: 2024-12-12

Initial database schema matching existing models.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '001_initial_schema'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create all tables for the FlyEase application."""
    
    # Users table
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), primary_key=True, index=True),
        sa.Column('username', sa.String(), unique=True, nullable=False),
        sa.Column('password_hash', sa.String(), nullable=False),
        sa.Column('role', sa.String(), nullable=False),
        sa.Column('email', sa.String(), unique=True, nullable=False),
        sa.Column('preferences', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(), server_default=sa.func.now()),
    )
    
    # Flights table
    op.create_table(
        'flights',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('airline_name', sa.String(), nullable=False),
        sa.Column('flight_number', sa.String(), nullable=False),
        sa.Column('origin', sa.String(), nullable=False),
        sa.Column('destination', sa.String(), nullable=False),
        sa.Column('departure_time', sa.DateTime(), nullable=False),
        sa.Column('arrival_time', sa.DateTime(), nullable=False),
        sa.Column('status', sa.String(), nullable=True),
    )
    
    # Luggage table
    op.create_table(
        'luggage',
        sa.Column('luggage_id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('weight', sa.Float(), nullable=True),
        sa.Column('status', sa.String(), nullable=True),
        sa.Column('last_location', sa.String(), nullable=True),
    )
    
    # Tickets table (references users and luggage)
    op.create_table(
        'tickets',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('airline_name', sa.String(), nullable=False),
        sa.Column('flight_number', sa.String(), nullable=False),
        sa.Column('origin', sa.String(), nullable=False),
        sa.Column('destination', sa.String(), nullable=False),
        sa.Column('departure_time', sa.DateTime(), nullable=False),
        sa.Column('arrival_time', sa.DateTime(), nullable=False),
        sa.Column('price', sa.Float(), nullable=False),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('luggage_id', sa.Integer(), sa.ForeignKey('luggage.luggage_id'), unique=True, nullable=True),
    )
    
    # Messages table
    op.create_table(
        'messages',
        sa.Column('id', sa.Integer(), primary_key=True, index=True),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id', ondelete='CASCADE')),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('status', sa.String(), default='unread'),
        sa.Column('created_at', sa.DateTime(), default=sa.func.now()),
    )
    
    # Locations table (for airport map)
    op.create_table(
        'locations',
        sa.Column('id', sa.Integer(), primary_key=True, index=True),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('type', sa.String(), nullable=False),
        sa.Column('category', sa.String(), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('coordinates', sa.JSON(), nullable=False),
    )
    
    # Paths table (connections between locations)
    op.create_table(
        'paths',
        sa.Column('id', sa.Integer(), primary_key=True, index=True),
        sa.Column('source_id', sa.Integer(), sa.ForeignKey('locations.id'), nullable=False),
        sa.Column('destination_id', sa.Integer(), sa.ForeignKey('locations.id'), nullable=False),
        sa.Column('distance', sa.Float(), nullable=False),
        sa.Column('congestion', sa.Integer(), default=1),
    )
    
    # Walls table (obstacles for pathfinding)
    op.create_table(
        'walls',
        sa.Column('id', sa.Integer(), primary_key=True, index=True),
        sa.Column('x1', sa.Float(), nullable=False),
        sa.Column('y1', sa.Float(), nullable=False),
        sa.Column('x2', sa.Float(), nullable=False),
        sa.Column('y2', sa.Float(), nullable=False),
    )
    
    # Hotels table
    op.create_table(
        'hotels',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('address', sa.Text(), nullable=False),
        sa.Column('latitude', sa.Float(), nullable=False),
        sa.Column('longitude', sa.Float(), nullable=False),
        sa.Column('rating', sa.Float()),
        sa.Column('total_ratings', sa.Integer()),
        sa.Column('place_id', sa.String(255), unique=True, nullable=False),
        sa.Column('photo_reference', sa.Text()),
        sa.Column('open_now', sa.Boolean()),
    )
    
    # Cars table
    op.create_table(
        'cars',
        sa.Column('id', sa.Integer(), primary_key=True, index=True),
        sa.Column('offer_id', sa.String(), unique=True, nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('vehicle_type', sa.String(), nullable=True),
        sa.Column('model', sa.String(), nullable=True),
        sa.Column('location', sa.String(), nullable=False),
        sa.Column('price', sa.Float(), nullable=True),
        sa.Column('currency', sa.String(), nullable=True),
        sa.Column('fuel_type', sa.String(), nullable=True),
        sa.Column('start_location', sa.JSON(), nullable=True),
        sa.Column('end_location', sa.JSON(), nullable=True),
        sa.Column('start_time', sa.DateTime(), nullable=True),
        sa.Column('end_time', sa.DateTime(), nullable=True),
        sa.Column('providers', sa.JSON(), nullable=True),
        sa.Column('passengers', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
    )
    
    # Create indexes
    op.create_index('ix_users_username', 'users', ['username'])
    op.create_index('ix_users_email', 'users', ['email'])
    op.create_index('ix_tickets_user_id', 'tickets', ['user_id'])
    op.create_index('ix_flights_flight_number', 'flights', ['flight_number'])


def downgrade() -> None:
    """Drop all tables."""
    op.drop_index('ix_flights_flight_number', 'flights')
    op.drop_index('ix_tickets_user_id', 'tickets')
    op.drop_index('ix_users_email', 'users')
    op.drop_index('ix_users_username', 'users')
    
    op.drop_table('cars')
    op.drop_table('hotels')
    op.drop_table('walls')
    op.drop_table('paths')
    op.drop_table('locations')
    op.drop_table('messages')
    op.drop_table('tickets')
    op.drop_table('luggage')
    op.drop_table('flights')
    op.drop_table('users')
