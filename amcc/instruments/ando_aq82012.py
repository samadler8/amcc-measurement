import pyvisa as visa
import numpy as np
import time
import threading

class AndoAQ82012(object):
    """Python class for base optical power meter, written by Sam Adler
    Use like ando = AndoAQ82012('GPIB0::5::INSTR')"""
    def __init__(self, address):
        self.rm = visa.ResourceManager()
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

    def find_key(self, d, v):
        for key, value in list(d.items()):
            if v == value:
                return key
        return

    def std_init(self, channel):
        self.instrument.write(f"C{channel}")
        self.instrument.write("PMO0")  # Set CW
        self.instrument.write("PDR0")  # Set no reference
        self.instrument.write("PH0")  # No max/min measurement
        self.instrument.write("PAD")  # average 10
        self.instrument.write("PFB")  # Unit: W
        print("std_init get_lambda", self.get_lambda(channel))
        self.set_unit(1)
        return

    def get_range(self, channel):
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

    def set_range(self, channel, value):
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
        check_value = self.get_range(channel)
        if value in rng_dict.keys():
            value = rng_dict[value]
            if isinstance(value, str):
                value = check_value
        if value != check_value:
            print(f"Problem setting power meter range to {value}, instead got {check_value}")
        return rng

    def get_lambda(self, channel):
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

    def set_lambda(self, channel, value):
        self.instrument.write(f"C{channel}")
        self.instrument.write(f"PW{float(value)}")
        time.sleep(0.5)
        check_value = self.get_lambda(channel)
        if f"{value:.1g}" != f"{check_value:.1g}":
            print(f"Problem setting wavelength on the power meter to {value}, instead got {check_value}")
            return -1
        return 0

    def get_atim(self, channel):
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

    def set_atim(self, channel, value):
        self.instrument.write(f"C{channel}")
        atime = self.atime_dict[value]
        self.instrument.write(f"PA{atime}")
        check_value = self.get_atim(channel)
        if value != check_value:
            print(f"Problem setting power meter atime to {value}, instead got {check_value}")
        return

    def set_unit(self, channel, value):
        self.instrument.write(f"C{channel}")
        if value == 1:
            self.instrument.write("PFA")  #  Watt
        elif value == 0:
            self.instrument.write("PFB")  # dBm
        return

    def get_power(self, channel):
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
    
    def get_status(self, channel):
        self.instrument.write(f"C{channel}")
        msgin = self.instrument.query("POD?",.3).strip().split("POD")[1]
        if len(msgin) < 2:
            msgin = "ZZZ"
        return msgin[2]

    def init_pwm_log(self, nreadings):
        self.nreadings = nreadings
        self.init_nreadings = nreadings

    def stop_pwm_log(self):
        self.nreadings = 0
        return

    def start_pwm_log(self):
        self.readings = []
        self.nreadings = self.init_nreadings
        self.measure_thread = threading.Timer(0, self.measure)
        self.measure_thread.start()

    def measure(self, channel):
        self.measure_wait_before(channel)
        return

    def measure_wait_before(self, channel):
        for _ in range(self.nreadings):
            w_thread = threading.Timer(0.67, self.wait)
            w_thread.start()
            w_thread.join()
            with self.instrument.lock:
                power = self.get_power(channel)
            self.readings.append(power)
        return

    def measure_wait_after(self, channel):
        for counter in range(self.nreadings):
            power = self.get_power(channel)
            self.readings.append(power)
            if counter == self.nreadings - 1:
                break
            w_thread = threading.Timer(1, self.wait)
            w_thread.start()
            w_thread.join()
        return

    def measure_old(self, channel):
        if self.nreadings > 0:
            self.nreadings -= 1
            threading.Timer(1.1, self.measure(channel)).start()
            power = self.get_power(channel)
            self.readings.append(power)
        return

    def measure2(self, channel):
        readings = []
        for _ in range(self.nreadings):
            readings.append(self.get_power(channel))
        self.nreadings = 0
        return

    def read_pwm_log(self):
        self.measure_thread.join()
        return np.array(self.readings)

    def zero(self, channel):
        zeroing_pending = True
        while zeroing_pending:
            start = time.time()
            self.instrument.write(f"C{channel}")
            self.instrument.write("PZ")
            time.sleep(1)
            while True:
                status = self.get_status(channel)

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