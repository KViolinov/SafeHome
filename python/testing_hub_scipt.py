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
# Dictionary to store MAC address and Localtunnel link
device_links = {}
# Last sent device links to prevent resending the same data
last_sent_device_links = {}

# Function to check if a device is already in the list
def is_device_already_discovered(ip, mac):
    global discovered_devices
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

                # Start Localtunnel for the discovered ESP32
                localtunnel_url = start_localtunnel(ip)
                if localtunnel_url:
                    device_links[mac_address] = localtunnel_url  # Add to dictionary
                    print(f"Device Links Dictionary: {device_links}")  # Print the dictionary to the terminal

                    # Send device links to the Firebase API
                    send_device_links_to_firebase()  # Updated function call

# Function to start Localtunnel and get the public URL
def start_localtunnel(esp32_ip, esp32_port=80):
    localtunnel_command = f"lt --port {esp32_port} --subdomain {esp32_ip.replace('.', '-')}"  # Replace dots in IP for subdomain

    # Start Localtunnel as a subprocess
    localtunnel_process = subprocess.Popen(localtunnel_command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    # Wait a moment for Localtunnel to initialize
    time.sleep(5)

    # Function to get the public URL from Localtunnel's API
    def get_localtunnel_url():
        try:
            # The output of Localtunnel includes the public URL; read from the process
            while True:
                output = localtunnel_process.stdout.readline()
                if output == b"" and localtunnel_process.poll() is not None:
                    break
                if output:
                    # Decode the output and print it for debugging
                    output_str = output.decode('utf-8').strip()
                    print(f"Localtunnel Output: {output_str}")  # Debugging output
                    if "your" in output_str and "localtunnel" in output_str:
                        return output_str.split(' ')[-1].strip() + "/video"
        except Exception as e:
            print(f"Error retrieving Localtunnel URL: {e}")
        return None

    # Try to get the public URL
    return get_localtunnel_url()

# Function to send device links to the PHP API
def send_device_links_to_firebase():
    global device_links

    # Firebase Realtime Database URL and folder path (adjust with your Firebase project URL)
    firebase_url = "https://safehome-c4576-default-rtdb.firebaseio.com/device_links.json"

    try:
        print("Sending device links to Firebase...")

        # Sending a PATCH request to add the device_links dictionary to /device_links folder in Firebase
        response = requests.patch(firebase_url, json=device_links)

        print("Response from Firebase:", response.status_code, response.text)  # Debugging response

        if response.status_code == 200:
            print("Device links successfully sent to Firebase.")
        else:
            print(f"Failed to send device links: {response.status_code}")

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
