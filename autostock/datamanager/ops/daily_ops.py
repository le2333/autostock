from pathlib import Path
from datetime import date
import pandas as pd

# 定义数据存储的根目录
DATA_ROOT = Path("datas/daily")


def save_daily_to_parquet(df: pd.DataFrame, data_path: Path):
    """
    将单只股票的日线历史数据DataFrame保存到Parquet文件中。

    文件将被保存在 `data_path/daily/{symbol}.parquet`。

    :param df: 包含日线数据的DataFrame，必须有 'symbol' 列。
    :param data_path: 数据存储的根目录 (Path对象)。
    """
    if df.empty:
        # print(f"WARN: DataFrame for symbol is empty, skipping save.")
        return

    symbol = df["symbol"].iloc[0]
    # 创建 'daily' 子目录（如果不存在）
    daily_data_path = data_path / "daily"
    daily_data_path.mkdir(parents=True, exist_ok=True)

    # 定义输出文件路径
    output_file = daily_data_path / f"{symbol}.parquet"

    # print(f"INFO: Saving daily data for {symbol} to {output_file}")
    df.to_parquet(output_file, index=False)


def read_daily_data(symbol: str) -> pd.DataFrame | None:
    """
    读取单只股票的日线历史数据Parquet文件。

    :param symbol: 股票代码 (e.g., 'sh600000')
    :return: 包含日线数据的DataFrame，如果文件不存在则返回None。
    """
    file_path = DATA_ROOT / f"{symbol}.parquet"

    if not file_path.exists():
        print(f"WARN: Daily data file for symbol {symbol} not found at {file_path}")
        return None

    try:
        df = pd.read_parquet(file_path)
        return df
    except Exception as e:
        print(f"ERROR: Failed to read daily data for {symbol}. Error: {e}")
        return None


def read_daily_from_parquet(
    symbol: str,
    data_path: Path,
    start_date: date | None = None,
    end_date: date | None = None,
) -> pd.DataFrame:
    """
    从Parquet文件中读取单只股票的日线历史数据，并可选择按日期范围筛选。

    :param symbol: 股票代码。
    :param data_path: 数据存储的根目录。
    :param start_date: 筛选的开始日期。
    :param end_date: 筛选的结束日期。
    :return: 包含日线数据的DataFrame。
    """
    daily_data_path = data_path / "daily"
    file_path = daily_data_path / f"{symbol}.parquet"

    if not file_path.exists():
        print(f"WARN: Data file not found for {symbol} at {file_path}")
        return pd.DataFrame()

    df = pd.read_parquet(file_path)

    # 如果从文件读取的DataFrame为空，直接返回，避免KeyError
    if df.empty:
        return df

    # 确保 'trade_date' 列是 datetime 类型以便比较
    df["trade_date"] = pd.to_datetime(df["trade_date"]).dt.date

    if start_date:
        df = df[df["trade_date"] >= start_date]
    if end_date:
        df = df[df["trade_date"] <= end_date]

    return df
