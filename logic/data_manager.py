# Class for reading, writing, and modifying config.json files

import json
import tkinter as tk
import os
import numpy as np

class DataManager:
    def __init__(self, filename = "config.json"):
        self.filename = filename

        #* Loading saved config - any default values that are saved in the entry box and appear on start are in this config.json and can be saved
        current_working_directory = os.path.dirname(__file__) # current working directory
        print(f"CWD: {current_working_directory}")
        self.config_filepath = os.path.join(current_working_directory, 'config.json')

        with open(self.config_filepath, "r") as file:
                config = json.load(file)
                self.config_json = config #! this gets used in update_config_file
                self.V_save = tk.BooleanVar(value=config['save'])
                self.V_FlashDelay_us = tk.DoubleVar(value=config['flash delay']) # Flash Delay (Default is Zero)
                self.V_DelayBetweenTriggers = tk.DoubleVar(value=config['delay between triggers'])  # Delay Between Triggers
                self.V_PrePulse = tk.BooleanVar(value = config['prepulse'])  # if true will send a pre pulse, otherwise it won't (Default is False)
                self.V_CamGain = tk.DoubleVar(value=config['camera gain'])  # Gain of the camera (Default is zero)
                self.V_q1c = tk.IntVar(value=config['q1c'])  # q1c of the PIRL
                self.V_MotorStepDistance = tk.DoubleVar(value = config['motor step size']) # Number of steps for the motor to move
                self.V_start_delay_us = tk.DoubleVar(value = config["flash delay start"])
                self.V_stop_delay_us = tk.DoubleVar(value = config['flash delay stop'])
                self.V_interval_us = tk.DoubleVar(value = config['flash delay step size'])
                self.V_meas_per_delay = tk.IntVar(value = config['flash delay measurements per step'])
                self.V_times_run = 0 # what is this - Daniel 2025
                self.folder = tk.StringVar(value = config['folder'])
                self.V_lens = tk.DoubleVar(value = config['lens focal length'])
                self.V_lens_height = tk.DoubleVar(value = config['lens height'])
                self.V_start_power = tk.DoubleVar(value = config['power start'])
                self.V_stop_power = tk.DoubleVar(value = config['power stop'])
                self.V_p_interval = tk.DoubleVar(value = config['power step size'])
                self.V_p_meas_per_delay = tk.IntVar(value = config['power measurements per step'])
                self.V_shot_count = tk.IntVar(value = config['shots wanted'])
                self.V_Kp= tk.DoubleVar(value = config['Kp'])
                self.V_Ki= tk.DoubleVar(value = config['Ki'])
                self.V_Kd= tk.DoubleVar(value = config['Kd'])
                self.V_target_temp_C = tk.DoubleVar(value = config['target temp'])
                self.V_autocorrector = tk.BooleanVar(value = config['autocorrect'])
                self.V_curr_x_position = tk.DoubleVar(value = config['current x pos'])
                self.V_curr_y_position = tk.DoubleVar(value = config['current y pos'])
                self.V_qTune_wavelength = tk.DoubleVar(value=config['qtune wavelength'])
                self.V_qTune_pump = tk.IntVar(value = config['qtune pump'])
                # note that config['max safety temp'] is ONLY modifiable by manually changing config.json. 
                self.V_max_target_temp = tk.DoubleVar(value = config['max safety temp']) # max target temperature allowed

                # These are variables created to store values and image currently display on the GUI
                self.currDelayTrue = 0.0
                self.currDelaySet = 0.0
                self.currVoltage = 0.0
                self.currPVoltage = 0.0
                self.currIsPrePulse = False
                self.currFiringDelay = 0.0
                self.currImage = np.empty([1,1])
                
                #Store the current state of the system
                self.pressure = 0.0

                # Store the maximum and minimum values for the motor position in [mm]
                self.max_x = 50.0
                self.min_x = -50.0
                self.max_y = 10.0
                self.min_y = -10.0
                
                # The photo object to store the image currently being displayed by the GUI 
                # This is to prevent the photo object from being erase after the camera_control thread ends
                self.photo = None
                




    def update_config_file(self):
        """
        DESCRIPTION:
            .get() on every tkinter variable we want to save and set it to it's respective json value in the class variable. Then, write this to the config.json file. 
        PARAMETERS:
            None
        RETURN:
            None.
        """
        # get every variable and set it to the self.config_json. Then write this c
        self.config_json['save'] = self.V_save.get()
        self.config_json['flash delay'] = self.V_FlashDelay_us.get()
        self.config_json['delay between triggers'] = self.V_DelayBetweenTriggers.get()
        self.config_json['prepulse'] = self.V_PrePulse.get()
        self.config_json['camera gain'] = self.V_CamGain.get()
        self.config_json['q1c'] = self.V_q1c.get()
        self.config_json['motor step size'] = self.V_MotorStepDistance.get()
        self.config_json['flash delay start'] = self.V_start_delay_us.get()
        self.config_json['flash delay stop'] = self.V_stop_delay_us.get()
        self.config_json['flash delay step size'] = self.V_interval_us.get()
        self.config_json['flash delay measurements per step'] = self.V_meas_per_delay.get()
        self.config_json['folder'] = self.folder.get()
        self.config_json['lens focal length'] = self.V_lens.get()
        self.config_json['lens height'] = self.V_lens_height.get()
        self.config_json['power start'] = self.V_start_power.get()
        self.config_json['power stop'] = self.V_stop_power.get()
        self.config_json['power step size'] = self.V_p_interval.get()
        self.config_json['power measurements per step'] = self.V_p_meas_per_delay.get()
        self.config_json['shots wanted'] = self.V_shot_count.get()
        self.config_json['Kp'] = self.V_Kp.get()
        self.config_json['Ki'] = self.V_Ki.get()
        self.config_json['Kd'] = self.V_Kd.get()
        self.config_json['target temp'] = self.V_target_temp_C.get()
        self.config_json['autocorrect'] = self.V_autocorrector.get()
        self.config_json['current x pos'] = self.V_curr_x_position.get()
        self.config_json['current y pos'] = self.V_curr_y_position.get()
        self.config_json['qtune wavelength'] = self.V_qTune_wavelength.get()
        self.config_json['qtune pump'] = self.V_qTune_pump.get()
        

        #* What's nice about this way of doing it is it's NON DESTRUCTIVE - if there are other variables living in config.json, it doesn't just eliminiate them like it used to with config.csv
    
        with open(self.config_filepath, "w") as file:
            json.dump(self.config_json, file, indent = 4)
        
        print("Updated config.json!")