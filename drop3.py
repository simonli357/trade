import yfinance as yf
import pandas as pd
import os
import matplotlib.pyplot as plt

# Parameters
ticker = "^IXIC"
year = "2016"
start_date = year + "-01-01"
end_date = year + "-12-31"
threshold = -2  # Threshold for drops in percentage (negative for drops)

# Determine threshold direction
if threshold < 0:
    name1 = "drops"
    name2 = "fell"
else:
    name1 = "increases"
    name2 = "rose"

# Download data
data = yf.download(ticker, start=start_date, end=end_date)

# Calculate daily percentage changes
data['Daily Change (%)'] = data['Adj Close'].pct_change() * 100

# Filter days exceeding the threshold
if threshold < 0:
    extreme_days = data[data['Daily Change (%)'] <= threshold]
else:
    extreme_days = data[data['Daily Change (%)'] >= threshold]
extreme_days = extreme_days[['Daily Change (%)']]

# Generate summary statistics
average_change = data['Daily Change (%)'].mean()
max_change = data['Daily Change (%)'].max()
min_change = data['Daily Change (%)'].min()
std_dev_change = data['Daily Change (%)'].std()

# Print summary
print(f"Summary for NASDAQ in {start_date[:4]}:")
print(f"Average Daily Change: {average_change:.2f}%")
print(f"Max Daily Change: {max_change:.2f}%")
print(f"Min Daily Change: {min_change:.2f}%")
print(f"Standard Deviation: {std_dev_change:.2f}%\n")

# Print extreme days
print(f"Days in {start_date[:4]} where NASDAQ {name2} more than {abs(threshold)}%:")
print(extreme_days)
print(f"Number of such days: {len(extreme_days)}")

# Save results
output_dir = "nasdaq_drop"
os.makedirs(output_dir, exist_ok=True)
output_file = f"{output_dir}/nasdaq_{name1}_beyond_{abs(threshold)}pct_{start_date[:4]}.csv"
extreme_days.to_csv(output_file, index=True)
print(f"Results saved to {output_file}")

# Plot data
plt.figure(figsize=(12, 6))
plt.plot(data['Adj Close'], label='Adjusted Close Price')
plt.title(f"NASDAQ Performance in {start_date[:4]}")
plt.xlabel('Date')
plt.ylabel('Price')
plt.legend()
plt.grid()
plt.savefig(f"{output_dir}/nasdaq_performance_{start_date[:4]}.png")
plt.show()

plt.figure(figsize=(12, 6))
plt.hist(data['Daily Change (%)'].dropna(), bins=50, alpha=0.75)
plt.axvline(threshold, color='r', linestyle='--', label=f'Threshold: {threshold}%')
plt.title(f"Distribution of Daily Percentage Changes in {start_date[:4]}")
plt.xlabel('Daily Change (%)')
plt.ylabel('Frequency')
plt.legend()
plt.grid()
plt.savefig(f"{output_dir}/nasdaq_daily_change_distribution_{start_date[:4]}.png")
plt.show()
