"""add phase 9 keyword metadata"""
from alembic import op
import sqlalchemy as sa
revision="e45a6b7c8d90"; down_revision="d72f1c8a9e55"; branch_labels=None; depends_on=None
def upgrade():
    with op.batch_alter_table("keywords", recreate="always") as batch:
        batch.add_column(sa.Column("category", sa.String(50), nullable=False, server_default="general"))
        batch.add_column(sa.Column("synonyms", sa.JSON(), nullable=False, server_default="[]"))
        batch.add_column(sa.Column("is_priority", sa.Boolean(), nullable=False, server_default=sa.false()))
        batch.add_column(sa.Column("is_excluded", sa.Boolean(), nullable=False, server_default=sa.false()))
def downgrade():
    with op.batch_alter_table("keywords", recreate="always") as batch:
        batch.drop_column("is_excluded"); batch.drop_column("is_priority"); batch.drop_column("synonyms"); batch.drop_column("category")
