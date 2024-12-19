import pyvisa as visa
import time

class AndoAQ8201418(object):
    """Python class for Ando base optical switch, written by Sam Adler
    Use like ando = AndoAQ8201418('GPIB0::5::INSTR')"""
    def __init__(self, address):
        self.rm = visa.ResourceManager()
        self.instrument = self.rm.open_resource(address)

    def get_route(self, channel):
        loop = 0
        while loop < 3:
            self.instrument.write(f"C{channel}")
            msg = self.instrument.query("SASB?", 0.5)
            msg = msg.strip()  # Removes leading/trailing whitespace
            if len(msg) > 0:
                if ("SSTRAIGHT" in msg) or ("SA1SB1" in msg):
                    output = 1
                elif ("SCROSS" in msg) or ("SA1SB2" in msg):
                    output = 2
                else:
                    output = 0
                return output
            else:
                loop += 1
        print("Problem getting route")
        output = -1
        return output

    def set_route(self, channel, value):
        self.instrument.write(f"C{channel}")
        self.instrument.write(f"SA1SB{value}")
        time.sleep(1)  # Adjust this based on your device's response time
        check_value = self.get_route(channel)
        if int(value) != int(check_value):
            print(f"Problem setting route to {value}, instead got {check_value}")
            retry_count = 3
            for i in range(retry_count):
                print(f"Retrying... ({i + 1}/{retry_count})")
                self.instrument.write(f"SA1SB{value}")
                time.sleep(1)  # Wait for the route change to take effect
                check_value = self.get_route(channel)
                if int(value) == int(check_value):
                    print(f"Route successfully set to {value}")
                    break
            else:
                print(f"Failed to set route to {value} after {retry_count} attempts")
        return

