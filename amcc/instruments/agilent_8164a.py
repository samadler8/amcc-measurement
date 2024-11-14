# -*- coding: utf-8 -*-
"""
Created on Tue Jul 16 08:00:39 2019

@author: smb2
"""

import visa
import time
import numpy as np
from pyvisa.resources import MessageBasedResource

class Agilent8164A(object):
    """Python class for Agilent E5061B Network Analyzer, written by Sonia, modified from Adams code"""

    def __init__(self, visa_name):
        self.rm = visa.ResourceManager()
        self.pyvisa = self.rm.open_resource(visa_name)
        self.pyvisa.timeout = 5000 # Set response timeout (in milliseconds)
        # self.pyvisa.query_delay = 1 # Set extra delay time between write and read commands

    def read(self):
        return self.pyvisa.read()
    
    def read_raw(self):
        return self.pyvisa.read_raw()
    
    def read_hex(self):
        return self.query_ascii_values(converter='x')
    
    def write(self, string):
        self.pyvisa.write(string)

    def query(self, string):
        return self.pyvisa.query(string)

    def close(self):
        self.pyvisa.close()

    def reset(self):
        self.write('*RST')
        self.timeout = 1
        
    def identify(self):
        return self.query('*IDN?')

    def set_laser_wav(self, wavelength_nm=1550, slot=0):
        self.write('SOUR'+str(slot)+':WAV '+str(wavelength_nm)+'NM')
 
    def set_laser_pow(self, power_dbm=6, slot=0):
        self.write('SOUR'+str(slot)+':POW '+str(power_dbm)+'DBM')

    def get_laser_wav(self, slot=1):
        return self.query('SOUR'+str(slot)+':WAV?')

    def set_meter_wav(self, wavelength_nm = 1550, slot=2):
        return self.write('SENS'+str(slot)+':POW:WAV '+str(wavelength_nm)+'NM')

    def get_meter_pow(self, slot=2):
        return self.query('READ'+str(slot)+':POW?')
            
    def toggle_laser(self, on=0, slot=1):
        self.write('OUTP'+str(slot)+':CHAN1:STAT '+str(on))
        
    def set_att(self, slot=3, attenuation = 15):
        self.write('INP'+str(slot)+':ATT '+str(attenuation))
 
    def get_att(self, slot=3):
        self.write('INP'+str(slot)+':ATT?')
        
    def set_att_wav(self, wavelength_nm=1550, slot=3):
        self.write('INP'+str(slot)+':WAV '+str(wavelength_nm)+' NM')
        
    def setup_lambda_sweep(self, start = 1510, stop = 1550, step = 20, speed = 20, slot = 3):
        self.write("sour"+str(slot)+":wav:swe:star "+str(start)+"nm")
        self.write("sour"+str(slot)+":wav:swe:stop "+str(stop)+"nm")
        self.write("sour"+str(slot)+":wav:swe:step "+str(step)+"pm")
        self.write("sour"+str(slot)+":wav:swe:spe "+str(speed)+"nm/s")
        self.write("sour"+str(slot)+":wav:swe:mode cont")
        self.write("sour"+str(slot)+":wav:swe:llog 1")
 
    def run_lambda_sweep(self, laser_slot = 3, pm_slot = 4):
        self.write("sens"+str(pm_slot)+":func:stat logg,star")
        self.write("sens"+str(pm_slot)+":func:res?")
        self.write("sour"+str(laser_slot)+":wav:swe 1")
        powerdata = self.read_raw()
        time.sleep(1)
        self.write("sour"+str(laser_slot)+":read:data? llog")
        wavelengthdata = self.read_raw()
        return wavelengthdata, powerdata