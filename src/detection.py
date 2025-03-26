import cv2
import imutils
import time
from datetime import datetime
from src.yoloDet import YoloTRT
from src.location import LocationManager
from src.firebase import DetectionUploader


def scale_coords(coords, orig_shape, small_shape):
    x1, y1, x2, y2 = coords
    scale_x = orig_shape[1] / small_shape[1]
    scale_y = orig_shape[0] / small_shape[0]
    return int(x1 * scale_x), int(y1 * scale_y), int(x2 * scale_x), int(y2 * scale_y)

def run_detection(dev_mode):
    # Initialize YOLO model
    model = YoloTRT(
        library="yolov7/build/libmyplugins.so",
        engine="yolov7/build/yolov7-tiny.engine",
        conf=0.5,
        yolo_ver="v7"
    )

    # Initialize location manager
    print("Initializing location manager...")
    location_manager = LocationManager()

    # Initialize Database manager
    print("Initializing Detection Uploader...")
    database_manager = DetectionUploader()

    # Keep checking until a camera is connected
    while True:
        cap = cv2.VideoCapture(0, cv2.CAP_V4L2)
        if cap.isOpened():
            print("Camera connected!")
            break
        else:
            print("Camera not connected. Retrying in 5 seconds...")
            time.sleep(5)
    
    cap.set(cv2.CAP_PROP_FPS, 60)
    cap.set(cv2.CAP_PROP_AUTOFOCUS, 0)
    cap.set(cv2.CAP_PROP_FOCUS, 200)

    frame_counter = 0
    skip_frames = 1  # Process every frame
    max_mosquito_counter = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Failed to grab frame")
            break

        if dev_mode: print("Max Mosquito Counter: ", max_mosquito_counter)

        if frame_counter % skip_frames == 0:
            detections, t = model.Inference(frame)
            fps = round(1 / t, 2)

            # add fps
            cv2.putText(frame, f"FPS: {fps}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 1)

            if dev_mode: print("Detections:", len(detections))
            if detections:
                lat, lon = location_manager.current_location()
                current_time = datetime.now()
                processed_detections = []
                    
                for detection in detections:
                    if detection['class'] in ["Aedes aegypti", "Aedes albopictus"]:
                        # Draw bounding box
                        x1, y1, x2, y2 = detection['box']
                        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 1)
                        # add to processed detections
                        processed_detections.append({
                            "class": detection['class'],
                            "confidence": detection['conf'],
                            "box": [x1, y1, x2, y2]
                        })

                if dev_mode: print("Processed Detections: ", len(processed_detections))

                # send to firebase if it exceeds the max mosquito counter
                if len(processed_detections) > max_mosquito_counter:
                    if dev_mode: print(f"Detected mosquito at {lat}, {lon} at {current_time.strftime('%Y-%m-%d %H:%M:%S')}. Uploading to Firebase...")
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