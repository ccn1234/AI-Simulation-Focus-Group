"""add google oauth fields"""
from alembic import op
import sqlalchemy as sa
revision="d72f1c8a9e55"; down_revision="c91e3a7b2d44"; branch_labels=None; depends_on=None
def upgrade():
    with op.batch_alter_table("users", recreate="always") as batch:
        batch.add_column(sa.Column("google_id", sa.String(255), nullable=True)); batch.add_column(sa.Column("auth_provider", sa.String(20), nullable=False, server_default="password")); batch.create_index("ix_users_google_id", ["google_id"], unique=True)
def downgrade():
    with op.batch_alter_table("users", recreate="always") as batch:
        batch.drop_index("ix_users_google_id"); batch.drop_column("auth_provider"); batch.drop_column("google_id")
