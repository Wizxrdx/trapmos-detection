import cv2
import time
from datetime import datetime
from src.yoloDet import YoloONNX
from src.location import LocationManager
from src.firebase import DetectionUploader
from src.oled import TrapmosDisplay
import numpy as np


def sharpen_image(image):
    kernel = np.array([[0, -2, 0],
                       [-2, 9, -2],
                       [0, -2, 0]])
    return cv2.filter2D(image, -1, kernel)

def scale_coords(coords, orig_shape, small_shape):
    x1, y1, x2, y2 = coords
    scale_x = orig_shape[1] / small_shape[1]
    scale_y = orig_shape[0] / small_shape[0]
    return int(x1 * scale_x), int(y1 * scale_y), int(x2 * scale_x), int(y2 * scale_y)

def run_detection(dev_mode, oled=None):
    # Initialize YOLO model
    model = YoloONNX("trapmos.onnx", conf_thres=0.25)

    # Initialize location manager
    print("Initializing location manager...")
    location_manager = LocationManager()

    # Initialize Database manager
    print("Initializing Detection Uploader...")
    database_manager = DetectionUploader()

    print("Initializing Trapmos Display...")
    TrapmosDisplay().show_detected("Initializing Trapmos Display...")

    # Keep checking until a camera is connected
    while True:
        cap = cv2.VideoCapture(0, cv2.CAP_V4L2)
        if cap.isOpened():
            print("Camera connected!")
            time.sleep(5)
            break
        else:
            print("Camera not connected. Retrying in 5 seconds...")
            time.sleep(5)

    cap.set(cv2.CAP_PROP_FPS, 5)
    cap.set(cv2.CAP_PROP_AUTOFOCUS, 0)
    cap.set(cv2.CAP_PROP_FOCUS, 200)
    cap.set(cv2.CAP_PROP_EXPOSURE, -6)
    cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*"MJPG"))

    frame_counter = 0
    skip_frames = 1  # Process every frame
    max_mosquito_counter = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Failed to grab frame")
            break

        print("Max Mosquito Counter: ", max_mosquito_counter)

        if frame_counter % skip_frames == 0:
            sharp_frame = sharpen_image(frame)
            detections, t = model.infer(sharp_frame)
            fps = round(1 / t, 2)

            # add fps
            cv2.putText(frame, f"FPS: {fps}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 1)

            if detections:
                lat, lon = location_manager.current_location()
                current_time = datetime.now()
                processed_detections = []

                for detection in detections:
                    # Draw bounding box
                    x1, y1, x2, y2 = scale_coords(detection['box'], frame.shape, sharp_frame.shape)

                    cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 1)
                    cv2.putText(frame, f"{detection['class']} - {detection['conf']:.2f}", (x1, y1+1), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 1)
                    # add to processed detections
                    processed_detections.append({
                        "class": "Aedes Mosquito",
                        "confidence": detection['conf'],
                        "box": [x1, y1, x2, y2]
                    })

                print("Processed Detections: ", len(processed_detections))

                # send to firebase if it exceeds the max mosquito counter
                if len(processed_detections) > max_mosquito_counter:
                    print(f"Detected mosquito at {lat}, {lon} at {current_time.strftime('%Y-%m-%d %H:%M:%S')}. Uploading to Firebase...")
                    max_mosquito_counter = len(processed_detections)

                    # Encode image as JPEG
                    _, buffer = cv2.imencode(".jpg", frame)

                    # Convert to bytes
                    image_bytes = buffer.tobytes()
                    database_manager.schedule_for_upload(image_bytes, {
                        "timestamp": current_time,
                        "latitude": lat,
                        "longitude": lon,
                        "detections": processed_detections
                    })

        frame_counter += 1

        if dev_mode:
            cv2.namedWindow("Output", cv2.WINDOW_NORMAL)
            cv2.resizeWindow("Output", 320, 240)
            cv2.imshow("Output", frame)

            if cv2.waitKey(1) == ord('q'):
                break
    
    cap.release()
    cv2.destroyAllWindows()
    location_manager.close()
    database_manager.wait_for_completion()
    TrapmosDisplay().stop()