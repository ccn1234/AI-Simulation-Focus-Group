"""add phase 7 authentication fields"""
from alembic import op
import sqlalchemy as sa
revision = "c91e3a7b2d44"
down_revision = "8b7d2a1f4c10"
branch_labels = None
depends_on = None

def upgrade():
    with op.batch_alter_table("users", recreate="always") as batch:
        batch.add_column(sa.Column("email", sa.String(255), nullable=True))
        batch.add_column(sa.Column("password_hash", sa.String(255), nullable=True))
        batch.add_column(sa.Column("role", sa.String(20), nullable=False, server_default="USER"))
        batch.add_column(sa.Column("created_at", sa.DateTime(), nullable=True))
        batch.create_index("ix_users_email", ["email"], unique=True)

def downgrade():
    with op.batch_alter_table("users", recreate="always") as batch:
        batch.drop_index("ix_users_email")
        batch.drop_column("created_at")
        batch.drop_column("role")
        batch.drop_column("password_hash")
        batch.drop_column("email")
