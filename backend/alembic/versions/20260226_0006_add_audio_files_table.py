"""add audio_files table

Revision ID: 20260226_0006
Revises: 20260225_0005_add_mvrv_z_score_to_market_data_snapshots
Create Date: 2026-02-26
"""
import sqlalchemy as sa

from alembic import op

# revision identifiers
revision = '20260226_0006'
down_revision = '20260225_0005'  # 20260225_0005_add_mvrv_z_score_to_market_data_snapshots
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'audio_files',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('title', sa.String(), nullable=False),
        sa.Column('filename', sa.String(), nullable=False),
        sa.Column('file_path', sa.String(), nullable=False),
        sa.Column('file_size', sa.Integer(), nullable=True),
        sa.Column('duration', sa.Integer(), nullable=True),
        sa.Column('mime_type', sa.String(), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('uploaded_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_audio_files_id', 'audio_files', ['id'], unique=False)


def downgrade() -> None:
    op.drop_index('ix_audio_files_id', table_name='audio_files')
    op.drop_table('audio_files')
