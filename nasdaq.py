import yfinance as yf
import pandas as pd

# Define the ticker symbol for NASDAQ Composite Index
ticker = '^IXIC'

# Define the start and end dates for January and February 2025
start_date = '2025-01-01'
end_date = '2025-02-28'

# Fetch the historical data (disable auto-adjustment to get "Adj Close")
data = yf.download(ticker, start=start_date, end=end_date, auto_adjust=False)

# Check column names
if 'Adj Close' in data.columns:
    data['Daily % Change'] = data['Adj Close'].pct_change() * 100
else:
    print("Warning: 'Adj Close' column is missing. Using 'Close' instead.")
    data['Daily % Change'] = data['Close'].pct_change() * 100  # Fallback to 'Close'

# Drop NaN values (first row will have NaN)
data = data.dropna()

# Categorize percentage change
def categorize_change(change):
    if -0.5 <= change <= 0.5:
        return 'Neutral'
    elif change < -1.2:
        return 'big Dip'
    elif change > 1.2:
        return 'big Up'
    elif change < -0.5:
        return 'Dip'
    else:
        return 'Up'

# Apply the categorization function
data['Category'] = data['Daily % Change'].apply(categorize_change)

# Display the result
result = data[['Close', 'Daily % Change', 'Category']]
print(result)
