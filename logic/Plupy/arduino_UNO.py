from logic.Plupy import Plupy as pl
import time
import numpy as np

class arduino_UNO:    
    def __init__(self, port, baud_rate, bit_size, parity, stop_bits, connection):
        """   
        class for arduino uno
        functions are designed to work with fifteen instruments TDC connected via USB host sheild to the UNO
        functions are designed to work with Arduino IDE code Z:/Users/coop/Chloe_Enzo_2024/Master codes/code_for_UNO
        
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
        
        self.connection.reset_input_buffer()  # Clear input buffer before starting
        self.connection.reset_output_buffer() # Clear output buffer


    def read_timestamps(self, binary_stream):
        """
        (Modified from S15lib.instruments)
        DESCRIPTION:
            Reads the timestamps accumulated in a binary sequence and returns a
            Tuple[List[float], List[str]]: with the event times in ns and the 
            corresponding event channel. The channel are returned as string where
            a 1 indicates the trigger channel. For example an event in channel 2
            would correspond to "0010". Two coinciding events in channel 3 and 4
            correspond to "1100".
        
        PARAMETERS:
            binary_stream: binary input to be read
            
        RETURNS
            ts_list: list containing the timestamps at which signals were received
            event_channel_list: list containing the respective channels which received the signals
        """
        # Changing the input
        bytes_hex = binary_stream[::-1].hex() # reverts the stream and converts is to hexadecimal
        ts_word_list = [    
            int(bytes_hex[i : i + 8], 16) for i in range(0, len(bytes_hex), 8)
            ][::-1] # Truncates the initial stream into packages of two 8-character "words" and 
                    # converts to integers and reverses back to the order from before

        # Initializing variables
        ts_list = []
        event_channel_list = []
        periode_count = 0 # How many rollovers (count restart) happend so far
        periode_duration = 1 << 27 # This is the length of 1 period (same as 2^27)
        prev_ts = -1 # means that no other timestamp was analysed yet
        
        # Iterating for each "words"
        for ts_word in ts_word_list:
            time_stamp = ts_word >> 5 # Removing the last five charachters since they dont have
                                      # timestamp information (only dummy flag and detector pattern)
                                      
            pattern = ts_word & 0x1F # This gets the last 5 bits of the word, that is, the dummy flag
                                     # and the detector pattern
            
            if prev_ts != -1 and time_stamp < prev_ts: # Checks if the new timestamp is  smaller than the 
                                                       # previous one (), which would happend if there is a
                                                       # rollover (restart the count)
                periode_count += 1 # increase the period count to use it latter
            
            prev_ts = time_stamp # sets the previous timestamp to compare with the next one
            
            if (pattern & 0x10) == 0: # Check if the 5 last bit (dummy flag) of the word is zero which indicates that the timestamp is valid.
                                     
                ts_list.append(time_stamp + periode_duration * periode_count)
                # This calculates the actual timestamp by adding the original value with the number of 
                # periods (number of rollovers) * the duration of the period and appends it to a list
                

                # Save the channels as a binary string
                event_channel_list.append("{0:04b}".format(pattern & 0xF))
               
        ts_list = np.array(ts_list, dtype="int64") * 2  # Each step is equivalent to 2ns
        
        return ts_list, event_channel_list
    
    
    def channel_cleaner(self, cha_info):
        """
        DESCRIPTION:
            takes an array of 4 digit code for channels sending the pulse and returns the 
            channels that sent the triggers
        
        PARAMETERS:
            cha_info(array): Array containg the code for the channels [   xxxx xxxx xxxx xxxx ...] 
            
        RETURNS
            cha_clean: List of the channels received in order correspondent to the counts
            
            (counts1, ...): tupple containing the number of counts each channel received
        """
        
        cha_clean = []
        counts_1 = 0
        counts_2 = 0
        counts_3 = 0
        counts_4 = 0
        
        # Converting from the 4 digits to channels
        for cha_list in cha_info: 
            channel = []
            if cha_list[0] == '1':
                channel.append('CH4')
                counts_4 += 1
    
            if cha_list[1] == '1':
                channel.append('CH3')
                counts_3 += 1
                
            if cha_list[2] == '1':
                channel.append('CH2')
                counts_2 += 1
    
            if cha_list[3] == '1':
                channel.append('CH1')
                counts_1 += 1
    
            cha_clean.append(channel)
        
        return cha_clean, (counts_1, counts_2, counts_3, counts_4)
        
    def start(self, start_command):
        """
        DESCRIPTION:
            sends the command to the arduino to start and will wait for a time (delay)
            before reading the results from the Uno. In the Arduino IDE, when we send start 
            this will trigger the arduino timing for the arduino to start the TDC, send the prepulse
            open the shutter, then recieve the results from the TDC and send them to the serial connection.
            This function will also use other functions to take the hex stream an clean it to a readable 
            depiction of the TDC results. 
    
        PARAMETERS:
            start_command(bit string) = Command to be sent to the arduino. It currently accepts b"start\n", which will open and close 
            the shutter, or b"start2\n", which will not change the shutter state.
            
        RETURNS:
            results from TDC
        """
        
        self.connection.reset_input_buffer()  # Clear input buffer before starting
        self.connection.reset_output_buffer() # Clear output buffer


        self.connection.write(str.encode(start_command)) # Send as a byte literal for consistency
        
        pl.flag()
        while self.connection.in_waiting == 0:
            #flag(True)
            pass
    
        #flag()
        # Read data efficiently (~0.01s)
        hex_stream = self.connection.read_until(b"END")  # Read until newline or custom delimiter

        
        hex_stream = hex_stream.strip(b"END")

        [counts, cha_info] = self.read_timestamps(hex_stream)
        channels, ch_counts =self.channel_cleaner(cha_info)
        
        return counts, channels, ch_counts