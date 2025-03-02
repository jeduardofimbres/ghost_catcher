import time
import glob
from luma.core.interface.serial import i2c
from luma.oled.device import ssd1306
from PIL import Image

# Initialize the I2C OLED display (address may be 0x3C or 0x3D, adjust as needed)
serial = i2c(port=1, address=0x3C)
device = ssd1306(serial)

# Animation parameters
frame_rate = 10              # Target frame rate in frames per second
frame_duration = 1.0 / frame_rate  # Duration per frame in seconds

# Load animation frames from a folder; adjust the path and file pattern as needed
frame_files = sorted(glob.glob("animation_frames/*.jpg"))
frames = [Image.open(frame_file).convert("1") for frame_file in frame_files]

# Play the animation
for frame in frames:
    device.display(frame)
    time.sleep(frame_duration)

# Display the last frame indefinitely
last_frame = frames[-1]
device.display(last_frame)

# Keep the program running to hold the last frame on display
while True:
    time.sleep(1)
