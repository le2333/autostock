from pathlib import Path
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
