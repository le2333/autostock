import pandas as pd
from sqlmodel import Session, select
from tqdm import tqdm
from autostock.database.engine import engine
from autostock.database.models import MarketOverview
from autostock.datamanager.session import get_session


def upsert_market_overview(session: Session, df: pd.DataFrame):
    """
    将DataFrame中的市场总览数据插入或更新到数据库中。
    """
    for _, row in df.iterrows():
        # 尝试查找具有相同主键（symbol）的现有记录
        existing_record = session.get(MarketOverview, row["symbol"])
        if existing_record:
            # 如果记录已存在，则更新它的字段
            for key, value in row.items():
                setattr(existing_record, key, value)
        else:
            # 如果记录不存在，则创建一个新实例并添加到会话中
            new_record = MarketOverview(**row.to_dict())
            session.add(new_record)

    # 提交事务，将所有更改（插入和更新）保存到数据库
    session.commit()


def get_all_market_overview() -> pd.DataFrame:
    """从数据库获取所有市场总览数据"""
    with get_session() as session:
        statement = select(MarketOverview)
        results = session.exec(statement).all()
        if not results:
            return pd.DataFrame()
        # 将结果转换为字典列表，然后创建DataFrame
        return pd.DataFrame([r.model_dump() for r in results])
