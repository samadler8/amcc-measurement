import serial
import time


class ThorLabsLFLTM:

    def __init__(self, port):
        self.ser = serial.Serial(
            port=port,  # Replace 'COM7' with the correct port for your system
            baudrate=115200,
            bytesize=serial.EIGHTBITS,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            timeout=1
        )

    def send_command(self, command):
        self.ser.write((command + '\r').encode())  # Append carriage return to the command
        time.sleep(0.1)
        response = self.ser.read(self.ser.in_waiting).decode()  # Read the response
        print(f"Response: {response}")
        return response

    # Function to turn the laser ON
    def enable(self):
        self.send_command("enable=1")  # Enable the laser

    # Function to turn the laser OFF
    def disable(self):
        self.send_command("enable=0")  # Disable the laser

    # Function to query laser status
    def get_status(self):
        status = self.send_command("enable?")
        print(f"Laser status: {'ON' if status.strip() == '1' else 'OFF'}")
