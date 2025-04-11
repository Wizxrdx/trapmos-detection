import cv2
import numpy as np
import onnxruntime as ort
import time
import random


class YoloONNX:
    def __init__(self, model_path, conf_thres=0.25, iou_thres=0.4):
        self.session = ort.InferenceSession(model_path, providers=['CPUExecutionProvider'])
        self.input_name = self.session.get_inputs()[0].name
        self.output_name = self.session.get_outputs()[0].name
        self.input_shape = self.session.get_inputs()[0].shape[2:]  # [H, W]
        self.conf_thres = conf_thres
        self.iou_thres = iou_thres
        self.categories = ["Aedes mosquito", "Aedes mosquito", "Aedes mosquito"]

    def preprocess(self, img):
        h, w, _ = img.shape
        image = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        image = cv2.resize(image, tuple(self.input_shape[::-1]))  # W, H
        image = image.astype(np.float32) / 255.0
        image = np.transpose(image, (2, 0, 1))
        image = np.expand_dims(image, axis=0)
        return image, img, h, w

    def postprocess(self, outputs, orig_h, orig_w):
        outputs = outputs[0]

        if outputs.ndim == 1:
            outputs = np.expand_dims(outputs, axis=0)

        if outputs.shape[0] == 0:
            return []

        boxes, scores, class_ids = [], [], []

        for det in outputs:
            if det[4] < self.conf_thres:
                continue
            conf = det[4] * det[5]
            if conf < self.conf_thres:
                continue
            cx, cy, w, h = det[0:4]
            x1 = int((cx - w / 2) * orig_w / self.input_shape[1])
            y1 = int((cy - h / 2) * orig_h / self.input_shape[0])
            x2 = int((cx + w / 2) * orig_w / self.input_shape[1])
            y2 = int((cy + h / 2) * orig_h / self.input_shape[0])
            boxes.append([x1, y1, x2, y2])
            scores.append(float(conf))
            class_ids.append(int(det[6]))

        indices = cv2.dnn.NMSBoxes(boxes, scores, self.conf_thres, self.iou_thres)
        results = []
        for i in indices:
            i = i[0] if isinstance(i, (list, tuple, np.ndarray)) else i
            result = {
                "class": self.categories[class_ids[i]],
                "conf": scores[i],
                "box": boxes[i]
            }
            results.append(result)
        return results

    def draw_boxes(self, img, detections):
        for det in detections:
            x1, y1, x2, y2 = det['box']
            label = f"{det['class']}:{det['conf']:.2f}"
            color = [random.randint(0, 255) for _ in range(3)]
            cv2.rectangle(img, (x1, y1), (x2, y2), color, 2)
            cv2.putText(img, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
        return img

    def infer(self, img):
        input_tensor, original_img, h, w = self.preprocess(img)
        start = time.time()
        outputs = self.session.run(None, {self.input_name: input_tensor})
        inference_time = time.time() - start
        detections = self.postprocess(outputs, h, w)
        self.draw_boxes(original_img, detections)
        return detections, inference_time
