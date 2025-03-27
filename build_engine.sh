#!/bin/bash

# Define the Google Drive file ID and output filename
FILE_ID="1_OHbpk1unIN6wG-fcQRY0E97s0766a3u"
OUTPUT="last.pt"

# Download last.pt from Google Drive
gdown --id $FILE_ID -O $OUTPUT || wget --no-check-certificate "https://drive.google.com/uc?export=download&id=$FILE_ID" -O $OUTPUT

# Generate .wts file
python3 gen_wts.py -w last.pt -o yolov7-tiny.wts

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
