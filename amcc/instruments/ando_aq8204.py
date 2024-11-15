import pyvisa
import numpy as np
import time
import math
import threading

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












    # Base Laser - aq820113
    def aq820113_std_init(self, channel):
        self.instrument.write(f"C{channel}")
        self.instrument.write("LUS0")  # Set to wavelength units of nm
        self.instrument.write("LEMO0")  # Set to external modulation off
        self.instrument.write("LIMO0")  # Set internal to CW
        self.instrument.write("LCOHR1")  # Set coherence ctrl on (wide bandwidth)
        return
       

    def aq820113_get_lambda(self, channel):
        self.instrument.write(f"C{channel}")
        msg = self.instrument.query("LW?")
        if len(msg.strip()) == 0:
            wl = float("NaN")
        else:
            wl = float(msg.strip().decode().lstrip("LW"))
        return wl

    def aq820113_set_lambda(self, channel, value):
        loop = 0
        while loop < 3:
            self.instrument.write(f"C{channel}")
            value = f"{np.around(value, 1)}"
            self.instrument.write("LW{value}")
            check_value = self.aq820113_get_lambda(channel)
            if value != check_value:
                loop += 1
            else:
                return 0
        print(f"Problem setting wavelength on the laser to {value}, instead got {check_value}")
        return -1

    def aq820113_get_cmd(self, channel, cmd):
        loop = 0
        while loop < 3:
            self.instrument.write(f"C{channel}")
            msg = self.instrument.query("%s?" % cmd)
            msg = msg.strip()
            if len(msg) > 0:
                value = float(msg.strip().split(cmd)[1])
                return value
            else:
                loop += 1
        print("Problem getting cohl from the laser")
        value = -1
        return value

    def aq820113_get_lopt(self, channel):
        lopt = self.aq820113_get_cmd(channel, "LOPT")
        lopt = int(lopt)
        if lopt < 0:
            return -1
        else:
            return lopt
        
    def aq820113_get_cohl(self, channel):
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

    def aq820113_set_cohl(self, channel, value):
        self.instrument.write(f"C{channel}")
        value = int(value)
        if value > 1:
            value = 1
        self.instrument.write(f"LCOHR{int(value)}")
        check_value = self.aq820113_get_cohl(channel)
        if value != check_value:
            print(f"Problem setting cohl on the laser to {value}, instead got {check_value}")
        return

    def aq820113_set_power(self, channel, value):
        self.instrument.write(f"C{channel}")
        value = 10. * math.log10(value) + 30
        self.instrument.write(f"LPL{float(value)}")
        check_value = self.aq820113_get_power(channel)
        if value != check_value:
            print(f"Problem setting the power on the laser to {value}, instead got {check_value}")
        return

    def aq820113_get_power(self, channel):
        self.instrument.write(f"C{channel}")
        msgin = self.instrument.query(b"LPL?")
        power = 10. ** (float(msgin)) * 1e-3
        return power

    def aq820113_set_lopt(self, channel, value):
        self.instrument.write(f"C{channel}")
        self.instrument.write(f"LOPT{value}")
        return

    def aq820113_set_lwlcal(self, channel, value):
        self.instrument.write(f"C{channel}")
        value = f"{np.around(value, 2)}"
        self.instrument.write("LWLCAL%s" % (value))
        check_value = self.aq820113_get_lwlcal(channel)
        if value != check_value:
            print(f"Problem setting the lwcal on the laser to {value}, instead got {check_value}")
        return

    def aq820113_set_latl(self, channel, value):
        self.instrument.write(f"C{channel}")
        self.instrument.write(f"LATL{float(value)}")
        check_value = self.aq820113_get_latl(channel)
        if value != check_value:
            print(f"Problem setting the latl level on the laser to {value}, instead got {check_value}")
        return

    def aq820113_get_lwlcal(self, channel):
        self.instrument.write(f"C{channel}")
        msgin = self.instrument.query("LWLCAL?").strip().lstrip("LWLCAL")
        return float(msgin)

    def aq820113_get_latl(self, channel):
        self.instrument.write(f"C{channel}")
        msgin = self.instrument.query("LATL?", 0.5)
        msgin = msgin.strip().lstrip("LATL")
        try:
            ans = float(msgin)
        except:
            print(f"could not convert {repr(msgin)}")
            ans = float("nan")
        return ans

    def aq820113_enable(self):
        self.set_lopt(1)
        return

    def aq820113_disable(self):
        self.set_lopt(0)
        return

    def aq820113_get_status(self, channel):
        self.instrument.write(f"C{channel}")
        msgin = self.instrument.query("LMSTAT?").strip().lstrip("LMSTAT")
        print("get_status", msgin)
        if len(msgin) != 1:
            msgin = "ZZZ"
        return msgin


    









    # Base Optical Power Meter - aq820121
    def aq820121_find_key(self, d, v):
        for key, value in list(d.items()):
            if v == value:
                return key
        return

    def aq820121_std_init(self, channel):
        self.instrument.write(f"C{channel}")
        self.instrument.write("D1")
        self.instrument.write("PMO0")  # Set CW
        self.instrument.write("PDR0")  # Set no reference
        self.instrument.write("PH0")  # No max/min measurement
        self.instrument.write("PAD")  # average 10
        self.instrument.write("PFB")  # Unit: W
        print("aq820121_std_init aq820121_get_lambda", self.aq820121_get_lambda(channel))
        self.set_unit(1)
        return

    def aq820121_get_range(self, channel):
        self.instrument.write(f"C{channel}")
        self.instrument.write("D1")
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

    def aq820121_set_range(self, channel, value):
        self.instrument.write(f"C{channel}")
        self.instrument.write("D1")
        if type(value) == str:
            rng = value.upper()
        else:
            rng = self.rng_dict[int(value)]
        self.instrument.write(f"PR{rng}")
        check_value = self.aq820121_get_range(channel)
        if value != check_value:
            print(f"Problem setting power meter range to {value}, instead got {check_value}")
        return rng

    def aq820121_get_lambda(self, channel):
        loop = 0
        while loop < 3:
            self.instrument.write(f"C{channel}")
            self.instrument.write("D1")
            msg = self.instrument.query("PW?", wait=0.1, attempts=3)
            msg = msg.strip().decode()
            if "," in msg:
                print("bad msg from power meter", repr(msg))
                msg = ""
            if len(msg) > 0:
                try:
                    pow_str = msg.strip().split("PW")[1]
                except:
                    print("Problem parsing get_lambda",repr(msg))
                    pow_str = ""
                if len(pow_str) > 0:
                    wl = float(pow_str)
                    return wl
                else:
                    print("trying to lambda again")
                    loop += 1
            else:
                print("trying to lambda again")
                loop += 1
        print("Problem getting the wavelength from the power meter")
        wl = -1
        return wl

    def aq820121_set_lambda(self, channel, value):
        self.instrument.write(f"C{channel}")
        self.instrument.write("D1")
        self.instrument.write(f"PW{float(value)}")
        time.sleep(0.5)
        check_value = self.aq820121_get_lambda(channel)
        if f"{value:.1g}" != f"{check_value:.1g}":
            print(f"Problem setting wavelength on the power meter to {value}, instead got {check_value}")
            return -1
        return 0

    def aq820121_get_atim(self, channel):
        self.instrument.write(f'C{channel}')
        self.instrument.write("D1")
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

    def aq820121_set_atim(self, channel, value):
        self.instrument.write(f"C{channel}")
        self.instrument.write("D1")
        atime = self.atime_dict[value]
        self.instrument.write(f"PA{atime}")
        check_value = self.aq820121_get_atim(channel)
        if value != check_value:
            print(f"Problem setting power meter atime to {value}, instead got {check_value}")
        return

    def aq820121_set_unit(self, channel, value):
        self.instrument.write(f"C{channel}")
        self.instrument.write("D1")
        if value == 1:
            self.instrument.write("PFA")  #  Watt
        elif value == 0:
            self.instrument.write("PFB")  # dBm
        return

    def aq820121_get_unit(self, channel):
        self.instrument.write(f"C{channel}")
        self.instrument.write("D1")
        msgin = self.instrument.query("PF?")
        unit = msgin.strip().split("PF")[1]
        if unit == "A":
            return 1
        elif unit == "B":
            return 0
        else:
            return -1

    def aq820121_parse_power(self, msg):
        if len(msg) == 0:
            print(f"problem with msg{repr(msg)}")
            return float("nan")
        status = msg[2]
        if status != "I":
            return float("nan")
        unit = msg[4]
        if unit == "U":
            power = 10 ** (float(msg[6:]) / 10.0) * 1e-3
        else:
            unit = self.unit_dict[msg[4]]
            power = float(msg[6:]) * (10 ** unit)

        rng = msg[5]
        rng = self.aq820121_find_key(self.rng_dict, rng)
        return power

    def aq820121_get_power(self, channel):
        self.instrument.write(f"C{channel}")
        self.instrument.write("D1")
        splitstr = f"POD{channel}"
        while True:
            msgin = self.instrument.query("POD?", wait=0.1, attempts=1)
            if len(msgin) > 0:
                break
        try:
            msgin = msgin.strip().split(splitstr)[1]
            msgin = f"{channel}{msgin.split(",")[0]}"
        except:
            print(f"Problem parsing power{repr(msgin)}")
            msgin = ""

        if msgin == "":
            return float("nan")
        power = self.parse_power(msgin)
        return power

    def aq820121_get_status(self, channel):
        self.instrument.write(f"C{channel}")
        self.instrument.write("D1")
        msgin = self.instrument.query("POD?",.3).strip().split("POD")[1]
        if len(msgin) < 2:
            msgin = "ZZZ"
        return msgin[2]

    def aq820121_init_pwm_log(self, nreadings):
        self.nreadings = nreadings
        self.init_nreadings = nreadings

    def aq820121_stop_pwm_log(self):
        self.nreadings = 0
        return

    def aq820121_start_pwm_log(self):
        self.readings = []
        self.nreadings = self.init_nreadings
        self.measure_thread = threading.Timer(0, self.measure)
        self.measure_thread.start()

    def aq820121_wait(self):
        return

    def aq820121_measure(self, channel):
        self.aq820121_measure_wait_before(channel)
        return

    def aq820121_measure_wait_before(self, channel):
        for _ in range(self.nreadings):
            w_thread = threading.Timer(0.67, self.wait)
            w_thread.start()
            w_thread.join()
            with self.instrument.lock:
                power = self.aq820121_get_power(channel)
            self.readings.append(power)
        return

    def aq820121_measure_wait_after(self, channel):
        for counter in range(self.nreadings):
            power = self.aq820121_get_power(channel)
            self.readings.append(power)
            if counter == self.nreadings - 1:
                break
            w_thread = threading.Timer(1, self.wait)
            w_thread.start()
            w_thread.join()
        return

    def aq820121_measure_old(self, channel):
        if self.nreadings > 0:
            self.nreadings -= 1
            threading.Timer(1.1, self.aq820121_measure(channel)).start()
            power = self.aq820121_get_power(channel)
            self.readings.append(power)
        return

    def aq820121_measure2(self, channel):
        readings = []
        for _ in range(self.nreadings):
            readings.append(self.aq820121_get_power(channel))
        self.nreadings = 0
        return

    def aq820121_read_pwm_log(self):
        self.measure_thread.join()
        return np.array(self.readings)

    def aq820121_zero(self, channel):
        zeroing_pending = True
        while zeroing_pending:
            start = time.time()
            self.instrument.write(f"C{channel}")
            self.instrument.write("D1")
            self.instrument.write("PZ")
            time.sleep(1)
            while True:
                status = self.aq820121_get_status(channel)

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
    
    def aq820121_get_powmeter(self, channel):
        self.instrument.write(f"C{channel}")
        msg = self.instrument.query("D?")
        value = msg.strip().lstrip("D")
        print(f"get_powmeter{value}")
        return int(value)  #  Need to change to try exception here...

    def aq820121_set_powmeter(self, channel, value):
        self.instrument.write(f"C{channel}")
        self.instrument.write(f"D{value}")
        time.sleep(0.5)
        check_value = self.aq820121_get_powmeter(channel)
        if value != check_value:
            print(f"Problem setting which powermeter to {value}, instead got {check_value}")
        return
    










    # Attenuator Functions - aq820133
    def aq820133_get_att(self, channel):
        loop = 0
        while loop < 3:
            self.instrument.write(f"C{channel}")
            msg = self.instrument.query("AAV?")
            msg = msg.strip()
            msg = msg.decode()
            if len(msg) > 0:
                try:
                    return float(msg.strip().split("AAV")[1])
                except:
                    loop += 1
            else:
                loop += 1
        print("Problem getting attenuator value")
        return

    def aq820133_set_att(self, channel, value):
        self.instrument.write(f"C{channel}")
        self.instrument.write(f"AAV{np.abs(value)}\n")
        time.sleep(.2)
        check_value = self.aq820133_get_att(channel)
        if f"{value:.3g}" != f"{check_value:.3g}":
            print(f"Problem setting attenuator to {value}, instead set to {check_value}")
        return

    def aq820133_get_lambda(self, channel):
        self.instrument.write(f"C{channel}")
        msg = self.instrument.query("AW?\n")
        msg = msg.decode()
        if len(msg) > 2:
            return float(msg.strip().split("AW")[1])
        else:
            return float("nan")

    def aq820133_set_lambda(self, channel, value):
        self.instrument.write(f"C{channel}")
        value = int(np.around(value))  # resolution is nearest nm
        self.instrument.write(f"AW{int(np.around(value))}\n")
        time.sleep(.2)
        check_value = self.aq820133_get_lambda(channel)
        if f"{value:.3g}" != f"{check_value:.3g}":
            print(f"Problem setting lambda to {value}, instead set to {check_value}")
        return

    def aq820133_enable(self, channel):
        self.instrument.write(f"C{channel}")
        self.instrument.write("ASHTR1\n")
        if not self.aq820133_get_ASHTR(channel):
            print("Problem with enable")
        return

    def aq820133_disable(self, channel):
        self.instrument.write(f"C{channel}")
        self.instrument.write("ASHTR0\n")
        if self.aq820133_get_ASHTR(channel):
            print("Problem with disable")
        return

    def aq820133_get_ASHTR(self, channel):
        self.instrument.write(f"C{channel}")
        msg = self.instrument.query("ASHTR?")
        msg = msg.strip()
        msg = msg.decode()
        if len(msg) > 0:
            return "1" == (msg.strip().split("ASHTR")[1])
        return

    















    # Base Optical Switch - aq8201422
    def aq8201422_get_route(self, channel):
        loop = 0
        while loop < 3:
            self.instrument.write(f"C{channel}")
            self.instrument.write("D%d" % self.bank)
            msg = self.instrument.query("SASB?", 0.5)
            msg = msg.strip()
            msg = msg.decode()
            # print 'msg from get_route',msg
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

    def aq8201422_set_route(self, channel, value):
        self.instrument.write(f"C{channel}\n")
        self.instrument.write("D%d\n" % self.bank)
        self.instrument.write(f"SA1SB{value}\n")
        check_value = self.aq8201422_get_route(channel)
        if value != check_value:
            print(f"Problem setting route to {value}, instead got {check_value}")
        return

    def aq8201422_route(self, channel, value):
        self.aq8201422_set_route(channel, value)
















    # Base Optical Switch - aq820143
    def aq820143_get_route(self, channel):
        loop = 0
        while loop < 3:
            self.instrument.write(f"C{channel}")
            self.instrument.write("D%d" % self.bank)
            msg = self.instrument.query("SASB?", 0.5)
            msg = msg.strip()
            # print 'msg from get_route',msg
            if len(msg) > 0:
                if ("SSTRAIGHT" in msg) or ("SA1SB1" in msg):
                    self.output = 1
                elif ("SCROSS" in msg) or ("SA1SB2" in msg):
                    self.output = 2
                else:
                    self.output = 0
                return self.output
            else:
                loop += 1
        print("Problem getting route")
        self.output = -1
        return self.output

    def aq820143_set_route(self, channel, value):
        self.instrument.write(f"C{channel}\n")
        self.instrument.write("D%d\n" % self.bank)
        self.instrument.write(f"SA1SB{value}\n")
        check_value = self.aq820143_get_route(channel)
        if value != check_value:
            print(f"Problem setting route to {value}, instead got {check_value}")
        return 

    def aq820143_route(self, channel, value):
        self.aq820143_set_route(value, channel)







