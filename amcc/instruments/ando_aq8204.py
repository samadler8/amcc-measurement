import pyvisa
import numpy as np
import time
import math
import threading
import re

class AndoAQ8204(object):
    """Python class for Ando rack aq8204, written by Sam Adler
    Use like ando = aq8204('GPIB0::5::INSTR')"""
    def __init__(self, address):
        self.rm = pyvisa.ResourceManager()
        self.instrument = self.rm.open_resource(address)

        rng_list = np.arange(30, -70, -10)
        self.rng_dict = {}
        for i, val in enumerate(rng_list):
            self.rng_dict[int(val)] = chr(ord("C") + i)
        self.rng_dict[111] = chr(65)

        self.atime_dict = {}
        atime_list = [1, 2, 5, 10, 20, 50, 100, 200]
        self.unit_dict = {
            "L": 9,
            "M": 6,
            "N": 3,
            "O": 0,
            "P": -3,
            "Q": -6,
            "R": -9,
            "S": -12,
            "T": -15,
            "Z": -18,
        }

        for i, val in enumerate(atime_list):
            self.atime_dict[int(val)] = chr(ord("A") + i)












    # Base Laser - aq82011
    def aq82011_std_init(self, channel):
        self.instrument.write(f"C{channel}")
        self.instrument.write("LUS0")  # Set to wavelength units of nm
        self.instrument.write("LEMO0")  # Set to external modulation off
        self.instrument.write("LIMO0")  # Set internal to CW
        self.instrument.write("LCOHR1")  # Set coherence ctrl on (wide bandwidth)
        return
       

    def aq82011_get_lambda(self, channel):
        self.instrument.write(f"C{channel}")
        msg = self.instrument.query("LW?")
        if len(msg.strip()) == 0:
            wl = float("NaN")
        else:
            wl = float(msg.strip().lstrip("LW"))
        return wl


    def aq82011_set_lambda(self, channel, value): 
        loop = 0
        while loop < 3:
            self.instrument.write(f"C{channel}")
            rounded_value = np.around(value, 1)
            self.instrument.write(f"LW{rounded_value}")
            check_value = self.aq82011_get_lambda(channel)
            if rounded_value != check_value:
                loop += 1
            else:
                return 0
        print(f"Problem setting wavelength on the laser to {rounded_value}, instead got {check_value}")
        return -1


    def aq82011_get_cmd(self, channel, cmd):
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

    def aq82011_get_lopt(self, channel):
        lopt = self.aq82011_get_cmd(channel, "LOPT")
        lopt = int(lopt)
        if lopt < 0:
            return -1
        else:
            return lopt
        
    def aq82011_get_cohl(self, channel):
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

    def aq82011_set_cohl(self, channel, value):
        self.instrument.write(f"C{channel}")
        value = int(value)
        if value > 1:
            value = 1
        self.instrument.write(f"LCOHR{int(value)}")
        check_value = self.aq82011_get_cohl(channel)
        if value != check_value:
            print(f"Problem setting cohl on the laser to {value}, instead got {check_value}")
        return

    def aq82011_set_power(self, channel, value):
        self.instrument.write(f"C{channel}")
        value = 10. * math.log10(value) + 30
        self.instrument.write(f"LPL{float(value)}")
        check_value = self.aq82011_get_power(channel)
        if value != check_value:
            print(f"Problem setting the power on the laser to {value}, instead got {check_value}")
        return

    def aq82011_get_power(self, channel):
        self.instrument.write(f"C{channel}")
        msgin = self.instrument.query(b"LPL?")
        power = 10. ** (float(msgin)) * 1e-3
        return power

    def aq82011_set_lopt(self, channel, value):
        self.instrument.write(f"C{channel}")
        self.instrument.write(f"LOPT{value}")
        return

    def aq82011_set_lwlcal(self, channel, value):
        self.instrument.write(f"C{channel}")
        value = f"{np.around(value, 2)}"
        self.instrument.write("LWLCAL%s" % (value))
        check_value = self.aq82011_get_lwlcal(channel)
        if value != check_value:
            print(f"Problem setting the lwcal on the laser to {value}, instead got {check_value}")
        return

    def aq82011_set_latl(self, channel, value):
        self.instrument.write(f"C{channel}")
        self.instrument.write(f"LATL{float(value)}")
        check_value = self.aq82011_get_latl(channel)
        if value != check_value:
            print(f"Problem setting the latl level on the laser to {value}, instead got {check_value}")
        return

    def aq82011_get_lwlcal(self, channel):
        self.instrument.write(f"C{channel}")
        msgin = self.instrument.query("LWLCAL?").strip().lstrip("LWLCAL")
        return float(msgin)

    def aq82011_get_latl(self, channel):
        self.instrument.write(f"C{channel}")
        msgin = self.instrument.query("LATL?", 0.5)
        msgin = msgin.strip().lstrip("LATL")
        try:
            ans = float(msgin)
        except:
            print(f"could not convert {repr(msgin)}")
            ans = float("nan")
        return ans

    def aq82011_enable(self, channel):
        self.aq82011_set_lopt(channel, 1)
        return

    def aq82011_disable(self, channel):
        self.aq82011_set_lopt(channel, 0)
        return

    def aq82011_get_status(self, channel):
        self.instrument.write(f"C{channel}")
        msgin = self.instrument.query("LMSTAT?").strip().lstrip("LMSTAT")
        print("get_status", msgin)
        if len(msgin) != 1:
            msgin = "ZZZ"
        return msgin


    









    # Base Optical Power Meter - aq82012
    def aq82012_find_key(self, d, v):
        for key, value in list(d.items()):
            if v == value:
                return key
        return

    def aq82012_std_init(self, channel):
        self.instrument.write(f"C{channel}")
        self.instrument.write("PMO0")  # Set CW
        self.instrument.write("PDR0")  # Set no reference
        self.instrument.write("PH0")  # No max/min measurement
        self.instrument.write("PAD")  # average 10
        self.instrument.write("PFB")  # Unit: W
        print("aq82012_std_init aq82012_get_lambda", self.aq82012_get_lambda(channel))
        self.set_unit(1)
        return

    def aq82012_get_range(self, channel):
        self.instrument.write(f"C{channel}")
        msg = self.instrument.query("PR?")
        try:
            value = msg.strip().split("PR")[1]
        except:
            print(f"Problem parsing range{repr(msg)}")
            value = ""
        
        key = None
        for k in list(self.rng_dict.keys()):
            if self.rng_dict[k] == value:
                key = k
                break
        if key == None:
            if value == "A":
                key = "A"
            else:
                key = float("NaN")
        return key

    def aq82012_set_range(self, channel, value):
        rng_dict = {'A': 'AUTO',
            'C': +30,
            'D': +20,
            'E': +10,
            'F': 0,
            'G': -10,
            'H': -20,
            'I' : -30,
            'J' : -40,
            'K': -50,
            'L' : -60,
            'Z' : 'HOLD',
        }
        self.instrument.write(f"C{channel}")
        if type(value) == str:
            rng = value.upper()
        else:
            rng = self.rng_dict[int(value)]
        self.instrument.write(f"PR{rng}")
        check_value = self.aq82012_get_range(channel)
        if value in rng_dict.keys():
            value = rng_dict[value]
            if isinstance(value, str):
                value = check_value
        if value != check_value:
            print(f"Problem setting power meter range to {value}, instead got {check_value}")
        return rng

    def aq82012_get_lambda(self, channel):
        loop = 0
        while loop < 3:
            self.instrument.write(f"C{channel}")
            try:
                msg = self.instrument.query("PW?")
                msg = msg.strip()  # Remove leading/trailing whitespace
                if "," in msg:
                    print("Bad message from power meter:", repr(msg))
                    msg = ""
                if len(msg) > 0:
                    try:
                        pow_str = msg.split("PW")[1]  # Split based on "PW"
                    except IndexError:
                        print("Problem parsing get_lambda:", repr(msg))
                        pow_str = ""
                    if len(pow_str) > 0:
                        wl = float(pow_str)
                        return wl
                    else:
                        print("Trying to get lambda again")
                        loop += 1
                else:
                    print("Trying to get lambda again")
                    loop += 1
            except Exception as e:
                print(f"Error querying instrument: {e}")
                loop += 1
                time.sleep(0.1)  # Wait before retrying
        print("Problem getting the wavelength from the power meter")
        return -1

    def aq82012_set_lambda(self, channel, value):
        self.instrument.write(f"C{channel}")
        self.instrument.write(f"PW{float(value)}")
        time.sleep(0.5)
        check_value = self.aq82012_get_lambda(channel)
        if f"{value:.1g}" != f"{check_value:.1g}":
            print(f"Problem setting wavelength on the power meter to {value}, instead got {check_value}")
            return -1
        return 0

    def aq82012_get_atim(self, channel):
        self.instrument.write(f'C{channel}')
        msg = self.instrument.query("PA?")
        key = None

        if len(msg) > 0:
            try:
                value = msg.strip().split("PA")[1]
            except:
                print("Problem parsing atim",repr(msg))
                value = ""
            for k in list(self.atime_dict.keys()):
                if self.atime_dict[k] == value:
                    key = k
                    break
        if key == None:
            key = float("NaN")
        return key

    def aq82012_set_atim(self, channel, value):
        self.instrument.write(f"C{channel}")
        atime = self.atime_dict[value]
        self.instrument.write(f"PA{atime}")
        check_value = self.aq82012_get_atim(channel)
        if value != check_value:
            print(f"Problem setting power meter atime to {value}, instead got {check_value}")
        return

    def aq82012_set_unit(self, channel, value):
        self.instrument.write(f"C{channel}")
        if value == 1:
            self.instrument.write("PFA")  #  Watt
        elif value == 0:
            self.instrument.write("PFB")  # dBm
        return

    def aq82012_get_power(self, channel):
        self.instrument.write(f"C{channel}")
        msgin = self.instrument.query("POD?", 0.3)
        power_val = msgin[10:]
        unit = msgin[7]
        if unit == "U":
            power = 1e-3 * 10 ** ((float(power_val)/10))
        else:
            unit = self.unit_dict[msgin[4]]
            power = float(power_val) * (10 ** unit)
        return power
    
    def aq82012_get_status(self, channel):
        self.instrument.write(f"C{channel}")
        msgin = self.instrument.query("POD?",.3).strip().split("POD")[1]
        if len(msgin) < 2:
            msgin = "ZZZ"
        return msgin[2]

    def aq82012_init_pwm_log(self, nreadings):
        self.nreadings = nreadings
        self.init_nreadings = nreadings

    def aq82012_stop_pwm_log(self):
        self.nreadings = 0
        return

    def aq82012_start_pwm_log(self):
        self.readings = []
        self.nreadings = self.init_nreadings
        self.measure_thread = threading.Timer(0, self.measure)
        self.measure_thread.start()

    def aq82012_measure(self, channel):
        self.aq82012_measure_wait_before(channel)
        return

    def aq82012_measure_wait_before(self, channel):
        for _ in range(self.nreadings):
            w_thread = threading.Timer(0.67, self.wait)
            w_thread.start()
            w_thread.join()
            with self.instrument.lock:
                power = self.aq82012_get_power(channel)
            self.readings.append(power)
        return

    def aq82012_measure_wait_after(self, channel):
        for counter in range(self.nreadings):
            power = self.aq82012_get_power(channel)
            self.readings.append(power)
            if counter == self.nreadings - 1:
                break
            w_thread = threading.Timer(1, self.wait)
            w_thread.start()
            w_thread.join()
        return

    def aq82012_measure_old(self, channel):
        if self.nreadings > 0:
            self.nreadings -= 1
            threading.Timer(1.1, self.aq82012_measure(channel)).start()
            power = self.aq82012_get_power(channel)
            self.readings.append(power)
        return

    def aq82012_measure2(self, channel):
        readings = []
        for _ in range(self.nreadings):
            readings.append(self.aq82012_get_power(channel))
        self.nreadings = 0
        return

    def aq82012_read_pwm_log(self):
        self.measure_thread.join()
        return np.array(self.readings)

    def aq82012_zero(self, channel):
        zeroing_pending = True
        while zeroing_pending:
            start = time.time()
            self.instrument.write(f"C{channel}")
            self.instrument.write("PZ")
            time.sleep(1)
            while True:
                status = self.aq82012_get_status(channel)

                if "Z" not in status:
                    zeroing_pending = False
                    break
                elif (time.time() -start) > 100:
                    break
                else:
                    time.sleep(1)
            t = time.time() - start
        print(f"Done zero: {t}")
        return t








    # Attenuator Functions - aq820133
    def aq820133_get_att(self, channel):
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

    def aq820133_set_att(self, channel, value):
        self.instrument.write(f"C{channel}")
        self.instrument.write(f"AAV{np.abs(value)}")
        time.sleep(0.2)
        check_value = self.aq820133_get_att(channel)
        if f"{value:.3g}" != f"{check_value:.3g}":
            print(f"Problem setting attenuator to {value}, instead set to {check_value}")
        return

    def aq820133_get_lambda(self, channel):
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

    def aq820133_set_lambda(self, channel, value):
        self.instrument.write(f"C{channel}")
        value = int(np.around(value))  # Resolution is nearest nm
        self.instrument.write(f"AW{value}")
        time.sleep(0.2)
        check_value = self.aq820133_get_lambda(channel)
        if f"{value:.3g}" != f"{check_value:.3g}":
            print(f"Problem setting lambda to {value}, instead set to {check_value}")
        return

    def aq820133_enable(self, channel):
        self.instrument.write(f"C{channel}")
        self.instrument.write("ASHTR1")
        if not self.aq820133_get_ASHTR(channel):
            print("Problem with enable")
        return

    def aq820133_disable(self, channel):
        self.instrument.write(f"C{channel}")
        self.instrument.write("ASHTR0")
        if self.aq820133_get_ASHTR(channel):
            print("Problem with disable")
        return

    def aq820133_get_ASHTR(self, channel):
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



    















    # Base Optical Switch - aq8201418
    def aq8201418_get_route(self, channel):
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

    def aq8201418_set_route(self, channel, value):
        self.instrument.write(f"C{channel}")
        self.instrument.write(f"SA1SB{value}")
        time.sleep(1)  # Adjust this based on your device's response time
        check_value = self.aq8201418_get_route(channel)
        if int(value) != int(check_value):
            print(f"Problem setting route to {value}, instead got {check_value}")
            retry_count = 3
            for i in range(retry_count):
                print(f"Retrying... ({i + 1}/{retry_count})")
                self.instrument.write(f"SA1SB{value}")
                time.sleep(1)  # Wait for the route change to take effect
                check_value = self.aq8201418_get_route(channel)
                if int(value) == int(check_value):
                    print(f"Route successfully set to {value}")
                    break
            else:
                print(f"Failed to set route to {value} after {retry_count} attempts")
        return

