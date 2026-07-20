# Plume experiment GUI main window

import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import time
import serial
import threading
from threading import Lock
from controllers.experiment import ExperimentController
from GUI.frames.laser import LaserFrame
from GUI.frames.image import ImageFrame
from GUI.frames.heater import HeatingFrame
from GUI.frames.pulse_generator import PulseGeneratorFrame
from GUI.frames.lens import LensFrame
from GUI.frames.camera import CameraFrame
from GUI.frames.pIRL import pIRLFrame
from GUI.frames.qTune import QTuneFrame
from GUI.frames.motor import MotorFrame
from GUI.frames.rs_flash_delay import RSFlashDelay

from logic.objects.laser import Laser
from logic.objects.experiment import Experiment
from logic.objects.data_manager import DataManager

from logic.Plupy import Plupy as pl
from logic.Plupy.pirl import pirl
from logic.Plupy.pulse_generator import pulse_generator
from logic.Plupy.teensy import teensy
from logic.Plupy.oscilloscope import oscilloscope
from logic.Plupy.function_generator import function_generator
from logic.Plupy.vacuum_meter import vacuumMeter
from logic.Plupy.heater import heater
from logic.Plupy.arduino_UNO import arduino_UNO
from logic.Plupy.stepper_motor import stepper_motor
from logic.Plupy.thor_camera import thor_camera
from logic.Plupy.Coherent import Coherent


