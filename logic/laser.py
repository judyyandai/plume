#
from threading import Event
import logic.devices.pyCurlModel as qTune


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

        # Default Q-Tune laser to internal triggering to confirm ethernet connection with Q-Tune is open
        qTune.trigModeInternal()
        
        #Event to track if the laser is on or off
        self.e_laserOn = Event()

        # Creating device objects  for GUI
        
        # Default Teensy to Regular Pulse mode
        # self.teensy.mode(0)


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
        if self.e_laserOn.is_set():
            if self.option == "Q-Tune":
                qTune.runLaser()
                print("Laser on")
            #elif self.option.get() == "PIRL": !!! deal with PIRL
                # self.T_autocorrector = Thread(target = self.autocorrector, name = "T_autocorrector", args = ([None]))
                # self.T_autocorrector.start()
            #    self.teensy.message("on")

        elif not self.e_laserOn.is_set():
            if self.option == "Q-Tune":
                qTune.stopLaser()
                print("Laser off")
            #elif self.option.get() == "PIRL":
            #    self.teensy.message("off")





    def change_option(self, option):
        """
        DESCRIPTION:
            Switches to selected laser (PIRL or Q-Tune)

        """
        self.option = option
        self.on_option_change()



    # !!! needs to be implemented
    def change_mode(self, mode):
        """
        DESCRIPTION:
            Switches to selected laser mode (Regular Pulse or Gallop)
        """
        self.mode = mode
        self.on_mode_change()



    def change_frequency(self, frequency):
        """
        DESCRIPTION:
            Changes to selected frequency (only relevant in regular pulse mode)
        """
        self.frequency = frequency
        self.on_frequency_change()


    def change_pulse_spacing(self, pulse_spacing):
        """
        DESCRIPTION:
            Changes to selected prepulse to ablation pulse spacing (only relevant in gallop mode with pirl)
        """
        self.pulse_spacing = pulse_spacing


    def on_mode_change(self):
        """
        DESCRIPTION:
            Configures neccesary changes in qTune and teensy according to laser mode selected: regular pulse or gallop. And prepulse or no prepulse.
        PARAMETERS
            None.
        RETURN: 
            None.
            
        """

        if self.mode == "Gallop":
            if self.option == "PIRL":
                print(self.pulse_spacing.get())
                # handle the two options within Gallop Mode
                if self.pulse_spacing.get() == "prepulse":
                    # self.teensy.mode(3) !!! deal with PIRL
                    print("GUI set pedal to Gallop, 2ms space")
                elif self.pulse_spacing.get() == "no prepulse":
                    # self.teensy.mode(4)
                    print("GUI set pedal to Gallop, 8ms space")
                else:
                    print("GUI ERROR invalid pulse spacing chosen. See on_mode_change()")
            else: #Laser is Q-Tune
                qTune.gallopModeInternal()
                print("Q-Tune now in Gallop Mode")

        else: # Pedal 0 mode, regular pulse 
            
            #if self.F_Experiment: #* if experiment is running, then stop it! Shouldn't be able to run experiment without Gallop  !!! is this needed?

            
            if self.mode == "Regular Pulse":
                if self.option == "PIRL":
                    # self.teensy.mode(0)
                    print("GUI set to pedal 0")
                else:
                    qTune.gallopModeOff()
                    try:
                        qTune.changeFrequency(10)
                        print("Q-Tune now in Regular Pulse Mode, at 10Hz")
                    except: 
                        print("on_laser_change: Q-Tune is inactive.")
            else:
                print("GUI ERROR Invalid Mode Command entered!")


    def on_option_change(self):
        """
        DESCRIPTION:
            Switches off non-corresponding laser if running
        PARAMETERS
            None.
        RETURN 
            None.
        """
        if self.option == "PIRL":
            # if Q-Tune is on but not the chosen laser, turn it off
            qTune.stopLaser()
            # self.teensy.message("q-tune please no") !!! fix when teensy is implemented
        elif self.option == "Q-Tune":
            #Switch laser mode to Regular Pulse Mode
            self.mode="Regular Pulse"
            #Default laser to 10 Hz
            try:
                qTune.changeFrequency(10)
            except: 
                print("on_laser_change: Q-Tune is inactive.")



    def on_frequency_change(self, event):
        """
        DESCRIPTION:
            Runs whenever a new laser frequency is chosen from the regular pulse frequency dropdown. Sends appropriate serial commands and does some error checking.
        PARAMETERS:
            None            
        RETURN: 
            None
        """
        # do Q-Tune frequency changes if laser is set at Q-Tune        
        if self.option == "Q-Tune":
            selection = self.frequency
            freq, *rest = selection.split()
            qTune.changeFrequency(float(freq))
            print(f"GUI change frequency to {freq} Hz")
        # should only change detach_time if we're pedal 0 mode. 
    # !!! fix once teensy is implemented   
    #    elif self.teensy.getMode() == 0:
    #        selection = self.frequency.get()
    #        # selection is in the format "XXX.X Hz" so we need to extract that number
    #        # .split() breaks the string at the space. 
    #        freq, *rest = selection.split() 
    #        detach_time = 1000*int(1000/float(freq)) - 500
    #        print(f"GUI change detach time to {detach_time}")
    #        self.teensy.Q23TriggerIgnoreWindow(detach_time)
        
        

    
    def change_qTune_wavelength(self, wavelength):
        qTune.changeWavelength(wavelength)
    

    def change_qTune_pump(self, pump):
        qTune.changePumpLevel(pump)