# Plume experiment GUI main window
# created by Judy Dai and Robyn Astridge, ,major work done by Enzo Picini, Chloe Lawson, Kenny Lai, Gabriel Caribe, and Daniel Pinto


import tkinter as tk
from tkinter import ttk
from tkinter import font
from GUI.frames.laser_option import LaserOptionFrame
from GUI.frames.laser_control import LaserControlFrame
import json # used for talking with config.json, which stores configuration variables for the GUI. 


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

        self.notebook = ttk.Notebook(self)
        self.notebook.pack(expand = True, fill = 'both')
        self.Experiment_Frame = tk.Frame(self.notebook, width = 1700, height = 1440)
        self.Experiment_Frame.pack()
        self.notebook.add(self.Experiment_Frame, text = "Experiment")

        # Frames
        self.laser_option_frame = LaserOptionFrame(self.Experiment_Frame)

        self.laser_control_frame = LaserControlFrame(self.Experiment_Frame)


