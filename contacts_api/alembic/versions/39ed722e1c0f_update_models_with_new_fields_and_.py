"""Update models with new fields and relationships

Revision ID: 39ed722e1c0f
Revises: ef4d76abe0b9
Create Date: 2024-08-11 09:56:37.083698

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '39ed722e1c0f'
down_revision: Union[str, None] = 'ef4d76abe0b9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('contacts', sa.Column('user_id', sa.Integer(), nullable=True))
    op.create_foreign_key(None, 'contacts', 'users', ['user_id'], ['id'])
    op.add_column('users', sa.Column('username', sa.String(length=50), nullable=True))
    op.add_column('users', sa.Column('created_at', sa.DateTime(), nullable=True))
    op.add_column('users', sa.Column('avatar', sa.String(length=255), nullable=True))
    op.alter_column('users', 'email',
               existing_type=sa.VARCHAR(length=150),
               type_=sa.String(length=250),
               existing_nullable=False)
    op.drop_index('ix_users_id', table_name='users')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_index('ix_users_id', 'users', ['id'], unique=False)
    op.alter_column('users', 'email',
               existing_type=sa.String(length=250),
               type_=sa.VARCHAR(length=150),
               existing_nullable=False)
    op.drop_column('users', 'avatar')
    op.drop_column('users', 'created_at')
    op.drop_column('users', 'username')
    op.drop_constraint(None, 'contacts', type_='foreignkey')
    op.drop_column('contacts', 'user_id')
    # ### end Alembic commands ###
