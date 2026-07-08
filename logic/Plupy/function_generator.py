from logic.Plupy import Plupy as pl
import time
import pyvisa

class function_generator:
    def __init__(self):
        """
        class for Tektronix AFG3101C Function Generator
        
        CLASS ELEMENTS:
            None
        """
        pass
    
    def restart(self):
        """
        DESCRIPTION:
            Restart the funciton generator
            
        PARAMETERS:
            None
            
        RETURNS:
            None
        """
        try:
            fg = pl.rm.open_resource('USB::0x0699::0x034B::C010943::INSTR', send_end=True)
            fg.timeout = None
        except pyvisa.Error as e:
            print(f'Error opening Function Generator: {str(e)}')


        # if the time stamps collected indicate the laser stopped do these, otherwise do nothing    
        fg.write("OUTput1:STATe OFF")   
        time.sleep(3)
        fg.write("OUTput1:STATe ON")   
        
    def start(self):
        """
        DESCRIPTION:
            Turn on the function generator output
            
        PARAMETERS:
            None
            
        RETURNS:
            None
        """
        try:
            fg = pl.rm.open_resource('USB::0x0699::0x034B::C010943::INSTR', send_end=True)
            fg.timeout = None
        except pyvisa.Error as e:
            print(f'Error opening Function Generator: {str(e)}')
   
        fg.write("OUTput1:STATe ON")   
        
    def end(self):
        """
        DESCRIPTION:
            Turn off the function generator output
            
        PARAMETERS:
            None
            
        RETURNS:
            None
        """
        try:
            fg = pl.rm.open_resource('USB::0x0699::0x034B::C010943::INSTR', send_end=True)
            fg.timeout = None
        except pyvisa.Error as e:
            print(f'Error opening Function Generator: {str(e)}')
  
        fg.write("OUTput1:STATe OFF")   

    
    
        
        
    def setup(self):
        """
        DESCRIPTION:
            Set the function generator to correct settings
            
        PARAMETERS:
            None
            
        RETURNS:
            None
        """
        try:
            fg = pl.rm.open_resource('USB::0x0699::0x034B::C010943::INSTR', send_end=True)
            fg.timeout = None
        except pyvisa.Error as e:
            print(f'Error opening Function Generator: {str(e)}')


        fg.write("SOURce1:PULSe:PERiod 200e-6s")

        fg.write("SOURce1:PULSe:WIDth 100e-6s")
        
        fg.write("SOURce1:VOLTage:LIMit:HIGH 4.5V")
        
        fg.write("SOURce1:VOLTage:LIMit:LOW 0V")
        
        fg.write("SOURce1:VOLTage:LEVel:IMMediate:HIGH 4.5V")
        
        fg.write("SOURce1:VOLTage:LEVel:IMMediate:LOW 0V")
        
        
        
        fg.write("SOURce1:BURSt:MODE TRIGgered")
        
        fg.write("SOURce1:BURSt:NCYCles 1")
        
        #more need to be added***
