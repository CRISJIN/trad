import os
from typing import Annotated
from datetime import datetime
import akshare as ak
import pandas as pd

# Initialize akshare (no token required for basic usage)
# Note: Some advanced features may require additional configuration
# ak.set_cookie("your_cookie")  # Optional: Set cookie if needed (method may not exist in current akshare version)

# Data validation configuration
MIN_RECORDS_THRESHOLD = 10
MAX_RESPONSE_TIME = 30  # seconds


def get_china_stock_data(
    symbol: Annotated[str, "ticker symbol of the company, e.g., 000001.SZ for 平安银行"],
    start_date: Annotated[str, "Start date in yyyy-mm-dd format"],
    end_date: Annotated[str, "End date in yyyy-mm-dd format"],
):
    """获取A股历史交易数据"""
    try:
        # Validate date format
        datetime.strptime(start_date, "%Y-%m-%d")
        datetime.strptime(end_date, "%Y-%m-%d")

        # Extract stock code without exchange suffix for akshare
        stock_code = symbol.split(".")[0]
        
        # 转换日期格式为AKShare要求的YYYYMMDD格式
        start_date_ak = start_date.replace("-", "")
        end_date_ak = end_date.replace("-", "")
        
        # Fetch historical data from akshare
        # Reference: https://akshare.akfamily.xyz/data/stock/stock.html#id2
        df = ak.stock_zh_a_hist(
            symbol=stock_code,
            period="daily",
            start_date=start_date_ak,
            end_date=end_date_ak,
            adjust="qfq"  # 前复权
        )

        # Check if data is empty
        if df.empty:
            return f"No data found for symbol '{symbol}' between {start_date} and {end_date}"

        # Data validation: Check minimum records
        if len(df) < MIN_RECORDS_THRESHOLD:
            return f"Warning: Only {len(df)} records found for {symbol}, which is below the minimum threshold of {MIN_RECORDS_THRESHOLD}"

        # Convert to the same format as other data sources
        df = df.sort_values(by="日期")
        df["日期"] = pd.to_datetime(df["日期"])
        df.set_index("日期", inplace=True)
        
        # Rename columns to match other data sources
        df = df.rename(columns={
            "开盘": "Open",
            "最高": "High",
            "最低": "Low",
            "收盘": "Close",
            "成交量": "Volume",
            "成交额": "Amount",
            "涨跌幅": "Change(%)",
            "涨跌额": "Change"
        })
        
        # Add Adj Close column (akshare provides adjusted close in qfq mode)
        df["Adj Close"] = df["Close"]
        
        # Round numerical values to 2 decimal places
        numeric_columns = ["Open", "High", "Low", "Close", "Adj Close"]
        df[numeric_columns] = df[numeric_columns].round(2)
        
        # Convert DataFrame to CSV string
        csv_string = df.to_csv()
        
        # Add header information
        header = f"# Stock data for {symbol} from {start_date} to {end_date}\n"
        header += f"# Total records: {len(df)}\n"
        header += f"# Data retrieved on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        header += f"# Data source: AKShare\n\n"
        
        return header + csv_string
        
    except Exception as e:
        return f"Error fetching data for {symbol}: {str(e)}"


