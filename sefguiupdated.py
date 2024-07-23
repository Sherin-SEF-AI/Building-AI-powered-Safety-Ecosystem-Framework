import sys
import csv
from datetime import datetime
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QLabel, QTextEdit, QTabWidget, QFormLayout, QLineEdit, QDialog, QFileDialog
)
from PyQt5 import QtCore
from PyQt5.QtGui import QFont
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

# Constants
ROLLING_WINDOW_SIZE = 20
CSV_FILE = 'sensor_data_log.csv'

# Mock sensor data
sensor_data = {
    'temperature': 0,
    'smoke_level': 0,
    'humidity': 0,
    'gas_level': 0,
    'vibration': 0
}

def update_sensor_data():
    """Mock function to update sensor data."""
    import random
    sensor_data['temperature'] = random.uniform(15, 30)
    sensor_data['smoke_level'] = random.uniform(0, 10)
    sensor_data['humidity'] = random.uniform(20, 80)
    sensor_data['gas_level'] = random.uniform(0, 5)
    sensor_data['vibration'] = random.uniform(0, 2)

def detect_threat():
    """Mock function to detect threats based on sensor data."""
    threats = []
    if sensor_data['temperature'] > 28:
        threats.append('High temperature detected!')
    if sensor_data['smoke_level'] > 5:
        threats.append('High smoke level detected!')
    if sensor_data['gas_level'] > 3:
        threats.append('High gas level detected!')
    return threats

class SensorPlot(QWidget):
    def __init__(self, title, xlabel, ylabel, parent=None):
        super().__init__(parent)
        self.figure, self.ax = plt.subplots()
        self.canvas = FigureCanvas(self.figure)
        layout = QVBoxLayout()
        self.ax.set_title(title)
        self.ax.set_xlabel(xlabel)
        self.ax.set_ylabel(ylabel)
        layout.addWidget(self.canvas)
        self.setLayout(layout)
        self.update_plot([], [])

    def update_plot(self, x_data, y_data):
        self.ax.clear()
        self.ax.plot(x_data, y_data, label='Sensor Data')
        self.ax.legend()
        self.canvas.draw()

class LoginDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('Login')
        self.setFixedSize(300, 150)
        layout = QVBoxLayout()
        self.username_input = QLineEdit(self)
        self.password_input = QLineEdit(self)
        self.password_input.setEchoMode(QLineEdit.Password)
        self.login_button = QPushButton('Login', self)
        self.message_label = QLabel('', self)
        
        form_layout = QFormLayout()
        form_layout.addRow('Username:', self.username_input)
        form_layout.addRow('Password:', self.password_input)
        layout.addLayout(form_layout)
        layout.addWidget(self.login_button)
        layout.addWidget(self.message_label)
        
        self.login_button.clicked.connect(self.handle_login)
        self.setLayout(layout)

    def handle_login(self):
        username = self.username_input.text()
        password = self.password_input.text()
        role = self.validate_user(username, password)
        if role:
            self.accept()  # Close dialog with success
        else:
            self.message_label.setText('Invalid username or password')

    def validate_user(self, username, password):
        # Example hardcoded users, replace with a secure database in production
        users = {
            'admin': ('adminpass', 'Admin'),
            'operator': ('operatorpass', 'Operator'),
            'viewer': ('viewerpass', 'Viewer')
        }
        return users.get(username)[1] if users.get(username) == (password, users.get(username)[1]) else None

