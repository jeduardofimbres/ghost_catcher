import time
from rpi_ws281x import PixelStrip, Color

# LED strip configuration:
LED_COUNT = 1           # Number of LED pixels (adjust if you have more than one)
LED_PIN = 13            # Use GPIO13 for data (must be PWM-capable)
LED_FREQ_HZ = 800000    # LED signal frequency in hertz (usually 800kHz)
LED_DMA = 10            # DMA channel to use for generating signal (try 10)
LED_BRIGHTNESS = 255    # Brightness (0 to 255)
LED_INVERT = False      # True to invert the signal (if using an inverting level shifter)
LED_CHANNEL = 1         # PWM channel (0 or 1)

# Create PixelStrip object with appropriate configuration.
strip = PixelStrip(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL)
strip.begin()

def set_all_color(color):
    for i in range(strip.numPixels()):
        strip.setPixelColor(i, color)
    strip.show()

try:
    while True:
        set_all_color(Color(255, 0, 0))  # Red
        print("Red")
        time.sleep(1)
        set_all_color(Color(0, 255, 0))  # Green
        print("Green")
        time.sleep(1)
        set_all_color(Color(0, 0, 255))  # Blue
        print("Blue")
        time.sleep(1)
        set_all_color(Color(255, 255, 0))  # Yellow
        print("Yellow")
        time.sleep(1)
        set_all_color(Color(0, 0, 0))    # Off
        print("Off")
        time.sleep(1)
except KeyboardInterrupt:
    # Clear the strip on exit.
    set_all_color(Color(0, 0, 0))
    print("Exiting and turning off LED.")
