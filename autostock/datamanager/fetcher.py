import pandas as pd
import akshare as ak
from functools import lru_cache


class AkshareFetcher:
    """
    一个使用 akshare 作为数据源的数据获取器。

    所有与 akshare API 的直接交互都应封装在此类中，
    为上层业务逻辑提供稳定、格式统一的 Pandas DataFrame。
    """

    def __init__(self):
        # 可以在这里添加缓存、代理等设置
        pass

    def get_market_overview(self) -> pd.DataFrame | None:
        """
        获取A股市场的实时概览数据（所有股票）。

        :return: 包含股票列表和基本信息的DataFrame，失败则返回None。
        """
        print("INFO: Fetching latest market overview from Akshare...")
        try:
            # stock_zh_a_spot_em() 是一个常用的获取A股所有股票信息的接口
            stock_df = ak.stock_zh_a_spot_em()
            return stock_df
        except Exception as e:
            print(f"ERROR: Failed to fetch market overview from Akshare. Error: {e}")
            return None

    @staticmethod
    @lru_cache(maxsize=1)
    def fetch_stock_list() -> pd.DataFrame:
        """
        获取A股所有股票的基本信息列表。

        使用东方财富的接口，数据较全。
        使用 lru_cache 缓存结果，避免在单次运行中重复从网络请求。

        :return: 包含股票代码、名称等信息的 DataFrame。如果获取失败则返回一个空的DataFrame。
        """
        try:
            print("INFO: Fetching stock list from akshare...")
            stock_df = ak.stock_zh_a_spot_em()
            print(f"INFO: Successfully fetched {len(stock_df)} stocks.")
            return stock_df
        except Exception as e:
            print(f"ERROR: Failed to fetch stock list from akshare: {e}")
            # 返回一个空的 DataFrame，列名与成功时一致，以避免下游代码出错
            return pd.DataFrame(
                columns=[
                    "代码",
                    "名称",
                    "最新价",
                    "涨跌幅",
                    "涨跌额",
                    "成交量",
                    "成交额",
                    "振幅",
                    "最高",
                    "最低",
                    "今开",
                    "昨收",
                    "量比",
                    "换手率",
                    "市盈率-动态",
                    "市净率",
                    "总市值",
                    "流通市值",
                    "涨速",
                    "5分钟涨跌",
                    "60日涨跌幅",
                    "年初至今涨跌幅",
                ]
            )

    @staticmethod
    def fetch_daily_history(
        symbol: str,
        start_date: str = "19900101",
        end_date: str = "20990101",
        adjust: str = "qfq",
    ) -> pd.DataFrame:
        """
        获取单个股票的日线历史数据。

        :param symbol: 股票代码, e.g., "000001"
        :param start_date: 开始日期, 格式 "YYYYMMDD"
        :param end_date: 结束日期, 格式 "YYYYMMDD"
        :param adjust: 复权类型, "qfq" for 前复权, "hfq" for 后复权, "" for 不复权. 默认为前复权。
        :return: 包含日线数据的 DataFrame，如果获取失败则返回空DataFrame。
        """
        try:
            print(
                f"INFO: Fetching daily history for {symbol} from {start_date} to {end_date} (adjust={adjust})..."
            )
            history_df = ak.stock_zh_a_hist(
                symbol=symbol,
                period="daily",
                start_date=start_date,
                end_date=end_date,
                adjust=adjust,
            )

            if history_df is None or history_df.empty:
                print(
                    f"WARN: No daily history data returned for {symbol}. It might be a new stock or an invalid code."
                )
                return pd.DataFrame()

            print(
                f"INFO: Successfully fetched {len(history_df)} days of history for {symbol}."
            )
            return history_df
        except Exception as e:
            print(f"ERROR: Failed to fetch daily history for {symbol}: {e}")
            return pd.DataFrame()

    def get_daily_history(
        self, symbol: str, period: str = "daily", adjust: str = ""
    ) -> pd.DataFrame | None:
        """
        获取单只股票的日线历史数据。

        :param symbol: 股票代码, e.g., "sh600000"
        :param period: 数据周期, "daily" for 日线
        :param adjust: 复权类型, "qfq" for 前复权.
        :return: 包含日线数据的 DataFrame，如果获取失败则返回None。
        """
        try:
            # Akshare需要纯数字代码
            numeric_symbol = "".join(filter(str.isdigit, symbol))

            history_df = ak.stock_zh_a_hist(
                symbol=numeric_symbol,
                period=period,
                adjust=adjust,
            )

            if history_df is None or history_df.empty:
                print(
                    f"WARN: No daily history data returned for {symbol}. It might be a new stock or an invalid code."
                )
                return None

            return history_df
        except Exception as e:
            print(f"ERROR: Failed to fetch daily history for {symbol}: {e}")
            return None
