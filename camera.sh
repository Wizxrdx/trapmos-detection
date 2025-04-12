#!/bin/bash
# This script sets up the camera for a specific configuration using v4l2-ctl.
# It sets the camera to a specific resolution, frame rate, and other parameters.
# Make sure to run this script with sudo privileges.
# Usage: sudo ./camera.sh
# Set the camera to 640x480 resolution at 30 fps

v4l2-ctl -d /dev/video0 -c auto_exposure=1
v4l2-ctl -d /dev/video0 -c exposure_time_absolute=18
v4l2-ctl -d /dev/video0 -c focus_automatic_continuous=0
v4l2-ctl -d /dev/video0 -c exposure_dynamic_framerate=0
v4l2-ctl -d /dev/video0 -c focus_absolute=200
v4l2-ctl -d /dev/video0 -c focus_absolute=200