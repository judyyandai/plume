import serial
import time
from contextlib import contextmanager
import logging
from threading import Lock
import inspect
import pyvisa

# global functions and variables, many of which are used in GUI.py as well. 

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename='plupy_log.log',
    filemode='w'  # Overwrites each time
)

# COM_ports = {"pg":"COM19", "motor":"COM25", "uno":"COM20",
#              "vacuumMeter":"COM7", "heater":"COM6", 
#              "pirl":"COM3", "teensy":"COM21", "Coherent": "COM9"}
COM_ports = {"pg":"COM19", "motor":"COM25", "uno":"COM20", 
             "vacuumMeter":"COM7", "heater":"COM26", 
             "pirl":"COM3", "teensy":"COM21", "Coherent": "COM9"}

rm = pyvisa.ResourceManager()


serial_lock = Lock()

t0 = time.time()


# use this function for debugging - will print what line ran when 
def flag(should_print = False, message = ""):
    """Print the line number and time called

    PARAMETERS:
        should_print    (bool) If False, the function is silent. If True, function prints line number, time ran, and message. Defaults to False.
        message         (str) Can add a custom message to print statement. Defaults to empty string.
    """

    if should_print:
        frame = inspect.currentframe()
        caller = frame.f_back
        line_num = caller.f_lineno
        print(message + f"line {line_num} ran at {time.time() - t0}")
    
    return None







@contextmanager
def initialize_device(port, brate, bsize, par, stopb):
    """
    DESCRIPTION:
        Stablishes communication with a device and closes the conection before finishing
            
    PARAMETERS:
        port(string): Port in which the device is connected in the format of "COM##"
        
        brate(int): Baud rate of the connected device defaults to 115200
        
        bsize: bytesize, defaults to default to EIGHTBITS, need to use the serial library variables
                                accepts: serial.EIGHTBITS, serial.SEVENBITS, serial.SIXBITS. serial.FIVEBITS
        
        par: Parity,need to use the serial library variables
                                accepts: serial.PARITY_NONE, serial.PARITY_EVEN, serial.PARITY_ODD, serial.PARITY_MARK, serial.PARITY_SPACE
        
        stopb: Stopbits, need to use the serial library variables
                                accepts: serial.STOPBITS_ONE, serial.STOPBITS_ONE_POINT_FIVE, serial.STOPBITS_TWO
    
    RETURNS:
        None
    """
    
    device = serial.Serial(port = port, baudrate=brate, bytesize=bsize, parity=par, stopbits=stopb, timeout = 1.5)
    try:
        yield device
    finally:
        device.close()
        
@contextmanager
def initialize_all():
    """
    DESCRIPTION:
        Stablishes communication with a device and closes the conection before finishing
            
    PARAMETERS:
       None
    
    RETURNS:
        None
    """
    
    pg = serial.Serial(COM_ports["pg"], 115200, serial.EIGHTBITS,serial.PARITY_NONE,  serial.STOPBITS_ONE, timeout = 1.5)
    motor = serial.Serial(COM_ports["motor"], 9600, serial.SEVENBITS, serial.PARITY_ODD, serial.STOPBITS_TWO, timeout = 1.5)
    uno = serial.Serial(COM_ports["uno"],  115200, serial.EIGHTBITS,  serial.PARITY_NONE, serial.STOPBITS_ONE, timeout = 1.5)
    #vacuumMeter =  serial.Serial(COM_ports["vacuumMeter"], 19200,  serial.EIGHTBITS,  serial.PARITY_NONE, serial.STOPBITS_ONE, timeout = 1.5)


    try: 
        heater = serial.Serial(COM_ports["heater"], 19200,  serial.EIGHTBITS,  serial.PARITY_NONE, serial.STOPBITS_ONE, timeout = 1.5)
        print("Heater connected")
    except:
        heater = None
        print("GUI Heater not connected, will continue to run anyways. ")


    try:
        pirl = serial.Serial(COM_ports["pirl"],  19200, serial.EIGHTBITS, serial.PARITY_NONE, serial.STOPBITS_ONE, timeout = 1.5)
        print("PIRL connected")
    except:
        pirl = None
        print("GUI Could not connect to PIRL laser, will run anyway")
    

    try:
        teensy = serial.Serial(COM_ports["teensy"],  115200, serial.EIGHTBITS,  serial.PARITY_NONE, serial.STOPBITS_ONE, timeout = 1.5)
    except:
        teensy = None
        print("GUI Could not connect to Teensy, will run GUI.py anyways.")

    try:
        coherent = serial.Serial(COM_ports["Coherent"], 19200, serial.EIGHTBITS, serial.PARITY_NONE, serial.STOPBITS_ONE, timeout = 1.5)
        print("Coherent connected!")
    except:
        coherent = None
        print("GUI Could not connect to Coherent, will run GUI.py anyways.")

    try:
        vacuumMeter =  serial.Serial(COM_ports["vacuumMeter"], 19200,  serial.EIGHTBITS,  serial.PARITY_NONE, serial.STOPBITS_ONE, timeout = 1.5)
        print("Vacuum connected!")
    except:
        vacuumMeter = None
        print("GUI Could not connect to Vacuum Meter, will run GUI.py anyways.")




    
    try:
        yield pirl,pg,motor,uno,teensy,vacuumMeter, heater, coherent
    finally:
        pg.close()
        motor.close()
        uno.close()
        # vacuumMeter.close()
        if heater:
            heater.close()
        if pirl:
            pirl.close()
        if teensy:
            teensy.close()
        if coherent:
            coherent.close()
        if vacuumMeter:
            vacuumMeter.close()
   



    
def command(command, connection, repeat = False, good_response = b"ok\r\n"):
    """
    DESCRIPTION:
        Sends the input serial command to the device connected to the specified port
        
    PAARAMETERS:
        command(str): The command which you wuld like to send to the device
        
        connection: Serial Connection to the device. Must be created using initialize_device() or initialize_devices()
                                
        repeat (optional): Repeat the command to ensure it returns the good response, default is False
        
        good_response (optional): Expected response if successfull, default is b"ok\r\n"
        
    RETURNS:
        res: the response from the device
    """
    while True:
        with serial_lock:
            connection.write(str.encode(command)) # Sending the command
            res = connection.readline() # Reading response
        if res == good_response: # Checking if the response is what we want
            repeat = False
            
        if not repeat: # Breaking the loop
            break
    return res

def get_file_name(set_delay, true_delay):
    """
    DESCRIPTION:
        Given the delay information for the flashlamp, generates the file name to be used, following the format "[time]_[set delay]_[true delay].[file type]"
        
    PARAMETERS:
        set_delay: ideal value of the delay between the last pulse and the flash lamp, set by the user
        
        true_delay: actual delay measured from the TDC
        
    RETURNS:
        filename: name of the file to be used
    """
    date = round(time.time())
    
    filename = str(date) + "_" + f"{set_delay:09d}" + "_" + f"{true_delay:09d}"
    
    return filename