import argparse
from datetime import datetime
import time
import os

SLEEP_TIME = 60 * 0.2  # 29 minutes
RUN_TIME = 60 * 0.5  # 1 minute

DEVICE_ID = "00000"
DEVICE_NAME = f"TRAPMOS_{DEVICE_ID}"
TIME_STARTED = int(time.time()) - 1640000000 + RUN_TIME

def main():
    from src.detection import run_detection
    from src.oled import TrapmosDisplay

    TrapmosDisplay()

    parser = argparse.ArgumentParser()
    parser.add_argument("-dev", action="store_true", help="Run in development mode")
    args = parser.parse_args()

    print("Running in development mode..." if args.dev else "Running in normal mode...")
    run_detection(args.dev)

if __name__ == "__main__":
    os.system('sudo ntpdate time.google.com')

    while not os.path.exists('/dev/video0'):
        print("Waiting for camera...")
        time.sleep(1)
    print("Camera found!")

    main()
