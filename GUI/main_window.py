# Plume experiment GUI main window

import tkinter as tk
from tkinter import ttk

from GUI.frames.laser import LaserFrame
from GUI.frames.heater import HeatingFrame
from GUI.frames.pulse_generator import PulseGeneratorFrame
from GUI.frames.file import FileFrame
from GUI.frames.folder import FolderFrame
from GUI.frames.camera import CameraFrame
from GUI.frames.pIRL import pIRLFrame
from GUI.frames.qTune import QTuneFrame
from GUI.frames.motor import MotorFrame
from GUI.frames.rs_flash_delay import RSFlashDelay

from logic.laser import Laser
from logic.PIDheater import Heater
from logic.experiment import Experiment
from logic.pulse_generator import PulseGenerator
from logic.motor import Motor
from logic.flash_delay_series import FlashDelaySeries
from logic.data_manager import DataManager


class MainWindow(tk.Tk):
     def __init__(self):# and device_connections"
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


        # Create instances of objects
        dataManager = DataManager()
        laser = Laser() 
        experiment = Experiment() 
        heater = Heater()
        pg = PulseGenerator()
        motor = Motor()
        flash_delay_series = FlashDelaySeries()


        # Frames
        self.laserControlFrame = LaserFrame(
            parent=self.Experiment_Frame, 
            laser=laser, 
            experiment=experiment,
            data_manager = dataManager)


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
            heater = heater, 
            data_manager=dataManager)

        self.inputsFrame = FileFrame(
            parent = self.scrollbar_frame)

        self.folderFrame = FolderFrame(
            parent = self.inputsFrame, 
            data_manager=dataManager)

        self.pgControlFrame = PulseGeneratorFrame(
            parent = self.scrollbar_frame, 
            data_manager = dataManager, 
            pg = pg)
        
        self.cameraFrame = CameraFrame(
            parent = self.scrollbar_frame, 
            data_manager=dataManager)
        
        self.pIRLFrame = pIRLFrame(
            parent = self.scrollbar_frame, 
            data_manager=dataManager)
        
        self.qTuneFrame = QTuneFrame(
            parent = self.scrollbar_frame, 
            data_manager= dataManager)
        
        self.motorFrame = MotorFrame(
            parent=self.scrollbar_frame, 
            data_manager=dataManager, 
            motor = motor)
        
 #       self.rsFlashDelayFrame = RSFlashDelay(
 #           parent = self.scrollbar_frame, 
 #           data_manager= dataManager, 
 #           pg_control_frame= self.pgControlFrame, 
 #           flash_delay_series= flash_delay_series)


