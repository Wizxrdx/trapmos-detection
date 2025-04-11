import time
import threading
from luma.core.interface.serial import i2c
from luma.oled.device import sh1106
from PIL import Image, ImageDraw, ImageFont

class TrapmosDisplay(threading.Thread):
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(TrapmosDisplay, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if hasattr(self, "_initialized") and self._initialized:
            return
        super().__init__(daemon=True)
        self.serial = i2c(port=1, address=0x3C)
        self.disp = sh1106(self.serial)
        self.width = self.disp.width
        self.height = self.disp.height
        self.image = Image.new('1', (self.width, self.height))
        self.draw = ImageDraw.Draw(self.image)
        self.subtitle_font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 12)
        self.text_font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 8)
        self.title_font = ImageFont.truetype('/home/trapmos/trapmos.otf', 20)
        self.message = "TRAPMOS"
        self.running = True
        self._initialized = True
        self.start()

    def run(self):
        while self.running:
            self.draw.rectangle((0, 0, self.width, self.height), outline=0, fill=0)
            if self.message == "TRAPMOS":
                self._draw_startup()
            else:
                self._draw_message(self.message)
            self.disp.display(self.image)
            time.sleep(1)

    def _draw_startup(self):
        team_text = "TEAM 40"
        team_bbox = self.draw.textbbox((0, 0), team_text, font=self.subtitle_font)
        team_width = team_bbox[2] - team_bbox[0]
        team_x = (self.width - team_width) // 2
        team_y = 10
        self.draw.text((team_x, team_y), team_text, font=self.subtitle_font, fill=255)

        trapmos_bbox = self.draw.textbbox((0, 0), self.message, font=self.title_font)
        trapmos_width = trapmos_bbox[2] - trapmos_bbox[0]
        trapmos_x = (self.width - trapmos_width) // 2
        trapmos_y = self.height - trapmos_bbox[3] + 5
        self.draw.text((trapmos_x, trapmos_y), self.message, font=self.title_font, fill=255)

    def _draw_message(self, message):
        self.draw.rectangle((0, 0, self.width, self.height), outline=0, fill=0)

        if isinstance(message, dict):
            detected = message.get("detected", 0)
            fps = message.get("fps", 0.0)
            ip = message.get("ip", "N/A")
            wifi = message.get("wifi", "Disconnected")
            now = time.strftime("%H:%M")

            lines = [
                f"Mosquitoes: {detected}",
                f"FPS: {fps:.1f}",
                f"WiFi: {wifi}",
                f"IP: {ip}",
                f"Time: {now}"
            ]
        else:
            # CLI-like output, support \n
            lines = message.split('\n')

        # Draw lines centered vertically and horizontally
        line_heights = [self.draw.textbbox((0, 0), l, font=self.text_font)[3] for l in lines]
        total_height = sum(line_heights)
        y = (self.height - total_height) // 2

        for i, line in enumerate(lines):
            bbox = self.draw.textbbox((0, 0), line, font=self.text_font)
            w = bbox[2] - bbox[0]
            h = line_heights[i]
            x = (self.width - w) // 2
            self.draw.text((x, y), line, font=self.text_font, fill=255)
            y += h

    def show_detected(self, count, fps):
        self.message = {"detected": count, "fps": fps}

    def show_message(self, msg):
        self.message = msg

    def stop(self):
        self.message = "Shutting down..."
        time.sleep(2)
        self.running = False
