import json
import asyncio
import threading
import uuid
import aiohttp
from google.auth.transport.requests import Request
from google.oauth2 import service_account
from datetime import datetime, timezone

from app import DEVICE_NAME, DEVICE_ID


class DetectionUploader:
    def __init__(self):
        self.__SERVICE_ACCOUNT_FILE = "trapmosCredentials.json"
        self.__BUCKET_NAME = "finaltrapmos.firebasestorage.app"
        self.__credentials = service_account.Credentials.from_service_account_file(
            self.__SERVICE_ACCOUNT_FILE,
            scopes=[
                "https://www.googleapis.com/auth/cloud-platform",
                "https://www.googleapis.com/auth/datastore"
                ]
        )
        self.__PROJECT_ID = self.__credentials.project_id

        auth_req = Request()
        self.__credentials.refresh(auth_req)
        self.__access_token = self.__credentials.token

        self.__queue = asyncio.Queue()
        self.__loop = asyncio.get_event_loop()
        self.__running = True
        self.__task = self.__loop.create_task(self.__worker())
        self.__thread = threading.Thread(target=self.__run_loop)
        self.__thread.start()

    def __run_loop(self):
        asyncio.set_event_loop(self.__loop)
        self.__loop.run_forever()

    async def __worker(self):
        """Background task that handles uploads."""
        async with aiohttp.ClientSession() as session:
            print("🚀 Uploader started")
            while self.__running:
                try:
                    image, data, firebase_path, detected = await asyncio.wait_for(self.__queue.get(), timeout=1.0)
                    if detected:
                        result = await self.__upload_to_firebase(session, image, data, firebase_path)
                    else:
                        result = await self.__upload_to_firebase_no_detected(session, image, data, firebase_path)
                    if result:
                        self.__queue.task_done()
                except asyncio.TimeoutError:
                    pass  # Prevents blocking if the queue is empty
                except:
                    print(data)
                    print("⚠️ Error uploading image")

    async def __upload_to_firebase(self, session, image, data, firebase_path):
        """Uploads an image to Firebase Storage via REST API asynchronously."""
        try:
            file_name = firebase_path.split("/")[-1]
            firebase_url = f"https://firebasestorage.googleapis.com/v0/b/{self.__BUCKET_NAME}/o?name={firebase_path}"
            firestore_url = f"https://firestore.googleapis.com/v1/projects/{self.__PROJECT_ID}/databases/(default)/documents/Uploads/{file_name}"

            headers = {
                "Authorization": f"Bearer {self.__access_token}",
                "Content-Type": "image/jpeg",
            }

            async with session.post(firebase_url, headers=headers, data=image) as response:
                if response.status == 200:
                    print("✅ Upload successful:", await response.json())
                else:
                    print("❌ Upload failed:", await response.text())
                    return False

            headers = {
                "Authorization": f"Bearer {self.__access_token}",
                "Content-Type": "application/json",
            }

            json_data_str = json.dumps(self.__to_firestore_json(data, file_name, True))

            async with session.patch(firestore_url, headers=headers, data=json_data_str) as response:
                if response.status == 200:
                    print("✅ Upload successful:", await response.json())
                else:
                    print("❌ Upload failed:", await response.text())
                    return False

        except Exception as e:
            print("⚠️ Error uploading image:", e)
            return False
        
    async def __upload_to_firebase_no_detected(self, session, image, data, firebase_path):
        """Uploads an image to Firebase Storage via REST API asynchronously."""
        try:
            file_name = firebase_path.split("/")[-1]
            firebase_url = f"https://firebasestorage.googleapis.com/v0/b/{self.__BUCKET_NAME}/o?name={firebase_path}"
            firestore_url = f"https://firestore.googleapis.com/v1/projects/{self.__PROJECT_ID}/databases/(default)/documents/images/{file_name}"

            headers = {
                "Authorization": f"Bearer {self.__access_token}",
                "Content-Type": "image/jpeg",
            }

            async with session.post(firebase_url, headers=headers, data=image) as response:
                if response.status == 200:
                    print("✅ Upload successful:", await response.json())
                else:
                    print("❌ Upload failed:", await response.text())
                    return False

            headers = {
                "Authorization": f"Bearer {self.__access_token}",
                "Content-Type": "application/json",
            }

            json_data_str = json.dumps(self.__to_firestore_json(data, file_name, False))

            async with session.patch(firestore_url, headers=headers, data=json_data_str) as response:
                if response.status == 200:
                    print("✅ Upload successful:", await response.json())
                else:
                    print("❌ Upload failed:", await response.text())
                    return False

        except Exception as e:
            print("⚠️ Error uploading image:", e)
            return False

    def schedule_for_upload(self, image, data, detected):
        """Schedules an image for upload without blocking."""
        file_path = self.__generate_name(data)
        self.__queue.put_nowait((image, data, file_path, detected))

    async def wait_until_done(self):
        """Waits for all uploads to complete before exiting."""
        await self.__queue.join()
        self.shutdown()  # Ensure cleanup

    def shutdown(self):
        """Properly stops the background worker task."""
        self.__running = False

    def wait_for_completion(self):
        """Blocks until all uploads are done."""
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self.wait_until_done())

    def __generate_name(self, data, detected):
        """Generates a unique name for the image based on the path.
                YYYYMMDD_HHMMSS_lat_lon_uniqueID.jpg
        """
        timestamp = data["timestamp"].strftime("%Y%m%d_%H%M%S")
        lat = round(data["latitude"], 4)
        lon = round(data["longitude"], 4)
        unique_id = uuid.uuid4().hex[:12]
        if detected:
            return f"{DEVICE_NAME}/{DEVICE_ID}_{timestamp}_{lat}_{lon}_{unique_id}.jpg"
        else:
            return f"{DEVICE_NAME}_no_aedes/{DEVICE_ID}_{timestamp}_{lat}_{lon}_{unique_id}_no_detected.jpg"

    def __to_firestore_json(self, data, file_name, detected):
        """Converts the data to Firestore JSON format."""
        timestamp = timestamp = data["timestamp"].astimezone(timezone.utc).replace(microsecond=0).isoformat()
        
        if detected:
            detections = [{
                "mapValue": {
                    "fields": {
                        "class": { "stringValue": detection["class"] },
                        "confidence": { "doubleValue": float(detection["confidence"]) },
                        "box": { "arrayValue": { "values": [
                            { "doubleValue": float(detection["box"][0]) },
                            { "doubleValue": float(detection["box"][1]) },
                            { "doubleValue": float(detection["box"][2]) },
                            { "doubleValue": float(detection["box"][3]) }
                        ] } }
                    }
                }
            } for detection in data["detections"]]

            return {
                "fields": {
                    "device": { "stringValue": DEVICE_NAME },
                    "file": { "stringValue": file_name },
                    "timestamp": { "timestampValue": timestamp },
                    "latitude": { "doubleValue": float(data["latitude"]) },
                    "longitude": { "doubleValue": float(data["longitude"]) },
                    "detections": { "arrayValue": { "values": detections } }
                }
            }
        else:
            return {
                "fields": {
                    "device": { "stringValue": DEVICE_NAME },
                    "file": { "stringValue": file_name },
                    "timestamp": { "timestampValue": timestamp },
                    "latitude": { "doubleValue": float(data["latitude"]) },
                    "longitude": { "doubleValue": float(data["longitude"]) }
                }
            }

if __name__ == "__main__":
    import cv2

    data = {
        "timestamp": datetime.now(),
        "latitude": 14.1234,
        "longitude": 121.1234,
        "detections": [
            {
                "class": "Aedes aegypti",
                "confidence": 0.95,
                "box": [0, 0, 100, 100]
            },
            {
                "class": "Aedes albopictus",
                "confidence": 0.85,
                "box": [100, 100, 200, 200]
            }
        ]
    }

    firebase = DetectionUploader()
    frame = cv2.imread("yolov7/images/mosquito.jpg")
    # Encode image as JPEG
    _, buffer = cv2.imencode(".jpg", frame)

    # Convert to bytes
    image_bytes = buffer.tobytes()
    firebase.schedule_for_upload(image_bytes, data, True)