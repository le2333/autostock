from datetime import datetime

import pandas as pd
from sqlmodel import Session, select

from autostock.database.models import DataTracking


def upsert_tracking_stocks(session: Session, market_overview: pd.DataFrame):
    """
    根据市场总览数据，在 data_tracking 表中插入新股票的跟踪记录
    """
    existing_symbols_stmt = select(DataTracking.symbol)
    existing_symbols = set(session.exec(existing_symbols_stmt).all())

    incoming_symbols = set(market_overview["symbol"])

    new_symbols = list(incoming_symbols - existing_symbols)

    if not new_symbols:
        print("No new stocks to track.")
        return 0

    print(f"Found {len(new_symbols)} new stocks to track.")

    # 从总览数据中筛选出新股票的信息
    new_stocks_df = market_overview[market_overview["symbol"].isin(new_symbols)][
        ["symbol", "name"]
    ]

    for _, row in new_stocks_df.iterrows():
        tracking_record = DataTracking(symbol=row["symbol"], name=row["name"])
        session.add(tracking_record)

    session.commit()
    print(f"Successfully added {len(new_symbols)} new stocks to data_tracking.")
    return len(new_symbols)


def update_daily_tracking_info(session: Session, symbol: str, daily_data: pd.DataFrame):
    """
    更新指定股票的日线数据跟踪信息
    """
    if daily_data.empty:
        return

    statement = select(DataTracking).where(DataTracking.symbol == symbol)
    tracking_record = session.exec(statement).one_or_none()

    if tracking_record:
        tracking_record.has_daily = True
        tracking_record.daily_start_date = daily_data["date"].min().date()
        tracking_record.daily_end_date = daily_data["date"].max().date()
        tracking_record.daily_last_sync = datetime.now()
        session.add(tracking_record)
        session.commit()


def get_all_tracked_symbols(session: Session) -> list[str]:
    """
    从 data_tracking 表中获取所有被跟踪的股票代码列表。
    """
    statement = select(DataTracking.symbol)
    symbols = session.exec(statement).all()
    return symbols
