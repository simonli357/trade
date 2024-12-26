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
    Reads a CSV file of call options, filters out puts, and calculates profit and % profit.
    Additionally calculates profit and % profit for buying the stock directly.
    
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
        
        # Filter only call options
        calls_data = options_data[options_data["Type"].str.lower() == "call"]
        
        # Calculate the mid-price of the option (average of bid and ask)
        calls_data["premium"] = ((calls_data["bid"] + calls_data["ask"]) / 2).round(2)
        
        calls_data["break_even"] = (calls_data["strike"] + calls_data["premium"]).round(2)
        
        calls_data["option_profit"] = (
            ((price_target - calls_data["strike"]).clip(lower=0) * 100 - calls_data["premium"] * 100).round(2)
        )
        calls_data["option_percent_profit"] = (
            (calls_data["option_profit"] / (calls_data["premium"] * 100) * 100).round(2)
        )
        
        calls_data.loc[calls_data["break_even"] > price_target, ["option_profit", "option_percent_profit"]] = None
        
        calls_data["stock_units"] = (calls_data["premium"] * 100 / stock_price).round(2)
        calls_data["stock_profit"] = (calls_data["stock_units"] * (price_target - stock_price)).round(2)
        calls_data["stock_percent_profit"] = (
            (calls_data["stock_profit"] / (calls_data["premium"] * 100) * 100).round(2)
        )
        
        relevant_columns = [
            "strike", "premium", "break_even", 
            "option_profit", "option_percent_profit", 
            "stock_profit", "stock_percent_profit"
        ]
        filtered_data = calls_data[relevant_columns]
        
        return filtered_data
    
    except Exception as e:
        print(f"Error: {e}")
        return None

if __name__ == "__main__":
    csv_file = input("Enter the path to the options CSV file (e.g., options\SOUN_options_2025-07-18.csv): ")
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
