#!/bin/bash

# Navigate to yolov7 build directory
cd yolov7/
cd build

# Copy the generated .wts file
cp ../../yolov7-tiny.wts .

# Build the project
cmake ..
make 

# Run the compiled YOLOv7 model
sudo ./yolov7 -s yolov7-tiny.wts yolov7-tiny.engine
