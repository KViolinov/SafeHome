# import socket
# import time
# from threading import Thread
#
# # List to store discovered devices
# discovered_devices = []
#
#
# # Function to check if a device is already in the list
# def is_device_already_discovered(ip, mac):
#     global discovered_devices
#     for device in discovered_devices:
#         if device['ip'] == ip and device['mac'] == mac:
#             return True
#     return False
#
#
# # Function to listen for ESP32 packages (UDP-based)
# def listen_for_esp32_packages(port=5005):
#     global discovered_devices
#
#     server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
#     server_socket.bind(("", port))
#
#     print(f"Listening for packages on port {port}...")
#
#     while True:
#         message, address = server_socket.recvfrom(1024)
#         ip, port = address
#
#         if b"ESP32_PACKAGE" in message:  # Expected message from ESP32
#             # Extract MAC address from the message (assuming it's sent after "ESP32_PACKAGE")
#             mac_address = message.split(b"ESP32_PACKAGE")[1].strip().decode()
#
#             # Check if this device is already discovered
#             if not is_device_already_discovered(ip, mac_address):
#                 print(f"Received package from {ip}: {message}")
#                 discovered_devices.append({'ip': ip, 'port': port, 'mac': mac_address})
#
#                 # Send response back to the ESP32
#                 response_message = b"DISCOVERED"
#                 server_socket.sendto(response_message, (ip, port))
#                 print(f"Sent DISCOVERED message to {ip}:{port}, MAC: {mac_address}")
#
#
# def print_discovered_devices(interval=10):
#     global discovered_devices
#
#     while True:
#         time.sleep(interval)
#         if discovered_devices:
#             print("Discovered Devices:")
#             for device in discovered_devices:
#                 print(f"IP: {device['ip']}, Port: {device['port']}, MAC: {device['mac']}")
#         else:
#             print("No devices discovered yet.")
#
#
# # Main function
# def main():
#     # Start listening for ESP32 packages
#     listen_thread = Thread(target=listen_for_esp32_packages)
#     listen_thread.start()
#
#     # Start the device printing thread
#     print_thread = Thread(target=print_discovered_devices)
#     print_thread.start()
#
#     # Keep the main thread alive
#     try:
#         while True:
#             time.sleep(1)
#     except KeyboardInterrupt:
#         print("Program terminated by user.")
#
#
# if __name__ == "__main__":
#     main()


# import subprocess
# import re
# import time
# import json
#
# # ESP32 IP and port
# esp32_ip = "192.168.43.245"
# esp32_port = "80"
#
# # Command to start ngrok
# ngrok_command = f"ngrok http {esp32_ip}:{esp32_port}"
#
# # Start ngrok as a subprocess
# ngrok_process = subprocess.Popen(ngrok_command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
#
# # Wait a moment for ngrok to initialize
# time.sleep(5)
#
# # Function to get the public URL from ngrok's API
# def get_ngrok_url():
#     try:
#         ngrok_api_command = "curl -s http://localhost:4040/api/tunnels"
#         output = subprocess.check_output(ngrok_api_command, shell=True).decode('utf-8')
#         # Parse the JSON output
#         tunnels_info = json.loads(output)
#         if tunnels_info['tunnels']:
#             # Get the public URL of the first tunnel
#             return tunnels_info['tunnels'][0]['public_url']
#     except Exception as e:
#         print(f"Error retrieving ngrok URL: {e}")
#     return None
#
# # Try to get the public URL
# public_url = get_ngrok_url()
# if public_url:
#     print(f"Public URL for ESP32: {public_url}")
# else:
#     print("Failed to retrieve ngrok URL. Please check if ngrok is running properly.")
#
# # Keep the script running to keep the ngrok process alive
# try:
#     while True:
#         time.sleep(5)
# except KeyboardInterrupt:
#     print("Shutting down ngrok...")
#     ngrok_process.terminate()
#


import socket
import subprocess
import re
import time
import json
from threading import Thread

# List to store discovered devices
discovered_devices = []


# Function to check if a device is already in the list
def is_device_already_discovered(ip, mac):
    global discovered_devices
    for device in discovered_devices:
        if device['ip'] == ip and device['mac'] == mac:
            return True
    return False


# Function to listen for ESP32 packages (UDP-based)
def listen_for_esp32_packages(port=5005):
    global discovered_devices

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
                start_ngrok(ip)


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
            ngrok_api_command = "curl -s http://localhost:4040/api/tunnels"
            output = subprocess.check_output(ngrok_api_command, shell=True).decode('utf-8')
            # Parse the JSON output
            tunnels_info = json.loads(output)
            if tunnels_info['tunnels']:
                # Get the public URL of the first tunnel
                return tunnels_info['tunnels'][0]['public_url']
        except Exception as e:
            print(f"Error retrieving ngrok URL: {e}")
        return None

    # Try to get the public URL
    public_url = get_ngrok_url()
    if public_url:
        public_url += "/video"  # Append "/video" to the end of the URL
        print(f"Public URL for ESP32: {public_url}")
    else:
        print("Failed to retrieve ngrok URL. Please check if ngrok is running properly.")


# Function to print discovered devices
def print_discovered_devices(interval=10):
    global discovered_devices

    while True:
        time.sleep(interval)
        if discovered_devices:
            print("Discovered Devices:")
            for device in discovered_devices:
                print(f"IP: {device['ip']}, Port: {device['port']}, MAC: {device['mac']}")
        else:
            print("No devices discovered yet.")


# Main function
def main():
    # Start listening for ESP32 packages
    listen_thread = Thread(target=listen_for_esp32_packages)
    listen_thread.start()

    # Start the device printing thread
    print_thread = Thread(target=print_discovered_devices)
    print_thread.start()

    # Keep the main thread alive
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Program terminated by user.")


if __name__ == "__main__":
    main()

