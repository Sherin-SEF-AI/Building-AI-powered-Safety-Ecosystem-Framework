import sys
import random
import threading
import time
from datetime import datetime
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtWidgets import QLabel, QPushButton, QTextEdit, QVBoxLayout, QHBoxLayout, QWidget, QMainWindow, QTabWidget
from PyQt5.QtGui import QFont
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.dates as mdates

# Simulated sensor data
sensor_data = {
    "temperature": 30,
    "smoke_level": 2,
    "humidity": 50,
    "gas_level": 1,
    "vibration": 0
}

# Thresholds for threat detection
THRESHOLDS = {
    "temperature": 50,
    "smoke_level": 5,
    "humidity": 80,
    "gas_level": 3,
    "vibration": 5
}

ROLLING_WINDOW_SIZE = 60  # Number of data points to keep in view (adjust as needed)

def update_sensor_data():
    """Simulate sensor data update."""
    sensor_data['temperature'] = random.randint(20, 60)
    sensor_data['smoke_level'] = random.randint(0, 10)
    sensor_data['humidity'] = random.randint(30, 90)
    sensor_data['gas_level'] = random.randint(0, 5)
    sensor_data['vibration'] = random.randint(0, 10)

def detect_threat():
    """Simple rule-based threat detection."""
    threats = []
    for key, threshold in THRESHOLDS.items():
        if sensor_data[key] > threshold:
            threats.append(f"High {key.replace('_', ' ')} detected: {sensor_data[key]}")
    return threats

class SensorPlot(QWidget):
    def __init__(self, title, xlabel, ylabel):
        super().__init__()
        self.figure = Figure()
        self.canvas = FigureCanvas(self.figure)
        self.plot = self.figure.add_subplot(111)
        self.plot.set_title(title)
        self.plot.set_xlabel(xlabel)
        self.plot.set_ylabel(ylabel)

        layout = QVBoxLayout()
        layout.addWidget(self.canvas)
        self.setLayout(layout)
        
        self.times = []
        self.data = []

    def update_plot(self, times, data):
        self.plot.clear()
        self.plot.plot(times, data, marker='o')
        self.plot.set_title(self.plot.get_title())
        self.plot.set_xlabel(self.plot.get_xlabel())
        self.plot.set_ylabel(self.plot.get_ylabel())

        # Format the x-axis to handle time data
        self.plot.xaxis.set_major_locator(mdates.SecondLocator(interval=10))
        self.plot.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))
        self.plot.figure.autofmt_xdate()

        # Set the x-axis limit to keep the most recent data visible
        if len(times) > ROLLING_WINDOW_SIZE:
            self.plot.set_xlim([times[-ROLLING_WINDOW_SIZE], times[-1]])

        self.canvas.draw()

class Dashboard(QMainWindow):
    update_signal = QtCore.pyqtSignal()

    def __init__(self):
        super().__init__()
        self.initUI()
        self.create_plots()
        self.update_signal.connect(self.update_data)

    def initUI(self):
        self.setWindowTitle('Industrial Safety Monitoring Dashboard')
        self.setGeometry(100, 100, 1200, 800)  # Adjusted size for better layout

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout()

        title = QLabel("Industrial Safety Monitoring Dashboard", self)
        title.setFont(QFont('Arial', 24, QFont.Bold))
        main_layout.addWidget(title)

        # Create and add buttons
        button_layout = QHBoxLayout()
        update_button = QPushButton("Update Sensor Data", self)
        update_button.clicked.connect(self.update_data)
        button_layout.addWidget(update_button)

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

def simulate_sensor_updates(app):
    """Simulate real-time sensor data updates."""
    while True:
        time.sleep(1)  # Reduce delay between updates
        app.update_signal.emit()

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    dashboard = Dashboard()
    dashboard.show()

    # Start a thread to simulate sensor data updates
    sensor_thread = threading.Thread(target=simulate_sensor_updates, args=(dashboard,))
    sensor_thread.start()
    
    sys.exit(app.exec_())

