import visa
import time

class Switchino(object):
    """Python class for a single-pull 10-throw switch,
    written by Adam McCaughan"""
    def __init__(self, visa_name):
        self.rm = visa.ResourceManager()
        self.pyvisa = self.rm.open_resource(visa_name)
        self.pyvisa.timeout = 5000 # Set response timeout (in milliseconds)
        self.pyvisa.query_delay = 1 # Set extra delay time between write and read commands

    def read(self):
        return self.pyvisa.read()
        time.sleep(1)
        
    def write(self, string):
        self.pyvisa.write(string)
        time.sleep(1)
    
    def query(self, string):
        return self.pyvisa.query(string)
        time.sleep(1)
    
    def close(self):
        self.pyvisa.close()
        time.sleep(1)
        
    def identify(self):
        return self.query('*IDN?')
        time.sleep(1)

    def select_port(self, port = 2, switch = 1):
        if port is None:
            self.disable(switch = switch)
            time.sleep(1)
        else:
            self.query('SWITCH %s PORT %s' % (switch, port))
        time.sleep(1)
        return port

    def select_ports(self, port_pair = (3,5)):
        self.select_port(port = port_pair[0], switch = 1)
        time.sleep(1)
        self.select_port(port = port_pair[1], switch = 2)
        time.sleep(1)
        return port_pair

    def disable(self, switch = None):
        if switch is None:
            self.query('SWITCH 1 OFF')
            time.sleep(1)
            self.query('SWITCH 2 OFF')
            time.sleep(1)
        if switch == 1:
            self.query('SWITCH 1 OFF')
            time.sleep(1)
        if switch == 2:
            self.query('SWITCH 2 OFF')
            time.sleep(1)
        
# g = GenericInstrument('GPIB0::24')
# g.identify()




