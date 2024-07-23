import time
from datetime import datetime
import tkinter as tk
from tkinter import messagebox
import random
import threading
import folium
from tkhtmlview import HTMLLabel

# Mock data
user_data = {
    "user_id": 1,
    "name": "John Doe",
    "location": "New Delhi",
    "emergency_contact": "+91-9876543210",
    "coordinates": [28.6139, 77.2090]  # Latitude and Longitude for New Delhi
}

# Function to detect threats
def detect_threat(sensor_data):
    """
    Simulate threat detection based on sensor data.
    """
    if sensor_data['temperature'] > 50 or sensor_data['smoke_level'] > 5:
        return "Fire detected"
    elif sensor_data['motion_detected']:
        return "Intruder detected"
    return None

# Function to send emergency alert
def send_emergency_alert(user, threat_type):
    """
    Simulate sending an emergency alert.
    """
    alert_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    messagebox.showwarning("Emergency Alert", f"User: {user['name']}\n"
                                              f"Location: {user['location']}\n"
                                              f"Threat: {threat_type}\n"
                                              f"Time: {alert_time}\n"
                                              f"Contacting Emergency Contact: {user['emergency_contact']}\n")
    log_event(f"Emergency Alert: {threat_type} for {user['name']} at {user['location']} at {alert_time}")
    update_responder_screen(f"Emergency Alert: {threat_type} for {user['name']} at {user['location']} at {alert_time}")
    show_map_on_responder_screen(user['coordinates'])

# Function to send personalized notification
def send_personalized_notification(user, message):
    """
    Simulate sending a personalized notification to the user.
    """
    notification_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"Notification for {user['name']}:\n"
          f"Message: {message}\n"
          f"Time: {notification_time}\n")
    log_event(f"Notification: {message}")
    update_responder_screen(f"Notification: {message}")

# Function to handle SOS button click
def handle_sos_button():
    send_emergency_alert(user_data, "SOS Button Pressed")

# Function to update sensor data
def update_sensor_data():
    sensor_data['temperature'] = random.randint(20, 60)
    sensor_data['smoke_level'] = random.randint(0, 10)
    sensor_data['motion_detected'] = random.choice([True, False])

# Function to log events
def log_event(event):
    log_text.insert(tk.END, f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - {event}\n")
    log_text.see(tk.END)

# Function to update responder screen with logs
def update_responder_screen(event):
    responder_log_text.insert(tk.END, f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - {event}\n")
    responder_log_text.see(tk.END)

# Function to update GUI with sensor data
def update_gui():
    temp_label.config(text=f"Temperature: {sensor_data['temperature']}°C")
    smoke_label.config(text=f"Smoke Level: {sensor_data['smoke_level']}/10")
    motion_label.config(text=f"Motion Detected: {'Yes' if sensor_data['motion_detected'] else 'No'}")
    root.after(1000, update_gui)

# Function to show map on responder screen
def show_map_on_responder_screen(coordinates):
    # Create map using folium
    map_ = folium.Map(location=coordinates, zoom_start=12)
    folium.Marker(coordinates, popup='User Location').add_to(map_)
    # Save map to HTML
    map_path = "responder_map.html"
    map_.save(map_path)
    # Display map in GUI
    map_view = HTMLLabel(responder_map_frame, html=open(map_path).read())
    map_view.pack(fill="both", expand=True)

# Function to simulate sensor monitoring and threat detection
def monitor_sensors():
    while True:
        update_sensor_data()
        threat = detect_threat(sensor_data)
        
        if threat:
            send_emergency_alert(user_data, threat)
            send_personalized_notification(user_data, "Please take necessary actions immediately!")
        else:
            send_personalized_notification(user_data, "All systems normal.")
        
        time.sleep(10)  # Wait for 10 seconds before checking again

# Simulate sensor data
sensor_data = {
    "temperature": 30,  # Temperature in Celsius
    "smoke_level": 2,   # Smoke level on a scale from 0 to 10
    "motion_detected": False
}

# GUI setup
root = tk.Tk()
root.title("Safety Ecosystem Framework (SEF)")

frame = tk.Frame(root, padx=10, pady=10)
frame.pack(pady=20)

# Title Label
label = tk.Label(frame, text="SEF Monitoring System", font=("Arial", 20, "bold"))
label.pack(pady=10)

# Sensor Data Display
temp_label = tk.Label(frame, text="Temperature: --°C", font=("Arial", 14))
temp_label.pack(pady=5)

smoke_label = tk.Label(frame, text="Smoke Level: --/10", font=("Arial", 14))
smoke_label.pack(pady=5)

motion_label = tk.Label(frame, text="Motion Detected: --", font=("Arial", 14))
motion_label.pack(pady=5)

# SOS Button
sos_button = tk.Button(frame, text="Panic/SOS", font=("Arial", 14), bg="red", fg="white", command=handle_sos_button)
sos_button.pack(pady=20)

# Event Log Display
log_label = tk.Label(frame, text="Event Log", font=("Arial", 16))
log_label.pack(pady=10)

log_text = tk.Text(frame, height=10, width=50, font=("Arial", 12))
log_text.pack(pady=10)

# Map Display
map_label = tk.Label(frame, text="Location Map", font=("Arial", 16))
map_label.pack(pady=10)

map_frame = tk.Frame(frame, width=600, height=400)
map_frame.pack(pady=10)

# Create map using folium
map_ = folium.Map(location=user_data['coordinates'], zoom_start=12)
folium.Marker(user_data['coordinates'], popup='User Location').add_to(map_)

# Save map to HTML
map_path = "map.html"
map_.save(map_path)

# Display map in GUI
map_view = HTMLLabel(map_frame, html=open(map_path).read())
map_view.pack(fill="both", expand=True)

# Responder Screen
responder_screen = tk.Toplevel(root)
responder_screen.title("Emergency Responder Screen")

responder_frame = tk.Frame(responder_screen, padx=10, pady=10)
responder_frame.pack(pady=20)

responder_label = tk.Label(responder_frame, text="Responder Log", font=("Arial", 16))
responder_label.pack(pady=10)

responder_log_text = tk.Text(responder_frame, height=20, width=60, font=("Arial", 12))
responder_log_text.pack(pady=10)

responder_map_frame = tk.Frame(responder_frame, width=600, height=400)
responder_map_frame.pack(pady=10)

# Start monitoring in a separate thread
monitoring_thread = threading.Thread(target=monitor_sensors, daemon=True)
monitoring_thread.start()

# Update GUI with sensor data
update_gui()

root.mainloop()

