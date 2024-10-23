import socket
import time
from threading import Thread

# List to store discovered devices
discovered_devices = []


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
            print(f"Received package from {ip}: {message}")
            discovered_devices.append({'ip': ip, 'port': port})

            # Send response back to the ESP32
            response_message = b"DISCOVERED"
            server_socket.sendto(response_message, (ip, port))
            print(f"Sent DISCOVERED message to {ip}:{port}")


def print_discovered_devices(interval=10):
    global discovered_devices

    while True:
        time.sleep(interval)
        if discovered_devices:
            print("Discovered Devices:")
            for device in discovered_devices:
                print(f"IP: {device['ip']}, Port: {device['port']}")
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
