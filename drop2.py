import yfinance as yf
import pandas as pd
import os

ticker = "^IXIC"
year = "2016"
start_date = year+"-01-01"
end_date = year+"-12-31"
threshold = -2  # Threshold for drops in percentage (negative for drops)
if threshold < 0:
    name1 = "drops"
    name2 = "fell"
else:
    name1 = "increases"
    name2 = "rose"

data = yf.download(ticker, start=start_date, end=end_date)

data['Daily Change (%)'] = data['Adj Close'].pct_change() * 100

if threshold < 0:
    drops_exceeding_threshold = data[data['Daily Change (%)'] <= threshold]
else:
    drops_exceeding_threshold = data[data['Daily Change (%)'] >= threshold]
drops_exceeding_threshold = drops_exceeding_threshold[['Daily Change (%)']]

print(f"Days in {start_date[:4]} where NASDAQ {name2} more than {abs(threshold)}%:")
print(drops_exceeding_threshold)
print(f"Number of days in {start_date[:4]} where NASDAQ {name2} more than {abs(threshold)}%: {len(drops_exceeding_threshold)}")
output_dir = "nasdaq_drop"
os.makedirs(output_dir, exist_ok=True)

output_file = f"{output_dir}/nasdaq_{name1}_beyond_{abs(threshold)}pct_{start_date[:4]}.csv"
drops_exceeding_threshold.to_csv(output_file, index=True)
print(f"Results saved to {output_file}")
