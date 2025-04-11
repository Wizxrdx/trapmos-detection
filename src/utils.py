import socket
import subprocess

# Get IP address
def get_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
    except:
        ip = "N/A"
    return ip

# Get WiFi SSID
def get_wifi():
    try:
        result = subprocess.check_output(["iwgetid", "-r"]).decode().strip()
        return result if result else "Disconnected"
    except:
        return "Disconnected"
