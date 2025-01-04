import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QCalendarWidget, QVBoxLayout, QWidget, QLineEdit, QPushButton, QHBoxLayout
from PyQt5.QtGui import QColor, QTextCharFormat
from PyQt5.QtCore import QDate, Qt
import yfinance as yf
from datetime import date as datetime_date
import random


class EarningsCalendar(QMainWindow):
    def __init__(self):
        super().__init__()
        self.tickers = []
        self.earnings_dates = {}
        self.symbols_on_dates = {}  # Store symbols for specific dates
        self.colors = {}  # Map each ticker to a specific color
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

        # Preserve previously set symbols and colors
        if not hasattr(self, 'symbols_on_dates'):
            self.symbols_on_dates = {}
        if not hasattr(self, 'colors'):
            self.colors = {}

        for ticker in self.tickers:
            if ticker not in self.colors:
                # Generate a random color for each ticker
                self.colors[ticker] = QColor(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))

            date = self.earnings_dates.get(ticker)
            if isinstance(date, datetime_date):  # Handle datetime.date directly
                date = QDate(date.year, date.month, date.day)
            elif isinstance(date, str):  # Handle string dates
                date = QDate.fromString(date, "yyyy-MM-dd")
            elif isinstance(date, (list, tuple)) and date:
                date = QDate(date[0].year, date[0].month, date[0].day)  # Use first date if list

            if date and date.isValid():
                # Append ticker to the list for that date
                if date not in self.symbols_on_dates:
                    self.symbols_on_dates[date] = []
                if ticker not in self.symbols_on_dates[date]:
                    self.symbols_on_dates[date].append(ticker)
                
                # Highlight the date with the ticker's specific color
                self.calendar.setDateTextFormat(date, self.create_highlight_format(ticker))

        # Pass updated symbols and colors to the calendar
        self.calendar.set_symbols(self.symbols_on_dates, self.colors)
        self.calendar.update()

    def create_highlight_format(self, ticker):
        """Create a text format for highlighting the date with specific color"""
        format = QTextCharFormat()
        format.setForeground(Qt.white)
        format.setBackground(self.colors[ticker])
        return format


class Scheduler(QCalendarWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.symbols_on_dates = {}
        self.colors = {}

    def paintCell(self, painter, rect, date):
        """Override paintCell to render custom text for specific dates"""
        super().paintCell(painter, rect, date)
        
        if date in self.symbols_on_dates:
            y_offset = 5  # Initial vertical offset for text placement
            
            for symbol in self.symbols_on_dates[date]:
                # Get the color for the current symbol
                background_color = self.colors.get(symbol, QColor(0, 0, 0))  # Default black if no color found
                
                # Draw a rectangle with the ticker's color
                painter.fillRect(rect.adjusted(0, y_offset - 2, 0, y_offset + 12), background_color)
                
                # Calculate luminance to decide text color (black or white)
                luminance = (0.299 * background_color.red() + 
                            0.587 * background_color.green() + 
                            0.114 * background_color.blue())
                text_color = QColor(0, 0, 0) if luminance > 186 else QColor(255, 255, 255)
                
                # Set the text color
                painter.setPen(text_color)
                
                # Draw the symbol
                painter.drawText(rect.adjusted(5, y_offset, -5, -5), Qt.AlignLeft, symbol)
                y_offset += 15  # Move to the next line for the next symbol


    def set_symbols(self, symbols, colors):
        self.symbols_on_dates = symbols
        self.colors = colors


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = EarningsCalendar()
    window.show()
    sys.exit(app.exec_())
