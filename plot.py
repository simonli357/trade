import yfinance as yf
import matplotlib.pyplot as plt
import pandas as pd
import os

def fetch_and_plot_data(start_date, end_date, tickers):
    os.makedirs("plots", exist_ok=True)

    stock_data = {}
    for ticker in tickers:
        stock_data[ticker] = yf.download(ticker, start=start_date, end=end_date)

    for ticker, data in stock_data.items():
        if not data.empty:
            plt.figure(figsize=(10, 5))
            plt.plot(data.index, data['Close'], label=ticker)
            plt.title(f'Stock Price for {ticker}')
            plt.xlabel('Date')
            plt.ylabel('Closing Price (USD)')
            plt.legend()
            plt.grid()
            plt.savefig(f"plots/{ticker}_stock_price_{start_date}_to_{end_date}.png")
            plt.close()
        else:
            print(f"No data found for ticker {ticker}")

start_date = input("Enter the starting date (YYYY-MM-DD): ")
end_date = input("Enter the ending date (YYYY-MM-DD): ")
tickers = input("Enter the stock symbols separated by commas (ex: GOOGL,TSLA): ").strip()
if not tickers:
    tickers = ["SOUN", "SOUNW", "NVDA", "PLTR", "AI", "GOOGL", "TSLA"]
else:
    tickers = [symbol.strip() for symbol in tickers.split(",")]

# Fetch and plot the data
fetch_and_plot_data(start_date, end_date, tickers)
