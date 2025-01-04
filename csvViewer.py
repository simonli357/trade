import sys
import pandas as pd
import yfinance as yf
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QWidget, QLabel,
    QLineEdit, QCalendarWidget, QSlider, QPushButton, QTableView, QFileDialog, QMessageBox, QHeaderView, QHBoxLayout, QGraphicsOpacityEffect
)
from PyQt5.QtCore import Qt, QDate, QPropertyAnimation, QEasingCurve, QTimer
from PyQt5.QtGui import QStandardItemModel, QStandardItem, QTextCharFormat, QBrush, QColor, QFont, QIntValidator, QDoubleValidator
import random

class OptionCalculatorUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Options Calculator")
        self.setGeometry(100, 100, 1000, 800)
        self.font = 12

        # Central widget and layout
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout()
        self.central_widget.setLayout(self.layout)

        # # Auto-adjust font size based on screen resolution
        # self.adjust_font_size()

        # Input field to change font size
        self.font_size_input = QLineEdit()
        self.font_size_input.setPlaceholderText("Enter font size (e.g. 12)")
        self.layout.addWidget(self.font_size_input)

        # Connect the input field to handle the Enter key press
        self.font_size_input.returnPressed.connect(self.adjust_font_size)

        # Input for stock ticker
        self.ticker_label = QLabel("Enter Stock Ticker:")
        self.layout.addWidget(self.ticker_label)
        self.ticker_input = QLineEdit()
        self.layout.addWidget(self.ticker_input)
        self.ticker_input.returnPressed.connect(self.fetch_options_data)

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

        # Target price slider label and input box
        target_price_layout = QHBoxLayout()

        self.slider_label_target_price = QLabel("Set Target Price:")
        target_price_layout.addWidget(self.slider_label_target_price)

        self.target_price_input = QLineEdit()
        self.target_price_input.setFixedWidth(300)  # Set a small width for the input box
        self.target_price_input.setPlaceholderText("Enter Price")
        self.target_price_input.setValidator(QIntValidator(1, 1000))  # Ensure only valid integers are entered
        self.target_price_input.returnPressed.connect(self.update_target_price_from_input)  # Update slider when Enter is pressed
        target_price_layout.addWidget(self.target_price_input)

        self.layout.addLayout(target_price_layout)  # Add the horizontal layout to the main layout

        # Target price slider
        self.slider_target_price = QSlider(Qt.Horizontal)
        self.slider_target_price.setMinimum(1)
        self.slider_target_price.setMaximum(1000)
        self.slider_target_price.setValue(100)
        self.slider_target_price.valueChanged.connect(self.update_target_price_label)
        self.layout.addWidget(self.slider_target_price)

        # Target price display label
        self.target_price_label = QLabel("Target Price: $100")
        self.layout.addWidget(self.target_price_label)

        # Commission price slider label and input box
        commission_price_layout = QHBoxLayout()

        self.slider_label_commission = QLabel("Set Commission Price ($USD per contract):")
        commission_price_layout.addWidget(self.slider_label_commission)

        self.commission_price_input = QLineEdit()
        self.commission_price_input.setFixedWidth(300)  # Set a small width for the input box
        self.commission_price_input.setPlaceholderText("Enter Commission")
        self.commission_price_input.setValidator(QDoubleValidator(0.01, 10.0, 2))  # Allow values from 0.01 to 10.00 with 2 decimal points
        self.commission_price_input.returnPressed.connect(self.update_commission_from_input)  # Update slider when Enter is pressed
        commission_price_layout.addWidget(self.commission_price_input)

        self.layout.addLayout(commission_price_layout)  # Add the horizontal layout to the main layout

        # Commission price slider
        self.slider_commission = QSlider(Qt.Horizontal)
        self.slider_commission.setMinimum(1)  # Representing 0.01
        self.slider_commission.setMaximum(1000)  # Representing 10.00
        self.slider_commission.setValue(200)  # Default value representing $2.00
        self.slider_commission.valueChanged.connect(self.update_commission_label)
        self.layout.addWidget(self.slider_commission)

        # Commission price display label
        self.commission_label = QLabel("Commission Price: $2.00")
        self.layout.addWidget(self.commission_label)

        # Load button to fetch data
        self.load_button = QPushButton("Fetch Options Data")
        self.load_button.clicked.connect(self.fetch_options_data)
        self.layout.addWidget(self.load_button)

        # Table to display data
        self.table_view = QTableView()
        self.table_view.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)  # Auto resize columns
        self.table_view.verticalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)  # Auto resize rows
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

        # Create a layout for the prediction widget
        self.predict_layout = QVBoxLayout()

        # Predict Target Price Button
        self.predict_button = QPushButton("Predict Target Price")
        self.predict_button.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                font-size: 16px;
                font-weight: bold;
                border-radius: 8px;
                padding: 10px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        self.predict_button.clicked.connect(self.generate_predicted_price)
        self.predict_layout.addWidget(self.predict_button)

        # Predicted Price Display Label
        self.predicted_price_label = QLabel("Predicted Price: 0.00$")
        self.predicted_price_label.setAlignment(Qt.AlignCenter)
        self.predicted_price_label.setStyleSheet("""
            QLabel {
                color: #FF5733;
                font-size: 24px;
                font-weight: bold;
            }
        """)
        self.predict_layout.addWidget(self.predicted_price_label)

        # Add prediction layout to the main layout
        self.layout.addLayout(self.predict_layout)

    def generate_predicted_price(self):
        """Generate a random price within the current price ±20%."""
        if not hasattr(self, "stock_price") or self.stock_price == 0:
            QMessageBox.warning(self, "Error", "Please fetch options data first to get the current stock price.")
            return

        # Generate random price within ±20% of the current price
        lower_bound = self.stock_price * 0.8
        upper_bound = self.stock_price * 1.2
        predicted_price = round(random.uniform(lower_bound, upper_bound), 2)

        # Update the predicted price label
        self.predicted_price_label.setText(f"Predicted Price: ${predicted_price:.2f}")

        # Add a flashy effect (e.g., fade-in animation)
        self.animate_predicted_price()

    # def animate_predicted_price(self):
    #     """Animate the predicted price, with each letter fading in one by one."""

    #     # Get the full text to animate
    #     text = self.predicted_price_label.text()
        
    #     # Clear existing text in the label (so we can add it letter by letter)
    #     self.predicted_price_label.setText("")
        
    #     # Create a list to store the individual characters
    #     self.animated_text = list(text)
        
    #     # Set an initial opacity effect to the label
    #     opacity_effect = QGraphicsOpacityEffect()
    #     self.predicted_price_label.setGraphicsEffect(opacity_effect)

    #     # Create a sequence of animations, one for each letter
    #     self.animations = []
        
    #     # Get the style of the original label and apply it to each letter
    #     original_style = self.predicted_price_label.styleSheet()
        
    #     # Calculate total width of all the letters combined (to center them)
    #     total_width = len(self.animated_text) * 20  # 20 is the width for each letter
        
    #     # Create a temporary label for each letter and apply opacity effect
    #     self.letter_labels = []  # Store references to each letter QLabel for later animation
    #     # Create a temporary label for each letter and apply opacity effect
    #     for i, char in enumerate(self.animated_text):
    #         # Create a temporary label for each letter
    #         letter_label = QLabel(char, self.predicted_price_label)
    #         letter_label.setStyleSheet(original_style)  # Apply original style to each letter
    #         letter_label.setAlignment(self.predicted_price_label.alignment())  # Same alignment as original
            
    #         # Set position and size for the letter (with initial opacity set to 0.0)
    #         letter_label.setGeometry(i * 20, 0, 20, 20)  # Adjust horizontal spacing
    #         letter_opacity_effect = QGraphicsOpacityEffect(letter_label)
    #         letter_label.setGraphicsEffect(letter_opacity_effect)
    #         letter_opacity_effect.setOpacity(0.0)  # Set the initial opacity to 0 (fully transparent)

    #         # Store the label for later use
    #         self.letter_labels.append(letter_label)
            
    #         # Show the label after setting opacity to 0 (it will be invisible until animation starts)
    #         letter_label.show()
            
    #         # Create an opacity animation for each letter
    #         opacity_animation = QPropertyAnimation(letter_opacity_effect, b"opacity")
    #         opacity_animation.setDuration(300)  # 300ms duration for each letter
    #         opacity_animation.setStartValue(0.0)  # Start fully transparent
    #         opacity_animation.setEndValue(1.0)    # End fully visible
    #         opacity_animation.setEasingCurve(QEasingCurve.OutQuad)
            
    #         # Add each animation to the list
    #         self.animations.append(opacity_animation)
        
    #     # Now, calculate the total width of the animated text and adjust positioning
    #     start_x = (self.predicted_price_label.width() - total_width) // 2  # Center the text horizontally
    #     for i, letter_label in enumerate(self.letter_labels):
    #         letter_label.setGeometry(start_x + i * 20, 0, 20, 20)  # Adjust horizontal spacing from the centered position
        
    #     # Start the animations one by one with a slight delay
    #     self.current_letter = 0
    #     self.animation_timer = QTimer(self)
    #     self.animation_timer.timeout.connect(self.show_next_letter)
    #     self.animation_timer.start(100)  # Start after a short delay

    # def show_next_letter(self):
    #     """Show the next letter by starting its animation."""
    #     if self.current_letter < len(self.animations):
    #         # Start the next animation (letter fade-in)
    #         self.animations[self.current_letter].start()
    #         self.current_letter += 1
    #     else:
    #         # Stop the timer once all letters are animated
    #         self.animation_timer.stop()

    def animate_predicted_price(self):
        """Add a fade-in animation for the predicted price label."""
        # Add an opacity effect to the QLabel
        opacity_effect = QGraphicsOpacityEffect()
        self.predicted_price_label.setGraphicsEffect(opacity_effect)

        # Set up the animation
        animation = QPropertyAnimation(opacity_effect, b"opacity")
        animation.setDuration(10000)  # 10 seconds fade-in
        animation.setStartValue(0.0)  # Start fully transparent
        animation.setEndValue(1.0)  # End fully visible
        animation.setEasingCurve(QEasingCurve.OutBounce)

        # Start the animation
        animation.start()

        # Store a reference to the animation to prevent it from being garbage-collected
        self.animation = animation


    def update_commission_from_input(self):
        """Update the slider value based on the commission input box."""
        try:
            commission = float(self.commission_price_input.text())
            # Convert commission value to slider value (e.g., $2.00 -> 200)
            slider_value = int(commission * 100)
            if 1 <= slider_value <= 1000:
                self.slider_commission.setValue(slider_value)
                self.commission_label.setText(f"Commission Price: ${commission}")
                if self.options_data is not None:
                    self.calculate_returns()
            else:
                raise ValueError
        except ValueError:
            QMessageBox.warning(self, "Input Error", "Please enter a valid commission between 0.01 and 10.00.")

    def update_target_price_from_input(self):
        """Update the slider value based on the input box."""
        try:
            target_price = int(self.target_price_input.text())
            self.slider_target_price.setValue(target_price)
            self.target_price_label.setText(f"Target Price: ${target_price}")
            if self.options_data is not None:
                self.calculate_returns()
        except ValueError:
            QMessageBox.warning(self, "Input Error", "Please enter a valid integer for the target price.")

    def adjust_font_size(self):
        """Dynamically adjust font size based on screen resolution."""
        try:
            screen = self.screen().size()  # Get screen resolution
            base_width = 1920  # Assumed base resolution width
            scaling_factor = screen.width() / base_width
            font_size = int(self.font_size_input.text())

            # Apply scaled font to the entire application
            font = QFont()
            font.setPointSizeF(font_size * scaling_factor)  # Scale the font size
            self.setFont(font)
        except ValueError:
            print("Please enter a valid number for the font size.")

    def resizeEvent(self, event):
        """Ensure table dynamically resizes with the window."""
        super().resizeEvent(event)
        self.table_view.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table_view.verticalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)

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
            self.target_price_label.setText(f"Target Price: ${self.stock_price:.2f}")
            self.slider_target_price.setValue(int(self.stock_price))

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
        target_price = self.slider_target_price.value()
        self.target_price_label.setText(f"Target Price: ${target_price}")
        self.target_price_input.setText(str(target_price))
        if self.options_data is not None:
            self.calculate_returns()

    def update_commission_label(self):
        commission = self.slider_commission.value()/100
        self.commission_label.setText(f"Commission Price: ${commission}")
        self.commission_price_input.setText(str(commission))
        if self.options_data is not None:
            self.calculate_returns()

    def calculate_returns(self):
        target_price = self.slider_target_price.value()  # Target price from the slider
        commission = self.slider_commission.value()/100 # Commission price from slider
        try:
            # Separate calls and puts
            calls_data = self.options_data[self.options_data["Type"] == "Call"].copy()
            puts_data = self.options_data[self.options_data["Type"] == "Put"].copy()

            # Calculate mid-price (average of bid and ask) for both calls and puts
            calls_data["premium"] = ((calls_data["bid"] + calls_data["ask"]) / 2).round(2)
            puts_data["premium"] = ((puts_data["bid"] + puts_data["ask"]) / 2).round(2)

            # Calculate break-even prices
            calls_data["break_even"] = (calls_data["strike"] + calls_data["premium"]).round(2)
            puts_data["break_even"] = (puts_data["strike"] - puts_data["premium"]).round(2)

            # Calculate returns for calls
            calls_data["option_profit"] = (
                ((target_price - calls_data["strike"]).clip(lower=0) * 100 - (calls_data["premium"] * 100 + commission)).round(2)
            )
            calls_data["option_percent_profit"] = (
                (calls_data["option_profit"] / (calls_data["premium"] * 100 + commission) * 100).round(2)
            )
            calls_data.loc[calls_data["break_even"] > target_price, ["option_profit", "option_percent_profit"]] = None

            # Calculate returns for puts
            puts_data["option_profit"] = (
                ((puts_data["strike"] - target_price).clip(lower=0) * 100 - (puts_data["premium"] * 100 + commission)).round(2)
            )
            puts_data["option_percent_profit"] = (
                (puts_data["option_profit"] / (puts_data["premium"] * 100 + commission) * 100).round(2)
            )
            puts_data.loc[puts_data["break_even"] < target_price, ["option_profit", "option_percent_profit"]] = None

            # Combine calls and puts into a single DataFrame
            combined_data = pd.concat([calls_data, puts_data], ignore_index=True)

            # Display the combined data in the table
            self.display_data(combined_data)
            self.resizeEvent(None)
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
