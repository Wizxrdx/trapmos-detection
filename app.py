import sys
import cv2
import imutils
from datetime import datetime
from src.yoloDet import YoloTRT
from src.location import LocationManager

# Initialize YOLO model
model = YoloTRT(
    library="yolov7/build/libmyplugins.so",
    engine="yolov7/build/yolov7-tiny.engine",
    conf=0.5,
    yolo_ver="v7"
)

# Initialize location manager
location_manager = LocationManager()

# Open the Logitech C920 HD Pro camera
cap = cv2.VideoCapture(0, cv2.CAP_V4L2)  # Use V4L2 backend for video capture
cap.set(cv2.CAP_PROP_FPS, 60)  # Set camera to 60 FPS (if supported)
frame_counter = 0
skip_frames = 1  # Process every frame to aim for 60 FPS

while True:
    ret, frame = cap.read()
    if not ret:
        print("Failed to grab frame")
        break
    
    small_frame = imutils.resize(frame, width=640)

    print(small_frame.shape)

    # Process every frame for 60 FPS target
    if frame_counter % skip_frames == 0:
        detections, t = model.Inference(small_frame)

        # Print number of detections
        print(f"Number of detections: {len(detections)}")

        # Calculate FPS
        fps = round(1 / t, 2)

        # Get current date and time
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Overlay FPS and Date/Time on frame
        cv2.putText(frame, f"FPS: {fps}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        cv2.putText(frame, f"Time: {current_time}", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

        # Check if any mosquito was detected
        if detections:
            for detection in detections:
                # print(detection)  # Debugging: print the detection object to inspect structure

                if 'class' in detection:
                    mosquito_classes = ['Culex', 'Aedes albopictus', 'Aedes aegypti']
                    if detection['class'] in mosquito_classes:
                        lat, lon = location_manager.current_location()

                    # Assuming 'bbox' or 'box' contains the coordinates for the bounding box
                    if 'bbox' in detection:
                        x, y, w, h = detection['bbox']
                    elif 'box' in detection:  # If it's stored under a different key
                        x, y, w, h = detection['box']
                    else:
                        continue  # If neither 'bbox' nor 'box' exists, skip

                    # Scale the coordinates to match the resized frame (320x240)
                    scale_x = frame.shape[1] / small_frame.shape[1]  # Scaling factor for width
                    scale_y = frame.shape[0] / small_frame.shape[0]  # Scaling factor for height

                    # Adjust bounding box coordinates based on the scaling factors
                    x1 = int(x * scale_x)
                    y1 = int(y * scale_y)
                    x2 = int((x + w) * scale_x)
                    y2 = int((y + h) * scale_y)

                    # Ensure bounding box is within frame bounds
                    x1 = max(0, x1)
                    y1 = max(0, y1)
                    x2 = min(frame.shape[1], x2)
                    y2 = min(frame.shape[0], y2)

                    # Draw the bounding box on the frame
                    cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 3)  # Green bounding box

                    # Optionally add label with confidence score
                    cv2.putText(frame, f"{detection['class']}",
                                (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX,
                                0.8, (0, 255, 0), 2)  # Text above the box

    frame_counter += 1

    # Display the output frame in a smaller window
    cv2.namedWindow("Output", cv2.WINDOW_NORMAL)
    cv2.resizeWindow("Output", 320, 240)  # Resize to 320x240 for smaller display
    cv2.imshow("Output", frame)

    # Exit on 'q' key
    if cv2.waitKey(1) == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
location_manager.close()