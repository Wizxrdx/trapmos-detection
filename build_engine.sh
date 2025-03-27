#!/bin/bash

python3 gen_wts.py -w last.pt -o yolov7-tiny.wts

cd yolov7/
cd build
cp ../../yolov7-tiny.wts .
cmake ..
make 

sudo ./yolov7 -s yolov7-tiny.wts  yolov7-tiny.engine t