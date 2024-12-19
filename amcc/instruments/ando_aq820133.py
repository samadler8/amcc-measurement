import pyvisa as visa
import numpy as np
import time

class AndoAQ820133(object):
    """Python class for ando attenuator, written by Sam Adler
    Use like ando = AndoAQ820133('GPIB0::5::INSTR')"""
    def __init__(self, address):
        self.rm = visa.ResourceManager()
        self.instrument = self.rm.open_resource(address)

    def get_att(self, channel):
        loop = 0
        while loop < 3:
            self.instrument.write(f"C{channel}")
            msg = self.instrument.query("AAV?")
            msg = msg.strip()  # Remove leading/trailing whitespace
            if len(msg) > 0:
                try:
                    # Extract and return the numeric value after "AAV"
                    return float(msg.strip().split("AAV")[1])
                except (IndexError, ValueError):
                    loop += 1
                    print(f"Invalid response format: {msg}")  # Debugging invalid response
            else:
                loop += 1
        print("Problem getting attenuator value")
        return float("nan")  # Return NaN if unable to retrieve value

    def set_att(self, channel, value):
        self.instrument.write(f"C{channel}")
        self.instrument.write(f"AAV{np.abs(value)}")
        time.sleep(0.2)
        check_value = self.get_att(channel)
        if f"{value:.3g}" != f"{check_value:.3g}":
            print(f"Problem setting attenuator to {value}, instead set to {check_value}")
        return

    def get_lambda(self, channel):
        self.instrument.write(f"C{channel}")
        msg = self.instrument.query("AW?")
        msg = msg.strip()  # Strip leading/trailing whitespace
        if len(msg) > 2:
            try:
                # Extract and return the numeric value after "AW"
                return float(msg.strip().split("AW")[1])
            except (IndexError, ValueError):
                print(f"Invalid response format: {msg}")  # Debugging invalid response
                return float("nan")
        else:
            return float("nan")

    def set_lambda(self, channel, value):
        self.instrument.write(f"C{channel}")
        value = int(np.around(value))  # Resolution is nearest nm
        self.instrument.write(f"AW{value}")
        time.sleep(0.2)
        check_value = self.get_lambda(channel)
        if f"{value:.3g}" != f"{check_value:.3g}":
            print(f"Problem setting lambda to {value}, instead set to {check_value}")
        return

    def enable(self, channel):
        self.instrument.write(f"C{channel}")
        self.instrument.write("ASHTR1")
        if not self.get_ASHTR(channel):
            print("Problem with enable")
        return

    def disable(self, channel):
        self.instrument.write(f"C{channel}")
        self.instrument.write("ASHTR0")
        if self.get_ASHTR(channel):
            print("Problem with disable")
        return

    def get_ASHTR(self, channel):
        self.instrument.write(f"C{channel}")
        msg = self.instrument.query("ASHTR?")
        msg = msg.strip()  # Remove leading/trailing whitespace
        if len(msg) > 0:
            try:
                # Extract and compare value after "ASHTR"
                return "1" == (msg.strip().split("ASHTR")[1])
            except IndexError:
                print(f"Invalid response format: {msg}")  # Debugging invalid response
        return False