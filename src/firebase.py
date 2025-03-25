import asyncio
import uuid
import aiohttp
from google.auth.transport.requests import Request
from google.oauth2 import service_account

import app

class DetectionUploader:
    def __init__(self):
        self.__SERVICE_ACCOUNT_FILE = "trapmosCredentials.json"
        self.__BUCKET_NAME = "finaltrapmos.firebasestorage.app"
        self.__credentials = service_account.Credentials.from_service_account_file(
            self.__SERVICE_ACCOUNT_FILE, scopes=["https://www.googleapis.com/auth/cloud-platform"]
        )

        auth_req = Request()
        self.__credentials.refresh(auth_req)
        self.__access_token = self.__credentials.token

        self.__queue = asyncio.Queue()
        self.__loop = asyncio.get_event_loop()
        self.__running = True
        self.__task = self.__loop.create_task(self.__worker())

    async def __worker(self):
        """Background task that handles uploads."""
        async with aiohttp.ClientSession() as session:
            while self.__running:
                try:
                    image, data, firebase_path = await asyncio.wait_for(self.__queue.get(), timeout=1.0)
                    await self.__upload_to_firebase(session, image, data, firebase_path)
                    self.__queue.task_done()
                except asyncio.TimeoutError:
                    pass  # Prevents blocking if the queue is empty

    async def __upload_to_firebase(self, session, image, data, firebase_path):
        """Uploads an image to Firebase Storage via REST API asynchronously."""
        try:
            with open(image_path, "rb") as image_file:
                image_data = image_file.read()

            url = f"https://firebasestorage.googleapis.com/v0/b/{self.__BUCKET_NAME}/o?name={firebase_path}"
            headers = {
                "Authorization": f"Bearer {self.__access_token}",
                "Content-Type": "image/jpeg",
            }

            async with session.post(url, headers=headers, data=image_data) as response:
                if response.status == 200:
                    print("✅ Upload successful:", await response.json())
                else:
                    print("❌ Upload failed:", await response.text())

        except Exception as e:
            print("⚠️ Error uploading image:", e)

    def schedule_for_upload(self, image, data):
        """Schedules an image for upload without blocking."""
        self.__generate_name(data)
        self.__queue.put_nowait((image, data))

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

    def __generate_name(self, data):
        """Generates a unique name for the image based on the path.
                YYYYMMDD_HHMMSS_lat_lon_uniqueID.jpg
        """
        timestamp = data["timestamp"].strftime("%Y%m%d_%H%M%S")
        lat = round(data["latitude"], 4)
        lon = round(data["longitude"], 4)
        unique_id = uuid.uuid4().hex[:12]
        data["firebase_path"] = f"{app.DEVICE_NAME}/{timestamp}_{lat}_{lon}_{unique_id}.jpg"

if __name__ == "__main__":
    firebase = DetectionUploader()
    firebase.schedule_for_upload("yolov7/images/mosquito.jpg", {"testing": "testing"}, "testing/test.jpg")
    firebase.wait_for_completion()