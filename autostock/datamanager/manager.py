import logging
from pathlib import Path

# 强制日志配置，必须在其他库（如akshare）导入前执行
# 将sqlalchemy的日志级别设置为WARNING，以减少不必要的输出
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logging.getLogger("sqlalchemy").setLevel(logging.WARNING)

# 1. 获取根logger
root_logger = logging.getLogger()
# 2. 设置我们期望的最低级别
root_logger.setLevel(logging.WARNING)

# 3. 移除并替换所有现存的handler，确保我们的配置是唯一的
for handler in root_logger.handlers[:]:
    root_logger.removeHandler(handler)
logging.basicConfig(level=logging.WARNING)

from tqdm import tqdm
from autostock.datamanager.fetcher import AkshareFetcher
from autostock.datamanager.cleaner import DataCleaner
from autostock.datamanager.ops import market_ops, daily_ops, tracking_ops
from autostock.datamanager.session import get_session


class DataManager:
    """
    数据管理器，负责协调整个数据获取、清洗和存储的流程。
    """

    def __init__(self, data_path: str = "./datas"):
        self.data_path = Path(data_path)
        self.fetcher = AkshareFetcher()
        self.cleaner = DataCleaner()
        self.market_ops = market_ops
        self.daily_ops = daily_ops
        self.tracking_ops = tracking_ops
        self.data_path.mkdir(parents=True, exist_ok=True)
        print("INFO: DataManager initialized.")

    def sync_market_overview(self):
        """
        获取、清洗并更新A股市场所有股票的概览信息。
        这是一个完整的"索引数据"更新流程。
        """
        print("\n--- Starting Market Overview Update ---")
        # 1. 获取
        print("STEP 1/3: Fetching market overview data from Akshare...")
        raw_df = self.fetcher.get_market_overview()
        if raw_df is None or raw_df.empty:
            print("ERROR: Failed to fetch market overview data. Aborting update.")
            return
        print(f"STEP 1/3: Fetched {len(raw_df)} raw records.")

        # 2. 清洗
        print("STEP 2/3: Cleaning data...")
        cleaned_df = self.cleaner.clean_market_overview(raw_df)
        print(f"STEP 2/3: Cleaned {len(cleaned_df)} records.")

        # 3. 存储
        print("STEP 3/3: Upserting data into database...")
        with get_session() as session:
            self.market_ops.upsert_market_overview(session, cleaned_df)
            print("Upserting tracking stocks to database...")
            self.tracking_ops.upsert_tracking_stocks(session, cleaned_df)
        print("--- Market Overview Update Finished ---")

    def sync_daily_history(self, codes: list[str]):
        """
        为指定的股票列表（或所有股票）获取、清洗并存储其日线历史数据。

        :param codes: 一个包含股票代码的列表。如果为None，则处理数据库中所有股票。
        """
        print("\n--- Starting Daily Histories Update ---")

        symbols_to_process: list[str]
        if codes is None:
            # 1. 如果未指定codes，则从数据库获取所有股票列表
            print(
                "STEP 1/4: No specific codes provided. Getting all stocks from database..."
            )
            stock_list_df = self.market_ops.get_all_market_overview()
            if stock_list_df.empty:
                print(
                    "ERROR: Market overview is empty in the database. Run `sync_market_overview` first. Aborting."
                )
                return
            symbols_to_process = stock_list_df["symbol"].tolist()
        else:
            # 1. 如果指定了codes，则直接使用该列表
            print(f"STEP 1/4: Processing a specific list of {len(codes)} code(s).")
            symbols_to_process = codes

        print(f"Found {len(symbols_to_process)} stocks to update.")

        for i, code in enumerate(
            tqdm(symbols_to_process, desc="Syncing Daily History")
        ):
            # 2. 获取原始数据
            # print(f"--> Processing {code} ({i+1}/{len(symbols_to_process)})...")
            raw_df = self.fetcher.fetch_daily_history(code)

            # 3. 清洗数据
            cleaned_df = self.cleaner.clean_daily_history(raw_df, code)

            if cleaned_df.empty:
                # print(f"No data for {code}, skipping.")
                continue

            # 4. 存储
            self.daily_ops.save_daily_to_parquet(cleaned_df, self.data_path)

            # 5. 更新跟踪表
            print(f"Updating tracking info for {code}...")
            with get_session() as session:
                self.tracking_ops.update_daily_tracking_info(session, code, cleaned_df)

        print("--- Daily Histories Update Finished ---")

    def get_stock_list(self) -> list[str]:
        """
        获取当前跟踪的所有股票代码列表。
        """
        print("Getting all tracked stocks from database...")
        with get_session() as session:
            symbols = self.tracking_ops.get_all_tracked_symbols(session)
        print(f"Found {len(symbols)} tracked stocks.")
        return symbols


if __name__ == "__main__":
    # 日志配置已在文件顶部完成

    # 这个部分可以作为一个简单的测试入口，直接运行此文件即可更新数据
    manager = DataManager()

    # 步骤1: 更新市场股票列表
    manager.sync_market_overview()

    # 步骤2: 获取当前跟踪的股票列表
    all_stocks = manager.get_stock_list()
    print("All tracked stocks sample:", all_stocks[:5])

    # 步骤3: 选择少量股票，同步其日线数据作为演示
    if all_stocks:
        codes_to_sync = all_stocks[:2]  # 选择前2只股票进行同步
        print(f"\n[DEMO] Will sync daily data for: {codes_to_sync}")
        manager.sync_daily_history(codes=codes_to_sync)
    else:
        print("\nNo stocks to sync. Run `sync_market_overview` first.")
