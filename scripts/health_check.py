import sqlalchemy
from sqlalchemy.engine import Engine
from autostock.database.engine import engine


def check_database_connection(db_engine: Engine):
    """Checks if the database connection is alive."""
    try:
        with db_engine.connect() as connection:
            print("✅ Database connection successful.")
            return True
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False


def check_table_exists(db_engine: Engine, table_name: str):
    """Checks if a specific table exists in the database."""
    try:
        inspector = sqlalchemy.inspect(db_engine)
        if inspector.has_table(table_name):
            columns = [col["name"] for col in inspector.get_columns(table_name)]
            print(f"✅ Table '{table_name}' exists with columns: {columns}")
            return True
        else:
            print(f"❌ Table '{table_name}' does not exist.")
            return False
    except Exception as e:
        print(f"❌ Failed to inspect table '{table_name}': {e}")
        return False


if __name__ == "__main__":
    print("🚀 Running database health check...")
    if check_database_connection(engine):
        check_table_exists(engine, "market_overview")
        check_table_exists(
            engine, "alembic_version"
        )  # Also check the migration version table
    print("🏁 Health check finished.")
