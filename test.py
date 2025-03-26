import cv2
import imutils
from datetime import datetime
from src.yoloDet import YoloTRT
from src.location import LocationManager
from src.firebase import DetectionUploader


def scale_coords(coords, orig_shape, small_shape):
    x1, y1, x2, y2 = coords
    scale_x = orig_shape[1] / small_shape[1]
    scale_y = orig_shape[0] / small_shape[0]
    return int(x1 * scale_x), int(y1 * scale_y), int(x2 * scale_x), int(y2 * scale_y)


def run_detection(image_path):
    model = YoloTRT(
        library="yolov7/build/libmyplugins.so",
        engine="yolov7/build/yolov7-tiny.engine",
        conf=0.5,
        yolo_ver="v7"
    )
    location_manager = LocationManager()
    database_manager = DetectionUploader()

    # Load the image
    frame = cv2.imread(image_path)
    if frame is None:
        print("Failed to load image")
        return

    small_frame = imutils.resize(frame, width=640)
    detections, t = model.Inference(small_frame)
    fps = round(1 / t, 2)

    if detections:
        lat, lon = location_manager.current_location()
        current_time = datetime.now()
        processed_detections = []

        for detection in detections:
            if detection['class'] in ["Aedes aegypti", "Aedes albopictus"]:
                x1, y1, x2, y2 = scale_coords(detection['box'], frame.shape, small_frame.shape)
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 1)
                cv2.putText(frame, f"FPS: {fps}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 1)
                processed_detections.append({
                    "class": detection['class'],
                    "confidence": detection['conf'],
                    "box": [x1, y1, x2, y2]
                })

        if processed_detections:
            print(f"Detected mosquito at {lat}, {lon} at {current_time.strftime('%Y-%m-%d %H:%M:%S')}")
            _, buffer = cv2.imencode(".jpg", frame)
            database_manager.schedule_for_upload(buffer.tobytes(), {
                "timestamp": current_time,
                "latitude": lat,
                "longitude": lon,
                "detections": processed_detections
            })
            database_manager

    # Always display the image
    cv2.imshow("Output", frame)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

    location_manager.close()
    database_manager.wait_for_completion()


image_path = "yolov7/images/mosquito.jpg"  # Replace with your image path
run_detection(image_path)
