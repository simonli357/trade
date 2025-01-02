import yfinance as yf
import pandas as pd
from pytz import timezone

# Define the stock symbol
symbol = "SOUNW"

# Fetch data for the stock, including extended hours
data = yf.download(symbol, period="1d", interval="1m", prepost=True)

# Convert the index (timestamps) from UTC to EST
data.index = data.index.tz_convert("US/Eastern")

# Filter for regular trading hours in EST (9:30 AM to 4:00 PM)
regular_hours = data.between_time("09:30", "16:00")

# Ensure there is data for the regular trading session
if regular_hours.empty:
    print("No data available for the regular trading session.")
else:
    # Get the opening price at 9:30 AM
    day_open_price = regular_hours.iloc[0]['Open']

    # Get the closing price at 4:00 PM
    day_close_price = regular_hours.iloc[-1]['Close']

    # Extract scalar values
    day_open_price_value = day_open_price.values[0]
    day_close_price_value = day_close_price.values[0]

    # Calculate the day change percentage
    day_change_percent = ((day_close_price_value - day_open_price_value) / day_open_price_value) * 100

    # Get the last closing price during regular trading hours
    regular_close_price = regular_hours['Close'].iloc[-1]

    # Get the last price during the aftermarket session
    aftermarket_close_price = data['Close'].iloc[-1]

    # Extract scalar values from the Series
    regular_close_price_value = regular_close_price.values[0]
    aftermarket_close_price_value = aftermarket_close_price.values[0]

    # Calculate the aftermarket change percentage
    aftermarket_change_percent = ((aftermarket_close_price_value - regular_close_price_value) / regular_close_price_value) * 100

    # Print results
    print(f"Day Open Price: {day_open_price_value}")
    print(f"Day Close Price: {day_close_price_value}")
    print(f"Day Change Percentage: {day_change_percent:.2f}%")
    print(f"Regular Close Price: {regular_close_price_value}")
    print(f"Aftermarket Close Price: {aftermarket_close_price_value}")
    print(f"Aftermarket Change Percentage: {aftermarket_change_percent:.2f}%")
