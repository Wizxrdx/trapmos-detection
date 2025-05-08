import onnxruntime as ort
import numpy as np
import cv2
import time

class YoloONNX:
    def __init__(self, model_path: str, conf_threshold: float = 0.25):
        self.session = ort.InferenceSession(model_path, providers=['CPUExecutionProvider'])
        self.input_name = self.session.get_inputs()[0].name
        self.conf_threshold = conf_threshold
        self.class_names = ["Culex Mosquito", "Aedes Mosquito", "Aedes Mosquito"]
        # self.class_names = ["Aedes Mosquito", "Aedes Mosquito", "Aedes Mosquito"]
        self.colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255)]

    def infer(self, img):
        original_h, original_w = img.shape[:2]
        img_resized = cv2.resize(img, (320, 320))
        img_input = img_resized.astype(np.float32) / 255.0
        img_input = np.transpose(img_input, (2, 0, 1))
        img_input = np.expand_dims(img_input, axis=0)

        start_time = time.time()
        outputs = self.session.run(None, {self.input_name: img_input})
        elapsed = time.time() - start_time

        detections = outputs[0]
        if detections.ndim == 3:
            detections = detections[0]

        h_ratio = original_h / 320
        w_ratio = original_w / 320

        valid_detections = []

        for det in detections:
            # Skip Culex Mosquito detections
            if int(det[5]) == 0:
                continue

            if len(det) < 7 or det[6] < self.conf_threshold:
                continue
            x1, y1, x2, y2 = map(float, [det[1], det[2], det[3], det[4]])
            x1 *= w_ratio
            y1 *= h_ratio
            x2 *= w_ratio
            y2 *= h_ratio
            class_id = self.class_names[int(det[5])]
            conf = det[6]
            valid_detections.append({
                "bbox": [x1, y1, x2, y2],
                "class_id": class_id,
                "confidence": conf
            })

        return valid_detections, elapsed
