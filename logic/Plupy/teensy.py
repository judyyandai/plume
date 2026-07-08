import time

class teensy:    
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
        self.connection = connection

        # *** test differenet time and see
        time.sleep(1)
        if self.connection:
            self.connection.reset_input_buffer()  # Clear input buffer before starting
            self.connection.reset_output_buffer() # Clear output buffer
        

    def mode(self, mode):
        """
        DESCRIPTION:
           Set the pedal mode on the Teensy.
   
        PARAMETERS:
           mode (int):
               0 - Continuous firing mode (fires on every external trigger, no UNO pulse required)
               1 - Gated timing + ablation mode (requires UNO pulse to fire amplified shots)
               2 - Multi-shot mode (fires a set number of amplified shots, then switches back to mode 1)
   
        RETURNS:
           None
        """
        if self.connection:
            self.connection.reset_input_buffer()
            self.connection.reset_output_buffer()
            if mode in [0, 3, 4]: # only accept 0, 3, 4 or       
                self.connection.write(str.encode(f"mode:{mode}\n"))
            else:
                print("teensy.mode() only accepts 0, 3, or 4 as valid inputs!")
            
            self.display_response_message()

        return
    
    
    def getMode(self):
        """
        DESCRIPTION:
            Query the current pedal mode of the Teensy.
    
        RETURNS:
            mode (int): Current firing mode set on the Teensy (0, 1, or 2).
        """
        if self.connection:
            self.connection.reset_input_buffer()
            self.connection.reset_output_buffer()
        
            #print("BEFORE: \n" + str(str.encode("mode:?\n")))
            self.connection.write(str.encode("mode:?\n"))
            #self.connection.write("mode:?\n").encode("utf-8")
            #print("AFTER:" + str(self.connection))

            #The main issue is that "mode" isn't decoded properly. Investigate the purpose behind str.encode("mode:?\n")
            mode = self.connection.read_until(b"\n").decode("utf-8") 
            print(f"Teensy in pedal {mode} mode")
            return int(mode)
        else:
            print("teensy.getPedalMode() unable to communicate with teensy!")
            return -1
    
       
    def delayBetweenTriggers(self, delay):
        """
        DESCRIPTION:
            Set the delay between triggers. This is the delay between the Q2&Q3W trigger
            and the UC laser trigger pulse.
    
        PARAMETERS:
            delay (int): Delay in microseconds (range: 5–900). Determines timing alignment of amplified shots.
    
        RETURNS:
            None
        """
        if self.connection:
            self.connection.reset_input_buffer()
            self.connection.reset_output_buffer()
        
            self.connection.write(str.encode(f"lead_delay:{int(delay)}\n"))
            
            self.display_response_message()

        return
    
    
    def shotWanted(self, shotWanted):
        """
        DESCRIPTION:
            Set the number of amplified shots to fire in pedal mode 2 (multi-shot mode).
    
        PARAMETERS:
            shotWanted (int): Total number of amplified shots to fire before returning to pedal mode 1.
    
        RETURNS:
            None
        """
        if self.connection:
            self.connection.reset_input_buffer()
            self.connection.reset_output_buffer()
        
            self.connection.write(str.encode(f"shotWanted:{int(shotWanted)}\n"))
            
            self.display_response_message()

    
    
    def Q23TriggerIgnoreWindow(self, Q23TriggerIgnoreWindow):
        """
        DESCRIPTION:
            Set the cooldown period after each shot before the Teensy is allowed to be triggered again.
            This is critical for preventing the UC laser from being triggered at ~1000 Hz.
    
        PARAMETERS:
            Q23TriggerIgnoreWindow (int): Time in microseconds to delay reattaching the external trigger interrupt.
                              Minimum is 1200 µs to stay below ~1000 Hz firing rate.
    
        RETURNS:
            None
        """
        if self.connection:
            self.connection.reset_input_buffer()
            self.connection.reset_output_buffer()
        
            self.connection.write(str.encode(f"Q23TriggerIgnoreWindow:{int(Q23TriggerIgnoreWindow)}\n"))
            
            self.display_response_message()


    def message(self, start_command):
        """
        DESCRIPTION:
            sends the command to the teensy to start and will wait for a time (delay)
            before reading the results from the Teensy. In the Arduino IDE, when we send start 
            this will trigger ...
    
        PARAMETERS:
            start_command(bit string) = Command to be sent to the arduino. As of June 2025 teensy accepts four different messages:
            "start" begins the laser firing sequence
            "stop" stops the laser firing
            "measure" begins taking measurements
            "stop measure" stops measurements
            
        RETURNS:
            nothing
        """
        if self.connection:
            self.connection.reset_input_buffer()  # Clear input buffer before starting
            self.connection.reset_output_buffer() # Clear output buffer

            self.connection.write(str.encode(f"{start_command}\n"))
            return self.display_response_message()

        
    
    def display_response_message(self):
        
        #while self.connection.in_waiting == 0: # I don't know what htis doe
            #pass
        if self.connection:
            received_message = self.connection.read_until(b"\n").decode("utf-8")
            received_message = received_message[0:-1] # remove \n at end of message
            print(received_message) 

            return received_message
        else:
            return "teensy.display_response_message() could not connect to teensy!"