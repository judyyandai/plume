# Plume experiment GUI main window

import tkinter as tk
from tkinter import ttk

from GUI.frames.laser_control import LaserControlFrame
from GUI.frames.heater_control import HeatingControlFrame
from GUI.frames.inputs_frame import InputsFrame
from GUI.frames.folder_frame import FolderFrame
from GUI.frames.camera_frame import CameraFrame

from logic.laser import Laser
from logic.PIDheater import Heater
from logic.experiment import Experiment

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


        # Frames
        self.laserControlFrame = LaserControlFrame(
            parent=self.Experiment_Frame, 
            laser=laser, 
            experiment=experiment,
            data_manager = dataManager)


        laser = Laser() # Create an instance of the Laser class to manage the laser state.
        experiment = Experiment() # Create an instance of the Experiment class to manage the experiment state.

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
        self.inputsFrame = InputsFrame(parent = self.scrollbar_frame)
        self.folderFrame = FolderFrame(parent = self.inputsFrame, data_manager=dataManager)

        heater = Heater() # Create an instance of the PID Heater class to manage the heater state.
        self.heaterControlFrame = HeatingControlFrame(parent = self.scrollbar_frame, heater = heater, data_manager=dataManager)

        self.cameraFrame = CameraFrame(parent = self.scrollbar_frame, data_manager=dataManager)

     def option_changed(self):
        """
        DESCRIPTION:
            When laser is option is changed in the Laser Option Frame,
            Laser Control Frame is updated accordingly.
        """
        self.laserControlFrame.update_b_beginMeasure()