from logic.Plupy import Plupy as pl

class pulse_generator:

    def __init__(self, port, baud_rate, bit_size, parity, stop_bits, connection):
        """        
        Class for the Quantum Composers Pulse Generator Series 9520
        
        CLASS ELEMENTS:
        
        port(string): Port in which the device is connected in the format of "COM##"
        
        baud_rate(int): Baud rate of the connected device defaults to 115200
        
        bit_size: bytesize, defaults to default to EIGHTBITS, need to use the serial library variables
                            accepts:
                                serial.EIGHTBITS, serial.SEVENBITS, serial.SIXBITS. serial.FIVEBITS
        
        parity: Parity, need to use the serial library variables
                            accepts: 
                                serial.PARITY_NONE, serial.PARITY_EVEN, serial.PARITY_ODD, serial.PARITY_MARK, serial.PARITY_SPACE
        
        stop_bits: Stopbits, need to use the serial library variables
                            accepts:
                                serial.STOPBITS_ONE, serial.STOPBITS_ONE_POINT_FIVE, serial.STOPBITS_TWO
                                
        connection: Serial Connection to the device. Must be created using initialize_device() or initialize_devices()
        """
        self.port = port
        self.baud_rate = baud_rate
        self.parity = parity
        self.stop_bits = stop_bits
        self.bit_size = bit_size
        self.connection = connection

    def run(self):
        """
        DESCRIPTION:
            Starts the Pulse Generator (equivalent to pressing the run/stop button)

        PARAMETERS:
            None
            
        RETURNS:
            res: Response from the Pulse generator
        """
        res = pl.command(":PULSE0:STATE ON\n", connection = self.connection)
        return res

    def stop(self):
        """
        DESCRIPTION:
            Stops the Pulse Generator (equivalent to pressing the run/stop button)
            
        PARAMETERS:
            None
        
        RETURNS:
            res: Response from the Pulse generator
        """        
        res = pl.command(":PULSE0:STATE OFF\n", connection = self.connection)
        return res
    
    def reset(self):
        """
        DESCRIPTION:
            Resets the Pulse Generator
            
        PARAMETERS:
            None
        
        RETURNS:
            res: Response from the Pulse generator
        """
        res = pl.command("*RST\n", connection = self.connection)
        return res

    def set_channel(self, channel, delay, width, amp = 3, mode = "TTL" ,ref = "T0", cmode = "SINGLE", enable = True):
        """
        DESCRIPTION:
            Sets all of the individual parameters of the specified channel
        
        PARAMETERS:
            channel: Channel to be set one of A, B, C or D
                                accepts:
                                    "A", "B", "C", "D"
            
            delay: delay in seconds for the pulse to be sent from the moment when the pulse generator starts
            
            width: width in seconds of the pulse
            
            amp (optional): amplitude of the pulse in Volts, will only be relevant if mode is adjustable, otherwise TTL is 5V. Defaults to 3V.
                                
            mode (optional): the mode of the output signal either defaults to "TTL"
                                accepts:
                                    "TTL", "ADJUSTABLE"
            
            ref (optional): Reference point of the delay (TO or one of the channels), default to TO
                                accepts:
                                    "T0", "CHA", "CHB", "CHC", "CHD"
            
            cmode (optional): Output mode of the pulse generator, default to Single Shot 
                                accepts:
                                    "NORMAL", "SINGLE", "BURTS", "DCYCLE"
            
            enable (optional): If True the channel will be enabled at the end of the settings, defaults to True
        
        RETURNS:
            True, if a
            ll settings are successfull

        """
        # Converting the imputs to String
        channel_str = str(ord(channel) - 64)
        delay_str = str(delay)
        width_str = str(width)
        amp_str = str(amp)
        
        
        if ref != "T0":
            ref = "CH" + ref
        
        pl.command(":PULSE" + channel_str + ":SYNC " + ref + "\n", repeat = True, connection = self.connection)
        pl.command(":PULSE" + channel_str + ":CMODE "+ cmode +"\n", repeat = True, connection = self.connection)
        pl.command(":PULSE" + channel_str + ":OUTPUT:AMPLITUDE " + amp_str + "V\n", repeat = True, connection = self.connection)
        pl.command(":PULSE" + channel_str + ":DELAY " + delay_str + "\n", repeat = True, connection = self.connection)
        pl.command(":PULSE" + channel_str + ":WIDTH " + width_str + "\n", repeat = True, connection = self.connection)
        pl.command(":PULSE" + channel_str + ":OUTPUT:MODE " + mode + "\n", repeat = True, connection = self.connection)
        
        if enable:
            pl.command(":PULSE" + channel_str + ":STATE ON\n", repeat = True, connection = self.connection)
        else:
            pl.command(":PULSE" + channel_str +":STATE OFF\n", repeat = True, connection = self.connection)
        
        return True

        
    def setup(self, flash_delay_s, prepulse_mode, exposure, laser):
        """
        DESCRIPTION:
            Calculates the time at which all the pulses must start so that to match the width of the pulse, and sets the channels accordingly

        PARAMETERS:
            flash_delay(float): Ideal time between the laser shot and the flashlamp in seconds with the smalles possible time being nanoseconds
            
            prepulse_mode(boolean): If prepulse_mode = True, then we're doing prepulse, if False, we're doing NO prepulse

            laser (str): "Q-Tune" or "PIRL"
        RETURNS:
            None
        """
        #constants
        

        
        print(f"flash delay in seconds {flash_delay_s}")
        
        # # The values are rounded to the 11th digit, since that is the precision of the Pulse Generator
        # if prepulse_mode == False: #NO prepulse
        #     print("\n\n\n here \n\n\n")
        #     # shift_correction_num = (13.2 + 0.3 - 1.5- 1.5)*1e-6
        #     shift_correction_num = -3e-9
        #     npp_flash_start = round(8*period+ flash_delay_s +shift_correction_num, 11) # the 8*period is entirely to allow enough delay time for hte shutter to open/close (it requires minimum 7ms to do this)
        # elif prepulse_mode == True: # prepulse
        #     # shift_correction_num = -2000*10e-9 + 17.9e-6 - 0.3e-6 + 1.2e-6 #! 16.8us
            
    
        
        exp = exposure * 1e-6
        exp_denom = 2 #1
        camera_delay = 100e-9 # The camera takes about 100 ns to actually start


        
        if laser == "Q-Tune":
            print("Laser is Q-Tune. Hope you wanted that.")
            period = 0.0039975 # Period of Q-Tune laser
            shift_correction_num = 305.4e-6 + 306.58e-9 #1.6 us PG delay from below, others from experimental correction

            flash_start = round(period + flash_delay_s + shift_correction_num , 11)  
        else:
            print("Laser is PIRL. Not sure why you would want that but here we are.")
            period = 2*0.00099997090 # Period of the PIRL Laser    
            shift_correction_num = -1.6e-6+1e-6+200e-9 

            #* Minimum 'reactino time' of pulse generator is 1.6us, 1us was added after
            pp_flash_start = round(period + flash_delay_s + shift_correction_num , 11)  
            npp_flash_start = pp_flash_start + 6e-3 -3e-6# adds 6ms delay

            flash_start = pp_flash_start if prepulse_mode else npp_flash_start
        
        camera_start = round(flash_start - exp/exp_denom - camera_delay, 11) #! currently Dly: 1987.14175us
        
        self.reset()
        self.set_trigger(level = 1.2)
        self.set_channel(channel = "C", delay = camera_start, width = 0.0005) # Cam
        self.set_channel(channel = "D", delay = flash_start, width = 0.000008) # Flash
        self.set_channel(channel = "B", delay = 0, width = 0.15) # Shutter # setting width to 8ms, change if needed

        print(f"flash start: {flash_start*10**6}us")
        print(f"camera start: {camera_start*10**6}us")
        return
    
    
  
    def set_trigger(self, level, edge = "RISING"):
        """
        DESCRIPTION:
            Sets the pulse generator to trigger mode and set the trigger parameters
            
        PARAMETERS:
            level: Required voltage to activate the trigger, 
                                accepts: 
                                    between 0.20V and 15V
            
            edge (optional): Edge logic of the trigger
                                accepts: 
                                    "RISING" or "FALLING", default to "RISING"
            
        RETURNS:
            True if sucessfull
        """
        # Converting the input to String
        level_str = str(level)
        
        pl.command(":PULSE0:TRIG:MODE TRIG\n", repeat = True, connection = self.connection)
        pl.command(":PULSE0:TRIGGER:LEVEL " + level_str + "\n", repeat = True, connection = self.connection)
        pl.command(":PULSE0:TRIGGER:EDGE " + edge + "\n", repeat = True, connection = self.connection)

        return True
        
    def set_gate(self, level, logic = "HIGH"):
        """
        DESCRIPTION:
            Set the pulse generator to gate mode and set the gate parameters
            
        PARAMETERS:
            level: Required voltage to activate the gate
            
            logic (optional): Gate logic
                                accepts:
                                    "HIGH" or "LOW", default to "HIGH"
            
        RETURNS:
            True if sucessfull
        """
        # Converting the input to String
        level_str = str(level)
        
        pl.command(":PULSE0:GATE:MODE PULSE\n", repeat = True, connection = self.connection)
        pl.command(":PULSE0:GATE:LEVEL " + level_str + "\n", repeat = True, connection = self.connection)
        pl.command(":PULSE0:GATE:LOGIC " + logic + "\n", repeat = True, connection = self.connection)

        return True 

