import visa
import numpy as np
import time


class FiberControlMPC101:
    """Class for controlling an MPC1 Polarization Controller."""
    
    def __init__(self, visa_name):
        self.rm = visa.ResourceManager()
        self.pyvisa = self.rm.open_resource(visa_name)
        self.pyvisa.timeout = 5000  # Set response timeout (in milliseconds)

    def read(self):
        return self.pyvisa.read()
    
    def write(self, command):
        self.pyvisa.write(command)
    
    def query(self, command):
        return self.pyvisa.query(command)
    
    def close(self):
        self.pyvisa.close()
    
    def identify(self):
        return self.query('*IDN?')
    
    def reset(self):
        """Reset the polarization controller."""
        self.write('*RST')
    
    def center_waveplates(self):
        """Center all waveplates."""
        self.write('CEN')
    
    def set_waveplate_position(self, axis, angle):
        """Set the position of a waveplate axis.
        Args:
            axis (str): 'X', 'Y', or 'Z'
            angle (float): Angle in degrees (-99.00° to +99.00°)
        """
        if axis not in ['X', 'Y', 'Z']:
            raise ValueError("Axis must be one of 'X', 'Y', or 'Z'.")
        self.write(f'{axis}={angle:.2f}')
    
    def get_waveplate_position(self, axis):
        """Get the position of a waveplate axis.
        Args:
            axis (str): 'X', 'Y', or 'Z'
        Returns:
            float: Current angle of the axis.
        """
        if axis not in ['X', 'Y', 'Z']:
            raise ValueError("Axis must be one of 'X', 'Y', or 'Z'.")
        response = self.query(f'{axis}?')
        return float(response.strip())
    
    def set_rate(self, rate):
        """Set the speed of waveplate motion."""
        if not (1 <= rate <= 20):
            raise ValueError("Rate must be in the range 1-20.")
        self.write(f'RATE={rate}')
    
    def sweep_polarizations(self, detector, step=1.0):
        """Sweep through all polarizations to find max and min counts.
        Args:
            detector (object): Detector object with a `get_counts()` method.
            step (float): Step size in degrees for the sweep.
        Returns:
            dict: A dictionary with max and min polarization settings and counts.
        """
        positions = np.arange(-99.0, 100.0, step)
        max_counts = -np.inf
        min_counts = np.inf
        max_position = None
        min_position = None

        for x in positions:
            for y in positions:
                for z in positions:
                    self.set_waveplate_position('X', x)
                    self.set_waveplate_position('Y', y)
                    self.set_waveplate_position('Z', z)
                    time.sleep(0.1)  # Wait for the motion to complete
                    counts = detector.get_counts()
                    if counts > max_counts:
                        max_counts = counts
                        max_position = (x, y, z)
                    if counts < min_counts:
                        min_counts = counts
                        min_position = (x, y, z)
        
        return {
            'max_counts': max_counts,
            'max_position': max_position,
            'min_counts': min_counts,
            'min_position': min_position
        }
