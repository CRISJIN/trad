import pysnowball as ball
import json

# 首先需要设置雪球token
# 获取token的方法：
# 1. 打开浏览器访问 https://xueqiu.com
# 2. 登录雪球账号
# 3. 按F12打开开发者工具，选择Network标签
# 4. 刷新页面，找到任意一个请求，在Headers标签中找到Cookie
# 5. 复制Cookie中的xq_a_token和u参数，格式如："xq_a_token=xxx;u=xxx"

# 使用用户提供的完整token信息
token = "xq_a_token=f6593a4fd56abaac3b5ccf53d71060eb1c6ddc2d;u=251754325966805"

# 设置token
try:
    ball.set_token(token)
    print("Token设置成功")
    
    # 测试获取股票实时行情
    print("\n1. 获取股票实时行情 (SH601127 赛力斯)")
    quote = ball.quotec('SH601127')
    print(f"状态码: {quote.get('error_code', '未知')}")
    if quote.get('error_code') == 0:
        data = quote.get('data', [])[0]
        print(f"股票代码: {data.get('symbol')}")
        print(f"股票名称: {data.get('name')}")
        print(f"当前价格: {data.get('current')}")
        print(f"涨跌幅: {data.get('percent')}%")
    
    # 测试获取股票详细行情
    print("\n2. 获取股票详细行情 (SH601127 赛力斯)")
    quote_detail = ball.quote_detail('SH601127')
    print(f"状态码: {quote_detail.get('error_code', '未知')}")
    if quote_detail.get('error_code') == 0:
        data = quote_detail.get('data', {})
        quote_info = data.get('quote', {})
        print(f"股票代码: {quote_info.get('symbol')}")
        print(f"股票名称: {quote_info.get('name')}")
        print(f"当前价格: {quote_info.get('current')}")
        print(f"市盈率(TTM): {quote_info.get('pe_ttm')}")
        print(f"市净率: {quote_info.get('pb')}")
        print(f"总市值: {quote_info.get('market_capital')}")
    
    # 测试获取公司基本信息
    print("\n3. 获取公司基本信息 (SH601127 赛力斯)")
    company_info = ball.stock_basic_info('SH601127')
    print(f"状态码: {company_info.get('error_code', '未知')}")
    if company_info.get('error_code') == 0:
        data = company_info.get('data', {})
        print(json.dumps(data, ensure_ascii=False, indent=2))
        # 检查是否有地区信息
        if 'province' in data or 'city' in data:
            print(f"地区信息: {data.get('province', '')} {data.get('city', '')}")
    
    # 测试获取财务数据
    print("\n4. 获取公司财务数据 - 资产负债表 (SH601127 赛力斯)")
    balance_sheet = ball.balance('SH601127')
    print(f"状态码: {balance_sheet.get('error_code', '未知')}")
    if balance_sheet.get('error_code') == 0:
        data = balance_sheet.get('data', {})
        print(f"财务数据年度列表: {list(data.keys())}")
        # 显示最新年度的部分数据
        latest_year = list(data.keys())[0] if data else None
        if latest_year:
            latest_data = data[latest_year]
            print(f"最新年度({latest_year})部分数据:")
            print(f"总资产: {latest_data.get('total_assets')}")
            print(f"总负债: {latest_data.get('total_liability')}")
            print(f"股东权益: {latest_data.get('total_owner_equities')}")
            
    print("\n使用提示：")
    print("1. 如果获取不到数据，请检查token是否正确")
    print("2. token可能会过期，需要定期更新")
    print("3. 更多API文档请参考: https://github.com/uname-yang/pysnowball")
    
except Exception as e:
    print(f"错误: {type(e).__name__}: {str(e)}")
    print("\n请检查token是否正确设置，获取token的方法：")
    print("1. 打开浏览器访问 https://xueqiu.com")
    print("2. 登录雪球账号")
    print("3. 按F12打开开发者工具，选择Network标签")
    print("4. 刷新页面，找到任意一个请求，在Headers标签中找到Cookie")
    print("5. 复制Cookie中的xq_a_token和u参数，格式如：\"xq_a_token=xxx;u=xxx\"")
