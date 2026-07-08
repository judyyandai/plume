from threading import Event

class Experiment:
    def __init__(self):
        """
        DESCRIPTION:

        PARAMETERS:

        """
        # Event to track if the experiment is running or not
        self.e_experimentOn = Event()


    def toggle(self):
        """
        DESCRIPTION:
            Switches the experiment on or off depending on its current state.
        PARAMETERS
            None.
        RETURN 
            None.
        """
        self.e_experimentOn.set() if not self.e_experimentOn.is_set() else self.e_experimentOn.clear()
        print("Experiment toggled")