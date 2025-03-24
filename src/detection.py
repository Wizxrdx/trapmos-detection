import cv2
import imutils
from datetime import datetime
from yoloDet import YoloTRT
from location import LocationManager


def run_detection(dev_mode):
    # Initialize YOLO model
    model = YoloTRT(
        library="yolov7/build/libmyplugins.so",
        engine="yolov7/build/yolov7-tiny.engine",
        conf=0.5,
        yolo_ver="v7"
    )

    # Initialize location manager
    location_manager = LocationManager()

    # Open the camera
    cap = cv2.VideoCapture(0, cv2.CAP_V4L2)
    cap.set(cv2.CAP_PROP_FPS, 60)
    frame_counter = 0
    skip_frames = 1  # Process every frame

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Failed to grab frame")
            break

        small_frame = imutils.resize(frame, width=640)

        if frame_counter % skip_frames == 0:
            detections, t = model.Inference(small_frame)

            print(f"Number of detections: {len(detections)}")
            fps = round(1 / t, 2)
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            cv2.putText(frame, f"FPS: {fps}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            cv2.putText(frame, f"Time: {current_time}", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

            if detections:
                for detection in detections:
                    if 'class' in detection:
                        mosquito_classes = ['Aedes Mosquito', 'Aedes Mosquito']
                        if detection['class'] in mosquito_classes:
                            lat, lon = location_manager.current_location()

                        print("Detected a mosquito! at: ", lat, lon)

                        if 'bbox' in detection:
                            x, y, w, h = detection['bbox']
                        elif 'box' in detection:
                            x, y, w, h = detection['box']
                        else:
                            continue

                        scale_x = frame.shape[1] / small_frame.shape[1]
                        scale_y = frame.shape[0] / small_frame.shape[0]

                        x1 = max(0, int(x * scale_x))
                        y1 = max(0, int(y * scale_y))
                        x2 = min(frame.shape[1], int((x + w) * scale_x))
                        y2 = min(frame.shape[0], int((y + h) * scale_y))

                        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 3)
                        cv2.putText(frame, f"{detection['class']}",
                                    (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX,
                                    0.8, (0, 255, 0), 2)
                        
                        image_filename = f"detection_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
                        cv2.imwrite(image_filename, frame)

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