def get_china_stock_indicators(
    symbol: Annotated[str, "ticker symbol of the company, e.g., 000001.SZ for 平安银行"],
    start_date: Annotated[str, "Start date in yyyy-mm-dd format"],
    indicator: Annotated[str, "Technical indicator name, e.g., macd, rsi, kdj"],
    window: Annotated[int, "Lookback window in days"] = 30,
):
    """获取A股技术指标数据"""
    try:
        # Validate date format
        datetime.strptime(start_date, "%Y-%m-%d")
        
        # Calculate end date based on start date and window
        end_date = datetime.now().strftime("%Y-%m-%d")
        
        # Extract stock code without exchange suffix for akshare
        stock_code = symbol.split(".")[0]
        
        # 转换日期格式为AKShare要求的YYYYMMDD格式
        start_date_ak = start_date.replace("-", "")
        end_date_ak = end_date.replace("-", "")
        
        # Fetch historical data from akshare
        df = ak.stock_zh_a_hist(
            symbol=stock_code,
            period="daily",
            start_date=start_date_ak,
            end_date=end_date_ak,
            adjust="qfq"  # 前复权
        )
        
        if df.empty:
            return f"No data found for symbol '{symbol}'"
        
        # Convert to the same format as other data sources
        df = df.sort_values(by="日期")
        df["日期"] = pd.to_datetime(df["日期"])
        df.set_index("日期", inplace=True)
        
        # Rename columns for compatibility
        df = df.rename(columns={
            "开盘": "Open",
            "最高": "High",
            "最低": "Low",
            "收盘": "Close",
            "成交量": "Volume"
        })
        
        # Calculate technical indicators
        if indicator.lower() == "macd":
            # Calculate MACD
            exp1 = df["Close"].ewm(span=12, adjust=False).mean()
            exp2 = df["Close"].ewm(span=26, adjust=False).mean()
            df["MACD"] = exp1 - exp2
            df["Signal"] = df["MACD"].ewm(span=9, adjust=False).mean()
            df["Histogram"] = df["MACD"] - df["Signal"]
            
            # Select relevant columns
            result_df = df[["MACD", "Signal", "Histogram"]]
        
        elif indicator.lower() == "rsi":
            # Calculate RSI
            delta = df["Close"].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            df["RSI"] = 100 - (100 / (1 + rs))
            
            # Select relevant columns
            result_df = df[["RSI"]]
        
        elif indicator.lower() == "kdj":
            # Calculate KDJ
            low_min = df["Low"].rolling(window=9).min()
            high_max = df["High"].rolling(window=9).max()
            df["RSV"] = (df["Close"] - low_min) / (high_max - low_min) * 100
            df["K"] = df["RSV"].ewm(com=2).mean()
            df["D"] = df["K"].ewm(com=2).mean()
            df["J"] = 3 * df["K"] - 2 * df["D"]
            
            # Select relevant columns
            result_df = df[["K", "D", "J"]]
        
        else:
            return f"Indicator '{indicator}' is not supported for China A-shares"
        
        # Round numerical values to 2 decimal places
        result_df = result_df.round(2)
        
        # Convert DataFrame to CSV string
        csv_string = result_df.to_csv()
        
        # Add header information
        header = f"# {indicator.upper()} data for {symbol} from {start_date} to {end_date}\n"
        header += f"# Lookback window: {window} days\n"
        header += f"# Data retrieved on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        header += f"# Data source: AKShare\n\n"
        
        return header + csv_string
        
    except Exception as e:
        return f"Error calculating {indicator} for {symbol}: {str(e)}"


