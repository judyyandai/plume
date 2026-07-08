import time

class vacuumMeter:    
    def __init__(self, port, baud_rate, bit_size, parity, stop_bits, connection):
        """   
        class for teensy multiplexer
        
        CLASS ELEMENTS:
            
            port(string): Port in which the device is connected in the format of "COM##"
        
            baud_rate(int): Baud rate of the connected device defaults to 115200
        
            bit_size: bytesize, defaults to default to EIGHTBITS, need to use the serial library variables
                                accepts: 
                                    serial.EIGHTBITS, serial.SEVENBITS, serial.SIXBITS. serial.FIVEBITS
        
            parity: Parity,need to use the serial library variables
                                accepts: 
                                    serial.PARITY_NONE, serial.PARITY_EVEN, serial.PARITY_ODD, serial.PARITY_MARK, serial.PARITY_SPACE
        
            stop_bits: Stopbits, need to use the serial library variables
                                accepts: 
                                    serial.STOPBITS_ONE, serial.STOPBITS_ONE_POINT_FIVE, serial.STOPBITS_TWO
        """
        self.port = port
        self.baud_rate = baud_rate
        self.parity = parity
        self.stop_bits = stop_bits
        self.bit_size = bit_size
        #self.connection = connection
        if connection:
            self.connection = connection
        else:
            self.connection = None

        # *** test differenet time and see
        time.sleep(1)
        if self.connection:
            self.connection.reset_input_buffer()  # Clear input buffer before starting
            self.connection.reset_output_buffer() # Clear output buffer


        
    def readChannel(self, channel):
        """
        DESCRIPTION:
            Read data of a specific channel

        PARAMETERS:
            channel(int): The number of the channel you want to read from

        RETURNS:
            data(float): The data in that channel
        """
        self.connection.reset_input_buffer()  # Clear input buffer before starting
        self.connection.reset_output_buffer() # Clear output buffer
    
        self.connection.write(bytearray("CH" + str(channel)+":READ\n",'ascii'))
        
        # wait for buffer (this delay can be adjusted)
        time.sleep(0.1)
        
        data = float(self.connection.readline())
        return data