import os
import sys
import requests
import json

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 导入配置文件
try:
    from tradingagents.default_config import DEFAULT_CONFIG
    print("成功导入配置文件")
except ImportError as e:
    print(f"导入配置文件失败: {e}")
    sys.exit(1)

# 检查是否有Alpha Vantage API密钥
api_keys = DEFAULT_CONFIG.get('api_keys', {})
alpha_vantage_key = api_keys.get('alpha_vantage')

if not alpha_vantage_key:
    print("错误: 未在配置文件中找到Alpha Vantage API密钥")
    sys.exit(1)

print(f"找到Alpha Vantage API密钥: {alpha_vantage_key}")

# 测试Alpha Vantage API连接
def test_alpha_vantage_connection():
    print("\n开始测试Alpha Vantage API连接...")
    
    # 使用简单的API端点来测试连接
    # 这里使用GLOBAL_QUOTE端点获取苹果股票的基本信息
    symbol = "AAPL"
    url = f"https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={symbol}&apikey={alpha_vantage_key}"
    
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()  # 检查HTTP错误
        
        data = response.json()
        
        # 检查API返回的数据
        if 'Error Message' in data:
            print(f"API错误: {data['Error Message']}")
            return False
        elif 'Information' in data:
            print(f"API信息: {data['Information']}")
            # 即使有信息消息（如限制提醒），我们也继续验证
        
        print(f"API响应状态码: {response.status_code}")
        print("API响应数据:")
        print(json.dumps(data, indent=2))
        
        # 检查是否返回了有效数据
        if 'Global Quote' in data and data['Global Quote']:
            print("\n✅ Alpha Vantage API连接成功!")
            return True
        else:
            print("\n⚠️  API连接成功，但未返回预期的数据结构")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"\n❌ 网络请求失败: {e}")
        return False
    except json.JSONDecodeError:
        print("\n❌ 无法解析API响应为JSON格式")
        print(f"响应内容: {response.text}")
        return False

if __name__ == "__main__":
    print("Alpha Vantage API测试脚本")
    print("=" * 50)
    
    # 打印配置信息
    print("\n配置信息:")
    print(f"- Alpha Vantage API密钥: {alpha_vantage_key}")
    print(f"- 数据供应商配置:")
    for key, value in DEFAULT_CONFIG.get('data_vendors', {}).items():
        print(f"  * {key}: {value}")
    
    # 测试API连接
    success = test_alpha_vantage_connection()
    
    # 输出测试结果摘要
    print("\n" + "=" * 50)
    if success:
        print("测试结果: 成功 ✅")
        print("API密钥有效，系统可以正常使用Alpha Vantage服务")
    else:
        print("测试结果: 失败 ❌")
        print("请检查API密钥是否正确，以及网络连接是否正常")
    print("=" * 50)
