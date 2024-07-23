import sys
import random
import requests
import pandas as pd
import folium
import matplotlib.pyplot as plt
from PyQt5.QtWidgets import (QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget, QPushButton, QFormLayout, QLineEdit, QFileDialog, QDialog, QTextEdit, QComboBox)
from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QPixmap
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

# Constants
API_KEY = 'h86qpRiVNOmhLe3Nk4sQ4kcLIDI0Rkde'  # Replace with your actual API key
LOCATION = '42.3478,-71.0466'  # Replace with your location coordinates

# Sample sensor data functions
def read_temperature():
    return round(random.uniform(15.0, 30.0), 2)

def read_humidity():
    return round(random.uniform(30.0, 80.0), 2)

def read_air_quality():
    return round(random.uniform(0, 100), 2)  # AQI (Air Quality Index)

def read_co2_level():
    return round(random.uniform(300, 1000), 2)  # CO2 in ppm

def read_light_intensity():
    return round(random.uniform(100, 1000), 2)  # Light intensity in lux

def read_noise_level():
    return round(random.uniform(30, 100), 2)  # Noise level in dB

def fetch_weather_data():
    url = f'https://api.tomorrow.io/v4/weather/forecast?location={LOCATION}&apikey={API_KEY}'
    try:
        response = requests.get(url)
        response.raise_for_status()  # Check for HTTP errors
        data = response.json()
        
        # Parse relevant weather data
        temperature = data['data']['timelines'][0]['intervals'][0]['values']['temperature']
        weather_description = data['data']['timelines'][0]['intervals'][0]['values']['weatherCode']
        return temperature, weather_description
    except requests.RequestException as e:
        return "N/A", f"Error: {str(e)}"
    except (KeyError, IndexError) as e:
        return "N/A", f"Error: Unexpected response format"

# Define thresholds for alerts
TEMPERATURE_THRESHOLD_HIGH = 25.0
TEMPERATURE_THRESHOLD_LOW = 18.0
HUMIDITY_THRESHOLD_HIGH = 70.0
HUMIDITY_THRESHOLD_LOW = 40.0
AIR_QUALITY_THRESHOLD = 50.0
CO2_THRESHOLD = 800.0
LIGHT_THRESHOLD_LOW = 200.0
NOISE_THRESHOLD_HIGH = 80.0

def check_temperature(temp):
    if temp > TEMPERATURE_THRESHOLD_HIGH:
        return "Alert: Temperature is too high!"
    elif temp < TEMPERATURE_THRESHOLD_LOW:
        return "Alert: Temperature is too low!"
    return "Temperature is normal."

def check_humidity(humidity):
    if humidity > HUMIDITY_THRESHOLD_HIGH:
        return "Alert: Humidity is too high!"
    elif humidity < HUMIDITY_THRESHOLD_LOW:
        return "Alert: Humidity is too low!"
    return "Humidity is normal."

def check_air_quality(aqi):
    if aqi > AIR_QUALITY_THRESHOLD:
        return "Alert: Air quality is poor!"
    return "Air quality is good."

def check_co2_level(co2):
    if co2 > CO2_THRESHOLD:
        return "Alert: CO2 level is too high!"
    return "CO2 level is normal."

def check_light_intensity(light):
    if light < LIGHT_THRESHOLD_LOW:
        return "Alert: Light intensity is too low!"
    return "Light intensity is normal."

def check_noise_level(noise):
    if noise > NOISE_THRESHOLD_HIGH:
        return "Alert: Noise level is too high!"
    return "Noise level is normal."

class FeedbackDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Feedback Form")
        self.setGeometry(200, 200, 400, 300)

        layout = QVBoxLayout()

        self.feedback_text = QTextEdit()
        self.feedback_text.setPlaceholderText("Enter your feedback or report issues here...")
        layout.addWidget(self.feedback_text)

        submit_button = QPushButton("Submit")
        submit_button.clicked.connect(self.submit_feedback)
        layout.addWidget(submit_button)

        self.setLayout(layout)

    def submit_feedback(self):
        feedback = self.feedback_text.toPlainText()
        if feedback:
            # Handle feedback here (e.g., save to file or send via email)
            print("Feedback Submitted:", feedback)
            self.accept()
        else:
            print("Feedback is empty.")

