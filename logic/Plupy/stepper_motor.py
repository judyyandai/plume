from logic.Plupy import Plupy as pl
import time

class stepper_motor:
    def __init__(self, port, baud_rate, bit_size, parity, stop_bits, connection):
        """
        class for SMD2 stepper motor driver 
        
        CLASS ELEMENTS:
            port: COM port to be used
            
            baud_rate: Baud rate of the device
            
            parity: Parity of the device
            
            stop_bits: stop bits of the device
            
            bit_size: bit size of the device
        
            connection: Serial Connection to the device. Must be created using initialize_device() or initialize_devices()        
        """
        self.port = port
        self.baud_rate = baud_rate
        self.parity = parity
        self.stop_bits = stop_bits
        self.bit_size = bit_size
        self.b1_flag = False
        self.b2_flag = False
        self.end = False
        self.connection = connection
        self.step_size = 5.26 #um
    
    def back(self, distance):
        """
        DESCRIPTION:
            Moves the motor back, looking from the breadboard, a specified number of steps
                
        PARAMETERS:
            distance: distance to move in mm
            
        RETURNS:
            res: Response from the device
        """
        
        steps = float(distance*10**3)/self.step_size
        print(steps)
        steps_str = f"{steps:.0f}"
        print(steps_str)
        
        pl.command("B1 \r", connection = self.connection)
        res = pl.command("-" + steps_str + "\r", self.connection)
        self.wait()
        
        return res

    def forward(self, distance):
        """
        DESCRIPTION:
            Moves the motor forward, looking from the breadboard, a specified number of steps
                
        PARAMETERS:
            distance: distance to move in mm

        RETURNS:
            res: Response from the device
        """
        steps = float(distance*10**3)/self.step_size
        print(steps)
        steps_str = f"{steps:.0f}"
        print(steps_str)
        
        pl.command("B1 \r", connection = self.connection)
        res = pl.command("+" + steps_str + "\r",  connection = self.connection)
        self.wait()
        return res
    
    def right(self, distance):
        """
        DESCRIPTION:
            Moves the motor right, looking from the breadboard, a specified number of steps
                
        PARAMETERS:
            distance: distance to move in mm
            
        RETURNS:
            res: Response from the device
        """
        steps = float(distance*10**3)/self.step_size
        print(steps)
        steps_str = f"{steps:.0f}"
        print(steps_str)
        
        pl.command("B2 \r", connection = self.connection)
        res = pl.command("-" + steps_str + "\r", connection = self.connection)
        self.wait()
        return res
        
    def left(self, distance):
        """
        DESCRIPTION:
            Moves the motor left, looking from the breadboard, a specified number of steps
                
        PARAMETERS:
            distance: distance to move in mm
            
        RETURNS:
            res: Response from the device
        """  
        steps = float(distance*10**3)/self.step_size
        print(steps)
        steps_str = f"{steps:.0f}"
        print(steps_str)
        
        pl.command("B2 \r", connection = self.connection)
        res = pl.command("+" + steps_str + "\r", connection = self.connection)
        self.wait()
        return res


    def set_home(self):
        """
        DESCRIPTION:
            sets the current location of ythe stage to 0 in both directions
            
        PARAMETERS:
            None
        """
        pl.command("I3 \r", connection = self.connection)

    def go_home(self):
        """
        DESCRIPTION:
            moves the motor to 0 in both directions
            
        PARAMETERS:
            None
        """
        
        pl.command("B1 \r", connection = self.connection)
        pl.command("G+0 \r", connection = self.connection)
        self.wait()
        pl.command("B2 \r", self.connection)
        pl.command("G+0 \r", connection = self.connection)
        self.wait()
        
        return 

    def is_moving(self):
        """
        DESCRIPTION:
            check if the motor is moving
        
        PARAMETERS:
            None
        
        RETURNS:
            res: Response from the device
        """
        res = pl.command("F \r", self.connection)
        return res

    def wait(self):
        """
        DESCRIPTION:
            Stops any code from running while the motor is still moving
            
        PARAMETERS:
            None
        
        RETURNS:
            None
        """        
        while self.is_moving() != b'Y\r':
            time.sleep(0.1)
            continue
        
    def position(self, x,y):
        """
        DESCRIPTION:
            will take the motor to the spesified position, with reference to (0,0) 
            
        PARAMETERS:
            x - motor 2 /right/left position of the motor relative to the calibrated 0, 
            y - motor 1 /forward/backwards position of the motor relative to the calibrated 0 

        RETURNS:
            None
        """
        x_com = "G" + str(x) +" \r"
        y_com = "G" + str(y) +" \r"
        
        pl.command("B2 \r", connection = self.connection)
        pl.command(x_com, connection = self.connection)
        self.wait()
        pl.command("B1 \r", connection = self.connection)
        pl.command(y_com, connection = self.connection)
        self.wait()
        
        return 
    
