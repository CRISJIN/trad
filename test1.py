import akshare as ak
df = ak.stock_zh_a_hist(symbol="600519", period="daily", 
                        start_date="20251101", end_date="20251201", adjust="qfq")
print(df.head())