class EnvironmentalMonitoringApp(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Environmental Monitoring System")
        self.setGeometry(100, 100, 800, 600)

        self.data = {
            'Temperature': [],
            'Humidity': [],
            'Air Quality': [],
            'CO2 Level': [],
            'Light Intensity': [],
            'Noise Level': []
        }
        
        self.initUI()
        
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_data)
        self.timer.start(60000)  # Update every 60 seconds

    def initUI(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout()

        # Sensor data labels
        self.temp_label = QLabel("Temperature: -- °C")
        self.humidity_label = QLabel("Humidity: -- %")
        self.air_quality_label = QLabel("Air Quality Index: --")
        self.co2_label = QLabel("CO2 Level: -- ppm")
        self.light_label = QLabel("Light Intensity: -- lux")
        self.noise_label = QLabel("Noise Level: -- dB")
        self.weather_label = QLabel("Weather: -- °C, --")

        layout.addWidget(self.temp_label)
        layout.addWidget(self.humidity_label)
        layout.addWidget(self.air_quality_label)
        layout.addWidget(self.co2_label)
        layout.addWidget(self.light_label)
        layout.addWidget(self.noise_label)
        layout.addWidget(self.weather_label)

        # Refresh button
        refresh_button = QPushButton("Refresh Data")
        refresh_button.clicked.connect(self.update_data)
        layout.addWidget(refresh_button)

        # Configuration for thresholds
        config_layout = QFormLayout()
        self.temp_high_input = QLineEdit(str(TEMPERATURE_THRESHOLD_HIGH))
        self.temp_low_input = QLineEdit(str(TEMPERATURE_THRESHOLD_LOW))
        self.humidity_high_input = QLineEdit(str(HUMIDITY_THRESHOLD_HIGH))
        self.humidity_low_input = QLineEdit(str(HUMIDITY_THRESHOLD_LOW))
        self.air_quality_input = QLineEdit(str(AIR_QUALITY_THRESHOLD))
        self.co2_input = QLineEdit(str(CO2_THRESHOLD))
        self.light_input = QLineEdit(str(LIGHT_THRESHOLD_LOW))
        self.noise_input = QLineEdit(str(NOISE_THRESHOLD_HIGH))

        config_layout.addRow("Temp High Threshold:", self.temp_high_input)
        config_layout.addRow("Temp Low Threshold:", self.temp_low_input)
        config_layout.addRow("Humidity High Threshold:", self.humidity_high_input)
        config_layout.addRow("Humidity Low Threshold:", self.humidity_low_input)
        config_layout.addRow("Air Quality Threshold:", self.air_quality_input)
        config_layout.addRow("CO2 Threshold:", self.co2_input)
        config_layout.addRow("Light Intensity Threshold:", self.light_input)
        config_layout.addRow("Noise Threshold:", self.noise_input)

        layout.addLayout(config_layout)

        # Add graph canvas
        self.figure = plt.figure()
        self.canvas = FigureCanvas(self.figure)
        layout.addWidget(self.canvas)

        # Add Export button
        export_button = QPushButton("Export Data to CSV")
        export_button.clicked.connect(self.export_data)
        layout.addWidget(export_button)

        # Add Interactive Map button
        map_button = QPushButton("Show Interactive Map")
        map_button.clicked.connect(self.show_interactive_map)
        layout.addWidget(map_button)

        # Add Data Import button
        import_button = QPushButton("Import Data from CSV")
        import_button.clicked.connect(self.import_data)
        layout.addWidget(import_button)

        # Add Filter options
        self.filter_combo = QComboBox()
        self.filter_combo.addItems(["No Filter", "Last 24 Hours", "Last Week"])
        self.filter_combo.currentIndexChanged.connect(self.update_data)
        layout.addWidget(self.filter_combo)

        # Add Feedback button
        feedback_button = QPushButton("Submit Feedback")
        feedback_button.clicked.connect(self.open_feedback_dialog)
        layout.addWidget(feedback_button)

        central_widget.setLayout(layout)

    def update_data(self):
        temperature = read_temperature()
        humidity = read_humidity()
        air_quality = read_air_quality()
        co2_level = read_co2_level()
        light_intensity = read_light_intensity()
        noise_level = read_noise_level()
        
        weather_temp, weather_description = fetch_weather_data()

        # Update labels with sensor data
        self.temp_label.setText(f"Temperature: {temperature} °C - {check_temperature(temperature)}")
        self.humidity_label.setText(f"Humidity: {humidity} % - {check_humidity(humidity)}")
        self.air_quality_label.setText(f"Air Quality Index: {air_quality} - {check_air_quality(air_quality)}")
        self.co2_label.setText(f"CO2 Level: {co2_level} ppm - {check_co2_level(co2_level)}")
        self.light_label.setText(f"Light Intensity: {light_intensity} lux - {check_light_intensity(light_intensity)}")
        self.noise_label.setText(f"Noise Level: {noise_level} dB - {check_noise_level(noise_level)}")
        self.weather_label.setText(f"Weather: {weather_temp} °C, {weather_description}")

        # Store data
        self.data['Temperature'].append(temperature)
        self.data['Humidity'].append(humidity)
        self.data['Air Quality'].append(air_quality)
        self.data['CO2 Level'].append(co2_level)
        self.data['Light Intensity'].append(light_intensity)
        self.data['Noise Level'].append(noise_level)

        self.plot_data()

    def plot_data(self):
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        for key, values in self.data.items():
            ax.plot(values, label=key)
        ax.set_title("Environmental Sensor Data")
        ax.set_xlabel("Time")
        ax.set_ylabel("Value")
        ax.legend()
        self.canvas.draw()

    def export_data(self):
        filename, _ = QFileDialog.getSaveFileName(self, "Save Data", "", "CSV Files (*.csv)")
        if filename:
            df = pd.DataFrame(self.data)
            df.to_csv(filename, index=False)

    def import_data(self):
        filename, _ = QFileDialog.getOpenFileName(self, "Open Data", "", "CSV Files (*.csv)")
        if filename:
            df = pd.read_csv(filename)
            for column in df.columns:
                self.data[column] = df[column].tolist()
            self.plot_data()

    def show_interactive_map(self):
        # Create a map centered around the location
        map = folium.Map(location=[42.3478, -71.0466], zoom_start=13)
        
        # Add a marker for the current location
        folium.Marker(
            location=[42.3478, -71.0466],
            popup='Current Location',
            icon=folium.Icon(color='blue')
        ).add_to(map)

        # Add additional markers for environmental hotspots
        for _ in range(5):  # Example: Adding 5 random hotspots
            folium.Marker(
                location=[42.3478 + random.uniform(-0.01, 0.01), -71.0466 + random.uniform(-0.01, 0.01)],
                popup='Hotspot Example',
                icon=folium.Icon(color='red')
            ).add_to(map)

        # Save map to HTML file
        map_file = 'interactive_map.html'
        map.save(map_file)

        # Open the map in the default web browser
        self.open_url(map_file)

    def open_url(self, url):
        import webbrowser
        webbrowser.open(url)

    def open_feedback_dialog(self):
        dialog = FeedbackDialog()
        dialog.exec_()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_win = EnvironmentalMonitoringApp()
    main_win.show()
    sys.exit(app.exec_())

