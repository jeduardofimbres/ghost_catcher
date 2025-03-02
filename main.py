import serial
import time
import threading
import sys

# Publisher frame (ID 0x26) data definitions:
DEFAULT_DATA = bytearray([0xF8, 0x88, 0xFF, 0xFF])
DATA_Q = bytearray([0xF8, 0xA8, 0xFF, 0xFF])  # Clock-wise
DATA_W = bytearray([0xF8, 0x98, 0xFF, 0xFF])  # Counter-clock-wise

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
        time.sleep(0.02)

def main():
    global device
    # Check for command-line arguments: expecting a direction and a duration in seconds.
    if len(sys.argv) < 3:
        print("Usage: python main.py [cw|ccw] <duration in seconds>")
        return

    direction = sys.argv[1].lower()
    try:
        duration = float(sys.argv[2])
    except ValueError:
        print("Invalid duration. Please provide a numeric value in seconds.")
        return

    # Create an instance of the PiCANFD LIN controller
    device = PiCANFD_LIN(port="/dev/ttyS0", baudrate=115200)
    print("Firmware version:", device.get_firmware_version())
    print("Hardware version:", device.get_hardware_version())
    
    # Start the publisher scheduler thread (sending frame every 20ms)
    pub_thread = threading.Thread(target=publisher_scheduler, daemon=True)
    pub_thread.start()

    # Update the publisher frame based on the argument:
    if direction == "cw":
        print("Sending CW (clock-wise) frame data.")
        update_publisher_data(DATA_Q)
    elif direction == "ccw":
        print("Sending CCW (counter-clock-wise) frame data.")
        update_publisher_data(DATA_W)
    else:
        print("Invalid direction. Use 'cw' or 'ccw'.")
        device.close()
        return

    # Continue sending the frame for the specified duration
    time.sleep(duration)

    # Revert to default data after duration
    update_publisher_data(DEFAULT_DATA)
    print(f"Duration of {duration} seconds expired, reverting to default frame data.")
    
    # Give some time for the default data to be transmitted
    time.sleep(1)
    device.close()
    print("Exiting.")

if __name__ == "__main__":
    main()
