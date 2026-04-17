"""Add legal_source_version_id to legal_unit_chunks for retrieval scoping."""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "0004_legal_unit_chunk_source_version"
down_revision = "0003_legal_handbook_knowledge_foundation"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # SQLite: avoid FK constraint in ALTER; ORM still declares the relationship.
    conn = op.get_bind()
    insp = sa.inspect(conn)
    cols = {c["name"] for c in insp.get_columns("legal_unit_chunks")}
    if "legal_source_version_id" not in cols:
        op.add_column(
            "legal_unit_chunks",
            sa.Column("legal_source_version_id", sa.String(), nullable=True),
        )
    ix = insp.get_indexes("legal_unit_chunks")
    names = {i["name"] for i in ix}
    if "idx_legal_unit_chunks_source_version" not in names:
        op.create_index(
            "idx_legal_unit_chunks_source_version",
            "legal_unit_chunks",
            ["legal_source_version_id"],
        )


def downgrade() -> None:
    op.drop_index("idx_legal_unit_chunks_source_version", table_name="legal_unit_chunks")
    op.drop_column("legal_unit_chunks", "legal_source_version_id")
