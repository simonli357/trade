import sys
import pandas as pd
import yfinance as yf
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QWidget, QLabel,
    QLineEdit, QCalendarWidget, QSlider, QPushButton, QTableView, QFileDialog, QMessageBox
)
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtGui import QStandardItemModel, QStandardItem, QTextCharFormat, QBrush, QColor


class OptionCalculatorUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Options Calculator")
        self.setGeometry(100, 100, 1000, 800)

        # Central widget and layout
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout()
        self.central_widget.setLayout(self.layout)

        # Input for stock ticker
        self.ticker_label = QLabel("Enter Stock Ticker:")
        self.layout.addWidget(self.ticker_label)
        self.ticker_input = QLineEdit()
        self.layout.addWidget(self.ticker_input)

        # Calendar widget for expiration date
        self.expiry_label = QLabel("Select Expiration Date:")
        self.layout.addWidget(self.expiry_label)
        self.calendar = QCalendarWidget()
        self.calendar.setGridVisible(True)
        self.calendar.selectionChanged.connect(self.update_selected_date)
        self.layout.addWidget(self.calendar)

        # Label for selected expiration date
        self.selected_date_label = QLabel("Selected Date: None")
        self.layout.addWidget(self.selected_date_label)

        # Target price slider
        self.slider_label = QLabel("Set Target Price:")
        self.layout.addWidget(self.slider_label)
        self.slider = QSlider(Qt.Horizontal)
        self.slider.setMinimum(1)
        self.slider.setMaximum(1000)
        self.slider.setValue(100)
        self.slider.valueChanged.connect(self.update_target_price_label)
        self.layout.addWidget(self.slider)
        self.target_price_label = QLabel("Target Price: $100")
        self.layout.addWidget(self.target_price_label)

        # Load button to fetch data
        self.load_button = QPushButton("Fetch Options Data")
        self.load_button.clicked.connect(self.fetch_options_data)
        self.layout.addWidget(self.load_button)

        # Table to display data
        self.table_view = QTableView()
        self.layout.addWidget(self.table_view)

        # Save button
        self.save_button = QPushButton("Save to CSV")
        self.save_button.clicked.connect(self.save_to_csv)
        self.save_button.setEnabled(False)  # Disabled until data is loaded
        self.layout.addWidget(self.save_button)

        # Internal state
        self.options_data = None
        self.stock_price = 0
        self.valid_expiration_dates = []

    def fetch_options_data(self):
        stock_ticker = self.ticker_input.text().strip().upper()
        if not stock_ticker:
            QMessageBox.warning(self, "Input Error", "Please enter a valid stock ticker.")
            return

        try:
            stock = yf.Ticker(stock_ticker)
            # self.valid_expiration_dates = stock.options
            self.valid_expiration_dates = [
                pd.to_datetime(date).strftime("%Y-%m-%d") for date in stock.options
            ]

            if not self.valid_expiration_dates:
                QMessageBox.warning(self, "Data Error", "No options data available for this stock.")
                return

            # Restrict calendar selection to valid expiration dates
            self.restrict_calendar_to_valid_dates()
            QMessageBox.information(
                self, "Data Loaded", f"Available expiration dates loaded for {stock_ticker}."
            )

            # Automatically fetch the current stock price
            self.stock_price = stock.history(period="1d")["Close"].iloc[-1]
            QMessageBox.information(self, "Stock Price", f"Current stock price: ${self.stock_price:.2f}")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to fetch data for {stock_ticker}: {e}")

    def restrict_calendar_to_valid_dates(self):
        """Highlight valid expiration dates on the calendar."""
        # Clear previous highlights
        self.calendar.setDateTextFormat(QDate.currentDate(), QTextCharFormat())

        # Create a QTextCharFormat for highlighting
        highlight_format = QTextCharFormat()
        highlight_format.setBackground(QBrush(QColor("yellow")))  # Highlight with yellow background
        highlight_format.setForeground(QBrush(QColor("black")))  # Set text color to black

        # Highlight only the valid expiration dates
        for date in self.valid_expiration_dates:
            qdate = QDate.fromString(date, "yyyy-MM-dd")
            self.calendar.setDateTextFormat(qdate, highlight_format)

        # Set the minimum and maximum date range for the calendar
        self.calendar.setMinimumDate(QDate.fromString(self.valid_expiration_dates[0], "yyyy-MM-dd"))
        self.calendar.setMaximumDate(QDate.fromString(self.valid_expiration_dates[-1], "yyyy-MM-dd"))

    def update_selected_date(self):
        selected_date = self.calendar.selectedDate().toString("yyyy-MM-dd")
        if selected_date in self.valid_expiration_dates:
            self.selected_date_label.setText(f"Selected Date: {selected_date}")
            self.expiration_date = selected_date
            self.load_options_data()
        else:
            self.selected_date_label.setText("Selected Date: Invalid (Not an expiration date)")
            self.expiration_date = None

    def load_options_data(self):
        if not self.expiration_date:
            QMessageBox.warning(self, "Selection Error", "Please select a valid expiration date.")
            return

        stock_ticker = self.ticker_input.text().strip().upper()
        try:
            stock = yf.Ticker(stock_ticker)
            options_chain = stock.option_chain(self.expiration_date)

            # Combine calls and puts
            calls = options_chain.calls
            puts = options_chain.puts
            calls["Type"] = "Call"
            puts["Type"] = "Put"
            self.options_data = pd.concat([calls, puts])

            # Display the initial data
            self.display_data(self.options_data)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error loading options data: {e}")

    def update_target_price_label(self):
        target_price = self.slider.value()
        self.target_price_label.setText(f"Target Price: ${target_price}")
        if self.options_data is not None:
            self.calculate_returns()

    def calculate_returns(self):
        target_price = self.slider.value()
        try:
            # Calculate returns for CALLS
            calls_data = self.options_data[self.options_data["Type"] == "Call"].copy()
            calls_data["premium"] = ((calls_data["bid"] + calls_data["ask"]) / 2).round(2)
            calls_data["break_even"] = (calls_data["strike"] + calls_data["premium"]).round(2)

            # Profit and percent profit for calls
            calls_data["option_profit"] = (
                ((target_price - calls_data["strike"]).clip(lower=0) * 100 - calls_data["premium"] * 100).round(2)
            )
            calls_data["option_percent_profit"] = (
                (calls_data["option_profit"] / (calls_data["premium"] * 100) * 100).round(2)
            )
            calls_data.loc[calls_data["break_even"] > target_price, ["option_profit", "option_percent_profit"]] = None

            # Calculate returns for PUTS
            puts_data = self.options_data[self.options_data["Type"] == "Put"].copy()
            puts_data["premium"] = ((puts_data["bid"] + puts_data["ask"]) / 2).round(2)
            puts_data["break_even"] = (puts_data["strike"] - puts_data["premium"]).round(2)

            # Profit and percent profit for puts
            puts_data["option_profit"] = (
                ((puts_data["strike"] - target_price).clip(lower=0) * 100 - puts_data["premium"] * 100).round(2)
            )
            puts_data["option_percent_profit"] = (
                (puts_data["option_profit"] / (puts_data["premium"] * 100) * 100).round(2)
            )
            puts_data.loc[puts_data["break_even"] < target_price, ["option_profit", "option_percent_profit"]] = None

            # Combine calls and puts
            combined_data = pd.concat([calls_data, puts_data])

            # Display updated data
            self.display_data(combined_data)

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error calculating returns: {e}")

    def display_data(self, data):
        model = QStandardItemModel()
        model.setHorizontalHeaderLabels(data.columns)

        for row in data.itertuples(index=False):
            items = [QStandardItem(str(item)) for item in row]
            model.appendRow(items)

        self.table_view.setModel(model)
        self.table_view.resizeColumnsToContents()
        self.save_button.setEnabled(True)

    def save_to_csv(self):
        if self.options_data is not None:
            file_name, _ = QFileDialog.getSaveFileName(self, "Save CSV", "", "CSV Files (*.csv);;All Files (*)")
            if file_name:
                self.options_data.to_csv(file_name, index=False)
                QMessageBox.information(self, "Success", f"Data saved to {file_name}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    ui = OptionCalculatorUI()
    ui.show()
    sys.exit(app.exec_())
