import pandas as pd
import numpy as np


class DataCleaner:
    """
    负责清洗从不同数据源获取的原始DataFrame。
    """

    @staticmethod
    def clean_stock_list(raw_df: pd.DataFrame) -> pd.DataFrame:
        """
        清洗从 akshare.stock_zh_a_spot_em() 获取的股票列表DataFrame。

        :param raw_df: 原始DataFrame
        :return: 清洗后的DataFrame，列名与 MarketOverview 模型对应。
        """
        if raw_df.empty:
            return pd.DataFrame()

        df = raw_df.copy()

        # 1. 定义列名映射关系
        column_mapping = {
            "代码": "symbol",
            "名称": "name",
            "最新价": "last_price",
            "市盈率-动态": "pe_ratio",
            "市净率": "pb_ratio",
            "总市值": "market_cap",
            # '上市日期' 需要从另一个接口获取，这里暂时留空
        }

        # 2. 选择并重命名列
        df = df[list(column_mapping.keys())]
        df.rename(columns=column_mapping, inplace=True)

        # 3. 数据类型转换和格式化

        # 转换数值列，将'-'等非数值替换为NaN
        numeric_cols = ["last_price", "pe_ratio", "pb_ratio", "market_cap"]
        for col in numeric_cols:
            df[col] = pd.to_numeric(df[col], errors="coerce")

        # 标准化股票代码
        def standardize_symbol(symbol: str) -> str:
            if symbol.startswith("6"):
                return f"{symbol}.SH"
            else:
                return f"{symbol}.SZ"

        df["symbol"] = df["symbol"].astype(str).apply(standardize_symbol)

        # 判断市场类型
        def get_market_type(symbol: str) -> str:
            if symbol.startswith("688"):
                return "科创板"
            if symbol.startswith("300"):
                return "创业板"
            if symbol.startswith("8") or symbol.startswith("4"):
                return "北交所"
            if symbol.startswith("60"):
                return "沪市主板"
            if symbol.startswith("00"):
                return "深市主板"
            return "未知"

        df["market_type"] = df["symbol"].apply(get_market_type)

        # 填充其他字段为默认值或None
        df["industry"] = None  # 行业信息需要从其他接口获取
        df["list_date"] = None  # 上市日期需要从其他接口获取
        df["status"] = "正常"  # 假设获取到的都是正常状态

        # 保证最终列的顺序和模型一致
        final_columns = [
            "symbol",
            "name",
            "industry",
            "market_type",
            "list_date",
            "status",
            "last_price",
            "market_cap",
            "pe_ratio",
            "pb_ratio",
        ]
        return df[final_columns]

    @staticmethod
    def clean_daily_history(raw_df: pd.DataFrame) -> pd.DataFrame:
        """
        清洗从 akshare.stock_zh_a_hist() 获取的日线历史数据DataFrame。

        :param raw_df: 原始DataFrame
        :return: 清洗后的DataFrame
        """
        if raw_df.empty:
            return pd.DataFrame()

        df = raw_df.copy()

        # 1. 定义列名映射关系
        column_mapping = {
            "日期": "trade_date",
            "开盘": "open",
            "收盘": "close",
            "最高": "high",
            "最低": "low",
            "成交量": "volume",
            "成交额": "amount",
            "换手率": "turnover_rate",
        }

        # 2. 选择并重命名我们需要的列
        df = df[list(column_mapping.keys())]
        df.rename(columns=column_mapping, inplace=True)

        # 3. 数据类型转换
        df["trade_date"] = pd.to_datetime(df["trade_date"]).dt.date
        numeric_cols = [
            "open",
            "close",
            "high",
            "low",
            "volume",
            "amount",
            "turnover_rate",
        ]
        for col in numeric_cols:
            df[col] = pd.to_numeric(df[col], errors="coerce")

        # 4. 成交量单位从"手"转换为"股"
        df["volume"] = df["volume"] * 100

        # 5. 确保数据按日期升序排列
        df.sort_values(by="trade_date", ascending=True, inplace=True)
        df.reset_index(drop=True, inplace=True)

        return df

    def clean_market_overview(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        清洗从Akshare获取的A股市场概览DataFrame。

        :param df: 原始DataFrame
        :return: 清洗后的DataFrame
        """
        # 重命名列
        rename_map = {
            "代码": "symbol",
            "名称": "name",
            "行业": "industry",
            "板块": "market_type",
            "上市日期": "list_date",
            "上市状态": "status",
            "最新价": "last_price",
        }

        # 只重命名DataFrame中实际存在的列
        df.rename(
            columns={k: v for k, v in rename_map.items() if k in df.columns},
            inplace=True,
        )

        # 增加一个更新时间戳
        df["updated_at"] = pd.Timestamp.now()

        # --- 安全地处理可选列 ---
        # 转换日期和时间戳
        if "list_date" in df.columns:
            df["list_date"] = pd.to_datetime(df["list_date"], errors="coerce").dt.date

        if "updated_at" in df.columns:
            df["updated_at"] = pd.to_datetime(df["updated_at"])

        # 标准化股票代码 (e.g., 600000 -> sh600000)
        def standardize_symbol(symbol: str) -> str:
            if symbol.startswith("6"):
                return f"sh{symbol}"
            elif symbol.startswith("0") or symbol.startswith("3"):
                return f"sz{symbol}"
            elif symbol.startswith("8") or symbol.startswith("4"):
                return f"bj{symbol}"
            else:
                return symbol

        df["symbol"] = df["symbol"].astype(str).apply(standardize_symbol)

        # 选择我们模型中需要的列
        required_columns = [
            "symbol",
            "name",
            "industry",
            "market_type",
            "list_date",
            "status",
            "last_price",
            "updated_at",
        ]
        df = df[required_columns]

        # 数据类型和空值处理
        df["pe_ratio"] = pd.to_numeric(df["pe_ratio"], errors="coerce").replace(
            [np.nan], [None]
        )
        df["last_price"] = pd.to_numeric(df["last_price"], errors="coerce")
        df["change_pct"] = pd.to_numeric(df["change_pct"], errors="coerce")
        df["total_market_cap"] = pd.to_numeric(df["total_market_cap"], errors="coerce")

        # 筛选出最终需要的列，并保证顺序与模型一致
        final_cols = [
            "symbol",
            "name",
            "industry",
            "market_type",
            "list_date",
            "status",
            "last_price",
            "updated_at",
        ]

        # 确保所有需要的列都存在，即使在API响应中它们是可选的
        for col in final_cols:
            if col not in df.columns:
                df[col] = None

        return df[final_cols]

    def clean_daily_history(self, df: pd.DataFrame, symbol: str) -> pd.DataFrame:
        """
        清洗单只股票的日线历史数据。
        """
        if df.empty:
            return pd.DataFrame()

        df = df.copy()

        # 重命名列
        rename_map = {
            "日期": "trade_date",
            "开盘": "open",
            "收盘": "close",
            "最高": "high",
            "最低": "low",
            "成交量": "volume",
            "成交额": "turnover",
            "换手率": "turnover_rate",
        }
        df.rename(columns=rename_map, inplace=True)

        # 增加symbol列
        df["symbol"] = symbol

        # 类型转换
        df["trade_date"] = pd.to_datetime(df["trade_date"]).dt.date
        numeric_cols = [
            "open",
            "close",
            "high",
            "low",
            "volume",
            "turnover",
            "turnover_rate",
        ]
        for col in numeric_cols:
            df[col] = pd.to_numeric(df[col], errors="coerce")

        # 筛选最终列
        final_cols = [
            "trade_date",
            "symbol",
            "open",
            "close",
            "high",
            "low",
            "volume",
            "turnover",
            "turnover_rate",
        ]

        return df[final_cols]
