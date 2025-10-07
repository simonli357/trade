import yfinance as yf
import pandas as pd
from yahooquery import Ticker

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
        stock = Ticker(stock_ticker)
        # print(stock)
        
        # Fetch the options chain for the specified expiry date
        options_chain = stock.option_chain.loc[stock_ticker,expiry_date]
        # print(options_chain)
        return options_chain
        
        # Combine calls and puts into a single DataFrame for better visualization
        # calls = options_chain.calls
        # puts = options_chain.puts
        # calls["Type"] = "Call"
        # puts["Type"] = "Put"
        
        # options_table = pd.concat([calls, puts])
        # return options_table
    
    except Exception as e:
        print(f"Error fetching options data: {e}")
        return None

if __name__ == "__main__":
    try:
        # Input stock ticker
        stock_ticker = input("Enter the stock ticker (e.g., SOUN): ").strip().upper()
        
        # Fetch stock data
        stock = Ticker(stock_ticker)
        options = stock.option_chain
        # print(options.loc[stock_ticker,'2025-10-17'])
        # print(stock)
        
        # Get all expiration dates for the options
        option_table = options.index.format()
        # print(option_table[0].strip(stock_ticker).strip().strip('calls').strip('puts'))
        i=0
        date_table = []
        if not option_table:
            print("No options data available for this stock.")
        else:
            print("\nAvailable Expiration Dates:")
            for date in (option_table):
                trim = date.strip(stock_ticker).strip().strip('calls').strip('puts').strip()
                if trim != '':
                    date_table.append(trim)
                    print(f"{i}. {trim}")
                    i += 1
            # print(date_table)
            
            # Select expiration date
            selected_index = int(input("\nSelect an expiration date by entering its number: ")) - 1
            if selected_index < 0 or selected_index >= len(option_table):
                raise ValueError("Invalid selection. Please restart and select a valid number.")
            
            expiry_date = date_table[selected_index]
            # print(expiry_date)
            # print(options.loc[stock_ticker,expiry_date])
            # print('ok')
            
            # Fetch and display the options table
            options_table = fetch_options_table(stock_ticker, expiry_date)
            
            if options_table is not None:
                print("\nOptions Table:")
                print(options_table)
                
                # Save to CSV
                output_file = f"options\{stock_ticker}_options_{expiry_date}.csv"
                options_table.to_csv(output_file, index=False)
                print(f"\nOptions table saved to {output_file}")
    
    except Exception as e:
        print(f"Error: {e}")
