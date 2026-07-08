from logic.Plupy import Plupy as pl

class Coherent:
    def __init__(self, port, baud_rate, bit_size, parity, stop_bits, connection):
        """        
        Class for the Coherent
        
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
        
        # MAKES Coherent print out "ok" when a valid command is inputted
        if self.connection:
            initiate = pl.command("INITiate\n", connection = self.connection)
            #handshake = command("SYSTem:COMMunicate:HANDshaking OFF\n", connection = self.connection)
            idn = pl.command("*IDN?\n", self.connection)
            nRecords = pl.command("FETCh:NRECords?\n", connection = self.connection)
            print("Coherent: " + idn.decode('UTF-8'))
            #print("Coherent: " + handshake.decode('UTF-8'))
            print("Coherent: " + nRecords.decode('UTF-8'))


    def command(self, command):
        """
        DESCRIPTION:
            Send command to Coherent and print out Coherent response
            
        PARAMETERS:
            command (String): The command that is sent to the Coherent
            
        RETURNS:
            res: Response from the Coherent
        """
        if self.connection:
            res = pl.command(str(command) + "\n", connection = self.connection)
            print(res)
            return res
        else:
            print("GUI Coherent not connected. Coherent.command() cannot run!")
            return -1

    
    def readValues(self):
        """
        DESCRIPTION:
            Reading
            
        PARAMETERS:
            None
            
        RETURNS:
            res: Response from the PIRL
        """
        if self.connection:
            nRecords = pl.command("FETCh:NRECords?\n", connection = self.connection)
            if (nRecords.decode('UTF-8') == '') or int(nRecords.decode('UTF-8')) == 0:
                print("Coherent: Pulses not registered.")
                return "undetected"
            else:
                energy = pl.command("FETCh:NEXT?\n", connection = self.connection)
                print("COHERENT ENERGY READING: " + energy.decode('UTF-8'))
                return energy.decode('UTF-8')
        else:
            print("GUI Coherent not connected. Coherent.readValues() cannot run!")
            return "not read"
        