def get_china_stock_fundamentals(
    symbol: Annotated[str, "ticker symbol of the company, e.g., 000001.SZ for 平安银行"],
    curr_date: Annotated[str, "Current date in yyyy-mm-dd format"],
):
    """获取A股上市公司基本面信息"""
    try:
        # Validate date format
        datetime.strptime(curr_date, "%Y-%m-%d")
        
        # Extract stock code without exchange suffix for akshare
        stock_code = symbol.split(".")[0]
        
        # Fetch basic company information from akshare
        try:
            # Get stock info from akshare
            stock_info = ak.stock_individual_info_em(symbol=stock_code)
            
            # Get financial indicators (try different methods if needed)
            try:
                # 尝试使用财务指标的替代接口
                fin_indicators = ak.stock_financial_analysis_indicator_em(symbol=stock_code)
            except Exception:
                # 尝试另一种财务指标接口
                try:
                    fin_indicators = ak.stock_business_analysis(symbol=stock_code)
                except Exception:
                    # Try alternative financial data source
                    fin_indicators = pd.DataFrame()
            
            # Get latest PE, PB data from real-time quotes
            try:
                realtime_data = ak.stock_zh_a_spot_em()
                realtime_data = realtime_data[realtime_data["代码"] == stock_code]
            except Exception:
                realtime_data = pd.DataFrame()
        except Exception as e:
            return f"Error fetching data from AKShare: {str(e)}"
        
        # Check if data is available
        if stock_info.empty:
            return f"No fundamental data found for {symbol}"
        
        # Extract relevant information with error handling
        try:
            company_name = stock_info.loc[stock_info["item"] == "股票简称", "value"].values[0]
        except (IndexError, KeyError):
            company_name = "N/A"
        
        # 添加调试信息查看stock_info的结构
        debug_info = ""
        if 'item' in stock_info.columns:
            debug_info = f"\nAvailable items in stock_info: {', '.join(stock_info['item'].tolist())[:100]}...\n"
        
        # 尝试不同的字段名来获取行业信息
        industry = "N/A"
        
        # 先尝试原始的字段名
        try:
            industry = stock_info.loc[stock_info["item"] == "所属行业", "value"].values[0]
        except (IndexError, KeyError):
            # 尝试其他可能的字段名
            try:
                industry = stock_info.loc[stock_info["item"].str.contains("行业"), "value"].values[0]
            except (IndexError, KeyError):
                pass
        
        # 如果还是获取不到行业信息，添加到调试信息中
        if industry == "N/A":
            debug_info += f"Failed to get industry. Stock_info columns: {list(stock_info.columns)}\n"
            debug_info += f"All items in stock_info: {', '.join(stock_info['item'].tolist())}\n"
            debug_info += f"Complete stock_info data:\n{stock_info.to_string()}\n"
            if 'xq_info' in locals():
                debug_info += f"Complete Xueqiu info data:\n{xq_info.to_string()}\n"
        
        # Get PE and PB from real-time data if available
        pe = "N/A"
        pb = "N/A"
        if not realtime_data.empty:
            pe = realtime_data.iloc[0]["市盈率-动态"]
            pb = realtime_data.iloc[0]["市净率"]
        
        # Create a formatted string with fundamentals
        result = f"# Fundamental Data for {company_name} ({symbol})\n"
        result += f"# As of {curr_date}\n\n"
        
        result += f"## Company Information\n"
        result += f"Company Name: {company_name}\n"
        result += f"Symbol: {symbol}\n"
        result += f"Industry: {industry}\n\n"
        
        result += f"## Financial Indicators\n"
        result += f"PE (Price-to-Earnings Ratio): {pe:.2f}\n" if pe != "N/A" else f"PE (Price-to-Earnings Ratio): N/A\n"
        result += f"PB (Price-to-Book Ratio): {pb:.2f}\n" if pb != "N/A" else f"PB (Price-to-Book Ratio): N/A\n"
        
        # Add financial indicators if available
        if not fin_indicators.empty:
            latest_fin = fin_indicators.iloc[0]
            result += f"ROE (Return on Equity): {latest_fin.get('roe', 'N/A'):.2f}%\n"
            result += f"ROA (Return on Assets): {latest_fin.get('roa', 'N/A'):.2f}%\n"
            result += f"Gross Profit Margin: {latest_fin.get('gross_profit_margin', 'N/A'):.2f}%\n"
            result += f"Net Profit Margin: {latest_fin.get('net_profit_margin', 'N/A'):.2f}%\n"
            result += f"EPS (Earnings Per Share): {latest_fin.get('eps', 'N/A'):.2f}\n"
        else:
            result += f"Detailed financial indicators not available\n"
        
        result += f"# Data source: AKShare\n"
        
        # Add debug information if available
        if debug_info:
            result += f"\n\n# DEBUG INFO:\n{debug_info}"
        
        return result
        
    except Exception as e:
        return f"Error fetching fundamentals for {symbol}: {str(e)}"


def get_china_stock_news(
    symbol: Annotated[str, "ticker symbol of the company, e.g., 000001.SZ for 平安银行"],
    start_date: Annotated[str, "Start date in yyyy-mm-dd format"],
    end_date: Annotated[str, "End date in yyyy-mm-dd format"],
):
    """获取A股相关新闻资讯"""
    try:
        # Validate date format
        datetime.strptime(start_date, "%Y-%m-%d")
        datetime.strptime(end_date, "%Y-%m-%d")
        
        # Extract stock code without exchange suffix for akshare
        stock_code = symbol.split(".")[0]
        
        # Fetch news related to the stock from akshare
        # Note: AKShare provides news through different interfaces
        try:
            # Get general financial news (stock_news_em doesn't support symbol parameter in latest AKShare)
            news = ak.stock_news_em()
            
            # Filter by date range if possible
            if 'pub_time' in news.columns:
                news['pub_time'] = pd.to_datetime(news['pub_time'])
                start_dt = pd.to_datetime(start_date)
                end_dt = pd.to_datetime(end_date)
                news = news[(news['pub_time'] >= start_dt) & (news['pub_time'] <= end_dt)]
        except Exception as e:
            # Fallback to empty DataFrame if news API fails
            news = pd.DataFrame()
        
        if news.empty:
            return f"No news found for {symbol} between {start_date} and {end_date}"
        
        # Sort news by publication time (newest first)
        news = news.sort_values(by=news.columns[2], ascending=False)  # Assuming third column is date
        
        # Create formatted news string
        result = f"# News for {symbol} from {start_date} to {end_date}\n"
        result += f"# Total news items: {len(news)}\n\n"
        
        for idx, row in news.iterrows():
            # Extract news details based on the interface used
            if 'title' in row:
                title = row['title']
            else:
                title = row.iloc[1]  # Assuming second column is title
            
            if 'pub_time' in row:
                pub_time = row['pub_time']
            elif 'pub_date' in row:
                pub_time = row['pub_date'].strftime("%Y-%m-%d %H:%M:%S")
            else:
                pub_time = row.iloc[2]  # Assuming third column is date
            
            if 'content' in row:
                content = row['content']
            else:
                content = "Content not available"
            
            if 'src' in row:
                source = row['src']
            else:
                source = "Unknown source"
            
            result += f"## {title}\n"
            result += f"Source: {source}\n"
            result += f"Published: {pub_time}\n\n"
            result += f"{content[:500]}...\n\n"  # Show first 500 characters
            result += "=" * 50 + "\n\n"
        
        return result
        
    except Exception as e:
        return f"Error fetching news for {symbol}: {str(e)}"


