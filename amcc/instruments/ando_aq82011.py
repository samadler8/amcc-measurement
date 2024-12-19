import pyvisa as visa
import numpy as np
import math

class AndoAQ82011(object):
    """Python class for Ando base laser, written by Sam Adler
    Use like ando = AndoAQ82011('GPIB0::5::INSTR')"""
    def __init__(self, address):
        self.rm = visa.ResourceManager()
        self.instrument = self.rm.open_resource(address)

    def std_init(self, channel):
        self.instrument.write(f"C{channel}")
        self.instrument.write("LUS0")  # Set to wavelength units of nm
        self.instrument.write("LEMO0")  # Set to external modulation off
        self.instrument.write("LIMO0")  # Set internal to CW
        self.instrument.write("LCOHR1")  # Set coherence ctrl on (wide bandwidth)
        return
       

    def get_lambda(self, channel):
        self.instrument.write(f"C{channel}")
        msg = self.instrument.query("LW?")
        if len(msg.strip()) == 0:
            wl = float("NaN")
        else:
            wl = float(msg.strip().lstrip("LW"))
        return wl


    def set_lambda(self, channel, value): 
        loop = 0
        while loop < 3:
            self.instrument.write(f"C{channel}")
            rounded_value = np.around(value, 1)
            self.instrument.write(f"LW{rounded_value}")
            check_value = self.get_lambda(channel)
            if rounded_value != check_value:
                loop += 1
            else:
                return 0
        print(f"Problem setting wavelength on the laser to {rounded_value}, instead got {check_value}")
        return -1


    def get_cmd(self, channel, cmd):
        loop = 0
        while loop < 3:
            self.instrument.write(f"C{channel}")
            msg = self.instrument.query(f"{cmd}?")
            msg = msg.strip()
            if len(msg) > 0:
                value = float(msg.strip().split(cmd)[1])
                return value
            else:
                loop += 1
        print("Problem getting cohl from the laser")
        value = -1
        return value

    def get_lopt(self, channel):
        lopt = self.get_cmd(channel, "LOPT")
        lopt = int(lopt)
        if lopt < 0:
            return -1
        else:
            return lopt
        
    def get_cohl(self, channel):
        loop = 0
        while loop < 3:
            self.instrument.write(f"C{channel}")
            msg = self.instrument.query("LCOHR?")
            msg = msg.strip()
            if len(msg) > 0:
                cohl = float(msg.strip().lstrip("LCOHR"))
                return cohl
            else:
                loop += 1
        print("Problem getting cohl from the laser")
        cohl = -1
        return cohl

    def set_cohl(self, channel, value):
        self.instrument.write(f"C{channel}")
        value = int(value)
        if value > 1:
            value = 1
        self.instrument.write(f"LCOHR{int(value)}")
        check_value = self.get_cohl(channel)
        if value != check_value:
            print(f"Problem setting cohl on the laser to {value}, instead got {check_value}")
        return

    def set_power(self, channel, value):
        self.instrument.write(f"C{channel}")
        value = 10. * math.log10(value) + 30
        self.instrument.write(f"LPL{float(value)}")
        check_value = self.get_power(channel)
        if value != check_value:
            print(f"Problem setting the power on the laser to {value}, instead got {check_value}")
        return

    def get_power(self, channel):
        self.instrument.write(f"C{channel}")
        msgin = self.instrument.query(b"LPL?")
        power = 10. ** (float(msgin)) * 1e-3
        return power

    def set_lopt(self, channel, value):
        self.instrument.write(f"C{channel}")
        self.instrument.write(f"LOPT{value}")
        return

    def set_lwlcal(self, channel, value):
        self.instrument.write(f"C{channel}")
        value = f"{np.around(value, 2)}"
        self.instrument.write("LWLCAL%s" % (value))
        check_value = self.get_lwlcal(channel)
        if value != check_value:
            print(f"Problem setting the lwcal on the laser to {value}, instead got {check_value}")
        return

    def set_latl(self, channel, value):
        self.instrument.write(f"C{channel}")
        self.instrument.write(f"LATL{float(value)}")
        check_value = self.get_latl(channel)
        if value != check_value:
            print(f"Problem setting the latl level on the laser to {value}, instead got {check_value}")
        return

    def get_lwlcal(self, channel):
        self.instrument.write(f"C{channel}")
        msgin = self.instrument.query("LWLCAL?").strip().lstrip("LWLCAL")
        return float(msgin)

    def get_latl(self, channel):
        self.instrument.write(f"C{channel}")
        msgin = self.instrument.query("LATL?", 0.5)
        msgin = msgin.strip().lstrip("LATL")
        try:
            ans = float(msgin)
        except:
            print(f"could not convert {repr(msgin)}")
            ans = float("nan")
        return ans

    def enable(self, channel):
        self.set_lopt(channel, 1)
        return

    def disable(self, channel):
        self.set_lopt(channel, 0)
        return

    def get_status(self, channel):
        self.instrument.write(f"C{channel}")
        msgin = self.instrument.query("LMSTAT?").strip().lstrip("LMSTAT")
        print("get_status", msgin)
        if len(msgin) != 1:
            msgin = "ZZZ"
        return msgin