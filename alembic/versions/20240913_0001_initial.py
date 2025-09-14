"""initial schema

Revision ID: 20240913_0001
Revises: 
Create Date: 2024-09-13 00:00:00.000000
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '20240913_0001'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    op.create_table('user',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('hashed_password', sa.String(length=255), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('role', sa.Enum('admin', 'user', name='userrole'), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_user_email'), 'user', ['email'], unique=True)
    op.create_index(op.f('ix_user_id'), 'user', ['id'], unique=False)

    op.create_table('wallet',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('balance', sa.Numeric(precision=18, scale=2), nullable=False),
        sa.Column('currency', sa.String(length=3), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['user.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id', name='uq_wallet_user')
    )
    op.create_index(op.f('ix_wallet_id'), 'wallet', ['id'], unique=False)
    op.create_index(op.f('ix_wallet_user_id'), 'wallet', ['user_id'], unique=False)

    op.create_table('transaction',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('type', sa.Enum('ADD_MONEY', 'WITHDRAW', 'TRANSFER', 'REQUEST_PAYMENT', 'REFUND', 'REVERSAL', name='transactiontype'), nullable=False),
        sa.Column('status', sa.Enum('PENDING', 'COMPLETED', 'FAILED', name='transactionstatus'), nullable=False),
        sa.Column('amount', sa.Numeric(precision=18, scale=2), nullable=False),
        sa.Column('from_wallet_id', sa.Integer(), nullable=True),
        sa.Column('to_wallet_id', sa.Integer(), nullable=True),
        sa.Column('reference', sa.String(length=64), nullable=True),
        sa.Column('idempotency_key', sa.String(length=64), nullable=True),
        sa.Column('metadata', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['from_wallet_id'], ['wallet.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['to_wallet_id'], ['wallet.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('idempotency_key', name='uq_transaction_idempotency')
    )
    op.create_index('ix_transaction_type_status', 'transaction', ['type','status'], unique=False)
    op.create_index(op.f('ix_transaction_created_at'), 'transaction', ['created_at'], unique=False)
    op.create_index(op.f('ix_transaction_from_wallet_id'), 'transaction', ['from_wallet_id'], unique=False)
    op.create_index(op.f('ix_transaction_id'), 'transaction', ['id'], unique=False)
    op.create_index(op.f('ix_transaction_status'), 'transaction', ['status'], unique=False)
    op.create_index(op.f('ix_transaction_to_wallet_id'), 'transaction', ['to_wallet_id'], unique=False)
    op.create_index(op.f('ix_transaction_type'), 'transaction', ['type'], unique=False)

    op.create_table('moneyrequest',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('requester_wallet_id', sa.Integer(), nullable=False),
        sa.Column('target_wallet_id', sa.Integer(), nullable=False),
        sa.Column('amount', sa.Numeric(precision=18, scale=2), nullable=False),
        sa.Column('status', sa.Enum('PENDING', 'APPROVED', 'REJECTED', name='moneyrequeststatus'), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('resolved_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['requester_wallet_id'], ['wallet.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['target_wallet_id'], ['wallet.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_moneyrequest_id'), 'moneyrequest', ['id'], unique=False)
    op.create_index(op.f('ix_moneyrequest_requester_wallet_id'), 'moneyrequest', ['requester_wallet_id'], unique=False)
    op.create_index(op.f('ix_moneyrequest_status'), 'moneyrequest', ['status'], unique=False)
    op.create_index(op.f('ix_moneyrequest_target_wallet_id'), 'moneyrequest', ['target_wallet_id'], unique=False)

    op.create_table('refund',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('original_transaction_id', sa.Integer(), nullable=False),
        sa.Column('amount', sa.Numeric(precision=18, scale=2), nullable=False),
        sa.Column('status', sa.Enum('PENDING', 'PROCESSED', 'FAILED', name='refundstatus'), nullable=False),
        sa.Column('reason', sa.String(length=255), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('processed_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['original_transaction_id'], ['transaction.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_refund_id'), 'refund', ['id'], unique=False)
    op.create_index(op.f('ix_refund_original_transaction_id'), 'refund', ['original_transaction_id'], unique=False)
    op.create_index(op.f('ix_refund_status'), 'refund', ['status'], unique=False)


def downgrade() -> None:
    op.drop_table('refund')
    op.drop_table('moneyrequest')
    op.drop_table('transaction')
    op.drop_table('wallet')
    op.drop_table('user')