def get_china_stock_announcements(
    symbol: Annotated[str, "ticker symbol of the company, e.g., 000001.SZ for 平安银行"],
    start_date: Annotated[str, "Start date in yyyy-mm-dd format"],
    end_date: Annotated[str, "End date in yyyy-mm-dd format"],
):
    """获取A股上市公司公告"""
    try:
        # Validate date format
        datetime.strptime(start_date, "%Y-%m-%d")
        datetime.strptime(end_date, "%Y-%m-%d")
        
        # Extract stock code without exchange suffix for akshare
        stock_code = symbol.split(".")[0]
        
        # Fetch announcements from akshare
        try:
            # Get stock announcements using AKShare
            announcements = ak.stock_announcement_em(symbol=stock_code)
            
            # Filter by date range
            if 'ann_date' in announcements.columns:
                announcements['ann_date'] = pd.to_datetime(announcements['ann_date'])
                start_dt = pd.to_datetime(start_date)
                end_dt = pd.to_datetime(end_date)
                announcements = announcements[(announcements['ann_date'] >= start_dt) & (announcements['ann_date'] <= end_dt)]
        except Exception as e:
            # Fallback to empty DataFrame if announcement API fails
            announcements = pd.DataFrame()
        
        if announcements.empty:
            return f"No announcements found for {symbol} between {start_date} and {end_date}"
        
        # Sort announcements by date (newest first)
        announcements = announcements.sort_values(by='ann_date', ascending=False)
        
        # Create formatted announcements string
        result = f"# Announcements for {symbol} from {start_date} to {end_date}\n"
        result += f"# Total announcements: {len(announcements)}\n\n"
        
        for idx, row in announcements.iterrows():
            # Extract announcement details based on the interface used
            if 'title' in row:
                title = row['title']
            else:
                title = row.iloc[1]  # Assuming second column is title
            
            if 'ann_date' in row:
                ann_date = row['ann_date'].strftime("%Y-%m-%d")
            else:
                ann_date = row.iloc[2].strftime("%Y-%m-%d")  # Assuming third column is date
            
            if 'content' in row:
                content = row['content']
            else:
                content = "Content not available"
            
            if 'file_url' in row:
                file_url = row['file_url']
            elif 'url' in row:
                file_url = row['url']
            else:
                file_url = "URL not available"
            
            result += f"## {title}\n"
            result += f"Announcement Date: {ann_date}\n\n"
            result += f"{content[:500]}...\n"  # Show first 500 characters
            result += f"Full announcement: {file_url}\n\n"
            result += "=" * 50 + "\n\n"
        
        return result
        
    except Exception as e:
        return f"Error fetching announcements for {symbol}: {str(e)}"


def get_china_stock_realtime(
    symbols: Annotated[str, "Comma-separated list of ticker symbols, e.g., 000001.SZ,600000.SH"]
):
    """获取A股实时行情数据"""
    try:
        # Split symbols string into list
        symbol_list = [s.strip() for s in symbols.split(",")]
        
        # Extract stock codes without exchange suffix for akshare
        stock_codes = [s.split(".")[0] for s in symbol_list]
        
        # Fetch all real-time data from akshare
        all_realtime_data = ak.stock_zh_a_spot_em()
        
        # Filter for the requested symbols
        realtime_data = all_realtime_data[all_realtime_data["代码"].isin(stock_codes)]
        
        if realtime_data.empty:
            return f"No real-time data found for symbols: {symbols}"
        
        # Create formatted real-time data string
        result = f"# Real-time Data for {symbols}\n"
        result += f"# As of {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        result += f"# Data source: AKShare\n\n"
        
        result += "Symbol,Name,Price,Change,Change(%),Open,High,Low,Volume,Amount\n"
        result += "-" * 120 + "\n"
        
        for idx, row in realtime_data.iterrows():
            # Map the original symbol with exchange suffix
            stock_code = row["代码"]
            original_symbol = next((s for s in symbol_list if s.split(".")[0] == stock_code), stock_code)
            
            # 使用更健壮的方式访问数据，避免直接依赖固定列名
            name = row.get('名称', '未知名称')
            price = row.get('最新价', '0.00')
            change = row.get('涨跌额', '0.00')
            change_pct = row.get('涨跌幅', '0.00')
            
            # 尝试获取开盘价、最高价、最低价、成交量、成交额
            # 不同的AKShare版本可能有不同的列名
            open_price = row.get('开盘价', row.get('开盘', '0.00'))
            high_price = row.get('最高价', row.get('最高', '0.00'))
            low_price = row.get('最低价', row.get('最低', '0.00'))
            volume = row.get('成交量', '0')
            amount = row.get('成交额', '0')
            
            result += f"{original_symbol},{name},{price},{change},{change_pct}%,{open_price},{high_price},{low_price},{volume},{amount}\n"
        
        return result
        
    except Exception as e:
        return f"Error fetching real-time data: {str(e)}"


