import yfinance as yf
import matplotlib.pyplot as plt
import pandas as pd
import os

def calculate_percentage_changes(data):
    """Calculate day and aftermarket percentage changes."""
    # Regular hours: 9:30 AM to 4:00 PM
    regular_hours = data.between_time("09:30", "16:00")

    # Calculate day percentage change
    if not regular_hours.empty:
        day_open_price = regular_hours.iloc[0]['Open']
        day_close_price = regular_hours.iloc[-1]['Close']
        day_change_percent = ((day_close_price - day_open_price) / day_open_price) * 100
    else:
        day_change_percent = None

    # Calculate aftermarket percentage change
    if not regular_hours.empty:
        regular_close_price = regular_hours.iloc[-1]['Close']
        overall_close_price = data['Close'].iloc[-1]
        aftermarket_change_percent = ((overall_close_price - regular_close_price) / regular_close_price) * 100
    else:
        aftermarket_change_percent = None

    return day_change_percent, aftermarket_change_percent

def fetch_and_plot_data(start_date, end_date, tickers):
    os.makedirs("plots", exist_ok=True)

    stock_data = {}
    for ticker in tickers:
        # Fetch stock data with extended hours
        stock_data[ticker] = yf.download(ticker, start=start_date, end=end_date, interval="1h", prepost=True)

    for ticker, data in stock_data.items():
        if not data.empty:
            # Convert index to EST
            # data.index = data.index.tz_localize("UTC").tz_convert("US/Eastern")
            data.index = data.index.tz_convert("US/Eastern")

            # print(data)

            # Calculate percentage changes over time
            day_changes = []
            aftermarket_changes = []
            dates = []

            for date, group in data.groupby(data.index.date):
                day_change, aftermarket_change = calculate_percentage_changes(group)
                if day_change is not None and aftermarket_change is not None:
                    day_changes.append(day_change)
                    aftermarket_changes.append(aftermarket_change)
                    dates.append(date)
            
            # Plotting
            plt.figure(figsize=(12, 6))
            plt.plot(dates, day_changes, label='Day % Change', color='blue')
            plt.plot(dates, aftermarket_changes, label='Aftermarket % Change', color='orange')
            plt.title(f'Percentage Changes for {ticker}')
            plt.xlabel('Date')
            plt.ylabel('% Change')
            plt.legend()
            plt.grid()

            # Save the plot
            plt.savefig(f"plots/{ticker}_percentage_changes_{start_date}_to_{end_date}.png")
            plt.close()
        else:
            print(f"No data found for ticker {ticker}")

start_date = input("Enter the starting date (YYYY-MM-DD): ")
if not start_date:
    start_date = "2024-12-01"

end_date = input("Enter the ending date (YYYY-MM-DD): ")
if not end_date:
    end_date = "2024-12-31"

tickers = input("Enter the stock symbols separated by commas (ex: GOOGL,TSLA): ").strip()
if not tickers:
    tickers = ["SOUN", "SOUNW", "NVDA", "PLTR", "AI", "GOOGL", "TSLA"]
else:
    tickers = [symbol.strip() for symbol in tickers.split(",")]

# Fetch and plot the data
fetch_and_plot_data(start_date, end_date, tickers)
