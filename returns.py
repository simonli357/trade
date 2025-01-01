import pandas as pd
import datetime
import yfinance as yf
import os

pd.set_option('display.max_columns', None)  # Show all columns
pd.set_option('display.width', 1000)       # Adjust display width for better console output
pd.set_option('display.max_rows', 100)     # Show more rows if needed
pd.set_option('display.float_format', '{:.2f}'.format)  # Limit floats to 2 decimal places globally

def calculate_profit(csv_file, price_target, stock_price):
    """
    Reads a CSV file of options, calculates profit and % profit for both calls and puts.

    Args:
        csv_file (str): The path to the CSV file containing the options data.
        price_target (float): The target stock price at expiration.
        stock_price (float): The current stock price.

    Returns:
        pd.DataFrame: A DataFrame with additional columns for profit and % profit.
    """
    try:
        # Load the options data
        options_data = pd.read_csv(csv_file)
        
        # Ensure required columns exist in the CSV
        required_columns = ["strike", "bid", "ask", "Type"]
        for column in required_columns:
            if column not in options_data.columns:
                raise ValueError(f"Missing required column: {column}")

        # Calculate the mid-price of the option (average of bid and ask)
        options_data["premium"] = ((options_data["bid"] + options_data["ask"]) / 2).round(2)
        
        # Initialize profit and percent profit columns
        options_data["break_even"] = 0.0
        options_data["option_profit"] = 0.0
        options_data["option_percent_profit"] = 0.0

        # Process calls
        calls = options_data[options_data["Type"].str.lower() == "call"].copy()
        calls["break_even"] = (calls["strike"] + calls["premium"]).round(2)
        calls["option_profit"] = (
            ((price_target - calls["strike"]).clip(lower=0) * 100 - calls["premium"] * 100).round(2)
        )
        calls["option_percent_profit"] = (
            (calls["option_profit"] / (calls["premium"] * 100) * 100).round(2)
        )

        # Process puts
        puts = options_data[options_data["Type"].str.lower() == "put"].copy()
        puts["break_even"] = (puts["strike"] - puts["premium"]).round(2)
        puts["option_profit"] = (
            ((puts["strike"] - price_target).clip(lower=0) * 100 - puts["premium"] * 100).round(2)
        )
        puts["option_percent_profit"] = (
            (puts["option_profit"] / (puts["premium"] * 100) * 100).round(2)
        )

        # Combine calls and puts
        combined_data = pd.concat([calls, puts])

        # Filter relevant columns
        relevant_columns = [
            "Type", "strike", "premium", "break_even", 
            "option_profit", "option_percent_profit"
        ]
        filtered_data = combined_data[relevant_columns]

        return filtered_data

    except Exception as e:
        print(f"Error: {e}")
        return None

if __name__ == "__main__":
    csv_file = input("Enter the path to the options CSV file (e.g., options/SOUN_options_2025-07-18.csv): ")
    price_target = float(input("Enter your price target at expiration: "))

    try:
        expiration_date = csv_file.split("_")[-1].split(".")[0]
    except IndexError:
        raise ValueError("CSV file name does not follow the expected format (e.g., SOUN_options_2025-07-18.csv).")

    stock_ticker = os.path.basename(csv_file).split("_")[0].upper()
    stock = yf.Ticker(stock_ticker)
    stock_price = stock.history(period="1d")["Close"].iloc[-1]
    print(f"Current stock price: {stock_price:.2f}")

    options_data_with_profits = calculate_profit(csv_file, price_target, stock_price)

    if options_data_with_profits is not None:
        print("\nOptions Data with Profit Calculations:")
        print(options_data_with_profits)

        output_file = f"return/{stock_ticker}_profit_{expiration_date}_{int(price_target)}.csv"
        options_data_with_profits.to_csv(output_file, index=False)
        print(f"\nFiltered results saved to {output_file}")
