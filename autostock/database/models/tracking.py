from datetime import date, datetime
from typing import Optional
from sqlmodel import Field, SQLModel


class DataTracking(SQLModel, table=True):
    __tablename__ = "data_tracking"

    # 对象的唯一标识，例如 'sz000001'
    symbol: str = Field(primary_key=True)
    name: Optional[str] = None

    # 日线行情跟踪状态
    has_daily: bool = Field(default=False)
    daily_start_date: Optional[date] = None
    daily_end_date: Optional[date] = None
    daily_last_sync: Optional[datetime] = None

    # 管理信息
    # 跟踪目的（例如：用于哪个策略、用于研究、在哪个关注列表）
    purpose: Optional[str] = None
    # 是否自动同步此数据
    auto_sync: bool = Field(default=True)

    # 审计字段
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        nullable=False,
        sa_column_kwargs={"onupdate": datetime.utcnow},
    )
