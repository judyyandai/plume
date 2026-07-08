from logic.Plupy import Plupy as pl

class pirl:
    def __init__(self, port, baud_rate, bit_size, parity, stop_bits, connection):
        """        
        Class for the PIRL
        
        CLASS ELEMENTS:
        
        port(string): Port in which the device is connected in the format of "COM##"
        
        baud_rate(int): Baud rate of the connected device defaults to 19200
        
        bit_size: bytesize, defaults to EIGHTBITS, need to use the serial library variables
                            accepts:
                                serial.EIGHTBITS, serial.SEVENBITS, serial.SIXBITS. serial.FIVEBITS
        
        parity: Parity, defaults to PARITY_NONE, need to use the serial library variables
                            accepts: 
                                serial.PARITY_NONE, serial.PARITY_EVEN, serial.PARITY_ODD, serial.PARITY_MARK, serial.PARITY_SPACE
        
        stop_bits: Stopbits, defaults to STOPBITS_ONE, need to use the serial library variables
                            accepts:
                                serial.STOPBITS_ONE, serial.STOPBITS_ONE_POINT_FIVE, serial.STOPBITS_TWO
                                
        connection ###
        """
        self.port = port
        self.baud_rate = baud_rate
        self.parity = parity
        self.stop_bits = stop_bits
        self.bit_size = bit_size
        self.connection = connection
        
    def command(self, command):
        """
        DESCRIPTION:
            Send command to PIRL and print out PRIL response
            
        PARAMETERS:
            command (String): The command that is sent to the PIRL
            
        RETURNS:
            res: Response from the PIRL
        """
        if self.connection:
            res = pl.command(str(command) + "\n", connection = self.connection)
            print(res)
            return res
        else:
            print("GUI PIRL not connected. PIRL.command() cannot run!")
            return -1

    
    def uc_on(self):
        """
        DESCRIPTION:
            Turning on the microchip laser inside the PIRL
            
        PARAMETERS:
            None
            
        RETURNS:
            res: Response from the PIRL
        """
        if self.connection:
            res = pl.command("uc SSSD_1\n", connection = self.connection)
        else:
            print("GUI PIRL not connected. PIRL.uc_on() cannot run!")
            return -1


        
    def uc_off(self):
        """
        DESCRIPTION:
            Turning off the microchip laser inside the PIRL
            
        PARAMETERS:
            None
            
        RETURNS:
            res: Response from the PIRL
        """
        if self.connection:
            res = pl.command("uc SSSD_0\n", connection = self.connection)
        else:
            print("GUI PIRL not connected. PIRL.uc_on() cannot run!")
            return -1
        
    def pedal(self, pedal_value):
        """
        DESCRIPTION:
            Changing the pedal mode of the PIRL
            
        PARAMETERS:
            pedal_value: If it is set to 0, the pedal is disabled (The laser would fire continously)
                         If it is set to 1, the pedal is enabled (The laser would fire only in the presence of external triggers)
            
        RETURNS:
            res: Response from the PIRL
        """
        if self.connection:
            res = pl.command("mode" + str(pedal_value) + "\n", connection = self.connection)
        else:
            print("GUI PIRL not connected. PIRL.pedal() cannot run!")
            return -1
        

    def check_code(self):
        '''
        DESCRIPTION:
            Checking the status of the microchip laser
        
        PARAMETERS:
            None
        
        RETURNS:
            res: Response from the PIRL. This response contains 12 hexidecimal digits which can be decoded to determine 
            the state of the microchip laser. 
            To access the decoder, go to massspec/Users/coop/Chloe_Enzo_2024/PIRL/PIRL ressurection/uc error interpretation/MicroChipLaser_Table
            Then input the last 6 hexidecimal digits into the decoder.
        '''
        if self.connection:
            res = pl.command("uc GSER\n", connection = self.connection)
            return res
        else:
            print("GUI PIRL not connected. PIRL.check_code() cannot run!")
            return -1
    
    def q1c(self, value):
        """
        DESCRIPTION:
            Setting the QCW1 Laser current setting
            
            
        PARAMETERS:
            value: The current value of the QCW1 Laser
            
        RETURNS:
            res: Response from the PIRL
        """
        
        # if(value > 1250):
        #     value = 1250
        if self.connection:
            res = pl.command("q1c "+str(value) + "\n", connection = self.connection)
        else:
            print("GUI PIRL not connected. PIRL.q1c() cannot run!")
            return -1
        
    def shutdown(self):
        """
        DESCRIPTION:
            Shutsdown the PIRL
            
        PARAMETERS:
            None
            
        RETURNS:
            res: Response from the PIRL
        """
        if self.conection:
            res = pl.command("shutdown\n", connection = self.connection)
        else:
            print("GUI PIRL not connected. PIRL.shutdown() cannot run!")
            return -1