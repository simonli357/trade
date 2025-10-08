# import requests

# API_KEY = "d1ul9u9r01qpci1d6890d1ul9u9r01qpci1d689g"

# for symbol in ["AAPL", "MSFT", "TSLA", "NVDA"]:
#     url = f"https://finnhub.io/api/v1/calendar/earnings?symbol={symbol}&token={API_KEY}"
#     response = requests.get(url)
#     print(f"\n{symbol} earnings:")
#     print(response.json())
from yahooquery import Ticker
from datetime import datetime

from yahooquery import Ticker
from PyQt5.QtCore import QDate
from datetime import datetime

def fetch_earnings_yahooquery(symbol):
    try:
        ticker = Ticker(symbol)
        events = ticker.calendar_events
        earnings_data = events.get(symbol, {}).get("earnings", {})
        earnings_date_list = earnings_data.get("earningsDate", [])

        if earnings_date_list:
            # Extract only the date part before space
            date_str = earnings_date_list[0].split()[0]  # '2025-07-23'
            date_obj = datetime.strptime(date_str, "%Y-%m-%d")
            return QDate(date_obj.year, date_obj.month, date_obj.day)

    except Exception as e:
        print(f"Error for {symbol}: {e}")

    return None

print(fetch_earnings_yahooquery('GOOG'))