def check_price_limit(
    symbol: Annotated[str, "ticker symbol of the company, e.g., 000001.SZ for 平安银行"],
    current_price: Annotated[float, "Current price of the stock"],
    previous_close: Annotated[float, "Previous closing price of the stock"]
):
    """检查A股涨跌幅限制
    
    A股市场涨跌幅限制规则：
    - 主板股票：±10%
    - 科创板和创业板股票：±20%
    - 新股上市首日：±44%
    - ST股票：±5%
    
    Args:
        symbol: 股票代码
        current_price: 当前价格
        previous_close: 前收盘价
        
    Returns:
        包含涨跌幅信息的字符串
    """
    # Determine the price limit based on stock type
    if symbol.startswith("688") or symbol.startswith("300"):
        # 科创板(688xxx)或创业板(300xxx)：±20%
        limit = 0.2
        market = "科创板" if symbol.startswith("688") else "创业板"
    elif symbol.startswith("60") or symbol.startswith("000") or symbol.startswith("001"):
        # 主板(60xxx, 000xxx, 001xxx)：±10%
        limit = 0.1
        market = "主板"
    elif symbol.startswith("002"):
        # 中小板(002xxx)：±10%
        limit = 0.1
        market = "中小板"
    elif symbol.startswith("ST") or symbol.startswith("*ST"):
        # ST股票：±5%
        limit = 0.05
        market = "ST板块"
    else:
        # 默认±10%
        limit = 0.1
        market = "未知板块"
    
    # Calculate price limits
    up_limit = previous_close * (1 + limit)
    down_limit = previous_close * (1 - limit)
    
    # Calculate current change percentage
    change_pct = (current_price - previous_close) / previous_close
    
    # Check if price is within limits
    is_within_limit = down_limit <= current_price <= up_limit
    
    # Create result string
    result = f"# A股涨跌幅限制检查\n"
    result += f"股票代码: {symbol}\n"
    result += f"所属板块: {market}\n"
    result += f"前收盘价: {previous_close:.2f}\n"
    result += f"当前价格: {current_price:.2f}\n"
    result += f"涨跌幅限制: ±{limit*100:.0f}%\n"
    result += f"涨停价: {up_limit:.2f}\n"
    result += f"跌停价: {down_limit:.2f}\n"
    result += f"当前涨跌幅: {change_pct*100:.2f}%\n"
    result += f"是否在涨跌幅限制内: {'是' if is_within_limit else '否'}\n"
    
    return result


def check_t1_trading(
    symbol: Annotated[str, "ticker symbol of the company, e.g., 000001.SZ for 平安银行"],
    buy_date: Annotated[str, "Date of purchase in yyyy-mm-dd format"],
    sell_date: Annotated[str, "Date of sale in yyyy-mm-dd format"]
):
    """检查T+1交易制度
    
    A股市场实行T+1交易制度：
    - 当日买入的股票，次日才能卖出
    - 当日卖出股票的资金，当日可以继续买入股票，但次日才能转出到银行
    
    Args:
        symbol: 股票代码
        buy_date: 买入日期
        sell_date: 卖出日期
        
    Returns:
        包含T+1交易检查结果的字符串
    """
    # Convert dates to datetime objects
    buy_dt = datetime.strptime(buy_date, "%Y-%m-%d")
    sell_dt = datetime.strptime(sell_date, "%Y-%m-%d")
    
    # Calculate the difference between sell date and buy date
    delta = sell_dt - buy_dt
    
    # Check if sell date is after buy date
    is_t1_compliant = delta.days >= 1
    
    # Create result string
    result = f"# A股T+1交易制度检查\n"
    result += f"股票代码: {symbol}\n"
    result += f"买入日期: {buy_date}\n"
    result += f"卖出日期: {sell_date}\n"
    result += f"买卖间隔天数: {delta.days}天\n"
    result += f"是否符合T+1交易制度: {'是' if is_t1_compliant else '否'}\n"
    result += f"交易建议: {'可以卖出' if is_t1_compliant else '不能卖出，需次日才能卖出'}\n"
    
    return result


