# IMPORTANT: In order for the oscilloscope to send correct measurements to the computer it needs to have
# the measure menu open on the left hand side of the screen (so you could read the measurement from the screen)
from logic.Plupy import Plupy as pl
import logging
import pyvisa

class oscilloscope:
    def __init__(self, model):
        """
        class for Tektronix TDS 2014C or DPO2024B oscilloscope 
        
        CLASS ELEMENTS:
            None
        """
        try:
            if(model == "TDS 2014C"):
                self.scope = pl.rm.open_resource('USB::0x0699::0x03A4::C015987::INSTR', send_end=True)
            elif(model == "DPO 2024B"):
                self.scope = pl.rm.open_resource('USB::0x0699::0x03A3::C031362::INSTR', send_end=True)
            self.scope.timeout = 5000
   
        except pyvisa.Error as e:
            print(f'Error opening oscilloscope: {str(e)}')
        
        
        pass
    
    def ready(self):
        """
        DESCRIPTION:
            tells the oscilloscope to wait for a single shot and when it recieves that single shot it will freeze, also puts oscilloscope to the measurement screen 
            
        PARAMETERS:
            None
            
        RETURNS:
            None
        """

        try:
            self.scope.write("ACQuire:STATE RUN")   
            self.scope.write("ACQuire:STOPAfter SEQuence")
        except Exception as e:
            logging.error(f"Scope failed: {e}")


         
          
        
        return 
    
    def setup(self, meas_num, meas_source, meas_type):
        """
        DESCRIPTION:
            Sets up the parameters for the measurement in the oscilloscope
            
        PARAMETERS:
            meas_num - the number between 1 and 5 spesifying the measurement on the oscilloscope which contains the desired value
                                    accepts (int): 1, 2, 3, 4 or 5
            meas_source - Channel used for the measurement
                                    accepts (int): 1, 2, 3 or 4
            
            meas_type - type of measurement, refeer to the manual: https://download.tek.com/manual/TBS1000-B-EDU-TDS2000-B-C-TDS1000-B-C-EDU-TDS200-TPS2000-Programmer.pdf
            
        RERTURN:
            None
        """
        meas_num_str = str(meas_num)
        meas_source_str = str(meas_source)
        
        try:
            self.scope.write("MEASUrement:MEAS"+ meas_num_str + ":SOUrce CH" + meas_source_str)
            self.scope.write("MEASUrement:MEAS"+ meas_num_str + ":TYPE " + meas_type)
        except Exception as e:
            logging.error(f"Scope failed: {e}")
        print("Completed tabletop oscilloscope setup")
        
    
    def save(self, mem = 1):
        """
        DESCRIPTION:
            saves the current settings to the memory location indicated
            
        PARAMETERS:
            mem - memory location block which desird settings will be located defaulst to 1
            
        RERTURN:
            None
        """
        mem_str = str(mem) 
        
        try:
            self.scope.write("SAVE:SETUP " + mem_str)  
        except Exception as e:
            logging.error(f"Scope failed: {e}")
        
        
        
        return 
        
    def recall(self, mem = 1):
        """
        DESCRIPTION:
            recalls the saved settings from the memory location indicated and tessl the oscilloscope to go to the measuremtn screen 
            
        PARAMETERS:
            mem - memory location block which desird settings are located defaults to 1

        RERTURN:
            None
        """

            
        mem_str = str(mem) 
        try:
            self.scope.write("RECALL:SETUP" + " " + mem_str)             #! space is important
        except Exception as e:
            logging.error(f"Scope failed: {e}")
     



        
    def get_value(self, meas_num):
        """
        DESCRIPTION:
            requests a measurement from the oscilloscope and prints it 
        
        PARAMETERS:
            meas_num - the number between 1 and 5 spesifying the measurement on the oscilloscope which contains the desired value
            
        RETURNS:
            voltage: The value measured for the voltage in the specified measurement number
        
        """
        meas_num_str = str(meas_num)
        
        try:
            voltage = float(self.scope.query("MEASUrement:MEAS" + meas_num_str + ":VALue?"))    
            return voltage

        except Exception as e:
            logging.error(f"Scope failed: {e}")


        