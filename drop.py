import yfinance as yf
import pandas as pd

ticker = "^IXIC"

data = yf.download(ticker, period="2y")

data['Daily Change (%)'] = data['Adj Close'].pct_change() * 100

largest_drops = data.sort_values('Daily Change (%)').head(30)

largest_drops = largest_drops[['Daily Change (%)']]

print("Top days where NASDAQ fell the most in the last 3 years:")
print(largest_drops)

# Save results to a CSV (optional)
largest_drops.to_csv("nasdaq_largest_drops.csv", index=True)

largest_increases = data.sort_values('Daily Change (%)', ascending=False).head(30)
largest_increases = largest_increases[['Daily Change (%)']]
print("Top days where NASDAQ rose the most in the last 3 years:")
print(largest_increases)
