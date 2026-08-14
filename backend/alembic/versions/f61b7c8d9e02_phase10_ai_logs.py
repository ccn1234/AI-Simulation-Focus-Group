"""expand ai usage logs for phase 10"""
from alembic import op
import sqlalchemy as sa
revision="f61b7c8d9e02"; down_revision="e45a6b7c8d90"; branch_labels=None; depends_on=None
def upgrade():
    with op.batch_alter_table("ai_usage_logs", recreate="always") as batch:
        batch.add_column(sa.Column("agent_name", sa.String(100), nullable=False, server_default="unknown"))
        batch.add_column(sa.Column("prompt_tokens", sa.Integer()))
        batch.add_column(sa.Column("completion_tokens", sa.Integer()))
        batch.add_column(sa.Column("elapsed_ms", sa.Integer()))
        batch.add_column(sa.Column("attempt", sa.Integer(), nullable=False, server_default="1"))
        batch.add_column(sa.Column("status", sa.String(20), nullable=False, server_default="succeeded"))
        batch.add_column(sa.Column("error_type", sa.String(100)))
        batch.add_column(sa.Column("error_message", sa.Text()))
def downgrade():
    with op.batch_alter_table("ai_usage_logs", recreate="always") as batch:
        for name in ["error_message","error_type","status","attempt","elapsed_ms","completion_tokens","prompt_tokens","agent_name"]: batch.drop_column(name)