def get_new_stocks(
    start_date: Annotated[str, "Start date in yyyy-mm-dd format"],
    end_date: Annotated[str, "End date in yyyy-mm-dd format"]
):
    """获取新股申购信息
    
    Args:
        start_date: 开始日期
        end_date: 结束日期
        
    Returns:
        包含新股申购信息的字符串
    """
    try:
        # Validate date format
        datetime.strptime(start_date, "%Y-%m-%d")
        datetime.strptime(end_date, "%Y-%m-%d")
        
        # Fetch new stock information from akshare
        try:
            new_stocks = ak.stock_new_share_em()
            
            # Filter by date range
            new_stocks['网上申购日'] = pd.to_datetime(new_stocks['网上申购日'])
            start_dt = pd.to_datetime(start_date)
            end_dt = pd.to_datetime(end_date)
            new_stocks = new_stocks[(new_stocks['网上申购日'] >= start_dt) & (new_stocks['网上申购日'] <= end_dt)]
        except Exception as e:
            # Fallback to another new stock interface if available
            new_stocks = ak.stock_new_share_cninfo()
            
            # Filter by date range if possible
            if '申购日期' in new_stocks.columns:
                new_stocks['申购日期'] = pd.to_datetime(new_stocks['申购日期'])
                start_dt = pd.to_datetime(start_date)
                end_dt = pd.to_datetime(end_date)
                new_stocks = new_stocks[(new_stocks['申购日期'] >= start_dt) & (new_stocks['申购日期'] <= end_dt)]
        
        if new_stocks.empty:
            return f"No new stocks found between {start_date} and {end_date}"
        
        # Create formatted new stocks string
        result = f"# 新股申购信息 ({start_date} 至 {end_date})\n"
        result += f"# 共找到 {len(new_stocks)} 只新股\n"
        result += f"# Data source: AKShare\n\n"
        
        for idx, row in new_stocks.iterrows():
            # Extract new stock details based on the interface used
            if '股票简称' in row:
                name = row['股票简称']
            elif '名称' in row:
                name = row['名称']
            else:
                name = row.iloc[1]  # Assuming second column is name
            
            if '股票代码' in row:
                ts_code = row['股票代码']
            elif '代码' in row:
                ts_code = row['代码']
            else:
                ts_code = row.iloc[0]  # Assuming first column is code
            
            if '网上申购日' in row:
                issue_date = row['网上申购日'].strftime("%Y-%m-%d")
            elif '申购日期' in row:
                issue_date = row['申购日期'].strftime("%Y-%m-%d")
            else:
                issue_date = "N/A"
            
            if '发行价格' in row:
                price = row['发行价格']
            elif '价格' in row:
                price = row['价格']
            else:
                price = 0.0
            
            if '申购上限' in row:
                limit_amount = row['申购上限']
            elif 'limit_amount' in row:
                limit_amount = row['limit_amount']
            else:
                limit_amount = 0.0
            
            if '发行数量' in row:
                market_amount = row['发行数量']
            elif 'market_amount' in row:
                market_amount = row['market_amount']
            else:
                market_amount = 0.0
            
            if '上市日期' in row:
                list_date = row['上市日期'] if row['上市日期'] else '待定'
            elif 'list_date' in row:
                list_date = row['list_date'] if row['list_date'] else '待定'
            else:
                list_date = '待定'
            
            result += f"## {name} ({ts_code})\n"
            result += f"申购日期: {issue_date}\n"
            result += f"发行价格: {price:.2f}元\n"
            result += f"申购上限: {limit_amount:.2f}万股\n"
            result += f"发行数量: {market_amount:.2f}万股\n"
            result += f"上市日期: {list_date}\n\n"
        
        return result
        
    except Exception as e:
        return f"Error fetching new stocks: {str(e)}"


