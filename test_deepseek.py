import os
import time
from datetime import datetime, timedelta
import pandas as pd
import requests
from openai import OpenAI
from tradingagents.dataflows.config import get_config

# 从.env文件加载环境变量
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    print("警告: python-dotenv模块未安装，尝试直接读取环境变量")

# Test configuration
test_ticker = "AAPL"
test_date = "2024-11-01"
test_start_date = "2024-10-01"
test_end_date = "2024-11-01"

print("=== Testing DeepSeek API Integration ===")

# 主要测试函数：使用Alpha Vantage获取NVDA数据并通过DeepSeek API进行分析
def test_akshare_week_trend_deepseek_600519():
    print("\n5. Testing DeepSeek analysis on Alpha Vantage data (NVDA, one week)...")
    if not os.getenv("DEEPSEEK_API_KEY"):
        print("⚠️  DEEPSEEK_API_KEY not set, skipping analysis test")
        return
    try:
        # 获取Alpha Vantage API密钥
        config = get_config()
        alpha_vantage_api_key = config.get("api_keys", {}).get("alpha_vantage", "OFF86KOMER1N6JE8")  # 默认值作为备份
        
        # 准备获取过去7天的数据
        end_dt = datetime.now()
        start_dt = end_dt - timedelta(days=7)
        
        # 使用Alpha Vantage获取NVDA的当前行情数据
        # 使用GLOBAL_QUOTE端点（免费）
        url = f"https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol=NVDA&apikey={alpha_vantage_api_key}"
        response = requests.get(url)
        data = response.json()
        
        # 处理Alpha Vantage返回的数据
        print(f"Alpha Vantage响应内容: {data}")  # 调试信息：打印完整响应
        if "Global Quote" not in data or not data["Global Quote"]:
            error_msg = data.get('Error Message', data.get('Information', '未知错误'))
            print(f"✗ Alpha Vantage API错误: {error_msg}")
            return
        
        # 从Global Quote中提取数据
        global_quote = data["Global Quote"]
        
        # 构建数据摘要
        close_end = float(global_quote.get("05. price", 0))
        close_start = float(global_quote.get("08. previous close", 0))
        high_max = float(global_quote.get("03. high", 0))
        low_min = float(global_quote.get("04. low", 0))
        latest_trading_day = global_quote.get("07. latest trading day", str(datetime.now().date()))
        
        # 计算涨跌幅
        change_pct = float(global_quote.get("10. change percent", "0").replace("%", ""))
        
        summary = {
            "symbol": "NVDA",
            "latest_trading_day": latest_trading_day,
            "close_start": close_start,
            "close_end": close_end,
            "change_pct": change_pct,
            "high_max": high_max,
            "low_min": low_min,
        }
        
        client = OpenAI(base_url=config["deepseek_backend_url"], api_key=os.getenv("DEEPSEEK_API_KEY"))
        prompt = (
            f"请基于Alpha Vantage的最新行情数据，用中文用两句话总结英伟达(NVDA)的近期表现。"
            f"最新交易日{summary['latest_trading_day']}，收盘价{summary['close_end']:.2f}，前收盘价{summary['close_start']:.2f}，"
            f"涨跌幅{summary['change_pct']:.2f}%；当日最高{summary['high_max']:.2f}，最低{summary['low_min']:.2f}。"
            f"只输出两句话且不添加多余信息。"
        )
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[{"role": "system", "content": "你是专业的A股分析助手，只输出两句话。"}, {"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=200,
            top_p=1,
        )
        content = response.choices[0].message.content
        assert isinstance(content, str) and len(content) > 0
        print(content)
        print("✓ DeepSeek two-sentence analysis completed")
    except Exception as e:
        print(f"✗ Analysis test failed: {e}")

# 运行测试的主函数
def run_all_tests():
    # 只运行我们需要的测试函数
    test_akshare_week_trend_deepseek_600519()
    print("\n=== All Tests Completed ===")

if __name__ == "__main__":
    run_all_tests()
