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
        self.team_font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 12)
        self.trapmos_font = ImageFont.truetype('/home/trapmos/trapmos.otf', 20)
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
        team_bbox = self.draw.textbbox((0, 0), team_text, font=self.team_font)
        team_width = team_bbox[2] - team_bbox[0]
        team_x = (self.width - team_width) // 2
        team_y = 10
        self.draw.text((team_x, team_y), team_text, font=self.team_font, fill=255)

        trapmos_bbox = self.draw.textbbox((0, 0), self.message, font=self.trapmos_font)
        trapmos_width = trapmos_bbox[2] - trapmos_bbox[0]
        trapmos_x = (self.width - trapmos_width) // 2
        trapmos_y = self.height - trapmos_bbox[3] + 5
        self.draw.text((trapmos_x, trapmos_y), self.message, font=self.trapmos_font, fill=255)

    def _draw_message(self, text):
        msg_bbox = self.draw.textbbox((0, 0), text, font=self.team_font)
        msg_width = msg_bbox[2] - msg_bbox[0]
        msg_x = (self.width - msg_width) // 2
        msg_y = (self.height - msg_bbox[3]) // 2
        self.draw.text((msg_x, msg_y), text, font=self.team_font, fill=255)

    def show_detected(self, msg):
        self.message = msg

    def stop(self):
        self.running = False
