import pyvisa as visa


class FiberControlMPC101:
    """Class for controlling an MPC1 Polarization Controller."""

    axes = ['X', 'Y', 'Z']
    
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
        if axis not in self.axes:
            raise ValueError("Axis must be one of 'X', 'Y', or 'Z'.")
        response = self.query(f'{axis}?')
        return float(response.strip())
    
    def set_waveplate_positions(self, angles):
        for i, angle in enumerate(angles):
            self.write(f'{self.axes[i]}={angle:.2f}')
        return
    
    def set_rate(self, rate):
        """Set the speed of waveplate motion."""
        if not (1 <= rate <= 20):
            raise ValueError("Rate must be in the range 1-20.")
        self.write(f'RATE={rate}')