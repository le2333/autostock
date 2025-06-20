from sqlmodel import create_engine

# 我们根据项目计划，使用 DuckDB，数据库文件存放在根目录的 `datas` 文件夹下
# 注意：这里的路径是相对于项目根目录的相对路径。
# 在 Alembic 配置中，我们需要确保它能正确解析这个路径。
DATABASE_URL = "duckdb:///datas/market.db"

# 创建数据库引擎
# 移除了 connect_args={"check_same_thread": False}，因为它与 duckdb 不兼容
engine = create_engine(DATABASE_URL, echo=True)
