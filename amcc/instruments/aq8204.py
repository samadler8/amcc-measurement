import pyvisa
import numpy as np
import time

class aq8204:
    """Python class for Ando rack aq8204, written by Sam Adler
    Use like ando = aq8204('GPIB0::5::INsTR')"""
    def __init__(self, address):
        self.rm = pyvisa.ResourceManager()
        self.instrument = self.rm.open_resource(address)


    #Attenuator Functions - aq820133
    def identify(self):
        chassisid = super(dev, self).identify()
        self.meter.write("C%d" % self.slot)
        slotid = self.meter.query("MODEL?", 0.1).strip()
        return "# Chassis gpib %d: \t%s\n# Slot %d: \t\t%s\n" % (
            self.addr,
            chassisid,
            self.slot,
            slotid,
        )

    def writeconfig(self, fp):
        super(dev, self).writeconfig(fp)
        msgin = self.meter.query("MODEL?")
        fp.write("#  MODEL?: %s\n" % msgin.strip())
        msgin = self.meter.query("AD?")
        fp.write("#  AD?: %s\n" % msgin.strip())
        fp.flush()

    def get_att(self):
        loop = 0
        while loop < 3:
            self.meter.write("C%d" % self.slot)
            msg = self.meter.query("AAV?")
            msg = msg.strip()
            msg = msg.decode()
            if len(msg) > 0:
                try:
                    #print('Message is' + str(msg))
                    self.att = float(msg.strip().split("AAV")[1])
                    return self.att
                except:
                    loop += 1
            else:
                loop += 1
        print("Problem getting attenuator value")
        self.att = -1
        return self.att

    def set_att_core(self, value):
        self.meter.write("C%d\n" % self.slot)
        time.sleep(.2)
        value = np.abs(value)
        self.meter.write("AAV%.3f\n" % (value))
        time.sleep(.2)
        testvalue = self.get_att()
        if "%.3f" % value != "%.3f" % testvalue:
            print(
                "Problem setting attenuator to %.3f, got: %.3f, gpib: %d, slot: %d"
                % (value, testvalue, self.addr, self.slot)
            )
        self.att = testvalue
        return self.att

    def set_att(self, value):
        while True:
            msg = self.set_att_core(value)
            if "%.3f" % msg != "%.3f" % value:
                print("retry")
            else:
                break

    def get_lambda(self):
        # self.meter.write('C%d\n'%self.slot)
        self.set_slot()
        msg = self.meter.query("AW?\n")
        # print 'Msg from query',msg
        msg = msg.decode()
        if len(msg) > 2:
            self.wl = float(msg.strip().split("AW")[1])
            return self.wl
        else:
            return float("nan")

    def set_lambda(self, value):
        self.meter.write("C%d\n" % self.slot)
        time.sleep(.2)
        value = int(np.around(value))  # resolution is nearest nm
        self.meter.write("AW%d\n" % int(value))
        time.sleep(.2)
        wl = self.get_lambda()
        if "%d" % value != "%d" % wl:
            print(
                "Problem setting wavelength on the attenuator to %.1f, got:%.1f, gpib: %d, slot: %d got: %f"
                % (value, wl, self.addr, self.slot, wl)
            )
        return None

    def enable(self):
        while True:
            self.meter.write("C%d\n" % self.slot)
            self.meter.write("ASHTR1\n")
            if not self.get_enable():
                print("Problem with enable")
            else:
                break
        return None

    def disable(self):
        while True:
            self.meter.write("C%d\n" % self.slot)
            self.meter.write("ASHTR0\n")
            if self.get_enable():
                print("Problem with disable")
            else:
                break
        return None

    def get_enable(self):
        self.meter.write("C%d" % self.slot)
        msg = self.meter.query("ASHTR?")
        msg = msg.strip()
        msg = msg.decode()
        if len(msg) > 0:
            return "1" == (msg.strip().split("ASHTR")[1])
        return None

    def set_attenuation(self, channel, attenuation_value):
        """Set the attenuation level for the attenuator module."""
        self.instrument.write(f"C{channel}")
        if 0 <= attenuation_value <= 60:  # Typical range; adjust based on module specs
            self.instrument.write(f"AAV{attenuation_value:.3f}")
        else:
            print("Error: Attenuation value out of range.")



    # Base Laser aq8201
    def std_init(self):
        self.meter.write("C%d" % self.slot)
        self.meter.write("LUS0")  # Set to wavelength units of nm
        self.meter.write("LEMO0")  # Set to external modulation off
        self.meter.write("LIMO0")  # Set internal to CW
        self.meter.write("LCOHR1")  # Set coherence ctrl on (wide bandwidth)
        """
        self.meter.write('C%d'%self.slot)
        self.wlmin = self.meter.query('LWMIN?').strip().lstrip('LWMIN')
        self.wlmin = float(self.wlmin)
        self.meter.write('C%d'%self.slot)
        #time.sleep(1)
        self.wlmax = self.meter.query('LWMAX?').strip().lstrip('LWMAX')
        self.wlmax = float(self.wlmax)
        print 'WL range: ',self.wlmin, self.wlmax
        """

    def identify(self):
        chassisid = super(dev, self).identify()
        # self.meter.write('C%d'%self.slot)
        # should we do a MOD?
        # slotid = self.meter.query('MOD?',0.1)
        slotid = ""
        return "# Chassis gpib %d: \t%s\n# Slot %d: \t\t%s\n" % (
            self.addr,
            chassisid,
            self.slot,
            slotid,
        )

    def writeconfig(self, fp):
        super(dev, self).writeconfig(fp)
        self.meter.write("C%d" % self.slot)
        msgin = self.meter.query("MODEL?")
        fp.write("#  MODEL?: %s\n" % msgin.strip())
        self.meter.write("C%d" % self.slot)
        msgin = self.meter.query("LD?")
        fp.write("#  LD?: %s\n" % msgin.strip())
        cohl = self.get_cohl()
        fp.write("#  Coherence Control: %d\n" % cohl)
        lwlcal = self.get_lwlcal()
        fp.write("#  LWLCAL: %.2f\n" % lwlcal)
        latl = self.get_latl()
        fp.write("#  LATL: %.2f\n" % latl)
        fp.flush()

    def get_lambda(self):
        # self.meter.write('C%d'%self.slot)
        self.set_slot()
        msg = self.meter.query("LW?")
        if len(msg.strip()) == 0:
            self.wl = float("NaN")
            # print 'Trying to read again',repr(self.meter.read(100))
        else:
            self.wl = float(msg.strip().decode().lstrip("LW"))
        return self.wl

    def set_lambda(self, value):
        loop = 0
        while loop < 3:
            self.meter.write("C%d" % self.slot)
            value = "%.1f" % np.around(value, 1)
            self.meter.write("LW%s" % (value))
            self.wl = self.get_lambda()
            if value != "%.1f" % self.wl:
                loop += 1
            else:
                return 0
        print(
            "Problem setting wavelength on the laser to %d, gpib: %d, slot: %d got:%f"
            % (value, self.addr, self.slot, self.wl)
        )
        return -1

    def get_cmd(self, cmd):
        loop = 0
        while loop < 3:
            self.meter.write("C%d" % self.slot)
            msg = self.meter.query("%s?" % cmd)
            msg = msg.strip()
            if len(msg) > 0:
                value = float(msg.strip().split(cmd)[1])
                return value
            else:
                loop += 1
        print("Problem getting cohl from the laser")
        value = -1
        return value

    def get_lopt(self):
        self.lopt = self.get_cmd("LOPT")
        self.lopt = int(self.lopt)
        if self.lopt < 0:
            return -1
        else:
            return self.lopt

    """
    def set_lopt(self,value):
        self.meter.write('C%d'%self.slot)
        self.meter.write('LOPT %d'%value)
        self.lopt=self.get_lopt()
        if value != self.lopt:
            print 'Problem setting lopt on the laser to %d, gpib: %d, slot: %d got: %f'%(value, self.addr, self.slot,self.lopt)
            return -1
        return 0
    """

    def get_cohl(self):
        loop = 0
        while loop < 3:
            self.meter.write("C%d" % self.slot)
            msg = self.meter.query("LCOHR?")
            msg = msg.strip()
            if len(msg) > 0:
                self.cohl = float(msg.strip().lstrip("LCOHR"))
                return self.cohl
            else:
                loop += 1
        print("Problem getting cohl from the laser")
        self.cohl = -1
        return self.cohl

    def set_cohl(self, value):
        self.meter.write("C%d" % self.slot)
        value = int(value)
        if value > 1:
            value = 1
        self.meter.write("LCOHR%d" % int(value))
        if value != self.get_cohl():
            print(
                "Problem setting cohl on the laser to %d, gpib: %d, slot: %d"
                % (value, self.addr, self.slot)
            )
        return None

    def set_power(self, value_W):
        self.meter.write("C%d" % self.slot)
        value = 10. * math.log10(value_W) + 30
        self.meter.write("LPL%.2f" % float(value))
        if value_W != self.get_power():
            print(
                "Problem setting the power on the laser to %f, gpib: %d, slot: %d"
                % (value_W, self.addr, self.slot)
            )
        return None

    def get_power(self):
        self.meter.write("C%d" % self.slot)
        msgin = self.meter.query(b"LPL?")
        # print 'power msgin',msgin
        power = 10. ** (float(msgin)) * 1e-3
        return power

    def set_lopt(self, value):
        self.meter.write("C%d" % self.slot)
        self.meter.write("LOPT%d" % value)

    def set_lwlcal(self, value):
        self.meter.write("C%d" % self.slot)
        value = "%.2f" % np.around(value, 2)
        self.meter.write("LWLCAL%s" % (value))
        if value != "%.2f" % self.get_lwlcal():
            print(
                "Problem setting the lwcal on the laser to %s, gpib: %d, slot: %d"
                % (value, self.addr, self.slot)
            )
        return None

    def set_latl(self, value):
        self.meter.write("C%d" % self.slot)
        self.meter.write("LATL%.2f" % float(value))
        if value != self.get_latl():
            print(
                "Problem setting the latl level on the laser to %f, gpib: %d, slot: %d"
                % (value, self.addr, self.slot)
            )
        return None

    def get_lwlcal(self):
        self.meter.write("C%d" % self.slot)
        msgin = self.meter.query("LWLCAL?").strip().lstrip("LWLCAL")
        return float(msgin)

    def get_latl(self):
        self.meter.write("C%d" % self.slot)
        # self.meter.write('LATL?')
        # msgin = self.meter.read(100)
        msgin = self.meter.query("LATL?", 0.5)
        msgin = msgin.strip().lstrip("LATL")
        try:
            ans = float(msgin)
        except:
            print("could not convert %s" % repr(msgin))
            ans = float("nan")
        return ans

    def enable(self):
        self.set_lopt(1)

    def disable(self):
        self.set_lopt(0)

    def get_status(self):
        self.meter.write("C%d" % self.slot)
        start = time.time()
        # while True: # wait while zeroing
        msgin = self.meter.query("LMSTAT?").strip().lstrip("LMSTAT")
        print("get_status", msgin)
        if len(msgin) != 1:
            msgin = "ZZZ"
        return msgin

    # Base Optical Power Meter - aq820121
    def std_init(self):
        self.meter.write("C%d" % self.slot)
        self.meter.write("D%d" % self.powmeter)
        self.meter.write("PMO0")  # Set CW
        self.meter.write("PDR0")  # Set no reference
        self.meter.write("PH0")  # No max/min measurement
        self.meter.write("PAD")  # average 10
        self.meter.write("PFB")  # Unit: W
        print("std_init get_lambda", self.get_lambda())
        self.set_unit(1)

    def identify(self):
        chassisid = super(dev, self).identify()
        self.meter.write("C%d" % self.slot)
        self.meter.write("D%d" % self.powmeter)

        # should we do a MOD?
        slotid = self.meter.query("MODEL?", 0.1).strip()
        # slotid = self.meter.query('MOD?',0.1)
        return "# Chassis gpib %d: \t%s\n# Slot %d: \t\t%s\n" % (
            self.addr,
            chassisid,
            self.slot,
            slotid,
        )

    def writeconfig(self, fp):
        super(dev, self).writeconfig(fp)
        msgin = self.meter.query("MODEL?")
        fp.write("#  MODEL?: %s\n" % msgin.strip())
        fp.write("#  UNIT?: %d\n" % self.get_unit())
        fp.flush()

    def get_range(self):
        self.meter.write("C%d" % self.slot)
        self.meter.write("D%d" % self.powmeter)
        msg = self.meter.query("PR?")
        try:
            value = msg.strip().split("PR")[1]
        except:
            print("Problem parsing range",repr(msg))
            value = ""
        key = None
        for k in list(rng_dict.keys()):
            if rng_dict[k] == value:
                key = k
                break
        if key == None:
            if value == "A":
                key = "A"
            else:
                key = float("NaN")
        return key

    def set_range(self, value):
        self.meter.write("C%d" % self.slot)
        self.meter.write("D%d" % self.powmeter)
        if type(value) == str:
            rng = value.upper()
        else:
            rng = rng_dict[int(value)]
        self.meter.write("PR%c" % rng)
        check = self.get_range()
        if value != check:
            if type(value) == str:
                print(
                    "Problem setting power meter range to %c, gpib: %d, slot: %d set to:%s"
                    % (value, self.addr, self.slot, repr(check))
                )
            else:
                print(
                    "Problem setting power meter range to %d, gpib: %d, slot: %d set to: %s"
                    % (value, self.addr, self.slot, repr(check))
                )
        return rng

    def get_lambda(self):
        loop = 0
        while loop < 3:
            # self.meter.write('C%d'%self.slot)
            self.set_slot()
            self.meter.write("D%d" % self.powmeter)
            msg = self.meter.query("PW?", wait=0.1, attempts=3)
            # if len(msg)==0:
            #    msg = self.meter.read()
            msg = msg.strip().decode()
            if "," in msg:
                print("bad msg from power meter", repr(msg))
                msg = ""
            # print loop,repr(msg)
            if len(msg) > 0:
                # print 'get_lambda: ',repr(msg)
                try:
                    pow_str = msg.strip().split("PW")[1]
                except:
                    print("Problem parsing get_lambda",repr(msg))
                    pow_str = ""
                # print 'get_lambda: ',repr(pow_str)
                if len(pow_str) > 0:
                    self.wl = flt(pow_str)
                    return self.wl
                else:
                    print("trying to lambda again")
                    loop += 1
            else:
                print("trying to lambda again")
                loop += 1
        print("Problem getting the wavelength from the power meter")
        self.wl = -1
        return self.wl
        """
        self.meter.write('C%d'%self.slot)
        msg = self.meter.query('PW?')
        self.wl = float(msg.strip().lstrip('PW'))
        return self.wl
        """

    def set_lambda(self, value):
        self.meter.write("C%d" % self.slot)
        self.meter.write("D%d" % self.powmeter)
        # value = int(value)
        self.meter.write("PW%.1f" % float(value))
        time.sleep(0.5)
        wl = self.get_lambda()
        if "%.1f" % value != "%.1f" % wl:
            print(
                "Problem setting wavelength on the power meter to %d, gpib: %d, slot: %d got:%f"
                % (value, self.addr, self.slot, wl)
            )
            return -1
        return 0

    def get_atim(self):
        # self.meter.write('C%d'%self.slot)
        self.set_slot()
        self.meter.write("D%d" % self.powmeter)
        msg = self.meter.query("PA?")
        key = None

        if len(msg) > 0:
            try:
                value = msg.strip().split("PA")[1]
            except:
                print("Problem parsing atim",repr(msg))
                value = ""
            for k in list(atime_dict.keys()):
                if atime_dict[k] == value:
                    key = k
                    break
        if key == None:
            key = float("NaN")
        return key

    def set_atim(self, value):
        self.meter.write("C%d" % self.slot)
        self.meter.write("D%d" % self.powmeter)
        atime = atime_dict[value]
        self.meter.write("PA%c" % atime)
        if value != self.get_atim():
            print(
                "Problem setting power meter atime to %d, gpib: %d, slot: %d"
                % (value, self.addr, self.slot)
            )
        return None

    def set_unit(self, value):
        self.meter.write("C%d" % self.slot)
        self.meter.write("D%d" % self.powmeter)
        if value == 1:
            self.meter.write("PFA")  #  Watt
        elif value == 0:
            self.meter.write("PFB")  # dBm
        return None

    def get_unit(self):
        self.meter.write("C%d" % self.slot)
        self.meter.write("D%d" % self.powmeter)
        msgin = self.meter.query("PF?")
        unit = msgin.strip().split("PF")[1]
        if unit == "A":
            return 1
        elif unit == "B":
            return 0
        else:
            return -1

    def parse_power(self, msg):
        # print 'parse power meter mesg',repr(msg)
        if len(msg) == 0:
            print("problem with msg", repr(msg))
            return float("nan")
        # print('parse_power',repr(msg))
        # print repr(msg)
        ch = int(msg[:2])
        status = msg[2]
        if status != "I":
            # print ('power meter not in range: ',status)
            return float("nan")
        measure = int(msg[3])
        unit = msg[4]
        if unit == "U":
            power = 10 ** (old_div(float(msg[6:]), 10.)) * 1e-3
        else:
            unit = unit_dict[msg[4]]
            power = float(msg[6:]) * (10 ** unit)

        # unit = find_key(unit_dict,unit)
        rng = msg[5]
        rng = find_key(rng_dict, rng)
        # rng = rng_dict[msg[5]]
        return power

    def get_power(self):
        self.set_slot()
        self.meter.write("D%d" % self.powmeter)
        splitstr = "POD%02d" % self.slot
        while True:
            msgin = self.meter.query("POD?", wait=0.1, attempts=1)
            if len(msgin) > 0:
                break
        try:
            msgin = msgin.strip().split(splitstr)[1]
            msgin = "%02d" % self.slot + msgin.split(",")[0]
        except:
            print("Problem parsing power", repr(msgin))
            msgin = ""

        # print msgin
        if msgin == "":
            return float("nan")
        power = self.parse_power(msgin)
        #  Need to parse power to get the reading
        #        print "in power"
        #        print power
        #        print "return"
        return power

    def get_status(self):
        time.sleep(0.2)
        self.meter.write("C%d" % self.slot)
        self.meter.write("D%d" % self.powmeter)
        start = time.time()
        # while True: # wait while zeroing
        msgin = self.meter.query("POD?",.3).strip().split("POD")[1]
        # print 'get_status',msgin
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
        # self.measure_thread = threading.Thread(None, self.measure,args=(readings))
        self.readings = []
        self.nreadings = self.init_nreadings
        # self.lock = threading.RLock()
        # self.measure_thread = threading.Timer(0, self.measure,[self.readings])
        self.measure_thread = threading.Timer(0, self.measure)
        self.measure_thread.start()

    # def measure(self, readings):
    def wait(self):
        return

    def measure(self):
        self.measure_wait_before()

    def measure_wait_before(self):
        # start = time.time()
        for counter in range(self.nreadings):
            w_thread = threading.Timer(0.67, self.wait)
            w_thread.start()
            w_thread.join()
            with self.meter.lock:
                power = self.get_power()
            # print self, time.time(), power
            self.readings.append(power)
        # stop = time.time()
        # print 'dt:',stop-start

    def measure_wait_after(self):
        for counter in range(self.nreadings):
            power = self.get_power()
            self.readings.append(power)
            if counter == self.nreadings - 1:
                break
            w_thread = threading.Timer(1, self.wait)
            w_thread.start()
            w_thread.join()

    def measure_old(self):
        # print self.nreadings
        if self.nreadings > 0:
            # threading.Timer(1.01, self.measure, [readings]).start()
            self.nreadings -= 1
            threading.Timer(1.1, self.measure).start()
            power = self.get_power()
            # print power
            self.readings.append(power)
            # print 'measure readings',self.readings
            # print self.nreadings

    def measure2(self):
        readings = []
        for loop in range(self.nreadings):
            readings.append(self.get_power())
        self.nreadings = 0

    def read_pwm_log(self):
        # while self.nreadings>0:
        # while len(self.readings) != self.init_nreadings:
        #    time.sleep(1)
        self.measure_thread.join()
        # print 'read_pwm_log',self.readings
        return np.array(self.readings)

    def zero(self):
        zeroing_pending = True
        while zeroing_pending:
            start = time.time()
            self.meter.write("C%d" % self.slot)
            self.meter.write("D%d" % self.powmeter)
            self.meter.write("PZ")
            # check status until zero is complete
            time.sleep(1)
            while True:
                status = self.get_status()

                if "Z" not in status:
                    zeroing_pending = False
                    break
                elif (time.time() -start) > 100:
                    break
                else:
                    time.sleep(1)
            t = time.time() - start
        print("Done zero: %.2f" % (t))
        return t
    
    # aq820121
    def get_powmeter(self):
        self.meter.write("C%d" % self.slot)
        msg = self.meter.query("D?")
        value = msg.strip().lstrip("D")
        print(("get_powmeter", value))
        return int(value)  #  Need to change to try exception here...

    def set_powmeter(self, value):
        self.meter.write("C%d" % self.slot)
        while True:
            self.meter.write("D%d" % value)
            time.sleep(0.5)
            # print 'readline after setting',repr(self.meter.readline())
            check = self.get_powmeter()
            if value != check:
                print(
                    "Problem setting which powermeter to %d, gpib: %d, slot: %d"
                    % (value, self.addr, self.slot)
                )
        return value

    def identify(self):
        # print('called identify')
        msg = super(dev, self).identify()
        msg += "#  power meter: %d\n" % self.powmeter
        return msg

    # Base Optical Switch - aq820143
    def identify(self):
        chassisid = super(dev, self).identify()
        self.meter.write("C%d" % self.slot)
        slotid = self.meter.query("MOD?", 0.1).strip()
        return "# Chassis gpib %d: \t%s\n# Slot %d: \t\t%s\n" % (
            self.addr,
            chassisid,
            self.slot,
            slotid,
        )

    def writeconfig(self, fp):
        super(dev, self).writeconfig(fp)
        msgin = self.meter.query("MODEL?")
        fp.write("#  MODEL?: %s\n" % msgin.strip())
        # msgin = self.meter.query('AD?')
        # fp.write('#  AD?: %s\n'%msgin.strip())
        fp.flush()

    def get_route(self):
        loop = 0
        while loop < 3:
            self.meter.write("C%d" % self.slot)
            self.meter.write("D%d" % self.bank)
            msg = self.meter.query("SASB?", 0.5)
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
        """
        self.meter.write('C%d\n'%self.slot)
        msg = self.meter.query('AAV?\n')
        self.att = float(msg.strip().lstrip('AAV'))
        return self.att
	"""

    def set_route(self, value):
        self.meter.write("C%d\n" % self.slot)
        self.meter.write("D%d\n" % self.bank)
        self.meter.write("SA1SB%d\n" % (value))
        # print 'get_route from set_route',self.get_route()
        if value != self.get_route():
            print(
                "Problem setting route to %d, gpib: %d, slot: %d"
                % (value, self.addr, self.slot)
            )
        return self.output

    def route(self, value):
        self.set_route(value)



    # Base Optical Switch - aq8201422
    def identify(self):
        chassisid = super(dev, self).identify()
        self.meter.write("C%d" % self.slot)
        slotid = self.meter.query("MOD?", 0.1).strip()
        return "# Chassis gpib %d: \t%s\n# Slot %d: \t\t%s\n" % (
            self.addr,
            chassisid,
            self.slot,
            slotid,
        )

    def writeconfig(self, fp):
        super(dev, self).writeconfig(fp)
        msgin = self.meter.query("MODEL?")
        fp.write("#  MODEL?: %s\n" % msgin.strip())
        # msgin = self.meter.query('AD?')
        # fp.write('#  AD?: %s\n'%msgin.strip())
        fp.flush()

    def get_route(self):
        loop = 0
        while loop < 3:
            self.meter.write("C%d" % self.slot)
            self.meter.write("D%d" % self.bank)
            msg = self.meter.query("SASB?", 0.5)
            msg = msg.strip()
            msg = msg.decode()
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
        """
        self.meter.write('C%d\n'%self.slot)
        msg = self.meter.query('AAV?\n')
        self.att = float(msg.strip().lstrip('AAV'))
        return self.att 
	"""

    def set_route(self, value):
        self.meter.write("C%d\n" % self.slot)
        self.meter.write("D%d\n" % self.bank)
        self.meter.write("SA1SB%d\n" % (value))
        # print 'get_route from set_route',self.get_route()
        if value != self.get_route():
            print(
                "Problem setting route to %d, gpib: %d, slot: %d"
                % (value, self.addr, self.slot)
            )
        return self.output

    def route(self, value):
        self.set_route(value)