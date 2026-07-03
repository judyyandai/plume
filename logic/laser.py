#
from threading import Event

class Laser():
    def __init__(self):
        """
        DESCRIPTION:

        PARAMETERS:

        """
        # Initialize the controller with PIRL laser selected, Regular Pulse, 100 Hz frequency
        self.option = "PIRL"
        self.mode = "Regular Pulse"
        self.frequency = 100 #Hz
        self.pulse_spacing = "prepulse" #only relevant for PIRL (prepulse 2ms, no prepulse 8ms)
        
        #Event to track if the laser is on or off
        self.e_laserOn = Event()






     # !!! all functions need to be implement
    def toggle(self):
        """
        DESCRIPTION:
            Switches the laser on or off depending on its current state.
        PARAMETERS
            None.
        RETURN 
            None.
        """
        self.e_laserOn.set() if not self.e_laserOn.is_set() else self.e_laserOn.clear()
        print("Laser toggled")



    def change_option(self, option):
        """
        DESCRIPTION:
            Switches to selected laser (PIRL or Q-Tune)

        """
        self.option = option
        print("Laser changed to", self.option)



    # !!! needs to be implemented
    def change_mode(self, mode):
        """
        DESCRIPTION:
            Switches to selected laser mode (Regular Pulse or Gallop)
        """
        self.mode = mode
        print("Laser mode changed to", self.mode)



    def change_frequency(self, frequency):
        """
        DESCRIPTION:
            Changes to selected frequency (only relevant in regular pulse mode)
        """
        self.frequency = frequency
        print("Laser frequency changed to", self.frequency)


    def change_pulse_spacing(self, pulse_spacing):
        """
        DESCRIPTION:
            Changes to selected prepulse to ablation pulse spacing (only relevant in gallop mode with pirl)
        """
        self.pulse_spacing = pulse_spacing
        print("In spacing mode:", self.pulse_spacing)      