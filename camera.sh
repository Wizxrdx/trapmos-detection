  GNU nano 7.2                                                  camera.sh                                                            #!/bin/bash
# This script sets up the camera for a specific configuration using v4l2-ctl.
# It sets the camera to a specific resolution, frame rate, and other parameters.
# Make sure to run this script with sudo privileges.
# Usage: sudo ./camera.sh
# Set the camera to 640x480 resolution at 30 fps

# sudo v4l2-ctl -d /dev/video0 -c gain=250
# sleep 1
sudo v4l2-ctl -d /dev/video0 -c auto_exposure=1
sleep 1
sudo v4l2-ctl -d /dev/video0 -c exposure_time_absolute=18
sleep 1
sudo v4l2-ctl -d /dev/video0 -c focus_automatic_continuous=0
sleep 1
sudo v4l2-ctl -d /dev/video0 -c focus_absolute=200
sleep 1