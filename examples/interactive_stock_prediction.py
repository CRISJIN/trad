#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
交互式股票预测程序
结合Akshare数据下载和Kronos模型进行股票预测
"""

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import akshare as ak
import os
import sys
from datetime import datetime, timedelta
import warnings
import holidays
warnings.filterwarnings('ignore')

# 添加项目根目录到路径
import os
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

from model import Kronos, KronosTokenizer, KronosPredictor

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'Arial Unicode MS', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

class InteractiveStockPredictor:
    """交互式股票预测器"""
    
    def __init__(self):
        """初始化预测器"""
        self.predictor = None
        self.model = None
        self.tokenizer = None
        self.device = "cuda:0" if self._check_cuda() else "cpu"
        print(f"使用设备: {self.device}")
        
        # 初始化中国节假日
        self.cn_holidays = holidays.China()
        
    def _check_cuda(self):
        """检查CUDA是否可用"""
        try:
            import torch
            return torch.cuda.is_available()
        except ImportError:
            return False
    
    def is_trading_day(self, date):
        """判断是否为交易日（排除周末和节假日）"""
        # 排除周末
        if date.weekday() >= 5:  # 5=周六, 6=周日
            return False
        # 排除节假日
        if date in self.cn_holidays:
            return False
        return True
    
    def generate_trading_days(self, start_date, num_days):
        """生成指定数量的交易日"""
        trading_days = []
        current_date = start_date
        
        while len(trading_days) < num_days:
            if self.is_trading_day(current_date):
                trading_days.append(current_date)
            current_date += timedelta(days=1)
        
        return trading_days
    
    def load_models(self):
        """加载Kronos模型和分词器"""
        try:
            print("正在加载Kronos模型...")
            self.tokenizer = KronosTokenizer.from_pretrained("NeoQuasar/Kronos-Tokenizer-base")
            self.model = Kronos.from_pretrained("NeoQuasar/Kronos-base")
            self.predictor = KronosPredictor(
                model=self.model, 
                tokenizer=self.tokenizer, 
                device=self.device, 
                max_context=512
            )
            print("✅ 模型加载成功!")
            return True
        except Exception as e:
            print(f"❌ 模型加载失败: {str(e)}")
            return False
    
    def get_stock_codes(self):
        """获取股票代码列表"""
        print("\n" + "="*60)
        print("股票代码输入方式")
        print("="*60)
        print("1. 手动输入股票代码")
        print("2. 从TXT文件读取股票代码列表")
        print()
        
        while True:
            choice = input("请选择输入方式 (1/2): ").strip()
            
            if choice == '1':
                return self._get_manual_codes()
            elif choice == '2':
                return self._get_codes_from_file()
            else:
                print("❌ 请输入 1 或 2")
    
    def _get_manual_codes(self):
        """手动输入股票代码"""
        print("\n手动输入股票代码")
        print("-" * 30)
        print("格式说明:")
        print("- 多个股票代码用逗号分隔")
        print("- 支持A股代码格式: 600030, 002261, 688326, 300364")
        print("- 示例: 600030,002261")
        print()
        
        while True:
            stock_input = input("请输入股票代码: ").strip()
            if not stock_input:
                print("❌ 请输入有效的股票代码")
                continue
            
            # 解析股票代码
            stock_codes = [code.strip() for code in stock_input.split(',')]
            stock_codes = [code for code in stock_codes if code]
            
            if not stock_codes:
                print("❌ 请输入有效的股票代码")
                continue
            
            # 验证股票代码格式
            valid_codes = []
            for code in stock_codes:
                if code.isdigit() and len(code) == 6:
                    valid_codes.append(code)
                else:
                    print(f"⚠️  股票代码 {code} 格式不正确，已跳过")
            
            if not valid_codes:
                print("❌ 没有有效的股票代码")
                continue
            
            return valid_codes
    
    def _get_codes_from_file(self):
        """从TXT文件读取股票代码"""
        print("\n从TXT文件读取股票代码")
        print("-" * 30)
        print("文件格式说明:")
        print("- 每行一个股票代码")
        print("- 支持注释行（以#开头）")
        print("- 示例文件内容:")
        print("  # 这是注释行")
        print("  600030")
        print("  002261")
        print()
        
        while True:
            filename = input("请输入TXT文件名 (例如: stock_codes.txt): ").strip()
            if not filename:
                print("❌ 请输入文件名")
                continue
            
            # 如果用户没有输入扩展名，自动添加.txt
            if not filename.endswith('.txt'):
                filename += '.txt'
            
            try:
                with open(filename, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                
                stock_codes = []
                for line in lines:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        stock_codes.append(line)
                
                if not stock_codes:
                    print("❌ 文件中没有有效的股票代码")
                    continue
                
                # 验证股票代码格式
                valid_codes = []
                for code in stock_codes:
                    if code.isdigit() and len(code) == 6:
                        valid_codes.append(code)
                    else:
                        print(f"⚠️  股票代码 {code} 格式不正确，已跳过")
                
                if not valid_codes:
                    print("❌ 文件中没有有效的股票代码")
                    continue
                
                return valid_codes
                
            except FileNotFoundError:
                print(f"❌ 文件 {filename} 不存在")
                continue
            except Exception as e:
                print(f"❌ 读取文件失败: {e}")
                continue
    
    def download_stock_data(self, stock_code, days=100, max_retries=5):
        """下载股票数据"""
        import time
        import requests
        from requests.adapters import HTTPAdapter
        from urllib3.util.retry import Retry
        
        # 配置重试策略
        session = requests.Session()
        retry_strategy = Retry(
            total=2,
            backoff_factor=2,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "OPTIONS"]
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        
        for attempt in range(max_retries):
            try:
                if attempt > 0:
                    print(f"正在重试下载股票 {stock_code} 的数据... (第 {attempt + 1} 次)")
                    # 递增等待时间，并添加随机抖动
                    import random
                    wait_time = 8 * attempt + random.uniform(1, 3)
                    print(f"⏳ 等待 {wait_time:.1f} 秒后重试...")
                    time.sleep(wait_time)
                else:
                    print(f"正在下载股票 {stock_code} 的数据...")
                
                # 计算日期范围（最近100个交易日）
                end_date = datetime.now()
                start_date = end_date - timedelta(days=days*2)  # 多取一些天数确保有足够的交易日
                
                print(f"   请求日期范围: {start_date.strftime('%Y-%m-%d')} 至 {end_date.strftime('%Y-%m-%d')}")
                
                # 添加请求前的短暂延迟，避免请求过于频繁
                if attempt > 0:
                    time.sleep(2)
                
                # 使用akshare下载数据
                data = ak.stock_zh_a_hist(
                    symbol=stock_code,
                    period="daily",
                    start_date=start_date.strftime('%Y%m%d'),
                    end_date=end_date.strftime('%Y%m%d'),
                    adjust="qfq"  # 前复权
                )
                
                if data.empty:
                    print(f"❌ 股票 {stock_code}: 未找到数据")
                    return None
                
                # 重命名列以匹配Kronos格式
                data = data.rename(columns={
                    '日期': 'timestamps',
                    '开盘': 'open',
                    '收盘': 'close',
                    '最高': 'high',
                    '最低': 'low',
                    '成交量': 'volume',
                    '成交额': 'amount'
                })
                
                # 设置日期为索引
                data['timestamps'] = pd.to_datetime(data['timestamps'])
                data = data.set_index('timestamps')
                
                # 只取最近100个交易日
                if len(data) > days:
                    data = data.tail(days)
                
                print(f"✅ 股票 {stock_code}: 成功下载 {len(data)} 条记录")
                print(f"   数据范围: {data.index[0].strftime('%Y-%m-%d')} 至 {data.index[-1].strftime('%Y-%m-%d')}")
                
                return data
                
            except Exception as e:
                error_msg = str(e)
                print(f"❌ 股票 {stock_code}: 下载失败 (第 {attempt + 1} 次) - {error_msg}")
                
                # 分析错误类型
                if "Connection reset by peer" in error_msg:
                    print("   🔍 分析: 连接被服务器重置，可能是请求过于频繁")
                elif "timeout" in error_msg.lower():
                    print("   🔍 分析: 请求超时，网络可能较慢")
                elif "Connection aborted" in error_msg:
                    print("   🔍 分析: 连接被中断，可能是网络不稳定")
                
                if attempt == max_retries - 1:
                    print(f"❌ 股票 {stock_code}: 经过 {max_retries} 次尝试后仍然失败")
                    print("💡 建议:")
                    print("   1. 检查网络连接是否稳定")
                    print("   2. 稍后重试（服务器可能负载较高）")
                    print("   3. 确认股票代码是否正确")
                    print("   4. 尝试使用其他网络环境")
                    return None
                else:
                    # 更长的等待时间
                    wait_time = 8 * (attempt + 1)
                    print(f"⏳ 等待 {wait_time} 秒后重试...")
                    time.sleep(wait_time)
        
        return None
    
    def prepare_prediction_data(self, data, lookback_days=100, pred_days=30):
        """准备预测数据"""
        try:
            # 确保数据长度足够
            if len(data) < lookback_days:
                print(f"⚠️  数据长度不足，需要 {lookback_days} 天，实际只有 {len(data)} 天")
                lookback_days = len(data)
            
            # 准备历史数据
            x_df = data.tail(lookback_days)[['open', 'high', 'low', 'close', 'volume', 'amount']].copy()
            x_timestamp = data.tail(lookback_days).index
            
            # 生成未来预测时间戳（交易日，排除周末和节假日）
            last_date = x_timestamp[-1]
            future_trading_days = self.generate_trading_days(last_date + timedelta(days=1), pred_days)
            
            y_timestamp = pd.Series(future_trading_days)
            
            # 确保时间戳是Series格式
            x_timestamp = pd.Series(x_timestamp)
            
            print(f"📅 预测期间: {future_trading_days[0].strftime('%Y-%m-%d')} 至 {future_trading_days[-1].strftime('%Y-%m-%d')}")
            print(f"📅 预测天数: {len(future_trading_days)} 个交易日")
            
            return x_df, x_timestamp, y_timestamp
            
        except Exception as e:
            print(f"❌ 数据准备失败: {str(e)}")
            return None, None, None
    
    def make_prediction(self, x_df, x_timestamp, y_timestamp, pred_len=30):
        """进行预测"""
        try:
            print("正在进行预测...")
            
            pred_df = self.predictor.predict(
                df=x_df,
                x_timestamp=x_timestamp,
                y_timestamp=y_timestamp,
                pred_len=pred_len,
                T=1.0,
                top_p=0.9,
                sample_count=1,
                verbose=True
            )
            
            print("✅ 预测完成!")
            return pred_df
            
        except Exception as e:
            print(f"❌ 预测失败: {str(e)}")
            return None
    
    def plot_prediction(self, stock_code, historical_data, pred_data, x_timestamp, y_timestamp):
        """绘制预测结果"""
        try:
            fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(16, 10), sharex=True)
            
            # 创建连续的时间轴索引
            x_indices = range(len(x_timestamp))
            y_indices = range(len(x_timestamp), len(x_timestamp) + len(y_timestamp))
            
            # 绘制价格图
            ax1.plot(x_indices, historical_data['close'], label='历史价格', color='blue', linewidth=2)
            ax1.plot(y_indices, pred_data['close'], label='预测价格', color='red', linewidth=2, linestyle='--')
            ax1.set_ylabel('收盘价 (元)', fontsize=12)
            ax1.set_title(f'股票 {stock_code} 价格预测 (排除节假日)', fontsize=14, fontweight='bold')
            ax1.legend(fontsize=11)
            ax1.grid(True, alpha=0.3)
            
            # 绘制成交量图
            ax2.plot(x_indices, historical_data['volume'], label='历史成交量', color='blue', linewidth=2)
            ax2.plot(y_indices, pred_data['volume'], label='预测成交量', color='red', linewidth=2, linestyle='--')
            ax2.set_ylabel('成交量', fontsize=12)
            ax2.set_xlabel('交易日', fontsize=12)
            ax2.legend(fontsize=11)
            ax2.grid(True, alpha=0.3)
            
            # 设置x轴刻度
            total_days = len(x_timestamp) + len(y_timestamp)
            step = max(1, total_days // 12)  # 显示约12个标签
            tick_positions = list(range(0, total_days, step))
            
            # 创建标签：历史数据用实际日期，预测数据用预测日期
            tick_labels = []
            for pos in tick_positions:
                if pos < len(x_timestamp):
                    # 历史数据标签
                    tick_labels.append(x_timestamp.iloc[pos].strftime('%m-%d'))
                else:
                    # 预测数据标签
                    pred_pos = pos - len(x_timestamp)
                    if pred_pos < len(y_timestamp):
                        tick_labels.append(y_timestamp.iloc[pred_pos].strftime('%m-%d'))
                    else:
                        tick_labels.append('')
            
            ax2.set_xticks(tick_positions)
            ax2.set_xticklabels(tick_labels, rotation=45, ha='right')
            
            # 添加分隔线区分历史和预测数据
            split_point = len(x_timestamp) - 0.5
            ax1.axvline(x=split_point, color='gray', linestyle=':', alpha=0.7, linewidth=2)
            ax2.axvline(x=split_point, color='gray', linestyle=':', alpha=0.7, linewidth=2)
            
            # 添加文本标注
            ax1.text(0.02, 0.98, f'历史数据: {len(x_timestamp)} 个交易日', 
                    transform=ax1.transAxes, verticalalignment='top',
                    bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.8))
            ax1.text(0.02, 0.88, f'预测数据: {len(y_timestamp)} 个交易日', 
                    transform=ax1.transAxes, verticalalignment='top',
                    bbox=dict(boxstyle='round', facecolor='lightcoral', alpha=0.8))
            
            # 添加日期范围标注
            ax1.text(0.98, 0.02, f'历史: {x_timestamp.iloc[0].strftime("%Y-%m-%d")} 至 {x_timestamp.iloc[-1].strftime("%Y-%m-%d")}', 
                    transform=ax1.transAxes, verticalalignment='bottom', horizontalalignment='right',
                    bbox=dict(boxstyle='round', facecolor='lightgray', alpha=0.8), fontsize=9)
            ax1.text(0.98, 0.12, f'预测: {y_timestamp.iloc[0].strftime("%Y-%m-%d")} 至 {y_timestamp.iloc[-1].strftime("%Y-%m-%d")}', 
                    transform=ax1.transAxes, verticalalignment='bottom', horizontalalignment='right',
                    bbox=dict(boxstyle='round', facecolor='lightgray', alpha=0.8), fontsize=9)
            
            plt.tight_layout()
            
            # 保存图片
            output_dir = "prediction_results"
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)
            
            timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{output_dir}/prediction_{stock_code}_{timestamp_str}.png"
            plt.savefig(filename, dpi=300, bbox_inches='tight')
            print(f"📊 预测图表已保存: {filename}")
            
            plt.show()
            
        except Exception as e:
            print(f"❌ 绘图失败: {str(e)}")
            import traceback
            traceback.print_exc()
    
    def save_prediction_results(self, stock_code, pred_data, y_timestamp):
        """保存预测结果"""
        try:
            output_dir = "prediction_results"
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)
            
            # 保存为CSV
            timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
            csv_filename = f"{output_dir}/prediction_{stock_code}_{timestamp_str}.csv"
            pred_data.to_csv(csv_filename, encoding='utf-8-sig')
            print(f"💾 预测结果已保存: {csv_filename}")
            
            # 保存为JSON
            json_filename = f"{output_dir}/prediction_{stock_code}_{timestamp_str}.json"
            pred_data.to_json(json_filename, orient='index', date_format='iso')
            print(f"💾 预测结果(JSON)已保存: {json_filename}")
            
        except Exception as e:
            print(f"❌ 保存结果失败: {str(e)}")
    
    def print_prediction_summary(self, stock_code, pred_data):
        """打印预测摘要"""
        print(f"\n📈 股票 {stock_code} 预测摘要")
        print("="*50)
        print(f"预测期间: {pred_data.index[0].strftime('%Y-%m-%d')} 至 {pred_data.index[-1].strftime('%Y-%m-%d')}")
        print(f"预测天数: {len(pred_data)} 个交易日")
        print()
        
        # 价格统计
        print("价格预测:")
        print(f"  起始价格: {pred_data['close'].iloc[0]:.2f}")
        print(f"  结束价格: {pred_data['close'].iloc[-1]:.2f}")
        print(f"  最高价格: {pred_data['high'].max():.2f}")
        print(f"  最低价格: {pred_data['low'].min():.2f}")
        print(f"  价格变化: {((pred_data['close'].iloc[-1] / pred_data['close'].iloc[0]) - 1) * 100:.2f}%")
        print()
        
        # 成交量统计
        print("成交量预测:")
        print(f"  平均成交量: {pred_data['volume'].mean():.0f}")
        print(f"  最大成交量: {pred_data['volume'].max():.0f}")
        print(f"  最小成交量: {pred_data['volume'].min():.0f}")
        print()
        
        # 显示前5天和后5天的预测
        print("预测详情 (前5天):")
        print(pred_data.head().round(2))
        print()
        print("预测详情 (后5天):")
        print(pred_data.tail().round(2))
    
    def run(self, test_mode=False, test_stock_codes=None):
        """运行主程序"""
        print("🚀 交互式股票预测程序")
        print("="*60)
        print("本程序使用Kronos模型预测股票未来走势")
        print("支持A股市场，预测未来30个交易日的价格和成交量")
        print()
        
        # 加载模型
        if not self.load_models():
            return
        
        # 获取股票代码
        if test_mode and test_stock_codes:
            stock_codes = test_stock_codes
            print(f"🧪 测试模式: 使用预设股票代码 {stock_codes}")
        else:
            stock_codes = self.get_stock_codes()
            if not stock_codes:
                print("❌ 未获取到有效的股票代码")
                return
        
        print(f"\n📊 将预测以下股票: {', '.join(stock_codes)}")
        
        # 对每只股票进行预测
        for i, stock_code in enumerate(stock_codes, 1):
            print(f"\n{'='*60}")
            print(f"正在处理股票 {i}/{len(stock_codes)}: {stock_code}")
            print('='*60)
            
            # 下载数据
            data = self.download_stock_data(stock_code, days=100)
            if data is None:
                continue
            
            # 准备预测数据
            x_df, x_timestamp, y_timestamp = self.prepare_prediction_data(data, lookback_days=100, pred_days=30)
            if x_df is None:
                continue
            
            # 进行预测
            pred_data = self.make_prediction(x_df, x_timestamp, y_timestamp, pred_len=30)
            if pred_data is None:
                continue
            
            # 打印预测摘要
            self.print_prediction_summary(stock_code, pred_data)
            
            # 绘制预测图
            self.plot_prediction(stock_code, x_df, pred_data, x_timestamp, y_timestamp)
            
            # 保存预测结果
            self.save_prediction_results(stock_code, pred_data, y_timestamp)
            
            print(f"✅ 股票 {stock_code} 预测完成!")
        
        print(f"\n🎉 所有股票预测完成!")
        print("预测结果已保存到 prediction_results 目录")

def main():
    """主函数"""
    predictor = InteractiveStockPredictor()
    
    # 检查是否为测试模式
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == '--test':
        # 测试模式：使用示例股票代码
        test_codes = ['600036', '000001']  # 招商银行、平安银行
        predictor.run(test_mode=True, test_stock_codes=test_codes)
    elif len(sys.argv) > 1:
        # 命令行模式：直接指定股票代码
        stock_codes = sys.argv[1:]
        # 验证股票代码格式
        valid_codes = []
        for code in stock_codes:
            if code.isdigit() and len(code) == 6:
                valid_codes.append(code)
            else:
                print(f"⚠️  股票代码 {code} 格式不正确，已跳过")
        
        if valid_codes:
            print(f"📊 将预测以下股票: {', '.join(valid_codes)}")
            predictor.run(test_mode=True, test_stock_codes=valid_codes)
        else:
            print("❌ 没有有效的股票代码")
    else:
        # 正常交互模式
        predictor.run()

if __name__ == "__main__":
    main()
