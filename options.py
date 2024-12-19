import yfinance as yf
import pandas as pd

def fetch_options_table(stock_ticker, expiry_date):
    """
    Fetches the options table for a specific stock ticker and expiry date.
    
    Args:
        stock_ticker (str): The stock ticker symbol (e.g., "AAPL", "SOUN").
        expiry_date (str): The expiration date in "YYYY-MM-DD" format.
        
    Returns:
        pd.DataFrame: DataFrame containing the options table (calls and puts).
    """
    try:
        # Fetch the stock data
        stock = yf.Ticker(stock_ticker)
        
        # Fetch the options chain for the specified expiry date
        options_chain = stock.option_chain(expiry_date)
        
        # Combine calls and puts into a single DataFrame for better visualization
        calls = options_chain.calls
        puts = options_chain.puts
        calls["Type"] = "Call"
        puts["Type"] = "Put"
        
        options_table = pd.concat([calls, puts])
        return options_table
    
    except Exception as e:
        print(f"Error fetching options data: {e}")
        return None

if __name__ == "__main__":
    try:
        # Input stock ticker
        stock_ticker = input("Enter the stock ticker (e.g., SOUN): ").strip().upper()
        
        # Fetch stock data
        stock = yf.Ticker(stock_ticker)
        
        # Get all expiration dates for the options
        expiration_dates = stock.options
        if not expiration_dates:
            print("No options data available for this stock.")
        else:
            print("\nAvailable Expiration Dates:")
            for i, date in enumerate(expiration_dates):
                print(f"{i + 1}. {date}")
            
            # Select expiration date
            selected_index = int(input("\nSelect an expiration date by entering its number: ")) - 1
            if selected_index < 0 or selected_index >= len(expiration_dates):
                raise ValueError("Invalid selection. Please restart and select a valid number.")
            
            expiry_date = expiration_dates[selected_index]
            
            # Fetch and display the options table
            options_table = fetch_options_table(stock_ticker, expiry_date)
            
            if options_table is not None:
                print("\nOptions Table:")
                print(options_table)
                
                # Save to CSV
                output_file = f"{stock_ticker}_options_{expiry_date}.csv"
                options_table.to_csv(output_file, index=False)
                print(f"\nOptions table saved to {output_file}")
    
    except Exception as e:
        print(f"Error: {e}")
