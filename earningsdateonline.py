import streamlit as st
from yahooquery import Ticker
import pandas as pd
import random
from datetime import datetime, timedelta
import calendar

# Random color generator
def random_color():
    return "#{:06x}".format(random.randint(0, 0xFFFFFF))

st.set_page_config(page_title="Earnings Calendar", layout="wide")
st.title("📅 Earnings Calendar")

# User input
ticker_input = st.text_input("Enter stock tickers (comma-separated)", "AAPL,MSFT,GOOG")
fetch = st.button("Fetch and Highlight")

if fetch:
    tickers = [t.strip().upper() for t in ticker_input.split(",") if t.strip()]
    colors = {}
    events = {}

    for ticker in tickers:
        try:
            t = Ticker(ticker)
            cal = t.calendar_events
            earnings_data = cal.get(ticker, {}).get("earnings", {})
            earnings_dates = earnings_data.get("earningsDate", [])
            if earnings_dates:
                date_str = earnings_dates[0].split()[0]
                date_obj = datetime.strptime(date_str, "%Y-%m-%d").date()
                events.setdefault(date_obj, []).append(ticker)
                if ticker not in colors:
                    colors[ticker] = random_color()
        except Exception as e:
            st.warning(f"Error fetching {ticker}: {e}")

    # Pick month range based on min/max event date
    if events:
        all_dates = list(events.keys())
        start_month = min(all_dates).replace(day=1)
        end_month = max(all_dates).replace(day=calendar.monthrange(max(all_dates).year, max(all_dates).month)[1])
        current = start_month

        while current <= end_month:
            st.subheader(current.strftime("%B %Y"))
            month_days = [datetime(current.year, current.month, d).date() for d in range(1, calendar.monthrange(current.year, current.month)[1] + 1)]
            weeks = []
            week = []
            for day in month_days:
                if day.weekday() == 0 and week:  # Monday start
                    weeks.append(week)
                    week = []
                week.append(day)
            if week:
                weeks.append(week)

            # Display as markdown table
            table_md = "| Mon | Tue | Wed | Thu | Fri | Sat | Sun |\n|---|---|---|---|---|---|---|\n"
            for week in weeks:
                row = []
                for i in range(7):
                    if i < len(week):
                        day = week[i]
                        cell = f"**{day.day}**"
                        if day in events:
                            for ticker in events[day]:
                                color = colors[ticker]
                                cell += f"<br><span style='background-color:{color};color:white;padding:2px 4px;border-radius:4px'>{ticker}</span>"
                        row.append(cell)
                    else:
                        row.append("")
                table_md += "|" + "|".join(row) + "|\n"

            st.markdown(table_md, unsafe_allow_html=True)
            current = (current + timedelta(days=32)).replace(day=1)
