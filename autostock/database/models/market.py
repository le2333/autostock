from typing import Optional
from datetime import date, datetime
from sqlmodel import Field, SQLModel, Column, DateTime, text


class MarketOverview(SQLModel, table=True):
    __tablename__ = "market_overview"

    symbol: str = Field(primary_key=True, description="股票代码")
    name: Optional[str] = Field(default=None, description="股票名称")
    industry: Optional[str] = Field(default=None, description="所属行业")
    market_type: Optional[str] = Field(
        default=None, description="市场类型（主板、创业板等）"
    )
    list_date: Optional[date] = Field(default=None, description="上市日期")
    status: Optional[str] = Field(default=None, description="状态（正常、停牌、退市）")
    last_price: Optional[float] = Field(default=None, description="最新价格")

    updated_at: Optional[datetime] = Field(
        sa_column=Column(
            DateTime,
            nullable=False,
            server_default=text("CURRENT_TIMESTAMP"),
            onupdate=datetime.now,
            comment="更新时间",
        )
    )