def get_china_tech_indicators(
    symbol: Annotated[str, "ticker symbol of the company, e.g., 000001.SZ for 平安银行"],
    start_date: Annotated[str, "Start date in yyyy-mm-dd format"],
    indicators: Annotated[str, "Comma-separated list of technical indicators, e.g., macd,rsi,kdj,ma,vol"]
):
    """获取符合中国投资者习惯的技术分析指标
    
    支持的技术指标：
    - MACD：平滑异同移动平均线
    - RSI：相对强弱指标
    - KDJ：随机指标
    - MA：移动平均线
    - VOL：成交量
    - BOLL：布林带
    - BIAS：乖离率
    - DMI：趋向指标
    - OBV：能量潮指标
    
    Args:
        symbol: 股票代码
        start_date: 开始日期
        indicators: 技术指标列表
        
    Returns:
        包含技术指标数据的字符串
    """
    try:
        # Validate date format
        datetime.strptime(start_date, "%Y-%m-%d")
        
        # Calculate end date based on start date (last 60 trading days)
        end_date = datetime.now().strftime("%Y-%m-%d")
        
        # Extract stock code without exchange suffix for akshare
        stock_code = symbol.split(".")[0]
        
        # 转换日期格式为AKShare要求的YYYYMMDD格式
        start_date_ak = start_date.replace("-", "")
        end_date_ak = end_date.replace("-", "")
        
        # Fetch historical data from akshare
        df = ak.stock_zh_a_hist(
            symbol=stock_code,
            period="daily",
            start_date=start_date_ak,
            end_date=end_date_ak,
            adjust="qfq"  # 前复权
        )
        
        if df.empty:
            return f"No data found for symbol '{symbol}'"
        
        # Convert to the same format as other data sources
        df = df.sort_values(by="日期")
        df["日期"] = pd.to_datetime(df["日期"])
        df.set_index("日期", inplace=True)
        
        # Rename columns for compatibility
        df = df.rename(columns={
            "开盘": "Open",
            "最高": "High",
            "最低": "Low",
            "收盘": "Close",
            "成交量": "Volume",
            "成交额": "Amount"
        })
        
        # Calculate requested technical indicators
        indicator_list = [ind.strip().lower() for ind in indicators.split(",")]
        result_df = pd.DataFrame(index=df.index)
        
        for indicator in indicator_list:
            if indicator == "macd":
                # Calculate MACD
                exp1 = df["Close"].ewm(span=12, adjust=False).mean()
                exp2 = df["Close"].ewm(span=26, adjust=False).mean()
                df["MACD"] = exp1 - exp2
                df["Signal"] = df["MACD"].ewm(span=9, adjust=False).mean()
                df["Histogram"] = df["MACD"] - df["Signal"]
                result_df = pd.concat([result_df, df[["MACD", "Signal", "Histogram"]]], axis=1)
            
            elif indicator == "rsi":
                # Calculate RSI
                delta = df["Close"].diff()
                gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
                loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
                rs = gain / loss
                df["RSI"] = 100 - (100 / (1 + rs))
                result_df = pd.concat([result_df, df[["RSI"]]], axis=1)
            
            elif indicator == "kdj":
                # Calculate KDJ
                low_min = df["Low"].rolling(window=9).min()
                high_max = df["High"].rolling(window=9).max()
                df["RSV"] = (df["Close"] - low_min) / (high_max - low_min) * 100
                df["K"] = df["RSV"].ewm(com=2).mean()
                df["D"] = df["K"].ewm(com=2).mean()
                df["J"] = 3 * df["K"] - 2 * df["D"]
                result_df = pd.concat([result_df, df[["K", "D", "J"]]], axis=1)
            
            elif indicator == "ma":
                # Calculate Moving Averages (5, 10, 20, 30 days) - 移除MA60因为需要至少60天数据
                df["MA5"] = df["Close"].rolling(window=5).mean()
                df["MA10"] = df["Close"].rolling(window=10).mean()
                df["MA20"] = df["Close"].rolling(window=20).mean()
                df["MA30"] = df["Close"].rolling(window=30).mean()
                result_df = pd.concat([result_df, df[["MA5", "MA10", "MA20", "MA30"]]], axis=1)
            
            elif indicator == "vol":
                # Calculate Volume Moving Averages (5, 10, 20 days)
                df["VOL5"] = df["Volume"].rolling(window=5).mean()
                df["VOL10"] = df["Volume"].rolling(window=10).mean()
                df["VOL20"] = df["Volume"].rolling(window=20).mean()
                result_df = pd.concat([result_df, df[["Volume", "VOL5", "VOL10", "VOL20"]]], axis=1)
            
            elif indicator == "boll":
                # Calculate Bollinger Bands
                df["MA20"] = df["Close"].rolling(window=20).mean()
                df["STD20"] = df["Close"].rolling(window=20).std()
                df["BOLL_UPPER"] = df["MA20"] + 2 * df["STD20"]
                df["BOLL_MIDDLE"] = df["MA20"]
                df["BOLL_LOWER"] = df["MA20"] - 2 * df["STD20"]
                result_df = pd.concat([result_df, df[["BOLL_UPPER", "BOLL_MIDDLE", "BOLL_LOWER"]]], axis=1)
            
            elif indicator == "bias":
                # Calculate BIAS (5, 10, 20 days)
                df["BIAS5"] = (df["Close"] - df["Close"].rolling(window=5).mean()) / df["Close"].rolling(window=5).mean() * 100
                df["BIAS10"] = (df["Close"] - df["Close"].rolling(window=10).mean()) / df["Close"].rolling(window=10).mean() * 100
                df["BIAS20"] = (df["Close"] - df["Close"].rolling(window=20).mean()) / df["Close"].rolling(window=20).mean() * 100
                result_df = pd.concat([result_df, df[["BIAS5", "BIAS10", "BIAS20"]]], axis=1)
            
            elif indicator == "dmi":
                # Calculate DMI (Directional Movement Index)
                # This is a simplified version of DMI
                df["TR"] = pd.concat([df["High"] - df["Low"], 
                                     abs(df["High"] - df["Close"].shift(1)), 
                                     abs(df["Low"] - df["Close"].shift(1))], axis=1).max(axis=1)
                df["+DM"] = df["High"] - df["High"].shift(1)
                df["-DM"] = df["Low"].shift(1) - df["Low"]
                df["+DM"] = df["+DM"].where((df["+DM"] > df["-DM"]) & (df["+DM"] > 0), 0)
                df["-DM"] = df["-DM"].where((df["-DM"] > df["+DM"]) & (df["-DM"] > 0), 0)
                
                # Calculate smoothed TR, +DM, -DM
                df["TR_SMA14"] = df["TR"].rolling(window=14).mean()
                df["+DM_SMA14"] = df["+DM"].rolling(window=14).mean()
                df["-DM_SMA14"] = df["-DM"].rolling(window=14).mean()
                
                # Calculate +DI, -DI, ADX
                df["+DI"] = (df["+DM_SMA14"] / df["TR_SMA14"]) * 100
                df["-DI"] = (df["-DM_SMA14"] / df["TR_SMA14"]) * 100
                df["DX"] = abs(df["+DI"] - df["-DI"]) / (df["+DI"] + df["-DI"]) * 100
                df["ADX"] = df["DX"].rolling(window=14).mean()
                
                result_df = pd.concat([result_df, df[["+DI", "-DI", "ADX"]]], axis=1)
            
            elif indicator == "obv":
                # Calculate OBV (On-Balance Volume)
                df["OBV"] = (df["Volume"] * ((df["Close"] > df["Close"].shift(1)).astype(int) - (df["Close"] < df["Close"].shift(1)).astype(int))).cumsum()
                result_df = pd.concat([result_df, df[["OBV"]]], axis=1)
        
        # Round numerical values to 2 decimal places
        result_df = result_df.round(2)
        
        # Data validation: Check if all indicators have sufficient data
        valid_records = len(result_df.dropna(subset=[col for col in result_df.columns if col not in ['MA30', 'VOL20']]))
        if valid_records < MIN_RECORDS_THRESHOLD:
            # 添加调试信息
            debug_info = f"\nDebug Info:\n"
            debug_info += f"原始数据行数: {len(df)}\n"
            debug_info += f"计算后数据行数: {len(result_df)}\n"
            debug_info += f"非空数据行数: {valid_records}\n"
            debug_info += f"数据列名: {list(result_df.columns)}\n"
            if len(result_df) > 0:
                debug_info += f"前5行数据:\n{result_df.head()}\n"
            return f"Warning: Insufficient valid data for indicators. Only {valid_records} valid records found." + debug_info
        
        # Convert DataFrame to CSV string
        csv_string = result_df.to_csv()
        
        # Add header information
        header = f"# Technical Indicators for {symbol} ({start_date} to {end_date})\n"
        header += f"# Indicators: {indicators}\n"
        header += f"# Total records: {len(result_df)}\n"
        header += f"# Valid records: {len(result_df.dropna())}\n"
        header += f"# Data retrieved on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        header += f"# Data source: AKShare\n\n"
        
        return header + csv_string
        
    except Exception as e:
        return f"Error calculating technical indicators: {str(e)}"
