#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试AKShare A股数据接口
"""

import sys
import os
import time
import random
from datetime import datetime, timedelta

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tradingagents.dataflows.china_stock import (
    get_china_stock_data,
    get_china_stock_indicators,
    get_china_stock_fundamentals,
    get_china_stock_news,
    get_china_stock_announcements,
    get_china_stock_realtime,
    check_price_limit,
    check_t1_trading,
    get_new_stocks,
    get_china_tech_indicators
)

# 测试股票代码：601919.SH (中远海控)
TEST_STOCK = "601919.SH"
TEST_STOCK_CODE = "601919"

# 测试日期
TODAY = datetime.now().strftime("%Y-%m-%d")
START_DATE = (datetime.now() - timedelta(days=60)).strftime("%Y-%m-%d")


def test_get_china_stock_data():
    """测试获取A股历史交易数据"""
    print("\n" + "="*60)
    print("测试：获取A股历史交易数据")
    print("="*60)
    
    start_time = time.time()
    result = get_china_stock_data(TEST_STOCK, START_DATE, TODAY)
    end_time = time.time()
    
    print(f"响应时间: {end_time - start_time:.4f}秒")
    print(f"结果类型: {type(result).__name__}")
    
    if isinstance(result, str):
        lines = result.splitlines()
        print(f"结果行数: {len(lines)}")
        print("前10行结果:")
        for line in lines[:10]:
            print(line)
    else:
        print(f"错误: {result}")


def test_get_china_stock_indicators():
    """测试获取A股技术指标数据"""
    print("\n" + "="*60)
    print("测试：获取A股技术指标数据")
    print("="*60)
    
    start_time = time.time()
    result = get_china_stock_indicators(TEST_STOCK, START_DATE, "macd")
    end_time = time.time()
    
    print(f"响应时间: {end_time - start_time:.4f}秒")
    print(f"结果类型: {type(result).__name__}")
    
    if isinstance(result, str):
        lines = result.splitlines()
        print(f"结果行数: {len(lines)}")
        print("前10行结果:")
        for line in lines[:10]:
            print(line)
    else:
        print(f"错误: {result}")


def test_get_china_stock_fundamentals():
    """测试获取A股上市公司基本面信息"""
    print("\n" + "="*60)
    print("测试：获取A股上市公司基本面信息")
    print("="*60)
    
    start_time = time.time()
    result = get_china_stock_fundamentals(TEST_STOCK, TODAY)
    end_time = time.time()
    
    print(f"响应时间: {end_time - start_time:.4f}秒")
    print(f"结果类型: {type(result).__name__}")
    
    if isinstance(result, str):
        lines = result.splitlines()
        print(f"结果行数: {len(lines)}")
        print("基本面信息:")
        for line in lines[:20]:  # 只显示前20行
            print(line)
    else:
        print(f"错误: {result}")


def test_get_china_stock_realtime():
    """测试获取A股实时行情数据"""
    print("\n" + "="*60)
    print("测试：获取A股实时行情数据")
    print("="*60)
    
    start_time = time.time()
    result = get_china_stock_realtime(TEST_STOCK)
    end_time = time.time()
    
    print(f"响应时间: {end_time - start_time:.4f}秒")
    print(f"结果类型: {type(result).__name__}")
    
    if isinstance(result, str):
        lines = result.splitlines()
        print(f"结果行数: {len(lines)}")
        print("实时行情:")
        for line in lines:
            print(line)
    else:
        print(f"错误: {result}")


def test_check_price_limit():
    """测试检查A股涨跌幅限制"""
    print("\n" + "="*60)
    print("测试：检查A股涨跌幅限制")
    print("="*60)
    
    # 假设当前价格和前收盘价
    current_price = 15.50
    previous_close = 14.00
    
    start_time = time.time()
    result = check_price_limit(TEST_STOCK, current_price, previous_close)
    end_time = time.time()
    
    print(f"响应时间: {end_time - start_time:.4f}秒")
    print(f"结果类型: {type(result).__name__}")
    
    if isinstance(result, str):
        print("涨跌幅限制检查结果:")
        print(result)
    else:
        print(f"错误: {result}")


def test_check_t1_trading():
    """测试检查T+1交易制度"""
    print("\n" + "="*60)
    print("测试：检查T+1交易制度")
    print("="*60)
    
    # 测试不同的买卖日期组合
    buy_date = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")  # 昨天买入
    sell_date = TODAY  # 今天卖出
    
    start_time = time.time()
    result = check_t1_trading(TEST_STOCK, buy_date, sell_date)
    end_time = time.time()
    
    print(f"响应时间: {end_time - start_time:.4f}秒")
    print(f"结果类型: {type(result).__name__}")
    
    if isinstance(result, str):
        print("T+1交易制度检查结果:")
        print(result)
    else:
        print(f"错误: {result}")


def test_get_china_tech_indicators():
    """测试获取中国投资者习惯的技术分析指标"""
    print("\n" + "="*60)
    print("测试：获取中国投资者习惯的技术分析指标")
    print("="*60)
    
    start_time = time.time()
    result = get_china_tech_indicators(TEST_STOCK, START_DATE, "macd,rsi,kdj,ma,vol")
    end_time = time.time()
    
    print(f"响应时间: {end_time - start_time:.4f}秒")
    print(f"结果类型: {type(result).__name__}")
    
    if isinstance(result, str):
        lines = result.splitlines()
        print(f"结果行数: {len(lines)}")
        print("技术指标结果前15行:")
        for line in lines[:15]:
            print(line)
    else:
        print(f"错误: {result}")


def test_invalid_stock():
    """测试无效股票代码"""
    print("\n" + "="*60)
    print("测试：无效股票代码")
    print("="*60)
    
    invalid_stock = "999999.SH"
    
    start_time = time.time()
    result = get_china_stock_data(invalid_stock, START_DATE, TODAY)
    end_time = time.time()
    
    print(f"响应时间: {end_time - start_time:.4f}秒")
    print(f"无效股票代码测试结果: {result}")


def run_all_tests():
    """运行所有测试"""
    print("开始测试AKShare A股数据接口")
    print(f"测试日期: {TODAY}")
    print(f"测试股票: {TEST_STOCK} (中远海控)")
    print("已启用风控措施：测试间添加随机延迟")
    
    # 运行测试用例
    test_get_china_stock_data()
    time.sleep(random.uniform(2, 6))
    
    test_get_china_stock_indicators()
    time.sleep(random.uniform(2, 6))
    
    test_get_china_stock_fundamentals()
    time.sleep(random.uniform(2, 6))
    
    test_get_china_stock_realtime()
    time.sleep(random.uniform(2, 6))
    
    test_check_price_limit()
    time.sleep(random.uniform(2, 6))
    
    test_check_t1_trading()
    time.sleep(random.uniform(2, 6))
    
    test_get_china_tech_indicators()
    time.sleep(random.uniform(2, 6))
    
    test_invalid_stock()
    
    print("\n" + "="*60)
    print("所有测试完成！")
    print("="*60)


if __name__ == "__main__":
    run_all_tests()
