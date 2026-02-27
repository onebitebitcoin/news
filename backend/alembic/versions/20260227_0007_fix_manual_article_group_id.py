"""fix manual article group_id null

Revision ID: 20260227_0007
Revises: 20260226_0006
Create Date: 2026-02-27
"""
from alembic import op

# revision identifiers
revision = '20260227_0007'
down_revision = '20260226_0006'
branch_labels = None
depends_on = None


def upgrade():
    # 수동 추가 아티클의 group_id가 NULL인 경우 id 값으로 보정
    op.execute("UPDATE feed_items SET group_id = id WHERE group_id IS NULL")


def downgrade():
    pass
