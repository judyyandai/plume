import tkinter as tk
from tkinter import ttk
from GUI.frames.container import ContainerFrame
from GUI.widgets.entry_box import EntryBox
from tkinter import messagebox
from GUI.widgets.tool_tip import ToolTip
 

class LaserFrame(ContainerFrame):
    def __init__(self, parent, laser, experiment, data_manager):
        """
        DESCRIPTION:
            Class used to create the laser control panel which contains:
                - laser option (PIRL or Q-Tune) selection
                - 'Start Laser' and 'Begin Measure' buttons
                - laser mode (Regular and Gallop) selection and their respective attributes
        PARAMETERS:
            parent - (tk.Frame) the frame laser control frame is placed in
            laser - (Laser) handles the state of the laser
            experiment - (Experiment) handles the state of the experiment
            data_manager - (dataManager) accesses and updates config.json files
        """
        super().__init__(parent, "Laser Control Panel")
        self.laser = laser
        self.experiment = experiment
        self.data_manager = data_manager

        
        # Default to PIRL selected
        self.laser_option = tk.StringVar(value = "PIRL")

        # Row 1: Q-Tune and PIRL radio buttons
        row_1 = tk.Frame(self)
        row_1.pack(anchor="w", pady=(15, 15))

        self.rb_QTune = tk.Radiobutton(
            row_1,
            text="Q-Tune",
            variable=self.laser_option,
            command=self.change_laser_option,
            value="Q-Tune"
        )
        self.rb_QTune.pack(anchor="w")
        ToolTip(self.rb_QTune, "qTune_option_button")

        self.rb_PIRL = tk.Radiobutton(
            row_1,
            text="PIRL",
            variable=self.laser_option,
            command=self.change_laser_option,
            value="PIRL"
        )
        self.rb_PIRL.pack(anchor="w")
        ToolTip(self.rb_PIRL, "pirl_option_button")

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
        ToolTip(self.b_startLaser, "LaserStart")


        self.b_beginMeasure = tk.Button(
            row_2,
            text="Begin Measuring",
            font=("Roboto", 16),
            command= self.experiment_toggle,
            state = 'disabled'
        )
        self.b_beginMeasure.pack(side="left", padx=20)
        ToolTip(self.b_beginMeasure, "Measure")

        # Row 3: Radio buttons for laser mode (Regular Pulse or Gallop) + additional options for each mode
        row_3 = tk.Frame(self)
        row_3.pack(anchor="w", pady=(15, 15))

        # Default to Regular pulse mode selected
        self.laser_mode =tk.StringVar(value = "Regular Pulse")


        # Regular pulse mode button
        self.rb_regPulse = tk.Radiobutton(
            row_3, 
            text = "Regular Pulse", 
            variable=self.laser_mode,
            command = self.change_laser_mode,
            value = "Regular Pulse")
        self.rb_regPulse.pack(anchor = 'nw', side = 'top')
        ToolTip(self.rb_regPulse, "regular_pulse_button")

        # Frequency dropdown menu and shot count request
        regPulseMenu = tk.Frame(row_3)
        regPulseMenu.pack(pady = 5, padx = 5)

        self.ddRegFreq = self.create_dropdown(regPulseMenu) # ddRegFreq stands for dropdown regular frequency. 

        # Gallop mode button
        self.rb_gallop = tk.Radiobutton(
            row_3, 
            text = "Gallop (for Experiment)",
            variable=self.laser_mode,
            command = self.change_laser_mode,
            value = "Gallop")
        self.rb_gallop.pack(anchor = 'nw', side = 'top')
        ToolTip(self.rb_gallop, 'gallop mode')

        # Prepulse modes
        gallop_frame = tk.Frame(row_3)
        gallop_frame.pack(side = tk.LEFT, padx = 5, pady = 5)

        self.pulse_spacing = tk.StringVar(value = "prepulse")

        self.rb_prepulse =tk.Radiobutton(
            gallop_frame, 
            text="prepulse (Q-Tune: 2ms/ PIRL: 4ms spacing)", 
            variable=self.pulse_spacing,
            command = self.change_laser_pulse_spacing, 
            value="prepulse",
            state = "disabled",
            padx = 15)
        self.rb_prepulse .pack(anchor = "w")
        ToolTip(self.rb_prepulse , "prepulse")

        self.rb_noprepulse =tk.Radiobutton(
            gallop_frame, 
            text="no prepulse (8ms spacing)", 
            variable=self.pulse_spacing,
            command = self.change_laser_pulse_spacing, 
            value="no prepulse",
            state = "disabled", 
            padx = 15)
        self.rb_noprepulse.pack(anchor="w")
        ToolTip(self.rb_noprepulse, "no prepulse")

        # Entry box for getting a specifc number of laser shots through the shutter (only relevant to PIRL)
        self.entry_shot_count = EntryBox(
            frame = gallop_frame, 
            label_text = "Request open-shutter shots [#]", 
            variable = self.data_manager.V_shot_count,
            data_manager = self.data_manager,
            function = self.start_shot_count, 
            send= True)
        ToolTip(self.entry_shot_count.label, 'shot count')


    # Methods for toggling objects

    def laser_toggle(self):
        """
        DESCRIPTION:
            Calls toggle function on laser object, updates GUI.
        """
        self.laser.toggle()
        self.update_frame()


    def experiment_toggle(self, total_measurements = 0, mode = None):
        """
        DESCRIPTION:
            Calls toggle function on experiment object, updates GUI.
        """
        if self.experiment.e_experimentOn.is_set():
            self.experiment.stop()
        else:
            user_entered_input_values = messagebox.askyesno(
                title = "Input Values", 
                message = "Have you chosen an appropriate file path & entered values under 'Input Values'? These are inmportant if you want to save your files!")
            user_closed_shutter = messagebox.askyesno(
                title = "Shutter Reminder", 
                message="Make sure to close the shutter before proceeding! The pulses will fire correctly only if the shutter is closed.")
            if user_entered_input_values and user_closed_shutter:
                if self.laser.mode == "Regular Pulse":
                    messagebox.showinfo(title = 'Invalid laser mode', message = """"Please change laser to Gallop Mode before measuring.
                                    This is the only valid laser mode for measurement.""")
                    return
                self.experiment.start(total_measurements, mode, option = self.laser.option)
        self.update_frame()



    # Methods for calling change on the laser object and update GUI elements in response to the change

    def change_laser_option(self):
        """
        DESCRIPTION:
            Calls change_option on the laser object. Updates the laser mode.
        """
        option = self.laser_option.get()
        self.laser.change_option(option)
        self.change_laser_mode()
    

    def change_laser_mode(self):
        """
        DESCRIPTION:
            Calls change_mode on the laser object, updates GUI. 
            For regular pulse resets frequency to 10Hz / 100Hz for Q-Tune/pIRL, updates pulse spacing for Gallop.
        """
        mode = self.laser_mode.get()
        self.laser.change_mode(mode)
        if self.laser_mode.get() == "Regular Pulse":
            if self.laser.option == "Q-Tune":
                self.laser.change_frequency("10 Hz")
            else:
                self.laser.change_frequency("100 Hz")
        elif self.laser.option == "PIRL":
            self.change_laser_pulse_spacing()
        self.update_frame()
    

    def change_laser_frequency(self, event):
        """
        DESCRIPTION:
            Calls change_frequency on the laser object
        """
        frequency = self.ddRegFreq.get()
        self.laser.change_frequency(frequency)       


    def change_laser_pulse_spacing(self):
        """
        DESCRIPTION:
            Updates prepulse boolean in config.json and calls change_pulse_spacing on the laser object.
        """
        pulse_spacing = self.pulse_spacing.get()
        if pulse_spacing == "prepulse":
            self.data_manager.V_prepulse = True 
        if pulse_spacing == "no prepulse":
            self.data_manager.V_prepulse = False
        self.laser.change_pulse_spacing(pulse_spacing)


    # Helper methods that update GUI elements
    def update_frame(self):
        """
        DESCRIPTION:
            Updates all the GUI elements in laser control panel
        """
        if self.laser.e_laserOn.is_set() or self.experiment.e_experimentOn.is_set():
            self.disable_laser_option()
            self.disable_laser_mode()
        else:
            self.enable_laser_option()
            self.enable_laser_mode()
        if self.laser.option == "Q-Tune":
            self.update_toggle_buttons_QTune()
            self.entry_shot_count.disable()
        else:
            self.update_toggle_buttons_PIRL()
            self.entry_shot_count.enable()

        self.update_b_startLaser_text()
        self.update_b_beginMeasure_text()
        self.update_pulse_frame()



    def update_pulse_frame(self):
        """
        DESCRIPTION:
            Updates the Pulse frame (prepulse options, frequency dropdown)
        """
        self.update_ddRegFreq()
        if self.laser.mode == "Regular Pulse":
            self.disable_pulse_spacing()
        else:
            self.ddRegFreq.config(state= "disabled")
            self.enable_pulse_spacing
            if self.laser.option == "Q-Tune":
                self.disable_pulse_spacing()
                


    def update_toggle_buttons_QTune(self):
        """
        DESCRIPTION:
            Updates which of Begin Measure and Start Laser buttons are disabled/enabled with Q-Tune   
        """
        if self.laser.e_laserOn.is_set():
            self.b_beginMeasure.config(state="disabled")
        else:
            if self.experiment.e_experimentOn.is_set():
                self.b_startLaser.config(state="disabled")
            else:
                self.b_beginMeasure.config(state="normal")
                self.b_startLaser.config(state="normal")



    def update_toggle_buttons_PIRL(self):
        """
        DESCRIPTION:
            Updates which of Begin Measure and Start Laser buttons are disabled/enabled with PIRL
        """
        if self.laser.e_laserOn.is_set():
            self.b_beginMeasure.config(state="normal")
            if self.experiment.e_experimentOn.is_set():
                self.b_startLaser.config(state ="disabled")             
            else: 
                self.b_startLaser.config(state="normal")
        else:
            self.b_beginMeasure.config(state="disabled")



    def update_b_startLaser_text(self):
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



    def update_b_beginMeasure_text(self):
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



    def update_ddRegFreq(self):
        """
        DESCRIPTION:
            Changes the dropdown for PRR selection based on which laser is selected
        """
        if self.laser.option == "PIRL":
            self.ddRegFreq.configure(values = self.pirl_PRR_options)
            self.ddRegFreq.current(self.pirl_PRR_options.index("100 Hz"))
        else:
            self.ddRegFreq.configure(values = self.qTune_PRR_options)
            self.ddRegFreq.current(self.qTune_PRR_options.index("10 Hz"))



    # Helper methods for disabling/enabling panels

    def disable_laser_option(self):
        """
        DESCRIPTION:
            Disables pIRL/Q-Tune radiobuttons.
        """
        self.rb_QTune.config(state="disabled")
        self.rb_PIRL.config(state="disabled")


    def enable_laser_option(self):
        """
        DESCRIPTION:
            Enables pIRL/Q-Tune radiobuttons.
        """
        self.rb_QTune.config(state="normal")
        self.rb_PIRL.config(state="normal")

    
    def disable_pulse_spacing(self):
        """
        DESCRIPTION:
            Disables prepulse/no prepulse radiobuttons.
        """
        self.rb_noprepulse.config(state="disabled")
        self.rb_prepulse.config(state="disabled")

    
    def enable_pulse_spacing(self):
        """
        DESCRIPTION:
            Enables prepulse/no prepulse radiobuttons.
        """
        self.rb_noprepulse.config(state="normal")
        self.rb_prepulse.config(state="normal")


    def disable_laser_mode(self):
        """
        DESCRIPTION:
            Disables regular pulse/gallop, prepulse/no prepulse, and frequency dropdown.
        """
        self.rb_regPulse.config(state="disabled")
        self.rb_gallop.config(state="disabled")
        self.disable_pulse_spacing()
        self.ddRegFreq.config(state="disabled")


    def enable_laser_mode(self):
        """
        DESCRIPTION:
            Enables regular pulse/gallop, prepulse/no prepulse, and frequency dropdown.
        """
        self.rb_regPulse.config(state="normal")
        self.rb_gallop.config(state="normal")
        self.enable_pulse_spacing()
        self.ddRegFreq.config(state="enabled")




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
        self.pirl_PRR_options = ["200 Hz", "166.6 Hz", "125 Hz", 
                       "111.1 Hz", "100 Hz", "90.9 Hz", 
                       "66.6 Hz", "50 Hz", "40 Hz", 
                       "33.3 Hz", "25 Hz", "20 Hz", "10 Hz"]
        
        self.qTune_PRR_options = ["10 Hz", "5 Hz", "3.33 Hz", "2 Hz",
                                "1 Hz"]
        
        dropdown = ttk.Combobox(dropdownFrame, values  = self.pirl_PRR_options, width =10) # default with PIRL selected
        dropdown.bind("<<ComboboxSelected>>", self.change_laser_frequency)
        dropdown.pack()
        dropdown.current(self.pirl_PRR_options.index("100 Hz")) # sets 100 Hz to be the default
        
        return dropdown
    

    def start_shot_count(self):
        """
        DESCRIPTION:
            Request Teensy open shutter for the requested number of laser pulses. Do some error checking and confirmation first.
        PARAMETERS
            None.
        RETURN: 
            None.
        """
        if not self.laser.e_laserOn.is_set(): # if Laser is OFF
            messagebox.showinfo(title = 'Laser not on!', message = 'You must turn the laser on BEFORE requesting a fixed number of shots!')
            return
        else:
            req_shot_count = self.entry_shot_count.entry.get()
            if messagebox.askyesno(
                title = "Shot count", 
                message = f"Confirm requested shot count: {req_shot_count}. This will open the shutter for {req_shot_count} laser pulses."):
                self.entry_shot_count.on_enter()
                # message = f"shot_count:{req_shot_count}"    ->  !!! to be implemented when logic is placed
                # self.teensy.message(message)
                print(f"GUI sent shot request for {req_shot_count} shots")
    
   