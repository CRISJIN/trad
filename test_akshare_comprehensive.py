#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
全面测试AKShare库的核心功能
"""

import os
import sys
import time
import pandas as pd
from datetime import datetime, timedelta

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import akshare as ak

# 测试配置
TODAY = datetime.now().strftime("%Y-%m-%d")
START_DATE = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
TEST_STOCK = "601919.SH"  # 中远海控
TEST_STOCK_CODE = "601919"
TEST_INDEX = "000001.SH"  # 上证指数
TEST_FUND = "000001"  # 华夏成长混合
TEST_FUTURE = "IF2403"  # 沪深300股指期货

# 测试结果记录
class TestResult:
    def __init__(self):
        self.total_tests = 0
        self.passed_tests = 0
        self.failed_tests = 0
        self.results = []
    
    def add_result(self, test_name, status, message, response_time):
        self.total_tests += 1
        if status == "PASS":
            self.passed_tests += 1
        else:
            self.failed_tests += 1
        
        self.results.append({
            "test_name": test_name,
            "status": status,
            "message": message,
            "response_time": response_time,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })
    
    def generate_report(self):
        report = "=" * 80 + "\n"
        report += "AKShare 全面测试报告\n"
        report += "=" * 80 + "\n"
        report += f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        report += f"总测试数: {self.total_tests}\n"
        report += f"通过测试: {self.passed_tests}\n"
        report += f"失败测试: {self.failed_tests}\n"
        report += f"通过率: {self.passed_tests / self.total_tests * 100:.2f}%\n"
        report += "=" * 80 + "\n\n"
        
        report += "详细测试结果:\n"
        report += "-" * 80 + "\n"
        report += f"{'测试名称':<40} {'状态':<8} {'响应时间(秒)':<15} {'消息':<20}\n"
        report += "-" * 80 + "\n"
        
        for result in self.results:
            report += f"{result['test_name']:<40} {result['status']:<8} {result['response_time']:<15.4f} {result['message']:<20}\n"
        
        report += "\n" + "=" * 80 + "\n"
        return report

# 测试结果实例
test_result = TestResult()


def test_stock_basic_info():
    """测试股票基本信息获取"""
    test_name = "股票基本信息获取"
    print(f"\n测试: {test_name}")
    
    try:
        start_time = time.time()
        # 获取股票列表
        stock_list = ak.stock_zh_a_spot_em()
        end_time = time.time()
        response_time = end_time - start_time
        
        if not stock_list.empty:
            test_result.add_result(test_name, "PASS", f"获取到 {len(stock_list)} 只股票", response_time)
            print(f"  ✓ 成功获取到 {len(stock_list)} 只股票")
        else:
            test_result.add_result(test_name, "FAIL", "未获取到股票列表", response_time)
            print(f"  ✗ 未获取到股票列表")
    
    except Exception as e:
        end_time = time.time()
        response_time = end_time - start_time
        test_result.add_result(test_name, "FAIL", str(e), response_time)
        print(f"  ✗ 失败: {e}")


def test_stock_historical_data():
    """测试股票历史数据获取"""
    test_name = "股票历史数据获取"
    print(f"\n测试: {test_name}")
    
    try:
        start_time = time.time()
        # 获取股票历史数据
        df = ak.stock_zh_a_hist(symbol=TEST_STOCK_CODE, period="daily", start_date=START_DATE, end_date=TODAY, adjust="qfq")
        end_time = time.time()
        response_time = end_time - start_time
        
        if not df.empty:
            test_result.add_result(test_name, "PASS", f"获取到 {len(df)} 条记录", response_time)
            print(f"  ✓ 成功获取到 {len(df)} 条记录")
        else:
            test_result.add_result(test_name, "FAIL", "未获取到历史数据", response_time)
            print(f"  ✗ 未获取到历史数据")
    
    except Exception as e:
        end_time = time.time()
        response_time = end_time - start_time
        test_result.add_result(test_name, "FAIL", str(e), response_time)
        print(f"  ✗ 失败: {e}")


def test_stock_realtime_quote():
    """测试股票实时行情获取"""
    test_name = "股票实时行情获取"
    print(f"\n测试: {test_name}")
    
    try:
        start_time = time.time()
        # 获取实时行情
        df = ak.stock_zh_a_spot_em()
        end_time = time.time()
        response_time = end_time - start_time
        
        if not df.empty:
            # 查找特定股票
            stock_data = df[df["代码"] == TEST_STOCK_CODE]
            if not stock_data.empty:
                test_result.add_result(test_name, "PASS", f"获取到 {TEST_STOCK_CODE} 实时数据", response_time)
                print(f"  ✓ 成功获取到 {TEST_STOCK_CODE} 实时数据")
            else:
                test_result.add_result(test_name, "PASS", f"获取到行情数据，但未找到 {TEST_STOCK_CODE}", response_time)
                print(f"  ✓ 获取到行情数据，但未找到 {TEST_STOCK_CODE}")
        else:
            test_result.add_result(test_name, "FAIL", "未获取到实时行情", response_time)
            print(f"  ✗ 未获取到实时行情")
    
    except Exception as e:
        end_time = time.time()
        response_time = end_time - start_time
        test_result.add_result(test_name, "FAIL", str(e), response_time)
        print(f"  ✗ 失败: {e}")


def test_index_data():
    """测试指数数据获取"""
    test_name = "指数数据获取"
    print(f"\n测试: {test_name}")
    
    try:
        start_time = time.time()
        # 获取上证指数历史数据
        df = ak.stock_zh_index_daily(symbol=TEST_INDEX)
        end_time = time.time()
        response_time = end_time - start_time
        
        if not df.empty:
            test_result.add_result(test_name, "PASS", f"获取到 {len(df)} 条指数记录", response_time)
            print(f"  ✓ 成功获取到 {len(df)} 条指数记录")
        else:
            test_result.add_result(test_name, "FAIL", "未获取到指数数据", response_time)
            print(f"  ✗ 未获取到指数数据")
    
    except Exception as e:
        end_time = time.time()
        response_time = end_time - start_time
        test_result.add_result(test_name, "FAIL", str(e), response_time)
        print(f"  ✗ 失败: {e}")


def test_fund_data():
    """测试基金数据获取"""
    test_name = "基金数据获取"
    print(f"\n测试: {test_name}")
    
    try:
        start_time = time.time()
        # 获取基金列表（使用更稳定的方法）
        try:
            # 尝试不同的基金数据获取方法
            fund_list = ak.fund_em_fund_name()
        except AttributeError:
            try:
                # 尝试另一种方法
                fund_list = ak.fund_all()
            except AttributeError:
                # 尝试第三种方法
                fund_list = pd.DataFrame()
        
        end_time = time.time()
        response_time = end_time - start_time
        
        if not fund_list.empty:
            test_result.add_result(test_name, "PASS", f"获取到 {len(fund_list)} 只基金", response_time)
            print(f"  ✓ 成功获取到 {len(fund_list)} 只基金")
        else:
            test_result.add_result(test_name, "FAIL", "未获取到基金列表", response_time)
            print(f"  ✗ 未获取到基金列表")
    
    except Exception as e:
        end_time = time.time()
        response_time = end_time - start_time
        test_result.add_result(test_name, "FAIL", str(e), response_time)
        print(f"  ✗ 失败: {e}")


def test_future_data():
    """测试期货数据获取"""
    test_name = "期货数据获取"
    print(f"\n测试: {test_name}")
    
    try:
        start_time = time.time()
        # 获取期货列表（使用更稳定的方法）
        try:
            # 尝试不同的期货数据获取方法
            future_list = ak.futures_zh_spot_name()
        except AttributeError:
            try:
                # 尝试另一种方法
                future_list = ak.futures_zh_spot()
            except AttributeError:
                # 尝试第三种方法
                future_list = pd.DataFrame()
        
        end_time = time.time()
        response_time = end_time - start_time
        
        if not future_list.empty:
            test_result.add_result(test_name, "PASS", f"获取到 {len(future_list)} 个期货品种", response_time)
            print(f"  ✓ 成功获取到 {len(future_list)} 个期货品种")
        else:
            test_result.add_result(test_name, "FAIL", "未获取到期货列表", response_time)
            print(f"  ✗ 未获取到期货列表")
    
    except Exception as e:
        end_time = time.time()
        response_time = end_time - start_time
        test_result.add_result(test_name, "FAIL", str(e), response_time)
        print(f"  ✗ 失败: {e}")


def test_financial_indicators():
    """测试财务指标获取"""
    test_name = "财务指标获取"
    print(f"\n测试: {test_name}")
    
    try:
        start_time = time.time()
        # 获取财务指标
        fin_indicators = ak.stock_financial_analysis_indicator(symbol=TEST_STOCK_CODE)
        end_time = time.time()
        response_time = end_time - start_time
        
        if not fin_indicators.empty:
            test_result.add_result(test_name, "PASS", f"获取到 {len(fin_indicators)} 条财务指标", response_time)
            print(f"  ✓ 成功获取到 {len(fin_indicators)} 条财务指标")
        else:
            test_result.add_result(test_name, "FAIL", "未获取到财务指标", response_time)
            print(f"  ✗ 未获取到财务指标")
    
    except Exception as e:
        end_time = time.time()
        response_time = end_time - start_time
        test_result.add_result(test_name, "FAIL", str(e), response_time)
        print(f"  ✗ 失败: {e}")


def test_news_data():
    """测试新闻数据获取"""
    test_name = "新闻数据获取"
    print(f"\n测试: {test_name}")
    
    try:
        start_time = time.time()
        # 获取财经新闻（使用更稳定的方法）
        try:
            # 尝试不同的新闻数据获取方法
            news = ak.stock_news_cninfo(symbol=TEST_STOCK_CODE)
        except AttributeError:
            try:
                # 尝试另一种方法
                news = ak.stock_news_em()
            except AttributeError:
                # 尝试第三种方法
                news = pd.DataFrame()
        
        end_time = time.time()
        response_time = end_time - start_time
        
        if not news.empty:
            test_result.add_result(test_name, "PASS", f"获取到 {len(news)} 条新闻", response_time)
            print(f"  ✓ 成功获取到 {len(news)} 条新闻")
        else:
            test_result.add_result(test_name, "FAIL", "未获取到新闻数据", response_time)
            print(f"  ✗ 未获取到新闻数据")
    
    except Exception as e:
        end_time = time.time()
        response_time = end_time - start_time
        test_result.add_result(test_name, "FAIL", str(e), response_time)
        print(f"  ✗ 失败: {e}")


def test_industry_data():
    """测试行业数据获取"""
    test_name = "行业数据获取"
    print(f"\n测试: {test_name}")
    
    try:
        start_time = time.time()
        # 获取行业板块数据
        industry_data = ak.stock_board_industry_name_em()
        end_time = time.time()
        response_time = end_time - start_time
        
        if not industry_data.empty:
            test_result.add_result(test_name, "PASS", f"获取到 {len(industry_data)} 个行业", response_time)
            print(f"  ✓ 成功获取到 {len(industry_data)} 个行业")
        else:
            test_result.add_result(test_name, "FAIL", "未获取到行业数据", response_time)
            print(f"  ✗ 未获取到行业数据")
    
    except Exception as e:
        end_time = time.time()
        response_time = end_time - start_time
        test_result.add_result(test_name, "FAIL", str(e), response_time)
        print(f"  ✗ 失败: {e}")


def test_stock_company_info():
    """测试上市公司信息获取"""
    test_name = "上市公司信息获取"
    print(f"\n测试: {test_name}")
    
    try:
        start_time = time.time()
        # 获取上市公司基本信息
        company_info = ak.stock_individual_info_em(symbol=TEST_STOCK_CODE)
        end_time = time.time()
        response_time = end_time - start_time
        
        if not company_info.empty:
            test_result.add_result(test_name, "PASS", f"获取到上市公司信息", response_time)
            print(f"  ✓ 成功获取到上市公司信息")
        else:
            test_result.add_result(test_name, "FAIL", "未获取到上市公司信息", response_time)
            print(f"  ✗ 未获取到上市公司信息")
    
    except Exception as e:
        end_time = time.time()
        response_time = end_time - start_time
        test_result.add_result(test_name, "FAIL", str(e), response_time)
        print(f"  ✗ 失败: {e}")


def test_stock_tech_indicators():
    """测试技术指标获取"""
    test_name = "技术指标获取"
    print(f"\n测试: {test_name}")
    
    try:
        start_time = time.time()
        # 获取股票历史数据
        df = ak.stock_zh_a_hist(symbol=TEST_STOCK_CODE, period="daily", start_date=START_DATE, end_date=TODAY, adjust="qfq")
        end_time = time.time()
        response_time = end_time - start_time
        
        if not df.empty:
            # 计算简单的技术指标（MA）
            df['MA5'] = df['收盘'].rolling(window=5).mean()
            df['MA10'] = df['收盘'].rolling(window=10).mean()
            df['MA20'] = df['收盘'].rolling(window=20).mean()
            
            if all(col in df.columns for col in ['MA5', 'MA10', 'MA20']):
                test_result.add_result(test_name, "PASS", "成功计算技术指标", response_time)
                print(f"  ✓ 成功计算技术指标")
            else:
                test_result.add_result(test_name, "FAIL", "技术指标计算失败", response_time)
                print(f"  ✗ 技术指标计算失败")
        else:
            test_result.add_result(test_name, "FAIL", "未获取到历史数据用于计算技术指标", response_time)
            print(f"  ✗ 未获取到历史数据用于计算技术指标")
    
    except Exception as e:
        end_time = time.time()
        response_time = end_time - start_time
        test_result.add_result(test_name, "FAIL", str(e), response_time)
        print(f"  ✗ 失败: {e}")


def test_different_time_frames():
    """测试不同时间周期数据获取"""
    test_name = "不同时间周期数据获取"
    print(f"\n测试: {test_name}")
    
    time_frames = ["daily", "weekly", "monthly"]
    
    for period in time_frames:
        try:
            start_time = time.time()
            df = ak.stock_zh_a_hist(symbol=TEST_STOCK_CODE, period=period, start_date=START_DATE, end_date=TODAY, adjust="qfq")
            end_time = time.time()
            response_time = end_time - start_time
            
            if not df.empty:
                test_result.add_result(f"{test_name}_{period}", "PASS", f"获取到 {len(df)} 条记录", response_time)
                print(f"  ✓ {period} 周期: 成功获取到 {len(df)} 条记录")
            else:
                test_result.add_result(f"{test_name}_{period}", "FAIL", "未获取到数据", response_time)
                print(f"  ✗ {period} 周期: 未获取到数据")
        
        except Exception as e:
            end_time = time.time()
            response_time = end_time - start_time
            test_result.add_result(f"{test_name}_{period}", "FAIL", str(e), response_time)
            print(f"  ✗ {period} 周期: 失败 - {e}")


def run_all_tests():
    """运行所有测试"""
    print("=" * 80)
    print("开始全面测试 AKShare 库")
    print("=" * 80)
    
    # 运行所有测试用例
    test_stock_basic_info()
    test_stock_historical_data()
    test_stock_realtime_quote()
    test_index_data()
    test_fund_data()
    test_future_data()
    test_financial_indicators()
    test_news_data()
    test_industry_data()
    test_stock_company_info()
    test_stock_tech_indicators()
    test_different_time_frames()
    
    # 生成测试报告
    report = test_result.generate_report()
    print(report)
    
    # 保存测试报告到文件
    report_file = f"akshare_test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    with open(report_file, "w", encoding="utf-8") as f:
        f.write(report)
    
    print(f"测试报告已保存到: {report_file}")


if __name__ == "__main__":
    run_all_tests()
