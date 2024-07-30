import qrcode
# pip install qrcode[pil] - for the lib

def generate_wifi_qr(ssid, password):
    # WiFi QR Code format: WIFI:S:<SSID>;T:WPA;P:<PASSWORD>;;
    qr_data = f"WIFI:S:{ssid};T:WPA;P:{password};;"
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(qr_data)
    qr.make(fit=True)
    img = qr.make_image(fill='black', back_color='white')
    img.save('wifi_qr_code.png')

ssid = input("Enter SSID: ")
password = input("Enter Password: ")

generate_wifi_qr(ssid, password)
print("QR code generated and saved as wifi_qr_code.png")