class Dashboard(QMainWindow):
    def __init__(self):
        super().__init__()
        self.current_user_role = None
        self.show_login_dialog()

    def show_login_dialog(self):
        login_dialog = LoginDialog(self)
        if login_dialog.exec_() == QDialog.Accepted:
            # Set user role based on the login dialog
            username = login_dialog.username_input.text()
            self.current_user_role = login_dialog.validate_user(username, login_dialog.password_input.text())
            self.initUI()
            self.create_plots()

            # Initialize CSV file for logging
            self.csv_file = open(CSV_FILE, 'w', newline='')
            self.csv_writer = csv.writer(self.csv_file)
            self.csv_writer.writerow(['Timestamp', 'Temperature', 'Smoke Level', 'Humidity', 'Gas Level', 'Vibration'])

            # Timer for regular updates
            self.timer = QtCore.QTimer(self)
            self.timer.timeout.connect(self.update_data)
            self.timer.start(2000)  # Update every 2 seconds
        else:
            sys.exit()

    def initUI(self):
        self.setWindowTitle('Industrial Safety Monitoring Dashboard')
        self.setGeometry(100, 100, 1200, 800)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout()

        title = QLabel("Industrial Safety Monitoring Dashboard", self)
        title.setFont(QFont('Arial', 24, QFont.Bold))
        main_layout.addWidget(title)

        button_layout = QHBoxLayout()

        # Show update button only for Admin and Operator
        if self.current_user_role in ['Admin', 'Operator']:
            update_button = QPushButton("Update Sensor Data", self)
            update_button.clicked.connect(self.update_data)
            button_layout.addWidget(update_button)

        # Show save CSV button only for Admin
        if self.current_user_role == 'Admin':
            save_csv_button = QPushButton("Save CSV Log", self)
            save_csv_button.clicked.connect(self.save_csv)
            button_layout.addWidget(save_csv_button)

        main_layout.addLayout(button_layout)

        self.alert_label = QLabel("Alerts: No issues detected", self)
        main_layout.addWidget(self.alert_label)

        self.alert_text = QTextEdit(self)
        self.alert_text.setReadOnly(True)
        main_layout.addWidget(self.alert_text)

        # Create the tab widget
        self.tabs = QTabWidget()

        # Create individual sensor plot widgets
        self.temperature_plot = SensorPlot('Temperature Over Time', 'Time', 'Temperature (°C)')
        self.smoke_plot = SensorPlot('Smoke Level Over Time', 'Time', 'Smoke Level')
        self.humidity_plot = SensorPlot('Humidity Over Time', 'Time', 'Humidity (%)')
        self.gas_plot = SensorPlot('Gas Level Over Time', 'Time', 'Gas Level')
        self.vibration_plot = SensorPlot('Vibration Over Time', 'Time', 'Vibration')

        # Add plots to tabs
        self.tabs.addTab(self.temperature_plot, 'Temperature')
        self.tabs.addTab(self.smoke_plot, 'Smoke Level')
        self.tabs.addTab(self.humidity_plot, 'Humidity')
        self.tabs.addTab(self.gas_plot, 'Gas Level')
        self.tabs.addTab(self.vibration_plot, 'Vibration')

        main_layout.addWidget(self.tabs)
        central_widget.setLayout(main_layout)

    def create_plots(self):
        """Initialize plot data."""
        self.temperature_data = []
        self.smoke_data = []
        self.humidity_data = []
        self.gas_data = []
        self.vibration_data = []
        self.times = []

    def update_data(self):
        """Update sensor data and refresh plots."""
        update_sensor_data()
        current_time = datetime.now()

        # Append new data and ensure the rolling window
        if len(self.times) >= ROLLING_WINDOW_SIZE:
            self.times.pop(0)
            self.temperature_data.pop(0)
            self.smoke_data.pop(0)
            self.humidity_data.pop(0)
            self.gas_data.pop(0)
            self.vibration_data.pop(0)

        self.times.append(current_time)
        self.temperature_data.append(sensor_data['temperature'])
        self.smoke_data.append(sensor_data['smoke_level'])
        self.humidity_data.append(sensor_data['humidity'])
        self.gas_data.append(sensor_data['gas_level'])
        self.vibration_data.append(sensor_data['vibration'])

        self.update_plots()
        self.check_for_threats()
        self.log_to_csv(current_time)

    def update_plots(self):
        """Update the plots with new data."""
        self.temperature_plot.update_plot(self.times, self.temperature_data)
        self.smoke_plot.update_plot(self.times, self.smoke_data)
        self.humidity_plot.update_plot(self.times, self.humidity_data)
        self.gas_plot.update_plot(self.times, self.gas_data)
        self.vibration_plot.update_plot(self.times, self.vibration_data)

    def check_for_threats(self):
        """Check sensor data against thresholds and update alerts."""
        threats = detect_threat()
        if threats:
            self.alert_label.setText("Alerts: Threat detected!")
            self.alert_text.setPlainText("\n".join(threats))
        else:
            self.alert_label.setText("Alerts: No issues detected")
            self.alert_text.clear()

    def log_to_csv(self, timestamp):
        """Log sensor data to CSV file."""
        self.csv_writer.writerow([
            timestamp.strftime('%Y-%m-%d %H:%M:%S'),
            sensor_data['temperature'],
            sensor_data['smoke_level'],
            sensor_data['humidity'],
            sensor_data['gas_level'],
            sensor_data['vibration']
        ])
        self.csv_file.flush()  # Ensure data is written to file

    def save_csv(self):
        """Save CSV file to user-specified location."""
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getSaveFileName(self, "Save CSV File", "", "CSV Files (*.csv)", options=options)
        if file_name:
            with open(file_name, 'w', newline='') as file:
                file.write('Timestamp,Temperature,Smoke Level,Humidity,Gas Level,Vibration\n')
                file.write(''.join(open(CSV_FILE).readlines()[1:]))  # Skip header and write data
        else:
            print("Save cancelled.")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    dashboard = Dashboard()
    dashboard.show()
    sys.exit(app.exec_())

