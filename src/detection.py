import cv2
import imutils
from datetime import datetime
from src.yoloDet import YoloTRT
from src.location import LocationManager


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

            cv2.putText(frame, f"FPS: {fps}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 1)
            cv2.putText(frame, f"Time: {current_time}", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 1)

            if detections:
                for detection in detections:
                    if 'class' in detection:
                        mosquito_classes = ["Culex quinquefasciatus", "Aedes albopictus", "Aedes Aegypti"]
                        if detection['class'] in mosquito_classes:
                            lat, lon = location_manager.current_location()

                            # Draw bounding box
                            x1, y1, x2, y2 = detection['box']

                            # ratio to scale the bounding box
                            scale_x = frame.shape[1] / small_frame.shape[1]
                            scale_y = frame.shape[0] / small_frame.shape[0]

                            # Scale the coordinates
                            x1 = int(x1 * scale_x)
                            y1 = int(y1 * scale_y)
                            x2 = int(x2 * scale_x)
                            y2 = int(y2 * scale_y)
                            
                            # print the location
                            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 1)
                            # or
                            # send to firebase
                            # firebase.send()

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