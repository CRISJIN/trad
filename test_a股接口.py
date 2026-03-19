import os
import time
import sys
from tradingagents.dataflows.interface import route_to_vendor
from tradingagents.dataflows.china_stock import (
    get_china_stock_data,
    get_china_stock_fundamentals,
    get_china_stock_news,
    get_china_stock_indicators,
    check_price_limit,
    check_t1_trading
)

# Test configuration
test_ticker = "601919.SH"  # 中远海控
test_invalid_ticker = "999999.SH"  # 无效股票代码
test_start_date = "2024-10-01"
test_end_date = "2024-11-01"
test_date = "2024-11-01"

print("=== Testing China A-share API Interface ===")

# Helper function to test API with timing
def test_api(func, *args, **kwargs):
    """测试API函数，记录请求参数、响应数据、状态码、错误信息和响应时间"""
    print(f"\n--- Testing {func.__name__} ---")
    print(f"Request parameters: args={args}, kwargs={kwargs}")
    
    # Record start time
    start_time = time.time()
    
    try:
        # Call the function
        result = func(*args, **kwargs)
        
        # Record end time
        end_time = time.time()
        response_time = end_time - start_time
        
        # Print results
        print(f"Status: SUCCESS")
        print(f"Response time: {response_time:.4f} seconds")
        print(f"Response data type: {type(result).__name__}")
        
        # Print response data (truncated if too long)
        if isinstance(result, str):
            if len(result) > 500:
                print(f"Response data (truncated): {result[:500]}...")
            else:
                print(f"Response data: {result}")
        else:
            print(f"Response data: {result}")
        
        return {
            "status": "success",
            "function": func.__name__,
            "args": args,
            "kwargs": kwargs,
            "response_time": response_time,
            "response_data": result,
            "error": None
        }
    except Exception as e:
        # Record end time
        end_time = time.time()
        response_time = end_time - start_time
        
        # Print error
        print(f"Status: ERROR")
        print(f"Response time: {response_time:.4f} seconds")
        print(f"Error: {type(e).__name__}: {str(e)}")
        
        return {
            "status": "error",
            "function": func.__name__,
            "args": args,
            "kwargs": kwargs,
            "response_time": response_time,
            "response_data": None,
            "error": str(e)
        }

# Test 1: Test get_stock_data with valid ticker using route_to_vendor
def test_get_stock_data_valid():
    return test_api(
        route_to_vendor,
        "get_stock_data",
        test_ticker,
        test_start_date,
        test_end_date
    )

# Test 2: Test get_stock_data with invalid ticker using route_to_vendor
def test_get_stock_data_invalid():
    return test_api(
        route_to_vendor,
        "get_stock_data",
        test_invalid_ticker,
        test_start_date,
        test_end_date
    )

# Test 3: Test get_fundamentals with valid ticker using route_to_vendor
def test_get_fundamentals_valid():
    return test_api(
        route_to_vendor,
        "get_fundamentals",
        test_ticker,
        test_date
    )

# Test 4: Test get_news with valid ticker using route_to_vendor
def test_get_news_valid():
    return test_api(
        route_to_vendor,
        "get_news",
        test_ticker,
        test_start_date,
        test_end_date
    )

# Test 5: Test get_indicators with valid ticker using route_to_vendor
def test_get_indicators_valid():
    return test_api(
        route_to_vendor,
        "get_indicators",
        test_ticker,
        "macd",
        test_start_date,
        30
    )

# Test 6: Test direct call to get_china_stock_data with valid ticker
def test_direct_get_china_stock_data_valid():
    return test_api(
        get_china_stock_data,
        test_ticker,
        test_start_date,
        test_end_date
    )

# Test 7: Test direct call to get_china_stock_fundamentals with valid ticker
def test_direct_get_china_stock_fundamentals_valid():
    return test_api(
        get_china_stock_fundamentals,
        test_ticker,
        test_date
    )

# Test 8: Test direct call to get_china_stock_news with valid ticker
def test_direct_get_china_stock_news_valid():
    return test_api(
        get_china_stock_news,
        test_ticker,
        test_start_date,
        test_end_date
    )

# Test 9: Test direct call to get_china_stock_indicators with valid ticker
def test_direct_get_china_stock_indicators_valid():
    return test_api(
        get_china_stock_indicators,
        test_ticker,
        test_start_date,
        "macd",
        30
    )

# Test 10: Test price limit check
def test_check_price_limit():
    return test_api(
        check_price_limit,
        test_ticker,
        12.5,
        11.8
    )

# Test 11: Test T+1 trading check
def test_check_t1_trading():
    return test_api(
        check_t1_trading,
        test_ticker,
        "2024-11-01",
        "2024-11-02"
    )

# Run all tests
def run_all_tests():
    results = []
    
    print("\n=== Test 1: Valid stock data request ===")
    results.append(test_get_stock_data_valid())
    
    print("\n=== Test 2: Invalid stock data request ===")
    results.append(test_get_stock_data_invalid())
    
    print("\n=== Test 3: Valid fundamentals request ===")
    results.append(test_get_fundamentals_valid())
    
    print("\n=== Test 4: Valid news request ===")
    results.append(test_get_news_valid())
    
    print("\n=== Test 5: Valid indicators request ===")
    results.append(test_get_indicators_valid())
    
    print("\n=== Test 6: Direct call to get_china_stock_data ===")
    results.append(test_direct_get_china_stock_data_valid())
    
    print("\n=== Test 7: Direct call to get_china_stock_fundamentals ===")
    results.append(test_direct_get_china_stock_fundamentals_valid())
    
    print("\n=== Test 8: Direct call to get_china_stock_news ===")
    results.append(test_direct_get_china_stock_news_valid())
    
    print("\n=== Test 9: Direct call to get_china_stock_indicators ===")
    results.append(test_direct_get_china_stock_indicators_valid())
    
    print("\n=== Test 10: Check price limit ===")
    results.append(test_check_price_limit())
    
    print("\n=== Test 11: Check T+1 trading ===")
    results.append(test_check_t1_trading())
    
    # Print summary
    print("\n=== Test Summary ===")
    print(f"Total tests: {len(results)}")
    
    success_count = sum(1 for r in results if r["status"] == "success")
    error_count = sum(1 for r in results if r["status"] == "error")
    
    print(f"Success: {success_count}")
    print(f"Error: {error_count}")
    
    # Print average response time
    response_times = [r["response_time"] for r in results]
    avg_response_time = sum(response_times) / len(response_times)
    print(f"Average response time: {avg_response_time:.4f} seconds")
    
    # Print detailed results
    print("\n=== Detailed Results ===")
    for i, result in enumerate(results):
        print(f"\nTest {i+1}: {result['function']}")
        print(f"Status: {result['status'].upper()}")
        print(f"Response time: {result['response_time']:.4f} seconds")
        if result['error']:
            print(f"Error: {result['error']}")
        else:
            print(f"Response data type: {type(result['response_data']).__name__}")

if __name__ == "__main__":
    run_all_tests()
