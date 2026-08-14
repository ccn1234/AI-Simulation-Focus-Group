"""complete phase 5 persistence schema"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = "8b7d2a1f4c10"
down_revision: Union[str, None] = "37a560058383"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    op.create_table("users",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("external_id", sa.String(255), nullable=False, unique=True),
    )
    with op.batch_alter_table("simulations", recreate="always") as batch:
        batch.add_column(sa.Column("user_id", sa.Integer(), nullable=True))
        batch.add_column(sa.Column("product_analysis", sa.JSON(), nullable=True))
        batch.create_index("ix_simulations_user_id", ["user_id"])
        batch.create_foreign_key("fk_simulations_user_id", "users", ["user_id"], ["id"], ondelete="CASCADE")
    with op.batch_alter_table("personas", recreate="always") as batch:
        batch.create_unique_constraint("uq_persona_simulation_number", ["simulation_id", "persona_number"])
    op.create_table("keywords",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("value", sa.String(100), nullable=False, unique=True),
    )
    op.create_index("ix_keywords_value", "keywords", ["value"])
    op.create_table("simulation_keywords",
        sa.Column("simulation_id", sa.Integer(), nullable=False),
        sa.Column("keyword_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["simulation_id"], ["simulations.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["keyword_id"], ["keywords.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("simulation_id", "keyword_id"),
    )
    op.create_table("ai_usage_logs",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("simulation_id", sa.Integer(), nullable=False),
        sa.Column("model_name", sa.String(100), nullable=False),
        sa.Column("total_tokens", sa.Integer()),
        sa.Column("estimated_cost", sa.String(40)),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["simulation_id"], ["simulations.id"], ondelete="CASCADE"),
    )
    op.create_index("ix_ai_usage_logs_simulation_id", "ai_usage_logs", ["simulation_id"])

def downgrade() -> None:
    op.drop_index("ix_ai_usage_logs_simulation_id", table_name="ai_usage_logs")
    op.drop_table("ai_usage_logs")
    op.drop_table("simulation_keywords")
    op.drop_index("ix_keywords_value", table_name="keywords")
    op.drop_table("keywords")
    op.drop_constraint("uq_persona_simulation_number", "personas", type_="unique")
    op.drop_constraint("fk_simulations_user_id", "simulations", type_="foreignkey")
    op.drop_index("ix_simulations_user_id", table_name="simulations")
    op.drop_column("simulations", "product_analysis")
    op.drop_column("simulations", "user_id")
    op.drop_table("users")
