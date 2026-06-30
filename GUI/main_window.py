# Plume experiment GUI main window
# created by Judy Dai and Robyn Astridge, ,major work done by Enzo Picini, Chloe Lawson, Kenny Lai, Gabriel Caribe, and Daniel Pinto


import tkinter as tk
from tkinter import ttk
from tkinter import font
import json # used for talking with config.json, which stores configuration variables for the GUI. 

class MainWindow:
     def __init__(self):# and device_connections"
        """
        DESCRIPTION:
            Initializes the main window of the GUI, sets up the layout, and initializes necessary components.
        CLASS ELEMENTS:
            window: Tkinter object for the root window, must be created by tk.Tk()
        """

        self.window = tk.Tk()
        self.window.title("Plume GUI 2026")
        self.window.geometry("1100x1300")