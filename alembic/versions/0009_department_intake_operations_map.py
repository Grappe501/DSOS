"""Department intake sessions + operations map tables."""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "0009_department_intake_operations_map"
down_revision = "0008_malone_review_loop_human_feedback"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "operations_departments",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("stable_key", sa.String(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("meta_json", sa.Text(), nullable=False, server_default="{}"),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_operations_departments_stable_key", "operations_departments", ["stable_key"], unique=True)
    op.create_index("ix_operations_departments_name", "operations_departments", ["name"])

    op.create_table(
        "department_intake_sessions",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("operations_department_id", sa.String(), sa.ForeignKey("operations_departments.id"), nullable=False),
        sa.Column("actor_user_id", sa.String(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("status", sa.String(), nullable=False, server_default="open"),
        sa.Column("proposal_id", sa.String(), sa.ForeignKey("malone_proposals.id"), nullable=True),
        sa.Column("scenario_memory_id", sa.String(), sa.ForeignKey("malone_scenario_memories.id"), nullable=True),
        sa.Column("state_json", sa.Text(), nullable=False, server_default="{}"),
        sa.Column("meta_json", sa.Text(), nullable=False, server_default="{}"),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
    )
    op.create_index(
        "ix_department_intake_sessions_operations_department_id",
        "department_intake_sessions",
        ["operations_department_id"],
    )
    op.create_index("ix_department_intake_sessions_actor_user_id", "department_intake_sessions", ["actor_user_id"])
    op.create_index("ix_department_intake_sessions_status", "department_intake_sessions", ["status"])
    op.create_index("ix_department_intake_sessions_proposal_id", "department_intake_sessions", ["proposal_id"])
    op.create_index("ix_department_intake_sessions_scenario_memory_id", "department_intake_sessions", ["scenario_memory_id"])

    op.create_table(
        "department_intake_answers",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("intake_session_id", sa.String(), sa.ForeignKey("department_intake_sessions.id"), nullable=False),
        sa.Column("question_key", sa.String(), nullable=True),
        sa.Column("prompt_snapshot", sa.Text(), nullable=True),
        sa.Column("answer_text", sa.Text(), nullable=False),
        sa.Column("entry_mode", sa.String(), nullable=False, server_default="text"),
        sa.Column("transcript_ref", sa.String(), nullable=True),
        sa.Column("parser_output_json", sa.Text(), nullable=False, server_default="{}"),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_department_intake_answers_intake_session_id", "department_intake_answers", ["intake_session_id"])
    op.create_index("ix_department_intake_answers_question_key", "department_intake_answers", ["question_key"])

    op.create_table(
        "operations_roles",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("operations_department_id", sa.String(), sa.ForeignKey("operations_departments.id"), nullable=False),
        sa.Column("title", sa.String(), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("meta_json", sa.Text(), nullable=False, server_default="{}"),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_operations_roles_operations_department_id", "operations_roles", ["operations_department_id"])

    op.create_table(
        "operations_workflows",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("operations_department_id", sa.String(), sa.ForeignKey("operations_departments.id"), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("owner_role_id", sa.String(), sa.ForeignKey("operations_roles.id"), nullable=True),
        sa.Column("inputs_summary", sa.Text(), nullable=True),
        sa.Column("outputs_summary", sa.Text(), nullable=True),
        sa.Column("ordinal", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("meta_json", sa.Text(), nullable=False, server_default="{}"),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_operations_workflows_operations_department_id", "operations_workflows", ["operations_department_id"])
    op.create_index("ix_operations_workflows_owner_role_id", "operations_workflows", ["owner_role_id"])

    op.create_table(
        "operations_system_tools",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("operations_department_id", sa.String(), sa.ForeignKey("operations_departments.id"), nullable=False),
        sa.Column("operations_workflow_id", sa.String(), sa.ForeignKey("operations_workflows.id"), nullable=True),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("category", sa.String(), nullable=True),
        sa.Column("meta_json", sa.Text(), nullable=False, server_default="{}"),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_operations_system_tools_operations_department_id", "operations_system_tools", ["operations_department_id"])
    op.create_index("ix_operations_system_tools_operations_workflow_id", "operations_system_tools", ["operations_workflow_id"])
    op.create_index("ix_operations_system_tools_category", "operations_system_tools", ["category"])

    op.create_table(
        "operations_dependencies",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("operations_department_id", sa.String(), sa.ForeignKey("operations_departments.id"), nullable=False),
        sa.Column("from_ref", sa.String(), nullable=False),
        sa.Column("to_ref", sa.String(), nullable=False),
        sa.Column("dependency_type", sa.String(), nullable=False, server_default="related"),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("meta_json", sa.Text(), nullable=False, server_default="{}"),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
    )
    op.create_index(
        "ix_operations_dependencies_operations_department_id", "operations_dependencies", ["operations_department_id"]
    )
    op.create_index("ix_operations_dependencies_dependency_type", "operations_dependencies", ["dependency_type"])

    op.create_table(
        "operations_handoffs",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("operations_department_id", sa.String(), sa.ForeignKey("operations_departments.id"), nullable=False),
        sa.Column("operations_workflow_id", sa.String(), sa.ForeignKey("operations_workflows.id"), nullable=True),
        sa.Column("to_counterparty", sa.String(), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("meta_json", sa.Text(), nullable=False, server_default="{}"),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_operations_handoffs_operations_department_id", "operations_handoffs", ["operations_department_id"])
    op.create_index("ix_operations_handoffs_operations_workflow_id", "operations_handoffs", ["operations_workflow_id"])

    op.create_table(
        "operations_escalations",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("operations_department_id", sa.String(), sa.ForeignKey("operations_departments.id"), nullable=False),
        sa.Column("operations_workflow_id", sa.String(), sa.ForeignKey("operations_workflows.id"), nullable=True),
        sa.Column("trigger_summary", sa.Text(), nullable=True),
        sa.Column("path_summary", sa.Text(), nullable=True),
        sa.Column("meta_json", sa.Text(), nullable=False, server_default="{}"),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_operations_escalations_operations_department_id", "operations_escalations", ["operations_department_id"])
    op.create_index("ix_operations_escalations_operations_workflow_id", "operations_escalations", ["operations_workflow_id"])

    op.create_table(
        "operations_blockers",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("operations_department_id", sa.String(), sa.ForeignKey("operations_departments.id"), nullable=False),
        sa.Column("operations_workflow_id", sa.String(), sa.ForeignKey("operations_workflows.id"), nullable=True),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("meta_json", sa.Text(), nullable=False, server_default="{}"),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_operations_blockers_operations_department_id", "operations_blockers", ["operations_department_id"])
    op.create_index("ix_operations_blockers_operations_workflow_id", "operations_blockers", ["operations_workflow_id"])

    op.create_table(
        "operations_artifact_refs",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("operations_department_id", sa.String(), sa.ForeignKey("operations_departments.id"), nullable=False),
        sa.Column("label", sa.String(), nullable=False),
        sa.Column("ref_kind", sa.String(), nullable=False, server_default="mentioned"),
        sa.Column("meta_json", sa.Text(), nullable=False, server_default="{}"),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_operations_artifact_refs_operations_department_id", "operations_artifact_refs", ["operations_department_id"])
    op.create_index("ix_operations_artifact_refs_ref_kind", "operations_artifact_refs", ["ref_kind"])


def downgrade() -> None:
    op.drop_table("operations_artifact_refs")
    op.drop_table("operations_blockers")
    op.drop_table("operations_escalations")
    op.drop_table("operations_handoffs")
    op.drop_table("operations_dependencies")
    op.drop_table("operations_system_tools")
    op.drop_table("operations_workflows")
    op.drop_table("operations_roles")
    op.drop_table("department_intake_answers")
    op.drop_table("department_intake_sessions")
    op.drop_table("operations_departments")
