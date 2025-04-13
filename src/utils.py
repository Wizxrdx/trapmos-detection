import socket
import subprocess
import numpy as np
import cv2

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

def focus_on_circle(img, radius=100):
    h, w = img.shape[:2]

    black_image = np.zeros_like(img)

    mask = np.zeros((h, w), dtype=np.uint8)
    center = (w // 2, h // 2)

    cv2.circle(mask, center, radius, (255), thickness=-1)

    circular_focus = cv2.bitwise_and(img, img, mask=mask)

    return circular_focus

def snip_sides(img, left_crop=50, right_crop=50):
    h, w = img.shape[:2]
    cropped = img[:, left_crop:w - right_crop]
    return cropped