class MainWindow(tk.Tk):
     def __init__(self, device_connections):
        """
        DESCRIPTION:
            Initializes the main window of the GUI, sets up the layout, and initializes necessary components.
        PARAMETERS:
            device_connections - serial connections
        """

        super().__init__()
        self.title("Plume GUI 2026")
        self.geometry("1100x1300")
        self.option_add("*Font", "Roboto 12")

        # Experiment tab, currently there are no other tabs, but future expansions may include additional tabs for other functionalities.
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(expand = True, fill = 'both')
        self.Experiment_Frame = tk.Frame(self.notebook, width = 1700, height = 1440)
        self.Experiment_Frame.pack()
        self.notebook.add(self.Experiment_Frame, text = "Experiment")

        # Creating plupy device objects for GUI
        COM_ports = pl.COM_ports
        self.pirl_con, self.pg_con, self.motor_con, self.uno_con, self.teensy_con, self.vaccumMeter_con, self.heater_con, self.coherent_con = device_connections
        self.pirl = pirl(COM_ports["pirl"],  19200, serial.EIGHTBITS, serial.PARITY_NONE, serial.STOPBITS_ONE, self.pirl_con)
        self.pg = pulse_generator(COM_ports["pg"],  115200, serial.EIGHTBITS, serial.PARITY_NONE,  serial.STOPBITS_ONE, self.pg_con)
        self.teensy = teensy(COM_ports["teensy"],  115200, serial.EIGHTBITS,  serial.PARITY_NONE, serial.STOPBITS_ONE, self.teensy_con)
        self.osc_TDS2014C = oscilloscope("TDS 2014C")
        self.osc_DPO2024B = oscilloscope("DPO 2024B")
        self.fg = function_generator()
        self.vacuumMeter = vacuumMeter(COM_ports["vacuumMeter"],  19200, serial.EIGHTBITS,  serial.PARITY_NONE, serial.STOPBITS_ONE, self.vaccumMeter_con) 
        self.heater = heater(COM_ports["heater"],  19200, serial.EIGHTBITS,  serial.PARITY_NONE, serial.STOPBITS_ONE, self.heater_con)
        self.uno = arduino_UNO(COM_ports["uno"],  115200, serial.EIGHTBITS,  serial.PARITY_NONE, serial.STOPBITS_ONE, self.uno_con)
        self.motor = stepper_motor(COM_ports["motor"], 9600, serial.SEVENBITS, serial.PARITY_ODD, serial.STOPBITS_TWO, self.motor_con)
        self.cam = thor_camera()
        self.coherent = Coherent(COM_ports["Coherent"], 19200, serial.EIGHTBITS, serial.PARITY_NONE,  serial.STOPBITS_ONE, self.coherent_con)
    
        # Create instances of objects
        #!!! IF TIME please make this Lock() object an attriibute of hte oscilloscope class, and include 'with Lock:' on every commmunication method
        self.visa_lock = Lock()  #used for all visa comms with the oscilloscope
        self.dataManager = DataManager()
        self.laser = Laser(
            teensy=self.teensy)
        self.experiment = Experiment(
            vacuum_meter=self.vacuumMeter, 
            data_manager=self.dataManager, 
            pg=self.pg,
            teensy = self.teensy,
            osc_TDS2014C = self.osc_TDS2014C,
            osc_DPO2024B = self.osc_DPO2024B,
            cam = self.cam,
            uno = self.uno,
            coherent = self.coherent,
            visa_lock = self.visa_lock) 


        # Image frame
        self.imageFrame = ImageFrame(
            parent = self.Experiment_Frame,
            data_manager = self.dataManager)

        self.laserControlFrame = LaserFrame(
            parent=self.Experiment_Frame, 
            laser=self.laser,
            data_manager = self.dataManager)
        
        # Create a canvas for scrollable content
        canvas = tk.Canvas(self.Experiment_Frame, width=500, height = 1500)
        canvas.pack(side="left", anchor = "nw", padx=5, pady= 20)

        # Add a scrollbar
        scrollbar = tk.Scrollbar(self.Experiment_Frame, orient="vertical", command=canvas.yview)
        scrollbar.pack(side="left", fill="y")

        # Configure the canvas to use the scrollbar
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.bind("<Configure>", lambda e: canvas.config(scrollregion=canvas.bbox("all")))
        
        # Create a frame inside the canvas to hold the widgets
        self.scrollbar_frame = tk.Frame(canvas)
        canvas.create_window((0, 0), window=self.scrollbar_frame, anchor="nw")


        # Frames inside Scrollable Content:
        self.heaterControlFrame = HeatingFrame(
            parent = self.scrollbar_frame, 
            heater = self.heater, 
            data_manager=self.dataManager)
        
        self.lensFrame = LensFrame(
            parent = self.scrollbar_frame, 
            data_manager=self.dataManager)

        self.pgControlFrame = PulseGeneratorFrame(
            parent = self.scrollbar_frame, 
            data_manager = self.dataManager, 
            pg = self.pg)
        
        self.cameraFrame = CameraFrame(
            parent = self.scrollbar_frame, 
            data_manager= self.dataManager,
            experiment = self.experiment)
        
        self.pIRLFrame = pIRLFrame(
            parent = self.scrollbar_frame, 
            data_manager= self.dataManager)
        
        self.qTuneFrame = QTuneFrame(
            parent = self.scrollbar_frame, 
            data_manager= self.dataManager,
            laser = self.laser)
        
        self.motorFrame = MotorFrame(
            parent=self.scrollbar_frame, 
            data_manager=self.dataManager, 
            motor = self.motor)

        
        self.rsFlashDelayFrame = RSFlashDelay(
           parent = self.scrollbar_frame, 
           data_manager= self.dataManager, 
           pg_control_frame= self.pgControlFrame,
           laser = self.laser)
        
        # Experiment controller to coordinate experiment object with image frame and pg frame
        self.experimentController = ExperimentController(
            experiment = self.experiment,
            laser_frame = self.laserControlFrame, 
            image_frame= self.imageFrame, 
            pg_frame = self.pgControlFrame, 
            rsfd_frame = self.rsFlashDelayFrame)

        # This line forces self.on_close to run whenever the red X is pressed on the GUI 
        self.protocol("WM_DELETE_WINDOW", self.on_close)

        #!!! pirl stuff?
        # try:
        #     teensy_state = int(self.teensy.message("on:?")) # ask the teensy if it's on
        # except:
        #     teensy_state = 1
        # if teensy_state == 1:
        #     print("GUI Laser was on before GUI bootup")
        #     self.laser.toggle() # make the button reflect that the laser is on
        # elif teensy_state == 0:
        #     pass
        # else:
        #     print(f"GUI confused, teensy responded to 'on?' with a number that is NOT 0 or 1. See line {inspect.currentframe().f_lineno}")

        with self.visa_lock:
            self.osc_TDS2014C.recall(9) # Recall setting 9 on TDS2014C oscilloscope
            self.osc_TDS2014C.setup(1, 1, "MAXImum")  # Let the first measurement probe the maximum voltage value of the first channel
        
            self.osc_DPO2024B.recall(8) #Recall setting 8 on DPO2024B     



     def on_close(self):
        """
        DESCRIPTION:
            Custom close function to ensure safe closing of the GUI software: Attempts to terminate all threads.
            Turns off laser. Turns off heater module. Turns off experiment.
        """
       
        if messagebox.askokcancel("Quit", "Do you want to quit?"):
            # shuts off laser if it's on. 
            if self.laser.e_laserOn.is_set():
                self.laser.toggle()
                
            if self.heaterControlFrame.e_heaterOn.is_set():
                self.heaterControlFrame.heater_toggle()
            
            if self.experiment.e_experimentOn.is_set():
                self.experiment.stop()
                
                
            #if self.F_1Hz:
            #    self.F_1Hz = False
            #    self.B_1Hz.config(text="Start 1Hz Imaging")
            #    self.Stop1Hz()    !!! implement later
        
                
            time.sleep(3)
            # Destroy the main window
            # check what threads are still running:
            
            self.heaterControlFrame.e_checkHeater.clear() # tell the heater thread to stop checking temperature.

            print(f"check heater Event value: {self.heaterControlFrame.e_checkHeater.is_set()}")
            for thread in threading.enumerate():
                print(f"{thread.name}, Alive: {thread.is_alive()}, {thread.daemon}")
 
            # closing the check_heater thread:
            self.heaterControlFrame.close_check_heater()

            self.destroy()