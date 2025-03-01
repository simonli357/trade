import pandas as pd
import yfinance as yf

# Fetch NASDAQ historical data for 2022
ticker = "^IXIC"  # NASDAQ Composite Index
nasdaq_data = yf.download(ticker, start="2022-01-01", end="2023-01-01", auto_adjust=False)

# Calculate daily percentage change
nasdaq_data["Pct_Change"] = nasdaq_data["Adj Close"].pct_change() * 100

# Find consecutive days where % change is below -1%
count = 0
streak = 0

for change in nasdaq_data["Pct_Change"]:
    if change < 0:
        streak += 1
        if streak == 5:
            count += 1
            streak -= 1  # To allow overlapping sequences
    else:
        streak = 0  # Reset streak if condition breaks

print(f"Number of times NASDAQ dropped more than 1% for 5 consecutive days in 2022: {count}")
