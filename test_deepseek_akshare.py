import os
import time
from datetime import datetime, timedelta
import pandas as pd
import akshare as ak
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
test_ticker = "600519.SH"  # 贵州茅台

print("=== Testing DeepSeek API Integration with A股数据 ===")

# 测试函数：使用AKShare获取A股数据并通过DeepSeek API进行分析
def test_akshare_a股_deepseek():
    print(f"\nTesting DeepSeek analysis on AKShare A股数据 ({test_ticker} 贵州茅台)...")
    if not os.getenv("DEEPSEEK_API_KEY"):
        print("⚠️  DEEPSEEK_API_KEY not set, skipping analysis test")
        return
    
    try:
        # 获取AKShare数据
        print("正在获取A股数据...")
        
        # 获取实时行情数据
        try:
            realtime_data = ak.stock_zh_a_spot_em()
            stock_data = realtime_data[realtime_data["代码"] == test_ticker.split(".")[0]]
            if stock_data.empty:
                print(f"✗ 未找到 {test_ticker} 的实时数据")
                return
            
            # 提取实时数据
            stock_info = stock_data.iloc[0]
            print(f" 成功获取实时行情数据")
            
        except Exception as e:
            print(f" 获取实时数据失败: {str(e)}")
            return
        
        # 获取历史K线数据（最近7天）
        try:
            end_date = datetime.now().strftime("%Y%m%d")
            start_date = (datetime.now() - timedelta(days=7)).strftime("%Y%m%d")
            
            # 打印调试信息
            print(f"尝试获取历史数据: {test_ticker.split('.')[0]}, 日期范围: {start_date} 到 {end_date}")
            
            # 获取日线数据 - 使用正确的ak.stock_zh_a_hist()函数
            kline_data = ak.stock_zh_a_hist(
                symbol=test_ticker.split(".")[0],
                period="daily",
                start_date=start_date,
                end_date=end_date,
                adjust="qfq"  # 前复权
            )
            
            # 打印数据结构信息
            print(f"数据类型: {type(kline_data)}")
            print(f"数据是否为空: {kline_data.empty}")
            
            if not kline_data.empty:
                print(f"数据形状: {kline_data.shape}")
                print(f"列名: {list(kline_data.columns)}")
                print(f"索引: {type(kline_data.index)}")
                print(f"前几行数据: {kline_data.head()}")
                print(f"✓ 成功获取历史数据（{len(kline_data)}天）")
            else:
                print(f"✗ 未找到 {test_ticker} 的历史数据")
                return
            
        except Exception as e:
            print(f"✗ 获取历史数据失败: {str(e)}")
            import traceback
            traceback.print_exc()
            return
        
        # 获取股票基本信息
        try:
            stock_info_em = ak.stock_individual_info_em(symbol=test_ticker.split(".")[0])
            print(f"股票基本信息数据形状: {stock_info_em.shape}")
            print(f"股票基本信息列名: {list(stock_info_em.columns)}")
            
            # 添加错误处理，就像china_stock.py中那样
            company_name = "贵州茅台"
            industry = "食品饮料"
            
            try:
                company_name = stock_info_em.loc[stock_info_em["item"] == "股票简称", "value"].values[0]
                print(f"成功获取公司名称: {company_name}")
            except (IndexError, KeyError) as e:
                print(f"获取公司名称失败: {str(e)}")
                # 尝试其他可能的字段名
                try:
                    company_name = stock_info_em.loc[stock_info_em["item"].str.contains("简称"), "value"].values[0]
                    print(f"通过其他字段获取公司名称: {company_name}")
                except (IndexError, KeyError):
                    print("使用默认公司名称")
            
            try:
                industry = stock_info_em.loc[stock_info_em["item"] == "所属行业", "value"].values[0]
                print(f"成功获取行业信息: {industry}")
            except (IndexError, KeyError) as e:
                print(f"获取行业信息失败: {str(e)}")
                # 尝试其他可能的字段名
                try:
                    industry = stock_info_em.loc[stock_info_em["item"].str.contains("行业"), "value"].values[0]
                    print(f"通过其他字段获取行业信息: {industry}")
                except (IndexError, KeyError):
                    print("使用默认行业信息")
                    
        except Exception as e:
            print(f"✗ 获取股票基本信息失败: {str(e)}")
            import traceback
            traceback.print_exc()
            company_name = "贵州茅台"
            industry = "食品饮料"
        
        # 构建数据摘要
        # 从实时数据获取
        close_price = stock_info["最新价"]
        prev_close = stock_info["昨收"]
        change_amount = stock_info["涨跌额"]
        change_pct = stock_info["涨跌幅"]
        high_price = stock_info["最高"]
        low_price = stock_info["最低"]
        volume = stock_info["成交量"]
        amount = stock_info["成交额"]
        latest_trading_day = datetime.now().strftime("%Y-%m-%d")
        
        # 从历史数据获取 - 注意ak.stock_zh_a_hist()返回的列名是中文
        if not kline_data.empty:
            week_high = kline_data["最高"].max()
            week_low = kline_data["最低"].min()
            week_start_price = kline_data.iloc[0]["开盘"]
            week_end_price = kline_data.iloc[-1]["收盘"]
            week_change_pct = ((week_end_price - week_start_price) / week_start_price) * 100
        else:
            week_high = high_price
            week_low = low_price
            week_start_price = prev_close
            week_end_price = close_price
            week_change_pct = change_pct
        
        # 准备发送给DeepSeek的提示信息
        prompt = (
            f"请基于以下A股数据，用中文分析{company_name}({test_ticker})的近期表现和走势：\n\n"
            f"【公司基本信息】\n"
            f"- 股票名称: {company_name}\n"
            f"- 股票代码: {test_ticker}\n"
            f"- 所属行业: {industry}\n"
            f"- 分析日期: {latest_trading_day}\n\n"
            f"【今日行情】\n"
            f"- 最新价: {close_price}元\n"
            f"- 涨跌幅: {change_pct}%\n"
            f"- 涨跌额: {change_amount}元\n"
            f"- 最高价: {high_price}元\n"
            f"- 最低价: {low_price}元\n"
            f"- 昨收价: {prev_close}元\n"
            f"- 成交量: {volume}手\n"
            f"- 成交额: {amount/100000000:.2f}亿元\n\n"
            f"【近7天走势】\n"
            f"- 周涨跌幅: {week_change_pct:.2f}%\n"
            f"- 周最高价: {week_high}元\n"
            f"- 周最低价: {week_low}元\n"
            f"- 周初开盘价: {week_start_price}元\n"
            f"- 周末收盘价: {week_end_price}元\n\n"
            f"请提供：\n"
            f"1. 近期走势总结\n"
            f"2. 技术面分析（如支撑位、压力位等）\n"
            f"3. 投资建议\n\n"
            f"分析要求：专业、简洁，重点突出，用中文回答，不超过300字。"
        )
        
        # 调用DeepSeek API
        try:
            print("正在调用DeepSeek API进行分析...")
            
            # 获取配置
            config = get_config()
            deepseek_api_key = os.getenv("DEEPSEEK_API_KEY")
            deepseek_backend_url = config.get("deepseek_backend_url", "https://api.deepseek.com/v1")
            
            # 创建OpenAI客户端
            client = OpenAI(base_url=deepseek_backend_url, api_key=deepseek_api_key)
            
            # 发送请求
            response = client.chat.completions.create(
                model="deepseek-chat",
                messages=[
                    {"role": "system", "content": "你是一位专业的A股分析师，具有丰富的市场经验和专业知识。请基于提供的数据进行客观、专业的分析。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=500,
                top_p=1,
            )
            
            # 获取分析结果
            analysis_result = response.choices[0].message.content
            
            # 输出结果
            print(f"\n=== DeepSeek API 分析结果 ===")
            print(analysis_result)
            print(f"\n=== 分析完成 ===")
            
            print("✓ DeepSeek A股数据分析测试完成")
            
        except Exception as e:
            print(f"✗ DeepSeek API调用失败: {str(e)}")
            import traceback
            traceback.print_exc()
            return
        
    except Exception as e:
        print(f"✗ 测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return

# 运行测试的主函数
def run_all_tests():
    # 只运行我们需要的测试函数
    test_akshare_a股_deepseek()
    print("\n=== All Tests Completed ===")

if __name__ == "__main__":
    run_all_tests()
