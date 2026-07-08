import time
from threading import Lock
class heater:
    def __init__(self, port, baud_rate, bit_size, parity, stop_bits, connection):
        self.port = port
        self.baud_rate = baud_rate
        self.parity = parity
        self.stop_bits = stop_bits
        self.bit_size = bit_size
        if connection:
            self.connection = connection
        else:
            self.connection = None
    

        # *** test differenet time and see
        time.sleep(1)
        if self.connection: 
            self.connection.reset_input_buffer()  # Clear input buffer before starting
            self.connection.reset_output_buffer() # Clear output buffer
        self.communication_lock = Lock() #* use this to avoid threads working at teh same time:
        #* notably the read temperature thread is loves to clobber without a lock

    def read_temps(self, curr_t1, curr_t2):
        # print("Here!")

        if self.connection:    
        
            self.connection.reset_input_buffer()  # Clear input buffer before starting
            self.connection.reset_output_buffer() # Clear output buffer
        
            self.connection.write(bytearray("temp:?\n",'ascii'))
            
                # wait for buffer (this delay can be adjusted)
            time.sleep(0.3)
            temp_string = str(self.connection.readline()) # remove the 'b' at the front of the string and the single quotes
            temp_only_string = "".join(c for c in temp_string if not c.isalpha()).replace("\\", "").replace("'", "")
            try:
                t1, t2 = temp_only_string.split(",")
                return float(t1), float(t2)

            except:# in some cases the string gets fucked up by other messages coming in, in this case, 
                return curr_t1, curr_t2


    
        else:
            # print("Returning!")
            return 9999999, 9999999 # purposefully ridicuolous numbers. 
        
    def start(self):
        if self.connection:
            
            with self.communication_lock:
                self.connection.reset_input_buffer()  # Clear input buffer before starting
                self.connection.reset_output_buffer() # Clear output buffer
                self.connection.write(bytearray("start\n",'ascii'))
                self.display_response_message()
            
        else:
            print("Heater not connected! heater.start() failed.")
        return
    
    def stop(self):
        
        if self.connection:
            with self.communication_lock:
                self.connection.reset_input_buffer()  # Clear input buffer before starting
                self.connection.reset_output_buffer() # Clear output buffer
        
                self.connection.write(bytearray("stop\n",'ascii'))
        
                self.display_response_message()
        else:
            print("Heater not connected! heater.stop()")

        return
    
    def set_coeff(self, coeff, val):
        if self.connection:
            with self.communication_lock:
                self.connection.reset_input_buffer()
                self.connection.reset_output_buffer()

                self.connection.write(bytearray(f"{coeff}:{val}\n", 'ascii'))
                self.display_response_message()

        
        else:
            print("GUI Heater not connected! heater.set_coeff() failed")

    def message(self, message): # generic messsaging function, I believe unused. 
        if self.connection:
            with self.communication_lock:
                self.connection.reset_input_buffer()  # Clear input buffer before starting
                self.connection.reset_output_buffer() # Clear output buffer
        
                self.connection.write(bytearray(message,'ascii'))
    
            self.display_response_message()
        else:
            print("GUI Heater not connected! heater.message() failed. ")

    def target_temp(self, temp):
        if self.connection:
            with self.communication_lock:
                self.connection.reset_input_buffer()  # Clear input buffer before starting
                self.connection.reset_output_buffer() # Clear output buffer
                command = f"temp:{temp}"
                self.connection.write(bytearray(command,'ascii'))
        
                self.display_response_message()
        else:
            print("GUI Heater not connected! heater.target_temp() failed. ")

    def check_PID_val(self) -> float:
        if self.connection:
            with self.communication_lock:
                self.connection.reset_input_buffer()  # Clear input buffer before starting
                self.connection.reset_output_buffer() # Clear output buffer
                command = f"PID"
                self.connection.write(bytearray(command,'ascii'))
                time.sleep(0.3)
                try:
                    PID_val = float(self.connection.readline())
                    return PID_val
                except:
                    print("heater.check_PID_val(): PID val from the heater was not a float, returning -1. ")
                    return -1
              
        else:
            pass #* the print statements were going off every second and were pretty annoying. 
            # print("GUI Heater not connected! heater.check_PID_val() failed. ")

       

    def display_response_message(self):
        if self.connection:
            t0 = time.time()
            while self.connection.in_waiting == 0: # this waits until there's some response
                if time.time() - t0 >= 1: # a kind of manual timeout I'm putting in. 
                    return
                pass
                
            received_message = self.connection.read_until(b"\n").decode("utf-8")
          
            print(received_message[0:-1]) # removing \n at end of message. 
        else:
            print("Heater not connected! heater.display_response_message() failed")

        return