import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QCalendarWidget, QVBoxLayout, QWidget, QLineEdit, QPushButton, QHBoxLayout
from PyQt5.QtGui import QColor, QTextCharFormat
from PyQt5.QtCore import QDate, Qt
import yfinance as yf
from datetime import date as datetime_date

class EarningsCalendar(QMainWindow):
    def __init__(self):
        super().__init__()
        self.tickers = []
        self.earnings_dates = {}
        self.symbols_on_dates = {}  # Store a list of stock symbols for specific dates
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Earnings Calendar')
        self.setGeometry(100, 100, 800, 600)
        
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        layout = QVBoxLayout()
        
        # Input field for stock tickers
        input_layout = QHBoxLayout()
        self.ticker_input = QLineEdit(self)
        self.ticker_input.setPlaceholderText("Enter stock tickers (e.g., AAPL,MSFT,GOOG)")
        input_layout.addWidget(self.ticker_input)
        self.ticker_input.returnPressed.connect(self.highlight_earnings_dates)

        self.submit_button = QPushButton("Fetch and Highlight")
        self.submit_button.clicked.connect(self.highlight_earnings_dates)
        input_layout.addWidget(self.submit_button)

        layout.addLayout(input_layout)

        # Calendar Widget
        self.calendar = Scheduler()
        layout.addWidget(self.calendar)

        self.central_widget.setLayout(layout)

    def fetch_earnings_dates(self):
        earnings_dates = {}
        for ticker in self.tickers:
            stock = yf.Ticker(ticker)
            try:
                calendar = stock.calendar
                earnings_date = calendar.get('Earnings Date', [None])[0]  # First earnings date
                earnings_dates[ticker] = earnings_date
            except Exception as e:
                earnings_dates[ticker] = f'Error: {str(e)}'
        return earnings_dates

    def highlight_earnings_dates(self):
        user_input = self.ticker_input.text()
        self.tickers = [ticker.strip().upper() for ticker in user_input.split(',') if ticker.strip()]
        self.earnings_dates = self.fetch_earnings_dates()
        self.symbols_on_dates = {}  # Reset the dictionary every time a new input is provided

        for ticker, date in self.earnings_dates.items():
            if isinstance(date, datetime_date):  # Handle datetime.date directly
                date = QDate(date.year, date.month, date.day)
            elif isinstance(date, str):  # Handle string dates
                date = QDate.fromString(date, "yyyy-MM-dd")
            elif isinstance(date, (list, tuple)) and date:
                date = QDate(date[0].year, date[0].month, date[0].day)  # Use first date if list
            if date and date.isValid():
                # Append ticker to the list for that date
                if date in self.symbols_on_dates:
                    self.symbols_on_dates[date].append(ticker)
                else:
                    self.symbols_on_dates[date] = [ticker]
                
                # Highlight the date
                self.calendar.setDateTextFormat(date, self.create_highlight_format())

        self.calendar.set_symbols(self.symbols_on_dates)
        self.calendar.update()  # Trigger an update to re-render the calendar

    def create_highlight_format(self):
        """Create a text format for highlighting the date"""
        format = QTextCharFormat()
        format.setForeground(Qt.white)
        format.setBackground(Qt.blue)
        return format

class Scheduler(QCalendarWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.symbols_on_dates = {}

    def paintCell(self, painter, rect, date):
        """Override paintCell to render custom text for specific dates"""
        super().paintCell(painter, rect, date)
        
        if date in self.symbols_on_dates:
            painter.setPen(QColor(255, 255, 255))  # White color for the stock symbol text
            # Draw the symbols, each symbol on a new line
            symbols = ', '.join(self.symbols_on_dates[date])
            painter.drawText(rect.adjusted(5, 5, -5, -5), Qt.AlignTop | Qt.AlignLeft, symbols)

    def set_symbols(self, symbols):
        self.symbols_on_dates = symbols

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = EarningsCalendar()
    window.show()
    sys.exit(app.exec_())
