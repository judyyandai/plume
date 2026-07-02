#Frame for laser control panel

import tkinter as tk
from tkinter import ttk
from GUI.frames.container_frame import ContainerFrame

class LaserControlFrame(ContainerFrame):
    def __init__(self, parent, laser, experiment):
        super().__init__(parent, "Laser Control Panel")
        self.laser = laser
        self.experiment = experiment
        row_1 = tk.Frame(self)
        row_1.pack(anchor="w", pady=(15, 15))

        # Default to PIRL selected
        self.laser_option = tk.StringVar(value = "PIRL")

        # Row 1: Q-Tune and PIRL radio buttons
        self.rb_QTune = tk.Radiobutton(
            row_1,
            text="Q-Tune",
            variable=self.laser_option,
            command=self.change_laser_option,
            value="Q-Tune"
        ).pack(anchor="w")

        self.rb_PIRL = tk.Radiobutton(
            row_1,
            text="PIRL",
            variable=self.laser_option,
            command=self.change_laser_option,
            value="PIRL"
        ).pack(anchor="w")

        # Row 2: Start Laser and Begin Measuring buttons
        row_2 = tk.Frame(self)
        row_2.pack(anchor="w", pady=(10, 0))

        self.b_startLaser = tk.Button(
            row_2,
            text="Start Laser",
            font=("Roboto", 16),
            command= self.laser_toggle
        )
        self.b_startLaser.pack(side="left", padx=20)


        self.b_beginMeasure = tk.Button(
            row_2,
            text="Begin Measuring",
            font=("Roboto", 16),
            command= self.experiment_toggle,
            state = 'disabled'
        )
        self.b_beginMeasure.pack(side="left", padx=20)

        # Row 3: Radio buttons for laser mode (Regular Pulse or Gallop) + additional options for each mode
        row_3 = tk.Frame(self)
        row_3.pack(anchor="w", pady=(15, 15))

        # Regular pulse mode button
        rb_regPulse = tk.Radiobutton(row_3, text = "Regular Pulse")
        rb_regPulse.pack(anchor = 'nw', side = 'top')

        # Frequency dropdown menu and shot count request
        regPulseMenu = tk.Frame(row_3)
        regPulseMenu.pack(pady = 5, padx = 5)

        self.ddRegFreq = self.create_dropdown(regPulseMenu) # ddRegFreq stands for dropdown regular frequency. 

        # Gallop mode button
        rb_gallop = tk.Radiobutton(row_3, text = "Gallop (for Experiment)")
        rb_gallop.pack(anchor = 'nw', side = 'top')

        # !!! Prepulse modes


    def laser_toggle(self):
        """
        DESCRIPTION:
        .
            
        """
        self.laser.toggle()
        self.update_buttons()


    def experiment_toggle(self):
        """
        DESCRIPTION:
        .
            
        """
      
        self.experiment.toggle()
        self.update_buttons()

    # !!! need to handle when this is attempted when laser/ experiment is on
    def change_laser_option(self):
        """
        DESCRIPTION:
        .
            
        """
        option = self.laser_option.get()
        self.laser.change_option(option)
        self.update_buttons()
    


    def update_buttons(self):
        """
        DESCRIPTION:
        .
            
        """
        if self.laser.option == "Q-Tune":
            self.update_buttons_QTune()
        else:
            self.update_buttons_PIRL()
        self.update_b_startLaser()
        self.update_b_beginMeasure()


    # !!! finish implementing this function
    def update_buttons_QTune(self):
        """
        DESCRIPTION:
        .
            
        """
        if self.laser.e_laserOn.is_set():
            self.b_beginMeasure.config(state="disabled")
        else:
            if self.experiment.e_experimentOn.is_set():
                self.b_startLaser.config(state="disabled")
            else:
                self.b_beginMeasure.config(state="normal")
                self.b_startLaser.config(state="normal")


     # !!! finish implementing this function
    def update_buttons_PIRL(self):
        """
        DESCRIPTION:
        .
            
        """
        if self.laser.e_laserOn.is_set():
            self.b_beginMeasure.config(state="normal")
        else:
            self.b_beginMeasure.config(state="disabled")



    def update_b_startLaser(self):
        """
        DESCRIPTION:
            Updates the text of the Start Laser button based on whether the laser is on or off.
            
        """
        if self.laser.e_laserOn.is_set():
            self.b_startLaser.config(
                text="LASER RUNNING\nClick to STOP",
                fg="red",
                font="Roboto 18"
            )


        else:
            self.b_startLaser.config(
                text="Start Laser",
                fg="black",
                font="Roboto 16"
            )



    def update_b_beginMeasure(self):
        """
        DESCRIPTION:
            Updates the text of the Begin Measuring button based on whether the experiment is running.
        """
        if self.experiment.e_experimentOn.is_set():
            self.b_beginMeasure.config(
                text="Stop Experiment"
            )

        else:
            self.b_beginMeasure.config(
                text="Begin Measuring"
            )



    def create_dropdown(self, frame):
        """
        DESCRIPTION:
            Currently only used to create the dropdown for PRR selection - 
        can be modified in the future to be more general of course.
        PARAMETERS: 
            frame: the parent frame in which the dropdown will be placed.       
        RETURN: 
            dropdown: the created dropdown object.
            
        """
        
        
        dropdownFrame = tk.Frame(frame)
        dropdownFrame.pack(side = "left", padx = 5, pady = 5)
        label = tk.Label(dropdownFrame, text = "Laser Pulse Repetition Rate (PRR):", padx = 15)
        label.pack(side = tk.LEFT)
        #NOTE: the space between the numbers and the Hz is required for the program to work!
        self.PRR_options = ["200 Hz", "166.6 Hz", "125 Hz", 
                       "111.1 Hz", "100 Hz", "90.9 Hz", 
                       "66.6 Hz", "50 Hz", "40 Hz", 
                       "33.3 Hz", "25 Hz", "20 Hz", "10 Hz"]
        
        dropdown = ttk.Combobox(dropdownFrame, values  = self.PRR_options, state = 'disabled', width =10)
        dropdown.bind("<<ComboboxSelected>>") # !!! need to add a function to be called when the dropdown is changed, (change_laser_frequency)
        dropdown.pack()
        dropdown.current(self.PRR_options.index("100 Hz")) # sets 100 Hz to be the default
        
        return dropdown
    
   