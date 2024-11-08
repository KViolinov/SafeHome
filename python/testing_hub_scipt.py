import socket
import subprocess
import time
import json
from threading import Thread
import tkinter as tk
from tkinter import scrolledtext
import requests

# List to store discovered devices
discovered_devices = []
# Dictionary to store MAC address and ngrok link
device_links = {}
# Last sent device links to prevent resending the same data
last_sent_device_links = {}

# Function to check if a device is already in the list
def is_device_already_discovered(ip, mac):
    for device in discovered_devices:
        if device['ip'] == ip and device['mac'] == mac:
            return True
    return False

# Function to listen for ESP32 packages (UDP-based)
def listen_for_esp32_packages(port=5005):
    global discovered_devices, device_links

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_socket.bind(("", port))

    print(f"Listening for packages on port {port}...")

    while True:
        message, address = server_socket.recvfrom(1024)
        ip, port = address

        if b"ESP32_PACKAGE" in message:  # Expected message from ESP32
            # Extract MAC address from the message (assuming it's sent after "ESP32_PACKAGE")
            mac_address = message.split(b"ESP32_PACKAGE")[1].strip().decode()

            # Check if this device is already discovered
            if not is_device_already_discovered(ip, mac_address):
                print(f"Received package from {ip}: {message}")
                discovered_devices.append({'ip': ip, 'port': port, 'mac': mac_address})

                # Send response back to the ESP32
                response_message = b"DISCOVERED"
                server_socket.sendto(response_message, (ip, port))
                print(f"Sent DISCOVERED message to {ip}:{port}, MAC: {mac_address}")

                # Start ngrok for the discovered ESP32
                ngrok_url = start_ngrok(ip)
                if ngrok_url:
                    # Check if MAC address is already in the dictionary and update the link if it exists
                    device_links[mac_address] = ngrok_url  # Update with the new link
                    print(f"Updated Device Links Dictionary: {device_links}")

                    # Send device links to Firebase API
                    send_device_links_to_firebase()

# Function to start ngrok and get the public URL
def start_ngrok(esp32_ip, esp32_port=80):
    ngrok_command = f"ngrok http {esp32_ip}:{esp32_port}"

    # Start ngrok as a subprocess
    ngrok_process = subprocess.Popen(ngrok_command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    # Wait a moment for ngrok to initialize
    time.sleep(5)

    # Function to get the public URL from ngrok's API
    def get_ngrok_url():
        try:
            # The output of ngrok includes the public URL; read from the process
            ngrok_api_command = "curl -s http://localhost:4040/api/tunnels"
            output = subprocess.check_output(ngrok_api_command, shell=True).decode('utf-8')
            tunnels_info = json.loads(output)
            if tunnels_info['tunnels']:
                return tunnels_info['tunnels'][0]['public_url'] + "/video"
        except Exception as e:
            print(f"Error retrieving ngrok URL: {e}")
        return None

    # Try to get the public URL
    return get_ngrok_url()

# Function to send device links to Firebase
def send_device_links_to_firebase():
    global device_links

    # Firebase Realtime Database URL and folder path (adjust with your Firebase project URL)
    firebase_url = "https://safehome-c4576-default-rtdb.firebaseio.com/device_links.json"

    try:
        print("Checking existing device links in Firebase...")

        # Fetch existing links from Firebase
        response = requests.get(firebase_url)
        existing_data = response.json() if response.status_code == 200 else {}

        if not existing_data:
            print("No existing data found. Adding new links to Firebase.")

        # Update existing entries or add new ones
        for mac, url in device_links.items():
            if mac in existing_data:
                print(f"Updating link for MAC: {mac} in Firebase.")
            else:
                print(f"Adding new link for MAC: {mac} in Firebase.")
            # Update Firebase with the new or updated link
            requests.patch(firebase_url, json={mac: url})

        print("Device links successfully sent to Firebase.")

    except Exception as e:
        print(f"Error sending to Firebase: {e}")

# Function to update GUI with the list of all devices and links
def update_gui():
    global device_links
    output_text.delete(1.0, tk.END)  # Clear previous text
    output_text.insert(tk.END, "Discovered Devices and Links:\n")
    for mac, url in device_links.items():
        output_text.insert(tk.END, f"MAC: {mac} - URL: {url}\n")
    output_text.see(tk.END)

# Main GUI application
def main_gui():
    global output_text
    window = tk.Tk()
    window.title("ESP32 Device Finder")
    window.geometry("500x300")

    # Scrolled text box for output display
    output_text = scrolledtext.ScrolledText(window, wrap=tk.WORD)
    output_text.pack(expand=True, fill='both')

    # Start listening for ESP32 packages in a separate thread
    listen_thread = Thread(target=listen_for_esp32_packages)
    listen_thread.start()

    window.mainloop()

# Run the GUI application
if __name__ == "__main__":
    main_gui()
