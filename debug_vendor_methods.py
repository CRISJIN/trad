from tradingagents.dataflows.interface import VENDOR_METHODS, VENDOR_LIST

print("=== Debugging Vendor Methods ===")
print(f"VENDOR_LIST: {VENDOR_LIST}")
print(f"\nVENDOR_METHODS keys: {list(VENDOR_METHODS.keys())}")

# Check get_fundamentals vendors
print(f"\nget_fundamentals vendors: {list(VENDOR_METHODS['get_fundamentals'].keys())}")

# Check get_news vendors
print(f"get_news vendors: {list(VENDOR_METHODS['get_news'].keys())}")

# Check get_global_news vendors
print(f"get_global_news vendors: {list(VENDOR_METHODS['get_global_news'].keys())}")
