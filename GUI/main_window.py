# Plume experiment GUI main window

import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import time
import serial

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
from logic.objects.PIDheater import Heater
from logic.objects.experiment import Experiment
from logic.objects.pulse_generator import PulseGenerator
from logic.objects.motor import Motor
from logic.objects.flash_delay_series import FlashDelaySeries
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
        CLASS ELEMENTS:
            window: Tkinter object for the root window, must be created by tk.Tk()
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


        # Creating device objects  for GUI
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
        
        # Data storage object
        self.dataManager = DataManager()
        
        # Image frame
        self.imageFrame = ImageFrame(
            parent = self.Experiment_Frame,
            data_manager = self.dataManager)
        
        

        # Create instances of objects
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
            image_frame=self.imageFrame) 
        self.heater = Heater()
        self.pg = PulseGenerator()
        self.motor = Motor()
        self.flash_delay_series = FlashDelaySeries()

        # Laser frame
        self.laserControlFrame = LaserFrame(
            parent=self.Experiment_Frame, 
            laser=self.laser, 
            experiment=self.experiment,
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
            data_manager= self.dataManager)
        
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
        
 #       self.rsFlashDelayFrame = RSFlashDelay(
 #           parent = self.scrollbar_frame, 
 #           data_manager= dataManager, 
 #           pg_control_frame= self.pgControlFrame, 
 #           flash_delay_series= flash_delay_series)



        # This line forces self.on_close to run whenever the red X is pressed on the GUI 
        self.protocol("WM_DELETE_WINDOW", self.on_close)


     def on_close(self):
        """
        DESCRIPTION:
            Custom close function to ensure safe closing of the GUI software: Attempts to terminate all threads. Turns off laser. Turns off heater module.
        """
       
        if messagebox.askokcancel("Quit", "Do you want to quit?"):
            # shuts off laser if it's on. 
            if self.laser.e_laserOn.is_set():
                self.laser.toggle()
                
            if self.heater.e_heaterOn.is_set():
                self.heater.toggle()
            
            if self.experiment.e_experimentOn.is_set():
                self.experiment.toggle()
                # self.StopExperiment() !!! do we need something similar?
                
                
            #if self.F_1Hz:
            #    self.F_1Hz = False
            #    self.B_1Hz.config(text="Start 1Hz Imaging")
            #    self.Stop1Hz()    !!! implement later
            
            # self.heater.stop() !!! need?
                
            time.sleep(3)
            # Destroy the main window
            # check what threads are still running:
            
            # self.E_check_heater.clear() # tell the heater thread to stop checking temperrature. !!! need to implement

        #    print(f"check heater Event value: {self.E_check_heater.is_set()}")
        #    for thread in threading.enumerate():
        #        print(f"{thread.name}, Alive: {thread.is_alive()}, {thread.daemon}")
        #        # if thread.name !="MainThread":
        #        #     thread.join(timeout = 5)
        #        #     if thread.is_alive():
        #        #         print(f"{thread.name} failed to close in time.")
        #    # closing the check_heater thread:
        #    if hasattr(self, "T_check_heater") and self.T_check_heater.is_alive():
        #        print("Waiting for heater thread to close . . ")
        #        self.T_check_heater.join(timeout = 5)
        #        if self.T_check_heater.is_alive():
        #            print("T_check_heater did not exit in time!")
        #        else:
        #            print("T_check_heater successfully closed")    !!! need

            self.destroy()