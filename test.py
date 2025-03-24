import cv2
from yoloDet import YoloTRT
import time

# Initialize YOLO model
model = YoloTRT(
    library="yolov7/build/libmyplugins.so",
    engine="yolov7/build/yolov7-tiny.engine",
    conf=0.5,
    yolo_ver="v7"
)

# Path to the input image
image_path = "yolov7/images/mosquito.jpg"  # Replace with your image path

# Read the image
frame = cv2.imread(image_path)
if frame is None:
    print(f"Failed to load image: {image_path}")
    exit()


test_time = []
for x in range(10):
    start_time = time.time()

    # Run inference
    detections, _ = model.Inference(frame)
    
    detections, t = model.Inference(frame)

    print(f"Number of detections: {len(detections)}")

    if detections:
        for detection in detections:
            if 'class' in detection:
                mosquito_classes = ['Aedes Mosquito', 'Aedes Mosquito']
                if detection['class'] in mosquito_classes:

                    if 'bbox' in detection:
                        x, y, w, h = detection['bbox']
                    elif 'box' in detection:
                        x, y, w, h = detection['box']
                    else:
                        continue

                    scale_x = frame.shape[1] / frame.shape[1]
                    scale_y = frame.shape[0] / frame.shape[0]

                    x1 = max(0, int(x * scale_x))
                    y1 = max(0, int(y * scale_y))
                    x2 = min(frame.shape[1], int((x + w) * scale_x))
                    y2 = min(frame.shape[0], int((y + h) * scale_y))

                    cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 3)
                    cv2.putText(frame, f"{detection['class']}",
                                (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX,
                                0.8, (0, 255, 0), 2)
                    
                    image_filename = f"detection_test.jpg"
                    cv2.imwrite(image_filename, frame)