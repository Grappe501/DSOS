from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import declarative_base, sessionmaker

DATABASE_URL = "sqlite:///./runtime_v5.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
Base = declarative_base()


def ensure_runtime_schema() -> None:
    """
    Lightweight schema repair for local/prototype SQLite runtime.

    The project is not on Alembic yet, so this keeps older local databases from
    drifting when columns are added in later phases.
    """
    inspector = inspect(engine)

    expected_columns = {
        "schedules": {
            "created_by_user_id": "ALTER TABLE schedules ADD COLUMN created_by_user_id VARCHAR",
            "department": "ALTER TABLE schedules ADD COLUMN department VARCHAR",
        },
        "audit_logs": {
            "actor_user_id": "ALTER TABLE audit_logs ADD COLUMN actor_user_id VARCHAR",
            "meta_json": "ALTER TABLE audit_logs ADD COLUMN meta_json TEXT NOT NULL DEFAULT '{}'",
        },
        "users": {
            "department": "ALTER TABLE users ADD COLUMN department VARCHAR",
        },
    }

    with engine.begin() as conn:
        for table_name, column_map in expected_columns.items():
            if not inspector.has_table(table_name):
                continue

            existing = {column["name"] for column in inspector.get_columns(table_name)}
            for column_name, ddl in column_map.items():
                if column_name not in existing:
                    conn.execute(text(ddl))

        index_statements = [
            "CREATE INDEX IF NOT EXISTS ix_schedules_department ON schedules (department)",
            "CREATE INDEX IF NOT EXISTS ix_schedules_created_by_user_id ON schedules (created_by_user_id)",
            "CREATE INDEX IF NOT EXISTS ix_audit_logs_actor_user_id ON audit_logs (actor_user_id)",
            "CREATE INDEX IF NOT EXISTS ix_users_department ON users (department)",
        ]
        for statement in index_statements:
            conn.execute(text(statement))
