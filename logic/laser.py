#
from threading import Event

class Laser():
    def __init__(self):

        # Initialize the controller with PIRL laser selected
        self.option = "PIRL"
        
        #Event to track if the laser is on or off
        self.e_laserOn = Event()





    # !!! needs to be implemented
    def change_option(self, option):
        """
        DESCRIPTION:
            Switches to selected laser if not already selected.
        PARAMETERS
            None.
        RETURN 
            None.
        """
        if self.e_laserOn.is_set():
            print("Cannot change laser option while laser is on.")
            return

        if option == "PIRL":
            if self.option != "PIRL":
                self.option = "PIRL"
                print(f"Laser option changed to: {self.option}")
            
        elif option == "Q-Tune":
            if self.option != "Q-Tune":
                self.option = "Q-Tune"
                print(f"Laser option changed to: {self.option}")




     # !!! to implement
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


