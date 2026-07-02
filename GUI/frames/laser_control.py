#Frame for laser control panel

import tkinter as tk
from tkinter import ttk
from GUI.frames.container_frame import ContainerFrame

class LaserControlFrame(ContainerFrame):
    def __init__(self, parent, laser):
        super().__init__(parent, "Laser Control Panel")
        self.laser = laser

        

        # Row 1: Start Laser and Begin Measuring buttons
        row_1 = tk.Frame(self)
        row_1.pack(anchor="w", pady=(10, 0))

        self.b_startLaser = tk.Button(
            row_1,
            text="Start Laser",
            font=("Roboto", 16),
            command= self.laser_toggle
        )
        self.b_startLaser.pack(side="left", padx=20)


        self.b_beginMeasure = tk.Button(
            row_1,
            text="Begin Measuring",
            font=("Roboto", 16),
            state = 'disabled'
        )
        self.b_beginMeasure.pack(side="left", padx=20)

        # Row 2: Radio buttons for laser mode (Regular Pulse or Gallop) + additional options for each mode
        row_2 = tk.Frame(self)
        row_2.pack(anchor="w", pady=(15, 15))

        # Regular pulse mode button
        rb_regPulse = tk.Radiobutton(row_2, text = "Regular Pulse")
        rb_regPulse.pack(anchor = 'nw', side = 'top')

        # Frequency dropdown menu and shot count request
        regPulseMenu = tk.Frame(row_2)
        regPulseMenu.pack(pady = 5, padx = 5)

        self.ddRegFreq = self.create_dropdown(regPulseMenu) # ddRegFreq stands for dropdown regular frequency. 

        # Gallop mode button
        rb_gallop = tk.Radiobutton(row_2, text = "Gallop (for Experiment)")
        rb_gallop.pack(anchor = 'nw', side = 'top')

        # !!! Prepulse modes


    def laser_toggle(self):
        self.laser.toggle()
        self.update_b_startLaser()


    def update_b_startLaser(self):
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
            self.b_beginMeasure.config(state = 'normal')
        self.update_b_beginMeasure()


    def update_b_beginMeasure(self):
        if self.laser.option == "Q-Tune":
            if self.laser.e_laserOn.is_set():
                self.b_beginMeasure.config(state="disabled")
            else:
                self.b_beginMeasure.config(state="normal")
        else:
            if self.laser.e_laserOn.is_set():
                self.b_beginMeasure.config(state="normal")
            else:
                self.b_beginMeasure.config(state="disabled")


    def create_dropdown(self, frame):
        """
        DESCRIPTION:
            Currently only used to create the dropdown for PRR selection - 
        can be modified in the future to be more general of course.
        PARAMETERS:
            
        RETURN: 
            
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
    
   