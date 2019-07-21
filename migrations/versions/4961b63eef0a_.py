"""empty message

Revision ID: 4961b63eef0a
Revises: 
Create Date: 2019-07-14 12:55:28.628777

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '4961b63eef0a'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('driver',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('name', sa.String(length=255), nullable=False),
    sa.Column('phone', sa.String(length=11), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('name'),
    sa.UniqueConstraint('phone')
    )
    op.create_table('user',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('username', sa.String(length=255), nullable=False),
    sa.Column('email', sa.String(), nullable=False),
    sa.Column('phone', sa.String(length=11), nullable=False),
    sa.Column('role', sa.Integer(), nullable=False),
    sa.Column('device_token', sa.String(), nullable=True),
    sa.Column('hased_password', sa.String(), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('device_token'),
    sa.UniqueConstraint('email'),
    sa.UniqueConstraint('phone'),
    sa.UniqueConstraint('username')
    )
    op.create_table('company',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('name', sa.String(length=255), nullable=False),
    sa.Column('_user_id', sa.Integer(), nullable=True),
    sa.Column('address', sa.String(), nullable=False),
    sa.ForeignKeyConstraint(['_user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('address'),
    sa.UniqueConstraint('name')
    )
    op.create_table('factory',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('name', sa.String(length=255), nullable=False),
    sa.Column('address', sa.String(length=255), nullable=False),
    sa.Column('hotline', sa.String(), nullable=False),
    sa.Column('_delegate_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['_delegate_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('address'),
    sa.UniqueConstraint('hotline'),
    sa.UniqueConstraint('name')
    )
    op.create_table('car',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('number', sa.String(length=255), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('capacity', sa.Float(), nullable=False),
    sa.Column('location_latitude', sa.Float(), nullable=True),
    sa.Column('location_longitude', sa.Float(), nullable=True),
    sa.Column('_owner', sa.Integer(), nullable=False),
    sa.Column('qr_code', sa.String(), nullable=False),
    sa.Column('_status', sa.Integer(), nullable=False),
    sa.Column('_type', sa.Integer(), nullable=False),
    sa.Column('current_order_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['_owner'], ['company.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('number'),
    sa.UniqueConstraint('qr_code')
    )
    op.create_table('order',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('from_latitude', sa.Float(), nullable=False),
    sa.Column('from_longitude', sa.Float(), nullable=False),
    sa.Column('to_latitude', sa.Float(), nullable=False),
    sa.Column('to_longitude', sa.Float(), nullable=False),
    sa.Column('pickup_location', sa.String(), nullable=False),
    sa.Column('dropoff_location', sa.String(), nullable=False),
    sa.Column('factory_id', sa.Integer(), nullable=False),
    sa.Column('status', sa.Integer(), nullable=False),
    sa.Column('ordered_at', sa.DateTime(), nullable=False),
    sa.Column('num_of_cars', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['factory_id'], ['factory.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('orderCarsAndDrivers',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('order_id', sa.Integer(), nullable=False),
    sa.Column('car_id', sa.Integer(), nullable=False),
    sa.Column('driver_id', sa.Integer(), nullable=False),
    sa.Column('status', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['car_id'], ['car.id'], ),
    sa.ForeignKeyConstraint(['driver_id'], ['driver.id'], ),
    sa.ForeignKeyConstraint(['order_id'], ['order.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('orderCarsTypes',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('order_id', sa.Integer(), nullable=False),
    sa.Column('cars_num', sa.Integer(), nullable=False),
    sa.Column('_type', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['order_id'], ['order.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('orderHistory',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('order_id', sa.Integer(), nullable=False),
    sa.Column('old_state', sa.Integer(), nullable=False),
    sa.Column('new_state', sa.Integer(), nullable=False),
    sa.Column('changed_on', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['order_id'], ['order.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('orderHistory')
    op.drop_table('orderCarsTypes')
    op.drop_table('orderCarsAndDrivers')
    op.drop_table('order')
    op.drop_table('car')
    op.drop_table('factory')
    op.drop_table('company')
    op.drop_table('user')
    op.drop_table('driver')
    # ### end Alembic commands ###