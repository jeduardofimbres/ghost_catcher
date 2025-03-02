from gpiozero import Button
from signal import pause
import serial
import time
import threading
import sys


# Publisher frame (ID 0x26) data definitions:
DEFAULT_DATA = bytearray([0xF8, 0x88, 0xFF, 0xFF])
DATA_UP = bytearray([0xF8, 0xA8, 0xFF, 0xFF])  # Clock-wise
DATA_DW = bytearray([0xF8, 0x98, 0xFF, 0xFF])  # Counter-clock-wise

# Global variable to hold the current publisher data
current_data = DEFAULT_DATA

class PiCANFD_LIN:
    def __init__(self, port="/dev/ttyS0", baudrate=115200):
        self.ser = serial.Serial(port, baudrate, timeout=0.1)
        # Open the LIN port by sending the "O" command
        self.send_command("O")
    
    def send_command(self, cmd):
        self.ser.reset_input_buffer()  # Clear any lingering data
        full_cmd = cmd + "\r"
        self.ser.write(full_cmd.encode('ascii'))
        time.sleep(0.05)
        try:
            response = self.ser.read_all().decode('ascii', errors='ignore')
            return response
        except Exception as e:
            print("Error reading from serial port:", e)
            return ""

    def get_firmware_version(self):
        """Get the firmware version by sending 'v'."""
        return self.send_command("v")
    
    def get_hardware_version(self):
        """Get the hardware version by sending 'V'."""
        return self.send_command("V")
    
    def transmit_frame(self, address, data: bytearray):
        """
        Transmit a LIN frame using the 't' command.
        Format: t + [2-digit hex address] + [data length digit] + [data as hex digits]
        """
        cmd = "T" + format(address, "02X") + str(len(data))
        cmd += ''.join(format(b, "02X") for b in data)
        return self.send_command(cmd)
    
    def request_response(self, address):
        """
        Send a request/respond command using 'r' followed by a 2-digit hex address.
        """
        cmd = "r" + format(address, "02X")
        return self.send_command(cmd)
        
    def close(self):
        self.ser.close()

    # Define callback functions for button presses
    def on_up_pressed(self):
        print("Up pressed!")
        update_publisher_data(DATA_UP)

    def on_down_pressed(self):
        print("Down pressed!")
        update_publisher_data(DATA_DW)

    # Define callback functions for when the button is released
    def on_up_released(self):
        print("Up released!")
        update_publisher_data(DEFAULT_DATA)

    def on_down_released(self):
        print("Down released!")
        update_publisher_data(DEFAULT_DATA)

# Global instance of the device
device = None

def update_publisher_data(data: bytearray):
    """
    Update the publisher frame (ID 0x26) with new data.
    This function sends a LIN frame with the given data.
    """
    global current_data
    current_data = data
    ret = device.transmit_frame(0x26, data)
    print("Updated frame 0x26 data to:", list(data), "Response:", ret)

def publisher_scheduler():
    """
    Continuously transmit the publisher frame (ID 0x26) every 20ms.
    This emulates the scheduler functionality from the original PLIN code.
    """
    while True:
        device.transmit_frame(0x26, current_data)
        #print(f"Transmitted data: {current_data}")
        time.sleep(0.02)

def main():
    global device

    # Define the GPIO pins for Up and Down
    up_button = Button(23, pull_up=True, bounce_time=0.2)
    down_button = Button(22, pull_up=True, bounce_time=0.2)

    # Create an instance of the PiCANFD LIN controller
    device = PiCANFD_LIN(port="/dev/ttyS0", baudrate=115200)
    print("Firmware version:", device.get_firmware_version())
    print("Hardware version:", device.get_hardware_version())

    # Assign the callbacks to the buttons
    up_button.when_pressed = device.on_up_pressed
    up_button.when_released = device.on_up_released
    down_button.when_pressed = device.on_down_pressed
    down_button.when_released = device.on_down_released
    
    # Start the publisher scheduler thread (sending frame every 20ms)
    pub_thread = threading.Thread(target=publisher_scheduler, daemon=True)
    pub_thread.start()

    print("Waiting for button presses. Press Ctrl+C to exit.")
    pause()  # Keeps the program running and listening for events

if __name__ == "__main__":
    main()
